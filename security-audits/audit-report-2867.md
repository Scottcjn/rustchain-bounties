# RustChain Security Audit Report — Bounty #2867

**Date**: 2026-04-09  
**Scope**: RustChain node codebase (Rust miner + Python tools)  
**Auditor**: zhaog100  

---

## Executive Summary

The audit reviewed `rustchain-miner/` (Rust), `star_tracker.py`, and related Python tooling. **6 findings** identified: 1 Critical, 2 High, 2 Medium, 1 Low.

---

## Findings

### CRITICAL-01: TLS Certificate Verification Disabled

**File**: `rustchain-miner/src/network/tls.rs`  
**Severity**: 🔴 Critical  
**Impact**: Man-in-the-middle attacks can intercept/modify all API communications

```rust
// tls.rs — accepts ANY certificate, including forged ones
let client = Client::builder()
    .danger_accept_invalid_certs(true)  // ⚠️ MITM possible
```

**Recommendation**: 
- Pin the node's self-signed certificate or use certificate pinning
- Implement a trust-on-first-use (TOFU) model
- At minimum, validate the certificate fingerprint matches expected value

---

### HIGH-01: Hardcoded Node IP Address

**File**: `rustchain-miner/src/config.rs`, `rustchain-miner/src/cli.rs`  
**Severity**: 🟠 High  
**Impact**: Single point of failure, DNS-less routing to a fixed IP

```rust
// config.rs
pub const DEFAULT_NODE_URL: &str = "https://50.28.86.131";

// cli.rs
#[arg(long, default_value = "https://50.28.86.131")]
pub node: String,
```

**Recommendation**: Use domain names with DNS, not raw IPs. Implement node discovery or fallback nodes.

---

### HIGH-02: Hardware Fingerprint Spoofing

**File**: `rustchain-miner/src/hardware/`, `rustchain-miner/src/payload.rs`  
**Severity**: 🟠 High  
**Impact**: Miners can spoof hardware fingerprints to bypass VM detection and run multiple instances

The fingerprint checks (`anti_emulation.rs`, `cache_timing.rs`, etc.) all run **client-side** with results self-reported to the server. A modified miner can:
1. Report `passed: true` for all checks regardless of actual state
2. Spoof MAC addresses, CPU serials, and timing data
3. Run unlimited instances on cloud VMs

**Recommendation**: Server-side validation of fingerprints. Implement challenge-response for timing-based checks.

---

### MEDIUM-01: Nonce Generation Without Server Verification

**File**: `rustchain-miner/src/payload.rs`  
**Severity**: 🟡 Medium  
**Impact**: Replay attacks possible with locally-generated nonces

```rust
pub fn generate_local_nonce() -> String {
    let mut bytes = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut bytes);
    hex::encode(bytes)
}
```

If the server nonce endpoint fails, the miner falls back to a local nonce, which could allow replay of attestation payloads.

**Recommendation**: Fail closed — if server nonce is unavailable, do not submit. Never use local nonces for production attestation.

---

### MEDIUM-02: SQLite SQL Injection Risk in star_tracker.py

**File**: `star_tracker.py`  
**Severity**: 🟡 Medium  
**Impact**: Potential SQL injection via unsanitized repo names

```python
# Uses string formatting in SQL queries
cursor.execute(f"SELECT * FROM repos WHERE name = '{repo_name}'")
```

While the data source (GitHub API) is somewhat trusted, this pattern is vulnerable if repo names contain SQL metacharacters.

**Recommendation**: Use parameterized queries: `cursor.execute("SELECT * FROM repos WHERE name = ?", (repo_name,))`

---

### LOW-01: Sensitive Data in CLI Output

**File**: `rustchain-miner/src/attestation.rs`  
**Severity**: 🟢 Low  
**Impact**: Wallet addresses and hardware info logged to stdout

```rust
println!("║  Wallet : {:<38} ║", wallet);
println!("  Serial : {}", hw.cpu_serial);
println!("  MACs   : {:?}", hw.macs);
```

Wallet addresses and hardware identifiers are printed in plaintext, visible in process lists and logs.

**Recommendation**: Mask sensitive output in production mode. Add `--quiet` flag.

---

## Summary

| ID | Severity | Finding | Status |
|----|----------|---------|--------|
| CRITICAL-01 | 🔴 | TLS verification disabled | Open |
| HIGH-01 | 🟠 | Hardcoded IP address | Open |
| HIGH-02 | 🟠 | Client-side fingerprint spoofing | Open |
| MEDIUM-01 | 🟡 | Local nonce fallback | Open |
| MEDIUM-02 | 🟡 | SQL injection risk | Open |
| LOW-01 | 🟢 | Sensitive data in output | Open |

**Overall Risk**: HIGH — The TLS issue alone allows full MITM, and combined with client-side fingerprinting, the integrity of the mining system cannot be guaranteed without server-side remediation.
