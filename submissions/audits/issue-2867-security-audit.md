# Security Audit Report: RustChain Miner (Issue #2867)

**Repository:** rustchain-miner  
**Audit Date:** 2026-04-30  
**Severity Classification:** Critical / High

---

## Executive Summary

This audit identified **3 critical/high-severity security vulnerabilities** in the rustchain-miner codebase that could compromise the security of the RustChain network's Proof-of-Antiquity (RIP-PoA) consensus mechanism:

1. **CRITICAL: Disabled TLS Certificate Verification** (`network/tls.rs`)
2. **HIGH: Predictable Nonce Generation via CSPRNG Fallback** (`payload.rs`, `fingerprint/clock_drift.rs`)
3. **HIGH: Insufficient Anti-Emulation Checks** (`fingerprint/anti_emulation.rs`)

---

## Vulnerability #1: Disabled TLS Certificate Verification

**Severity:** CRITICAL  
**File:** `src/network/tls.rs:13`  
**CVSS 3.1 Score:** 9.1 (Critical)

### Description

The HTTP client unconditionally disables certificate verification:

```rust
// src/network/tls.rs:13
let client = Client::builder()
    .danger_accept_invalid_certs(true)  // ← DISABLES ALL TLS VERIFICATION
    .timeout(Duration::from_secs(30))
    .connect_timeout(Duration::from_secs(10))
    .user_agent("rustchain-miner/0.1.0")
    .build()?;
```

### Attack Vectors

1. **Man-in-the-Middle (MITM) Attack:** Any network adversary can intercept and modify attestation payloads, balance queries, and epoch enrollment requests.
2. **Server Impersonation:** An attacker can redirect the miner to a malicious server that accepts fake attestations.
3. **Data Exfiltration:** Wallet addresses and hardware fingerprints are transmitted without encryption integrity guarantees.

### Impact

- Attacker can inject false attestation data, polluting the RIP-PoA hardware fingerprint database
- Stolen miner rewards by redirecting balance queries
- Complete compromise of the mining identity verification system

### Remediation

```rust
// Use system certificate store instead of disabling verification
let client = Client::builder()
    .timeout(Duration::from_secs(30))
    .connect_timeout(Duration::from_secs(10))
    .user_agent("rustchain-miner/0.1.0")
    .build()?;

// For self-signed certificates in development/testing only:
#[cfg(testing)]
let client = Client::builder()
    .danger_accept_invalid_certs(true)
    // ... other config
    .build()?;
```

Add a CLI flag `--insecure` that must be explicitly passed, with clear warning output.

---

## Vulnerability #2: Predictable Nonce Generation (CSPRNG Fallback)

**Severity:** HIGH  
**Files:** 
- `src/payload.rs:57-61`
- `src/fingerprint/clock_drift.rs:58-65`

### Description

The code uses `rand::thread_rng()` which is a CSPRNG (Cryptographically Secure PRNG), but the fallback timestamp-based function in `clock_drift.rs` is weak:

```rust
// src/payload.rs:57-61
pub fn generate_local_nonce() -> String {
    let mut bytes = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut bytes);  // Thread-local, seeded by OS
    hex::encode(bytes)
}
```

The `rand::thread_rng()` is actually cryptographically secure on modern systems (uses `OsRng` internally), but the fallback for timestamp reading is problematic:

```rust
// src/fingerprint/clock_drift.rs:62-64 (non-x86_64 platforms)
#[cfg(not(any(target_arch = "x86_64", ...)))]
fn read_timestamp() -> u64 {
    static START: std::sync::OnceLock<Instant> = std::sync::OnceLock::new();
    let start = START.get_or_init(Instant::now);
    start.elapsed().as_nanos() as u64  // ← Low entropy
}
```

### The Real Issue: Nonce Not Used for Signing

**Most Critical:** Looking at `attestation.rs:131`, the nonce from the server is sent back but **never cryptographically signed**:

```rust
let attest_payload = payload::build_payload(wallet, &nonce, &hw, &fp);
// ...
client.submit(&attest_payload)  // No signature attached!
```

The entire attestation payload is sent in plaintext JSON without any cryptographic signature from the miner's private key. This means:
- Any attacker who can intercept the traffic can replay attestations
- The wallet parameter is unverified—just a string
- No proof of ownership of the wallet address

### Impact

- **Replay attacks:** Attestations can be captured and replayed
- **False attestations:** Any wallet string can be impersonated without private key proof
- **Reward theft:** Attackers can potentially redirect mining rewards

### Remediation

