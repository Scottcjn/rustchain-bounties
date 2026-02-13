# RustChain Architecture Overview

System architecture and design documentation for RustChain network.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      RustChain Network                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│  │   Validator  │◄────►│   Validator  │◄────►│   Validator  │   │
│  │    Node 1    │     │    Node 2    │     │    Node 3    │   │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘   │
│         │                     │                     │           │
│         └────────────────────┼─────────────────────┘           │
│                              │                                 │
│                    ┌─────────▼─────────┐                       │
│                    │   Consensus Layer │                       │
│                    │  (RIP-200 PoA)   │                       │
│                    └─────────┬─────────┘                       │
│                              │                                 │
│         ┌───────────────────┼───────────────────┐           │
│         │                   │                   │           │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐   │
│  │   Miner 1   │    │   Miner 2    │    │   Miner N    │   │
│  │  (Attestor) │    │  (Attestor)  │    │  (Attestor)  │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Wallet     │    │    Bounty    │    │   Explorer   │    │
│  │   Service    │    │    Board     │    │    Service   │    │
│  └──────────────┘    └──────────────┘    └──────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Node Layer

#### Full Node

```
Full Node Responsibilities:
├── P2P Network Connectivity
│   ├── Bootstrap discovery
│   ├── Peer management
│   └── Gossip protocol
│
├── State Management
│   ├── Block storage
│   ├── Transaction index
│   └── State database
│
├── RPC Interface
│   ├── HTTP API
│   ├── WebSocket API
│   └── Debug endpoints
│
└── Block Production
    ├── Transaction validation
    ├── State transition
    └── Block proposal
```

#### Light Node

```
Light Node Features:
├── SPV (Simplified Payment Verification)
├── Block header sync only
├── Transaction bloom filters
└── On-demand state queries
```

### 2. Consensus Layer (RIP-200)

#### Proof-of-Attestation Mechanism

```
RIP-200 Consensus Flow:

1. Hardware Fingerprinting
   ┌─────────────────────┐
   │  CPUID Analysis     │  ← Extract CPU features
   │  CPU Cache Size    │
   │  Instruction Set    │
   │  Microcode Version  │
   └──────────┬──────────┘
              │
              ▼
2. Entropy Generation
   ┌─────────────────────┐
   │  Hardware RNG      │  ← True randomness
   │  Timing Jitter     │  ← CPU timing variations
   │  Memory Access     │  ← Cache timing patterns
   └──────────┬──────────┘
              │
              ▼
3. Proof Generation
   ┌─────────────────────┐
   │  Hash Computation   │  ← Combine entropy + work
   │  Nonce Search      │  ← Find valid hash
   │  Difficulty Check  │  ← Verify proof
   └──────────┬──────────┘
              │
              ▼
4. Attestation Submission
   ┌─────────────────────┐
   │  Node Verification  │  ← Validate hardware proof
   │  Weight Assignment  │  ← Based on multiplier
   │  Epoch Inclusion    │  ← Add to consensus round
   └─────────────────────┘
```

#### Epoch Structure

```
Epoch Timing:
┌──────────────────────────────────────────────────────────────┐
│                    EPOCH (10 minutes)                        │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │
│  │Slot 1  │ │Slot 2  │ │Slot 3  │ │Slot 4  │ │Slot N  │  │
│  │2 min   │ │2 min   │ │2 min   │ │2 min   │ │...     │  │
│  └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘  │
│       │          │          │          │          │       │
│       └──────────┴──────────┴──────────┴──────────┘       │
│                          │                                  │
│                    Reward Distribution                      │
│                    (1.5 RTC/epoch)                        │
└──────────────────────────────────────────────────────────────┘
```

### 3. Mining Layer

#### Miner Components

