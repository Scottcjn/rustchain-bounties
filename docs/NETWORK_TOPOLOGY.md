# RustChain Network Topology

## Overview

RustChain operates a decentralized Proof-of-Antiquity blockchain network with a lightweight, accessible architecture designed to support vintage hardware participation.

## Network Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RustChain Network                               │
│                                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │   Node 1     │──── │   Node 2     │──── │   Node 3     │            │
│  │ 50.28.86.131 │     │ 50.28.86.153 │     │ 76.8.228.245 │            │
│  │              │     │              │     │              │            │
│  │ • Primary    │     │ • Ergo       │     │ • Community  │            │
│  │ • Explorer   │     │   Anchor     │     │   Node       │            │
│  │ • API        │     │ • Backup     │     │              │            │
│  └──────┬───────┘     └──────────────┘     └──────────────┘            │
│         │                                                               │
│         │ P2P Sync                                                      │
│         ▼                                                               │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │              Distributed Miner Network                  │           │
│  │  (PowerPC G3/G4/G5, POWER8, x86_64, Apple Silicon)     │           │
│  └─────────────────────────────────────────────────────────┘           │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │              Ergo Blockchain Anchor                     │           │
│  │         (Periodic State Commitment via R4)             │           │
│  └─────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Node Architecture

### Active Nodes (3)

| Node | IP Address | Role | Status | Location |
|------|------------|------|--------|----------|
| **Node 1** | 50.28.86.131 | Primary + Explorer + API | ✅ Active | US |
| **Node 2** | 50.28.86.153 | Ergo Anchor + Backup | ✅ Active | US |
| **Node 3** | 76.8.228.245 | External (Community) | ✅ Active | US |

### Node Responsibilities

#### Node 1 (Primary)
- **Explorer UI**: Serves the block explorer at `/explorer`
- **API Gateway**: Handles all REST API requests
- **Wallet Services**: Manages wallet balance queries and transactions
- **Governance UI**: Hosts governance proposal interface
- **Health Monitoring**: Provides network health endpoints

#### Node 2 (Ergo Anchor)
- **Blockchain Anchoring**: Periodically commits RustChain state to Ergo blockchain
- **Backup Node**: Maintains full chain state replica
- **R4 Register**: Stores commitment hashes in Ergo's R4 register
- **Immutability Layer**: Provides cryptographic proof of chain state

#### Node 3 (Community Node)
- **Decentralization**: Independent node operated by community member
- **Redundancy**: Provides additional network resilience
- **P2P Sync**: Participates in consensus and block propagation

## Network Layers

### Layer 1: Consensus Layer (Proof-of-Antiquity)

```
┌─────────────────────────────────────────────────────────────┐
│              Proof-of-Antiquity Consensus                   │
├─────────────────────────────────────────────────────────────┤
│ 1. Hardware Fingerprinting (RIP-PoA)                        │
│    - Clock-skew & oscillator drift                          │
│    - Cache timing fingerprint                               │
│    - SIMD unit identity (AltiVec/SSE/NEON)                 │
│    - Thermal drift entropy                                  │
│    - Instruction path jitter                                │
│    - Anti-emulation checks                                  │
│                                                             │
│ 2. Round-Robin Voting (RIP-200)                             │
│    - 1 CPU = 1 vote (regardless of speed)                  │
│    - Equal reward split × antiquity multiplier             │
│    - No advantage from multiple threads                    │
│                                                             │
│ 3. Epoch-Based Rewards                                      │
│    - Epoch duration: 10 minutes (600 seconds)              │
│    - Base reward pool: 1.5 RTC per epoch                   │
│    - Distribution: Equal split × antiquity multiplier      │
└─────────────────────────────────────────────────────────────┘
```

### Layer 2: P2P Network Layer

**Connection Type**: Peer-to-Peer mesh network

**Protocol**: HTTP/HTTPS with Ed25519 signature verification

**Node Communication**:
- Block propagation via P2P sync
- State reconciliation every epoch
- Health checks and heartbeat monitoring

**Miner-to-Node Communication**:
```
Miner → Node (HTTPS POST)
  ├─ Hardware fingerprint submission
  ├─ Attestation proof
  └─ Reward claim request

Node → Miner (HTTPS Response)
  ├─ Validation result
  ├─ Reward calculation
  └─ Next epoch info
```

### Layer 3: Application Layer

**API Endpoints** (served by Node 1):
```bash
# Network Health
GET /health

# Current Epoch
GET /epoch

# Active Miners List
GET /api/miners

# Wallet Services
GET /wallet/balance?miner_id=<wallet>
POST /wallet/create

# Governance
GET /governance/proposals
POST /governance/propose
POST /governance/vote
GET /governance/ui

# Block Explorer
GET /explorer (Web UI)
```

### Layer 4: Blockchain Anchoring Layer

