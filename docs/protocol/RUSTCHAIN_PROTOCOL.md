# RustChain Protocol Documentation

> **Version:** 1.0  
> **Status:** Draft  
> **Author:** zp6  
> **Date:** 2026-05-14  
> **RIP Reference:** RIP-0008

---

## Table of Contents

1. [Overview](#1-overview)
2. [Consensus Mechanism: Proof of Antiquity](#2-consensus-mechanism-proof-of-antiquity)
3. [Node Architecture](#3-node-architecture)
4. [Mining Flow](#4-mining-flow)
5. [Token Economics](#5-token-economics)
6. [Security Model](#6-security-model)
7. [RIP Proposal Process](#7-rip-proposal-process)
8. [API Endpoint Reference](#8-api-endpoint-reference)
9. [Comparison with Other Chains](#9-comparison-with-other-chains)
10. [Glossary](#10-glossary)

---

## 1. Overview

RustChain is a Layer-1 blockchain protocol implemented in Rust, designed to provide a secure, decentralized, and hardware-attested mining environment. Unlike traditional Proof-of-Work (PoW) chains that rely on computational brute force, RustChain introduces **Proof of Antiquity (PoA)** — a consensus mechanism that ties mining rights to authenticated, unique hardware identities and temporal slot assignments.

The protocol enforces strict hardware verification, eliminates mock signatures in production, and implements robust replay protection across epochs. RustChain's architecture prioritizes transparency and auditability, making every block's provenance traceable to a specific, cryptographically verified hardware device.

### Key Design Goals

- **Hardware-rooted trust:** Mining eligibility requires genuine hardware attestation, preventing Sybil attacks through virtualized environments.
- **Temporal fairness:** Epochs and slots distribute mining opportunities evenly across time, reducing variance and discouraging pool centralization.
- **Minimal attack surface:** No admin keys, no mock signatures in production, and strict consensus rule validation.
- **Sustainable issuance:** Fixed supply with deterministic halving ensures long-term economic stability.

---

## 2. Consensus Mechanism: Proof of Antiquity

### 2.1 Core Concept

Proof of Antiquity (PoA) is RustChain's novel consensus algorithm. Rather than requiring miners to solve computationally intensive puzzles (as in Bitcoin's SHA-256 PoW), PoA assigns the right to produce blocks based on:

1. **Hardware Identity Verification:** Each miner must prove possession of a unique, physically authentic hardware device through cryptographic attestation.
2. **Epoch Enrollment:** Miners register for a mining epoch by submitting a hardware attestation proof during a designated enrollment window.
3. **Slot Assignment:** Within each epoch, enrolled miners are assigned specific time slots during which they are eligible to propose blocks. Slot assignment is deterministic, derived from a seed computed from the previous epoch's final block hash combined with the miner's hardware identity hash.

### 2.2 Epoch Lifecycle

An epoch progresses through the following phases:

| Phase | Duration | Description |
|-------|----------|-------------|
| **Enrollment** | ~100 slots | Miners submit hardware attestation proofs to enroll for the next epoch |
| **Active Mining** | ~1000 slots | Enrolled miners produce blocks in their assigned slots |
| **Finalization** | ~50 slots | Final blocks of the epoch are produced; epoch seed is computed |

The epoch seed for epoch N+1 is computed as:

```
epoch_seed = SHA256(last_block_hash_epoch_N || enrollment_merkle_root_epoch_N)
```

This ensures that slot assignments cannot be predicted before the enrollment window closes, preventing front-running attacks.

### 2.3 Fork Choice Rule

RustChain uses a **heaviest valid chain** rule, similar to GHOST, but weighted by:

- Number of valid hardware-attested blocks
- Chain quality score (ratio of unique miners to total blocks)

A chain with higher diversity of unique hardware identities is preferred over a chain with equivalent length but lower diversity.

---

## 3. Node Architecture

### 3.1 Component Overview

A RustChain full node consists of the following core components:

```
┌─────────────────────────────────────────────┐
│              RustChain Full Node             │
├─────────────────────────────────────────────┤
│  REST API Layer (Actix-Web / Axum)          │
│  ├── /health, /api/stats, /epoch, /balance  │
│  └── /block, /tx, /miner                    │
├─────────────────────────────────────────────┤
│  Consensus Engine                            │
│  ├── Epoch Manager                           │
│  ├── Slot Scheduler                          │
│  ├── Block Validator                         │
│  └── Fork Choice                             │
├─────────────────────────────────────────────┤
│  Hardware Attestation Module                 │
│  ├── Device Identity (TPM/TEE)              │
│  ├── Challenge-Response Handler             │
│  └── Enrollment Manager                      │
├─────────────────────────────────────────────┤
│  Storage Layer (RocksDB)                     │
│  ├── Block Store                             │
│  ├── State Trie                              │
│  └── UTXO / Account Index                    │
├─────────────────────────────────────────────┤
│  P2P Network (libp2p)                        │
│  ├── Gossipsub (blocks, txs)                │
│  ├── Kademlia DHT (peer discovery)          │
│  └── Request-Response (sync)                │
└─────────────────────────────────────────────┘
```

### 3.2 REST API

The REST API is the primary interface for interacting with a RustChain node. It exposes endpoints for querying chain state, submitting transactions, and monitoring node health. See [Section 8](#8-api-endpoint-reference) for the full reference.

### 3.3 Epoch Manager

The Epoch Manager tracks the current epoch number, phase, and enrollment state. It coordinates transitions between enrollment, active mining, and finalization phases. The manager persists epoch metadata to RocksDB for crash recovery.

Key responsibilities:
- Track enrollment submissions and validate hardware attestations
- Compute the enrollment Merkle root at enrollment close
- Trigger slot assignment computation at epoch boundary
- Emit epoch transition events to other components

### 3.4 Slot Scheduler

The Slot Scheduler assigns time slots to enrolled miners using the epoch seed. Each slot has a fixed duration (configurable, default ~6 seconds). The scheduler notifies the mining module when a slot belonging to this node's hardware identity is approaching.

Slot assignment algorithm:
```rust
fn assign_slots(enrolled_miners: &[MinerId], epoch_seed: [u8; 32]) -> Vec<(Slot, MinerId)> {
    let mut assignments = Vec::new();
    for slot in 0..SLOTS_PER_EPOCH {
        let seed = hash(epoch_seed || slot.to_le_bytes());
        let index = seed.as_u64() % enrolled_miners.len();
        assignments.push((slot, enrolled_miners[index as usize].clone()));
    }
    assignments
}
```

### 3.5 Block Structure

A RustChain block contains:

| Field | Type | Description |
|-------|------|-------------|
| `header` | BlockHeader | Metadata including height, epoch, slot, parent hash |
| `transactions` | Vec\<Transaction\> | Ordered list of transactions |
| `miner_attestation` | HardwareAttestation | Proof that the block producer is the assigned miner |
| `signature` | SchnorrSignature | Miner's signature over the block header |

**BlockHeader:**
```rust
struct BlockHeader {
    version: u32,
    height: u64,
    epoch: u64,
    slot: u32,
    parent_hash: [u8; 32],
    tx_merkle_root: [u8; 32],
    state_root: [u8; 32],
    timestamp: u64,
}
```

---

## 4. Mining Flow

### 4.1 Hardware Certification

Before mining, a device must obtain a **Hardware Certificate** from the RustChain attestation infrastructure. This involves:

1. **TEE/TPM Quote:** The device generates a quote from its Trusted Execution Environment or Trusted Platform Module, proving it runs on genuine, unmodified hardware.
2. **Device Identity Key (DIK):** A unique key pair burned into the device during manufacturing. The public key is registered on-chain.
3. **Certificate Issuance:** The network verifies the TEE/TPM quote and issues a Hardware Certificate binding the DIK to a specific device serial.

### 4.2 Challenge-Response Protocol

During enrollment, the network issues a **challenge** to each prospective miner:

```
Challenge: nonce || epoch_number || challenge_seed
```

The miner's device must:
1. Receive the challenge
2. Generate a response within its TEE, signing: `SHA256(challenge || device_serial || timestamp)`
3. Return the response along with the TEE attestation quote

The network validates:
- The response signature matches a registered DIK
- The TEE quote is valid and recent
- The challenge was issued within the current enrollment window

### 4.3 Epoch Enrollment

The enrollment process:

1. **Enrollment Window Opens:** The Epoch Manager broadcasts an enrollment start event at the beginning of the enrollment phase.
2. **Miner Submits Enrollment:** Each miner submits a transaction containing:
   - Hardware Certificate reference
   - Challenge-Response proof
   - Staking deposit (if required by current RIP parameters)
3. **Validation:** Network validators verify the enrollment proof against the current epoch's challenge.
4. **Enrollment Confirmation:** Valid enrollments are included in the enrollment Merkle tree, which becomes part of the epoch seed computation.

### 4.4 Block Production

When a miner's assigned slot arrives:

1. The miner collects pending transactions from the mempool
2. Constructs a block with valid header fields
3. Signs the block header with the DIK private key
4. Attaches the hardware attestation for the current slot
5. Broadcasts the block to the P2P network

If a miner misses their slot, no block is produced for that slot (the chain has a "gap"). Network participants track slot attendance to compute miner reliability scores.

---

## 5. Token Economics

### 5.1 RTC Token

RustChain's native token is **RTC (RustChain Token)**.

| Parameter | Value |
|-----------|-------|
| **Total Supply** | 8,388,608 RTC (2²³) |
| **Initial Block Reward** | 1.5 RTC per epoch |
| **Halving Interval** | Every 524,288 epochs (2¹⁹) |
| **Smallest Unit** | 1 LINT = 10⁻⁸ RTC |
| **Genesis Allocation** | Determined by genesis block configuration |

### 5.2 Issuance Schedule

The emission follows a controlled decay curve:

```
Epochs 0 – 524,287:     1.5 RTC/epoch
Epochs 524,288 – 1,048,575:  0.75 RTC/epoch
Epochs 1,048,576 – 1,572,863: 0.375 RTC/epoch
...continues halving until minimal
```

Total theoretical issuance through all halvings converges toward 1.5 × 2 × 524,288 = **1,572,864 RTC** from mining alone. The remaining supply is allocated as follows:

### 5.3 Allocation

| Allocation | Percentage | Amount (RTC) |
|------------|-----------|--------------|
| **Mining Rewards** | ~18.75% | 1,572,864 |
| **Foundation Reserve** | 20% | 1,677,721 |
| **Ecosystem Development** | 15% | 1,258,291 |
| **Community Grants** | 10% | 838,860 |
| **Initial Contributors** | 15% | 1,258,291 |
| **Liquidity Provision** | 10% | 838,860 |
| **Bug Bounty & Security** | 5% | 419,430 |
| **Advisory & Partnerships** | 6.25% | 524,288 |

### 5.4 Transaction Fees

Transaction fees are denominated in LINT and paid to the block producer. The base fee is determined by a dynamic fee market:

- **Minimum fee:** 1,000 LINT per transaction
- **Priority fee:** Optional tip for faster inclusion
- **Fee burn:** 50% of base fees are burned, creating deflationary pressure

### 5.5 Staking (Future — RIP-0005)

RIP-0005 proposes a staking mechanism where miners must stake a minimum amount of RTC to participate in mining. This adds an economic cost to malicious behavior and aligns miner incentives with network health.

Proposed parameters:
- Minimum stake: 100 RTC
- Stake lock period: 10 epochs
- Slashing conditions: double-signing, invalid attestation, missed slots > 30%

---

## 6. Security Model

### 6.1 No Mock Signatures

RustChain has a hard rule: **mock signatures are never valid in production.** During development and testing, the `--dev` flag enables mock signature verification, but the production binary enforces strict cryptographic verification of all signatures.

```rust
#[cfg(feature = "production")]
fn verify_signature(sig: &Signature, msg: &[u8], pk: &PublicKey) -> bool {
    sig.verify(msg, pk) // Real crypto only
}

#[cfg(not(feature = "production"))]
fn verify_signature(sig: &Signature, msg: &[u8], pk: &PublicKey) -> bool {
    if cfg!(feature = "allow_mock") {
        sig.verify(msg, pk) || sig.is_mock()
    } else {
        sig.verify(msg, pk)
    }
}
```

This is enforced at the compile level — production builds simply do not include mock signature code paths.

### 6.2 No Admin Keys

There are **no admin keys, no privileged accounts, and no governance multisigs** with special protocol-level powers. Protocol upgrades follow the RIP process (see Section 7) and require node operator adoption through software upgrades.

### 6.3 Replay Protection

Every transaction includes:
- **Nonce:** Sequential per-account, preventing same-tx replay
- **Epoch number:** Transactions are only valid within the epoch they are signed for (plus/minus a configurable grace period of 2 epochs)
- **Chain ID:** Prevents cross-chain replay attacks

```rust
struct Transaction {
    sender: PublicKey,
    nonce: u64,
    epoch: u64,
    chain_id: u64,
    payload: Vec<u8>,
    signature: SchnorrSignature,
}
```

### 6.4 Hardware Identity Anti-Sybil

The hardware attestation requirement makes Sybil attacks economically infeasible:
- Each mining identity requires a genuine hardware device
- Virtual machines cannot produce valid TEE/TPM quotes
- Device serial numbers are tracked on-chain; duplicate registrations are rejected
- Compromised devices can be revoked through a consensus-based revocation process

### 6.5 Consensus Finality

RustChain provides **probabilistic finality** similar to Bitcoin, with additional guarantees from hardware attestation:
- A block is considered "reasonably final" after 6 confirmations
- A block is considered "deeply final" after 100 confirmations
- Hardware-attested blocks cannot be re-orged by non-attested chains due to the fork choice rule

---

## 7. RIP Proposal Process

RustChain Improvement Proposals (RIPs) are the mechanism for proposing protocol changes, new features, and standards.

### 7.1 RIP Categories

| Category | Prefix | Description |
|----------|--------|-------------|
| **Core** | RIP-0xxx | Consensus, protocol rules |
| **Networking** | RIP-1xxx | P2P, gossip, discovery |
| **API/Interface** | RIP-2xxx | REST API, RPC, SDK |
| **Application** | RIP-3xxx | Smart contracts, DeFi standards |
| **Informational** | RIP-9xxx | Guidelines, best practices |

### 7.2 RIP Lifecycle

```
Draft → Review → Last Call → Accepted → Final
                 ↓
              Withdrawn/Rejected
```

1. **Draft:** Author submits RIP as a markdown file in the `RIPs/` repository directory
2. **Review:** Community and core developers discuss the proposal (minimum 14 days)
3. **Last Call:** Final review period (7 days) before acceptance decision
4. **Accepted:** RIP is approved for implementation
5. **Final:** RIP has been implemented and deployed

### 7.3 Notable RIPs

| RIP | Title | Status | Description |
|-----|-------|--------|-------------|
| RIP-0005 | Miner Staking Requirements | Draft | Proposes minimum RTC staking for mining eligibility |
| RIP-0008 | Protocol Documentation Standard | Draft | Establishes standards for protocol documentation (this document) |
| RIP-0001 | Initial Protocol Parameters | Final | Defines genesis parameters: supply, epoch length, slot duration |
| RIP-0002 | Hardware Attestation v1 | Final | Specifies TEE/TPM attestation format and verification |
| RIP-0003 | Dynamic Fee Market | Review | Implements EIP-1559-style fee mechanism with burn |

### 7.4 Submission Template

```markdown
# RIP-XXXX: [Title]

## Summary
[One paragraph summary]

## Motivation
[Why is this change needed?]

## Specification
[Technical details]

## Backward Compatibility
[Impact on existing nodes/contracts]

## Reference Implementation
[Link to code or PR]

## Security Considerations
[Potential risks and mitigations]
```

---

## 8. API Endpoint Reference

All endpoints are served over the node's REST API (default port: `8080`).

### 8.1 Node Health

#### `GET /health`

Returns node health status.

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 86400,
  "version": "1.0.0",
  "peer_count": 42
}
```

### 8.2 Chain Statistics

#### `GET /api/stats`

Returns global chain statistics.

**Response:**
```json
{
  "block_height": 123456,
  "current_epoch": 123,
  "current_slot": 456,
  "total_transactions": 9876543,
  "active_miners": 1024,
  "hash_rate_equivalent": "N/A (PoA)"
}
```

### 8.3 Epoch Information

#### `GET /epoch`

Returns current epoch details.

**Response:**
```json
{
  "epoch_number": 123,
  "phase": "active_mining",
  "enrolled_miners": 1024,
  "slots_per_epoch": 1000,
  "current_slot": 456,
  "epoch_seed": "0xabc123...",
  "start_time": 1715700000,
  "end_time": 1715760000
}
```

#### `GET /epoch/{number}`

Returns details for a specific epoch.

### 8.4 Balance

#### `GET /balance/{address}`

Returns the RTC balance for a given address.

**Response:**
```json
{
  "address": "rc1q...",
  "balance_rtc": "1234.56789000",
  "balance_lint": "123456789000",
  "nonce": 42,
  "staked_rtc": "100.00000000"
}
```

### 8.5 Block

#### `GET /block/{height_or_hash}`

Returns block details by height or hash.

**Response:**
```json
{
  "header": {
    "height": 123456,
    "epoch": 123,
    "slot": 456,
    "parent_hash": "0xdef456...",
    "tx_merkle_root": "0x789abc...",
    "state_root": "0x123def...",
    "timestamp": 1715712345
  },
  "transaction_count": 15,
  "miner_id": "rc_miner1q...",
  "attestation_valid": true
}
```

### 8.6 Transaction

#### `GET /tx/{hash}`

Returns transaction details.

**Response:**
```json
{
  "hash": "0xabc...",
  "sender": "rc1q...",
  "nonce": 42,
  "epoch": 123,
  "payload_type": "transfer",
  "amount": "10.00000000",
  "fee": "0.00010000",
  "status": "confirmed",
  "block_height": 123456
}
```

#### `POST /tx`

Submit a new transaction.

**Request Body:**
```json
{
  "sender": "rc1q...",
  "nonce": 42,
  "epoch": 123,
  "chain_id": 1,
  "payload": "0x...",
  "signature": "0x..."
}
```

### 8.7 Miner

#### `GET /miner/{address}`

Returns miner information and statistics.

**Response:**
```json
{
  "address": "rc_miner1q...",
  "hardware_certified": true,
  "enrollment_epoch": 120,
  "blocks_produced": 150,
  "slots_attended": 162,
  "slots_missed": 3,
  "reliability_score": 0.981
}
```

---

## 9. Comparison with Other Chains

### 9.1 RustChain vs. Bitcoin

| Feature | RustChain | Bitcoin |
|---------|-----------|---------|
| **Language** | Rust | C++ |
| **Consensus** | Proof of Antiquity (hardware attestation) | Proof of Work (SHA-256) |
| **Energy Usage** | Minimal (no hash computation) | Extremely high (~150 TWh/year) |
| **Block Time** | ~6s (slot-based) | ~10 min |
| **Max Supply** | 8,388,608 RTC | 21,000,000 BTC |
| **Mining Hardware** | Any TEE/TPM device | Specialized ASICs |
| **Sybil Resistance** | Hardware identity | Computational power |
| **Finality** | ~36 seconds (6 blocks) | ~60 minutes (6 blocks) |

**Key Advantage:** RustChain achieves Sybil resistance without the massive energy waste of PoW, while maintaining decentralization through hardware-level identity verification.

### 9.2 RustChain vs. Ethereum

| Feature | RustChain | Ethereum |
|---------|-----------|----------|
| **Consensus** | Proof of Antiquity | Proof of Stake |
| **Staking Required** | Optional (RIP-0005) | Mandatory (32 ETH) |
| **Smart Contracts** | Not in v1 | Full EVM + L2 ecosystem |
| **Validator Entry** | Hardware attestation | 32 ETH stake |
| **Slashing** | Planned (missed slots) | Active (various conditions) |
| **MEV Resistance** | Slot-based (no priority gas auction) | PBS / MEV-Boost |
| **Token Supply** | Fixed (8.3M) | Uncapped (deflationary via burn) |

**Key Advantage:** RustChain's hardware attestation provides a physical anchor for identity that Ethereum's stake-based system cannot. This makes certain classes of attacks (e.g., buying up stake to attack the chain) economically bounded by physical hardware supply rather than liquid token markets.

### 9.3 RustChain vs. Solana

| Feature | RustChain | Solana |
|---------|-----------|--------|
| **Language** | Rust | Rust |
| **Consensus** | Proof of Antiquity | Proof of History + PoS |
| **TPS** | ~1,000 (v1 target) | ~65,000 (theoretical) |
| **Clock Mechanism** | Hardware-attested slots | SHA-256 VDF sequence |
| **Downtime History** | New (no history) | Multiple outages (2022) |
| **Hardware Req.** | TEE/TPM consumer device | High-end server (128GB RAM) |

**Key Advantage:** RustChain targets lower hardware requirements for node operation while maintaining a strong identity foundation, whereas Solana's high TPS comes at the cost of expensive validator hardware and historical network stability issues.

### 9.4 RustChain vs. Chia

| Feature | RustChain | Chia |
|---------|-----------|------|
| **Consensus** | Proof of Antiquity | Proof of Space and Time |
| **Storage Waste** | None | Significant (plotting) |
| **Identity Binding** | Hardware TPM/TEE | Plot NFTs |
| **Hardware Wear** | Minimal | SSD wear from plotting |

**Key Advantage:** Both chains avoid compute-intensive mining, but RustChain avoids the storage waste associated with Chia's plotting process.

---

## 10. Glossary

| Term | Definition |
|------|-----------|
| **PoA** | Proof of Antiquity — RustChain's hardware-attested consensus mechanism |
| **Epoch** | A time period during which a fixed set of miners is enrolled to produce blocks |
| **Slot** | A sub-division of an epoch during which a specific miner is eligible to propose a block |
| **DIK** | Device Identity Key — a unique key pair tied to physical hardware |
| **TEE** | Trusted Execution Environment — a secure area within a processor |
| **TPM** | Trusted Platform Module — a dedicated hardware security component |
| **RTC** | RustChain Token — the native token of the RustChain network |
| **LINT** | Smallest denomination of RTC (10⁻⁸) |
| **RIP** | RustChain Improvement Proposal |
| **Enrollment** | The process by which a miner registers for a mining epoch |
| **Attestation** | A cryptographic proof generated by TEE/TPM hardware |
| **Epoch Seed** | A random value derived from the previous epoch, used for slot assignment |
| **Chain Quality** | Ratio of unique miners to total blocks in a chain, used in fork choice |

---

## Appendix A: References

- [RustChain GitHub Repository](https://github