```
┌─────────────────────────────────────────────────────────┐
│                    RustChain Miner                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐    ┌─────────────────────────┐ │
│  │ Hardware Scanner │───►│ Entropy Generator       │ │
│  │                 │    │  - CPU features          │ │
│  │ - CPUID         │    │  - Cache timing         │ │
│  │ - Cache size     │    │  - RNG patterns         │ │
│  │ - Instruction set│    │                         │ │
│  └────────┬────────┘    └────────────┬──────────────┘ │
│           │                        │                  │
│           ▼                        ▼                  │
│  ┌─────────────────────────────────────────────┐     │
│  │            Proof Generator                   │     │
│  │                                             │     │
│  │  SHA-256 hash of:                           │     │
│  │  - Hardware fingerprint                      │     │
│  │  - Nonce                                    │     │
│  │  - Previous block hash                       │     │
│  │                                             │     │
│  └───────────────────────┬─────────────────────┘     │
│                          │                            │
│                          ▼                            │
│  ┌─────────────────────────────────────────────────┐│
│  │              Attestation Submitter               ││
│  │                                               ││
│  │  POST /attestation                             ││
│  │  {                                            ││
│  │    "miner_id": "xxx",                          ││
│  │    "proof": "...",                             ││
│  │    "hardware_hash": "..."                       ││
│  │  }                                            ││
│  └─────────────────────────────────────────────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Hardware Fingerprinting

```
┌─────────────────────────────────────────────────────────┐
│           Hardware Fingerprint Components              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. CPU Identification                                   │
│     ├── Vendor (Intel/AMD/Apple)                      │
│     ├── Model name                                     │
│     ├── Family/Stepping                                │
│     └── Microcode version                              │
│                                                         │
│  2. Cache Configuration                                 │
│     ├── L1/L2/L3 cache sizes                          │
│     ├── Cache line size                                │
│     └── Cache associativity                             │
│                                                         │
│  3. Instruction Set Extensions                          │
│     ├── SSE4.1/4.2                                    │
│     ├── AVX/AVX2/AVX-512                              │
│     ├── AES-NI                                         │
│     └── SHA extensions                                  │
│                                                         │
│  4. Timing Measurements                                 │
│     ├── Memory access timing                           │
│     ├── Computation timing                             │
│     └── Interrupt latency                              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4. Application Layer

#### Wallet System

```
Wallet Architecture:
┌─────────────────────────────────────────────────────────┐
│                     Wallet Service                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐│
│  │ Key Manager │  │Tx Builder  │  │ Balance Tracker ││
│  │             │  │            │  │                 ││
│  │ - Generate  │  │ - Create    │  │ - Query node   ││
│  │ - Import    │  │ - Sign      │  │ - Cache        ││
│  │ - Export    │  │ - Broadcast │  │ - Notify       ││
│  └─────────────┘  └─────────────┘  └─────────────────┘│
│         │               │                  │           │
│         └───────────────┼──────────────────┘           │
│                         ▼                                │
│              ┌────────────────────────┐                │
│              │     Transaction Pool    │                │
│              │                        │                │
│              │  - Pending transactions │                │
│              │  - Fee calculation     │                │
│              │  - Gas estimation       │                │
│              └────────────┬───────────┘                │
│                           │                            │
│                           ▼                            │
│              ┌────────────────────────┐                │
│              │   Node Interface        │                │
│              │                        │                │
│              │  - Submit transaction  │                │
│              │  - Monitor confirmations │                │
│              │  - Query balance       │                │
│              └────────────────────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Bounty Board

```
Bounty Flow:
┌─────────────────────────────────────────────────────────┐
│                   Bounty Board System                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. POST BOUNTY                                        │
│     Sponsor → Create Issue → Add bounty label          │
│              → Fund escrow (x402)                       │
│                                                         │
│  2. CLAIM                                              │
│     Developer → Comment "Claim" → Reserve bounty       │
│                                                         │
│  3. WORK                                                │
│     Developer → Submit PR → Address issue             │
│                                                         │
│  4. REVIEW                                             │
│     Maintainer → Review PR → Approve/Reject            │
│                                                         │
│  5. MERGE                                              │
│     PR merged → Webhook triggers payout                 │
│                                                         │
│  6. PAY                                                │
│     Sponsor → Release funds → x402 payment → Developer │
│              → RTC in wallet (30 seconds)               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Network Protocol

### P2P Communication

```
Gossip Protocol:
                    ┌─────────────────┐
                    │    Bootstrap    │
                    │     Node        │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │  Peer 1 │  │  Peer 2 │  │  Peer 3 │
        └────┬────┘  └────┬────┘  └────┬────┘
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Block/Attest   │
                  │   Propagation   │
                  └─────────────────┘
```

### Message Types

| Message Type | Purpose | Frequency |
|-------------|---------|-----------|
| `NewBlock` | Announce new block | Per block |
| `Attestation` | Submit proof | Per slot |
| `PeerList` | Share peers | Periodic |
| `Transaction` | Broadcast TX | Per TX |
| `GetState` | Request state | On demand |

---

## Data Structures

### Block Structure