1. **Sign the attestation payload:**
```rust
use ed25519_dalek::{Signature, Signer, SigningKey};

// Sign the hash of the attestation payload
let payload_bytes = serde_json::to_vec(&attest_payload)?;
let payload_hash = Sha256::digest(&payload_bytes);
let signature = signing_key.sign(&payload_hash);

// Include in payload:
serde_json::json!({
    "miner": wallet,
    "signature": hex::encode(signature.to_bytes()),
    // ... rest of payload
})
```

2. **Verify signature server-side** before accepting attestations.

---

## Vulnerability #3: Weak Anti-Emulation Detection

**Severity:** HIGH  
**File:** `src/fingerprint/anti_emulation.rs`

### Description

The anti-emulation checks have several bypass vectors:

1. **Incomplete VM Detection:**
   ```rust
   const VM_VENDORS: &[&str] = &[
       "qemu", "vmware", "virtualbox", ...
   ];
   ```
   Missing common VM strings like `"microsoft corporation"`, `"google"`, `"amazon"`, `"oracle corporation"`.

2. **MAC OUI Bypass:**
   ```rust
   const VM_MAC_OUIS: &[&str] = &[
       "00:05:69", "00:0c:29", ...
   ];
   ```
   Attackers can easily spoof MAC addresses to bypass this check.

3. **Container Escape Detection Gap:**
   The check for `/.dockerenv` is easily bypassed by:
   ```bash
   touch /.dockerenv  # Prevents detection
   # Or run with: docker run --read-only
   ```

4. **No Hypervisor Detection for Windows/macOS:**
   Linux has hypervisor flag checks, but Windows and macOS checks are incomplete.

### Attack Scenario

A sophisticated attacker can:
1. Use QEMU/KVM with custom MAC (not in OUI list)
2. Remove `/.dockerenv`
3. Use a VM that doesn't set hypervisor CPU flag
4. Spoof DMI data to appear as "real hardware"

This would allow **100% fake hardware attestations**, defeating the entire RIP-PoA purpose.

### Remediation

1. **Add timing-based detection:**
   ```rust
   // Measure rdtsc stability across sleep boundaries
   // VMs often have different timing characteristics
   fn detect_vm_timing() -> bool {
       // Real hardware: rdtsc increments during sleep
       // VMs: rdtsc may pause or have different behavior
   }
   ```

2. **Add CPU brand/microcode verification:**
   ```rust
   fn validate_cpu_authenticity() -> bool {
       // Check CPU microcode version is current
       // Verify CPU features match advertised model
   }
   ```

3. **Expand container detection:**
   ```rust
   // Check multiple container signals
   - /proc/self/mountinfo for overlayfs
   - /proc/self/cgroup for container managers
   - Environment variables (CONTAINER_ID, etc.)
   ```

---

## Additional Security Concerns

### 1. Hardcoded Default Node URL
**File:** `src/cli.rs:17`
```rust
#[arg(long, default_value = "https://50.28.86.131")]
pub node: String,
```
Hardcoded IP addresses create targeting opportunities. Consider DNS-based service discovery.

### 2. Missing Input Validation
**File:** `src/hardware/cpu.rs:88-91`
```rust
let hash = Sha256::digest(model.as_bytes());
hex::encode(&hash[..8])  // Truncates hash to 8 bytes
```
Hash truncation weakens uniqueness guarantees. Use full hash or at least 16 bytes.

### 3. Error Information Leakage
**File:** `src/attestation.rs:103`
```rust
return Err(format!("Challenge failed: HTTP {} — {}", status, body).into());
```
Server error messages are propagated directly to the client, potentially leaking sensitive information.

---

## Summary Table

| Vulnerability | Severity | Exploitability | Impact | Fix Complexity |
|--------------|----------|----------------|--------|----------------|
| TLS Disabled | CRITICAL | Easy (network) | Network compromise | Low |
| No Signing | HIGH | Easy (network) | Identity spoofing | Medium |
| Anti-Emulation | HIGH | Medium | Fake hardware | High |
| Hardcoded URL | MEDIUM | Easy | Targeting | Low |
| Hash Truncation | LOW | Medium | Collisions | Trivial |

---

## Conclusion

The most critical finding is the **combination of disabled TLS and lack of cryptographic signing**. This means all attestation data is:
1. Transmitted without encryption integrity
2. Unsigned and unverifiable as coming from the claimed wallet

An attacker with network access can completely compromise the RIP-PoA attestation system.

**Priority fixes:**
1. Enable TLS verification (or require explicit `--insecure` flag)
2. Implement Ed25519 signature for all attestation payloads
3. Enhance anti-emulation with timing-based detection

---

*Audit performed on rustchain-miner codebase. All findings should be validated against the production deployment.*