**Ergo Integration**:
```
RustChain Epoch → Commitment Hash → Ergo Transaction (R4 register)
```

**Process**:
1. Every N epochs, Node 2 calculates state commitment hash
2. Hash is embedded in Ergo transaction's R4 register
3. Transaction ID provides cryptographic proof of existence
4. Immutable timestamp from Ergo blockchain

**Benefits**:
- Tamper-proof state verification
- Independent blockchain validation
- Long-term archival of chain state

## Connection Topology

### Physical Connections

```
                    Internet
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │ Node 1  │   │ Node 2  │   │ Node 3  │
    │  :443   │   │  :443   │   │  :443   │
    └────┬────┘   └────┬────┘   └────┬────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
    │ Miner 1 │   │ Miner 2 │   │ Miner N │
    │ (G4)    │   │ (G5)    │   │ (x86)   │
    └─────────┘   └─────────┘   └─────────┘
```

### Logical Connections

**Miner → Node**:
- Protocol: HTTPS (TLS 1.3)
- Authentication: Ed25519 signed requests
- Port: 443
- State: Stateless HTTP requests

**Node ↔ Node**:
- Protocol: P2P sync over HTTPS
- Frequency: Every epoch (10 minutes)
- Data: Block state, miner attestations, governance votes
- Consensus: Round-robin with hardware-weighted voting

## Network Security

### Anti-Sybil Mechanisms

1. **Hardware Fingerprinting**: Each unique hardware device gets one identity
2. **Hardware Binding**: Fingerprint bound to single wallet address
3. **Anti-VM Detection**: VMs receive 1 billionth normal rewards
4. **Ed25519 Signatures**: All transactions cryptographically signed

### Network Hardening

- **Self-Signed SSL**: Nodes use self-signed certificates (-sk flag required for curl)
- **Rate Limiting**: API endpoints implement request throttling
- **Signature Verification**: All wallet operations require valid signatures
- **Hardware Attestation**: miners must prove real hardware every epoch

## Scalability Considerations

### Current Capacity
- **Active Nodes**: 3
- **Supported Miners**: Unlimited (theoretically)
- **Epoch Duration**: 10 minutes
- **Transactions per Epoch**: Limited by node capacity

### Future Scaling Plans

1. **Additional Community Nodes**: Decentralize beyond 3 nodes
2. **Sharded Attestation**: Parallel hardware verification
3. **Layer-2 Solutions**: State channels for micro-transactions
4. **Cross-Chain Bridges**: EVM compatibility via FlameBridge

## Monitoring & Observability

### Health Endpoints

```bash
# Node Health Check
curl -sk https://rustchain.org/health

# Active Miners Count
curl -sk https://rustchain.org/api/miners

# Current Epoch Status
curl -sk https://rustchain.org/epoch

# Block Explorer
https://rustchain.org/explorer
```

### Metrics Tracked

- Active miner count
- Epoch progression
- Reward distribution
- Hardware diversity (antiquity multipliers)
- Node synchronization status

## Disaster Recovery

### Node Failure Scenarios

| Scenario | Impact | Recovery |
|----------|--------|----------|
| Node 1 down | API/Explorer unavailable | Node 2 can take over |
| Node 2 down | Ergo anchoring paused | Resume when restored |
| Node 3 down | Minimal (community node) | No action needed |
| 2+ nodes down | Consensus at risk | Emergency protocol |

### Backup Strategy

- **Full State Replication**: All nodes maintain complete chain state
- **Ergo Anchors**: Periodic immutable backups on Ergo blockchain
- **Miner Data**: Wallet balances stored in SQLite with replication

## Network Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| Epoch Duration | 600 seconds | Time between blocks |
| Base Reward | 1.5 RTC | Per epoch reward pool |
| Min Multiplier | 1.0× | Modern hardware |
| Max Multiplier | 2.5× | PowerPC G4 |
| Multiplier Decay | 15%/year | Prevents permanent advantage |
| Vote Weight | 1 CPU = 1 vote | Round-robin consensus |
| Signature Algorithm | Ed25519 | Cryptographic signing |

## Geographic Distribution

```
United States (3 nodes)
├── Node 1: 50.28.86.131 (Primary)
├── Node 2: 50.28.86.153 (Ergo Anchor)
└── Node 3: 76.8.228.245 (Community)
```

**Future Goals**: Expand to EU, Asia, and other regions for better decentralization and latency.

## References

- [RustChain Whitepaper](./RustChain_Whitepaper_Flameholder_v0.97-1.pdf)
- [Proof-of-Antiquity Specification](./proof_of_antiquity.md)
- [RIP-200: One CPU One Vote](./rip_200.md)
- [Hardware Fingerprinting Guide](./fingerprint_checks.md)
- [Ergo Anchoring Protocol](./ergo_anchor.md)

---

*Last Updated: March 2026*
*Version: 1.0*
*Author: RustChain Contributors*