```go
type Block struct {
    Header        BlockHeader
    Transactions  []Transaction
    Attestations  []Attestation
    StateRoot     [32]byte
    ReceiptRoot   [32]byte
}

type BlockHeader struct {
    Version      uint32
    Height       uint64
    Timestamp    uint64
    PrevBlock    [32]byte
    MerkleRoot   [32]byte
    AttestRoot   [32]byte
    StateRoot    [32]byte
    Validator    [20]byte
    Signature    [64]byte
}
```

### Attestation Structure

```go
type Attestation struct {
    MinerID      string
    BlockHeight  uint64
    HardwareHash [32]byte
    Nonce       uint64
    Proof       [64]byte
    Timestamp   uint64
    Signature   [64]byte
}
```

---

## Security Model

### Threat Model

```
┌─────────────────────────────────────────────────────────┐
│                 Security Layers                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Layer 1: Network Security                            │
│  ├── Encrypted P2P (noise protocol)                    │
│  ├── Peer authentication                               │
│  └── Sybil resistance                                  │
│                                                         │
│  Layer 2: Consensus Security                          │
│  ├── Hardware fingerprinting                            │
│  ├── VM detection                                      │
│  └── Anti-emulation measures                          │
│                                                         │
│  Layer 3: Transaction Security                         │
│  ├── Digital signatures (secp256k1)                    │
│  ├── Nonce management                                  │
│  └── Replay protection                                 │
│                                                         │
│  Layer 4: Data Integrity                             │
│  ├── Merkle proofs                                     │
│  ├── State commitments                                 │
│  └── Cryptographic hashing                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### VM Detection

```
VM Detection Techniques:
├── CPUID Analysis
│   ├── Hypervisor vendor strings
│   │   ├── "VMwareVirtualPlatform"
│   │   ├── "Virtual Platform"
│   │   └── "KVMKVMKVM"
│   └── CPU features differences
│
├── Timing Analysis
│   ├── Memory access timing
│   ├── Instruction timing
│   └── Interrupt latency
│
├── Hardware Access
│   ├── Model-specific registers
│   ├── MSR access patterns
│   └── Device enumeration
│
└── System Properties
    ├── SMBIOS data
    ├── DMI/SMBIOS info
    └── ACPI tables
```

---

## Performance Considerations

### Throughput Targets

| Metric | Target | Notes |
|--------|--------|-------|
| TPS | 10,000+ | Transactions per second |
| Block Time | 2-5 seconds | Per block |
| Finality | < 30 seconds | Economic finality |
| Light Sync | < 5 seconds | Initial sync |

### Optimization Strategies

```
┌─────────────────────────────────────────────────────────┐
│              Performance Optimization                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Parallel Processing                                │
│     ├── Sharded state                                  │
│     ├── Parallel transaction validation                 │
│     └── Concurrent block processing                     │
│                                                         │
│  2. Efficient Data Structures                          │
│     ├── Merkle Patricia Trees                          │
│     ├── Bloom filters for light clients               │
│     └── Compressed state proofs                        │
│                                                         │
│  3. Network Optimization                               │
│     ├── Gossip subnets                                 │
│     ├── Block compression                              │
│     └── Peer scoring and selection                     │
│                                                         │
│  4. Storage Optimization                              │
│     ├── Pruning strategies                             │
│     ├── Cold/warm storage tiers                        │
│     └── Archive mode for full nodes                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Upgrade Path

```
┌─────────────────────────────────────────────────────────┐
│              Version Upgrade Strategy                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  v2.2.x (Current)                                      │
│  ├── RIP-200 consensus                                 │
│  ├── Basic staking                                      │
│  └── CLI wallet                                        │
│                                                         │
│  v2.3.x (Planned)                                     │
│  ├── Cross-chain bridges                               │
│  ├── Advanced staking features                         │
│  └── Mobile wallet                                     │
│                                                         │
│  v3.0.x (Roadmap)                                      │
│  ├── RIP-300 (Enhanced consensus)                      │
│  ├── Layer 2 support                                   │
│  └── Full smart contract platform                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| [API_REFERENCE.md](./API_REFERENCE.md) | Complete API docs |
| [MINERS_SETUP_GUIDE.md](./MINERS_SETUP_GUIDE.md) | Mining setup |
| [NODE_OPERATOR_GUIDE.md](./NODE_OPERATOR_GUIDE.md) | Node operation |
| [PYTHON_SDK_TUTORIAL.md](./PYTHON_SDK_TUTORIAL.md) | SDK usage |

---

*Last updated: 2026-02-12*
*Architecture Version: 2.2.1*
