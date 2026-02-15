# Proof-of-Attestation & Hardware Fingerprinting

## Overview
Proof-of-Attestation (PoA) is the core security layer of RustChain. It ensures that every participating miner is a unique, physical piece of hardware. This is achieved through a multi-layered fingerprinting system that detects Virtual Machines (VMs), containers, and hardware emulation.

## The Attestation Lifecycle

### 1. Challenge Phase
Miners must request a fresh **Nonce** from the node before every submission. Nonces are short-lived (usually 10 minutes) to prevent replay attacks.
- **Endpoint**: `POST /attest/challenge`
- **Response**: `{ "nonce": "...", "server_time": 1771038696 }`

### 2. Hardware Fingerprinting (The 6+1 Checks)
The miner client executes a suite of checks to prove its physical identity. If any check fails, the miner is flagged as "Flagged" and receives a **0x multiplier** (or a 1-billionth penalty).

| Check ID | Name | Description |
|---|---|---|
| **Check 1** | **Anti-Emulation** | Detects VM signatures (e.g., VirtIO, VMware/VirtualBox MACs, QEMU CPU flags). |
| **Check 2** | **CPU Features** | Verifies specific hardware flags (e.g., AltiVec for PowerPC, AVX-512 for modern x86) to match claimed architecture. |
| **Check 3** | **I/O Latency** | Measures disk and network stack jitter. Emulated I/O paths typically show lower jitter than physical disks. |
| **Check 4** | **Serial Binding** | Extracts and binds the submission to hardware serials (DMI/UUID on Linux, IOKit on macOS). |
| **Check 5** | **MAC Consistency** | Verifies the hardware MAC address against vendor OUI databases to ensure it's not a spoofed virtual interface. |
| **Check 6** | **Network Topology** | Analyzes the network path and hostname to ensure it matches a typical physical machine setup. |
| **+1 Bonus** | **Entropy Score** | Measures CPU clock drift (jitter) using tight execution loops. Higher entropy = more likely to be real silicon. |

### 3. Submission Phase
The miner constructs a JSON payload containing the hardware report and a cryptographic commitment.

**Payload Structure:**
```json
{
  "miner": "WALLET_ADDRESS_RTC",
  "miner_id": "FRIENDLY_DEVICE_NAME",
  "nonce": "SERVER_PROVIDED_NONCE",
  "report": {
    "commitment": "sha256(nonce + wallet + entropy_data)",
    "entropy_score": 0.0045,
    "derived": { "mean_ns": 25000, "variance_ns": 450 }
  },
  "device": {
    "family": "PowerPC",
    "arch": "g4",
    "model": "PowerMac3,6",
    "serial": "CK245..."
  },
  "fingerprint": {
    "all_passed": true,
    "checks": { ... }
  }
}
```

## Validation Logic
The node performs the following validation:
1. **Nonce Verification**: Is the nonce fresh and issued by this node?
2. **Commitment Check**: Does the hash match the provided entropy and wallet?
3. **Fingerprint Score**: Does the `fingerprint` data indicate a VM? (Node-side verification uses a weighted model).
4. **Architecture Match**: Does the `cpu_brand` match the `device_arch`?

## Security: Prevention of "Mining Farms"
By requiring unique hardware serials and MAC addresses, RustChain prevents the use of cloud providers (AWS/GCP) or local virtualization clusters. The **Antiquity Multiplier** (see Tokenomics) further disincentivizes modern hardware farms by making vintage, harder-to-scale hardware more profitable.

---
*Next: See [Token Economics & Multipliers](./TOKENOMICS.md).*
