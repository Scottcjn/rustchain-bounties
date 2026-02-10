# RustChain Architecture Overview

High-level architecture of the RustChain network.

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      RustChain Network                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Miners    │────▶│ Attestation │────▶│   Ledger    │
│             │     │    Nodes    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                    │
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Hardware   │     │ Consensus   │     │  Database   │
│ Fingerprint │     │   Engine    │     │             │
└─────────────┘     └─────────────┘     └─────────────┘

           ┌─────────────────────────┐
           │   Solana Bridge (wRTC)  │
           └─────────────────────────┘
                      │
                      ▼
           ┌─────────────────────────┐
           │    Raydium DEX / DeFi   │
           └─────────────────────────┘
```

## Core Components

### 1. Miners

Miners run attestation proofs to earn RTC rewards.

**Key Features:**
- CPU-based Proof-of-Attestation (RIP-200)
- Hardware fingerprinting (6-point validation)
- Anti-VM detection
- Vintage hardware bonuses (up to 2.5x)

**Technology Stack:**
- Python 3.7+
- Hardware introspection libraries
- HTTPS client for attestation submission

**Data Flow:**
```
Miner → Hardware Fingerprint → Attestation Proof → Node → Reward
```

### 2. Attestation Nodes

Nodes validate attestations and distribute rewards.

**Responsibilities:**
- Validate hardware fingerprints
- Detect VMs and emulators
- Calculate multipliers for vintage hardware
- Distribute epoch rewards
- Maintain consensus

**Technology Stack:**
- Python/Rust backend
- PostgreSQL or SQLite
- Nginx reverse proxy
- SSL/TLS encryption

**Data Flow:**
```
Attestation → Validation → Multiplier Calculation → Reward Distribution
```

### 3. Ledger

The RustChain ledger records all transactions and balances.

**Structure:**
- Account-based model (not UTXO)
- Immutable transaction log
- Fast balance lookups
- No gas fees

**Database Schema:**
```sql
CREATE TABLE wallets (
    wallet_id TEXT PRIMARY KEY,
    balance REAL NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE transactions (
    tx_hash TEXT PRIMARY KEY,
    from_wallet TEXT,
    to_wallet TEXT,
    amount REAL,
    timestamp TIMESTAMP
);

CREATE TABLE attestations (
    id SERIAL PRIMARY KEY,
    miner_id TEXT,
    hardware_fingerprint JSONB,
    multiplier REAL,
    epoch INTEGER,
    timestamp TIMESTAMP
);
```

### 4. Consensus Engine

RustChain uses **RIP-200 Proof-of-Attestation** consensus.

**Mechanism:**
1. Miners submit hardware attestations every epoch
2. Nodes validate attestations using 6-point fingerprint
3. VMs detected via hardware inconsistencies (0x reward)
4. Vintage hardware receives multiplier bonuses
5. Rewards distributed proportionally to attestation weight

**Epoch Parameters:**
- Duration: 3600 seconds (1 hour)
- Reward pool: 1.5 RTC per epoch
- Distribution: Proportional to (uptime × multiplier)

**Finality:**
- Instant transaction finality
- No block confirmations needed
- Deterministic reward distribution

### 5. Hardware Fingerprint

6-point fingerprint prevents VM spoofing.

**Fingerprint Components:**
1. **CPU Model**: Exact processor name
2. **CPU Cores**: Physical core count
3. **Architecture**: x86_64, ppc64, arm64, etc.
4. **Vendor ID**: Intel, AMD, IBM, Apple
5. **Physical ID**: Unique hardware identifier
6. **Timestamp**: Attestation submission time

**VM Detection:**
- Hypervisor CPUID flags
- Virtualization indicators (VMware, VirtualBox, QEMU)
- Inconsistent hardware topology
- Missing physical hardware features

**Example Fingerprint:**
```json
{
  "cpu_model": "PowerPC_970MP",
  "cpu_cores": 2,
  "arch": "ppc64",
  "vendor_id": "IBM",
  "physical_id": "G5_12345_unique",
  "timestamp": 1704067200
}
```

### 6. Solana Bridge (wRTC)

Bridge RTC to wRTC on Solana for DeFi access.

**Architecture:**
```
RustChain Ledger ↔ Bridge Contract ↔ Solana Program ↔ wRTC SPL Token
```

**Bridge Process (RTC → wRTC):**
1. User locks RTC in bridge contract
2. Bridge contract mints equivalent wRTC on Solana
3. wRTC SPL tokens sent to user's Solana wallet

**Bridge Process (wRTC → RTC):**
1. User burns wRTC on Solana
2. Bridge contract verifies burn transaction
3. Equivalent RTC unlocked and sent to user's RustChain wallet

**Security:**
- Multi-signature bridge contract
- Time-lock on withdrawals
- Proof-of-reserve audits
- 1:1 backing guarantee

**wRTC Token:**
- Mint: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`
- Standard: SPL Token
- Decimals: 9
- Tradable on Raydium DEX

## Data Flow

### Mining Flow

```
1. Miner starts with wallet ID
2. Miner collects hardware fingerprint
3. Miner submits attestation to node
4. Node validates fingerprint (VM check)
5. Node calculates multiplier (vintage bonus)
6. Node records attestation for epoch
7. Epoch ends, rewards distributed
8. Miner balance updated in ledger
```

### Transfer Flow

```
1. User initiates transfer (from, to, amount)
2. User signs transaction with private key
3. Node validates signature
4. Node checks sender balance ≥ amount
5. Node updates balances atomically
6. Transaction recorded in ledger
7. Recipients can verify via /wallet/balance
```

### Bridge Flow (RTC → wRTC)

```
1. User deposits RTC to bridge address
2. Bridge contract locks RTC
3. Bridge contract calls Solana program
4. Solana program mints wRTC SPL tokens
5. wRTC sent to user's Solana wallet
6. User can trade wRTC on DEXes
```

## Network Topology

### Node Types

1. **Validator Nodes**: Participate in consensus
2. **Archive Nodes**: Store full ledger history
3. **RPC Nodes**: Serve API requests
4. **Bridge Nodes**: Manage Solana bridge

### Node Communication

```
Miner ────HTTPS───▶ RPC Node ────Internal───▶ Validator Node
                                       │
                                       ▼
                                  Consensus
                                       │
                                       ▼
Web Wallet ────HTTPS───▶ RPC Node ◀───Ledger Update
```

## Security Model

### Threat Model

**Threats:**
1. VM farms attempting to farm rewards
2. Double-spend attacks
3. Sybil attacks (multiple wallet IDs)
4. Bridge exploits
5. Node DDoS attacks

**Mitigations:**
1. 6-point hardware fingerprint with VM detection
2. Atomic ledger updates, signed transactions
3. Hardware attestation limits per fingerprint
4. Multi-sig bridge, time-locks, audits
5. Rate limiting, IP reputation, Cloudflare

### Cryptography

- **Signatures**: SHA-256 HMAC
- **Transaction hashing**: SHA-256
- **Bridge proofs**: ECDSA (secp256k1)
- **TLS**: TLS 1.3 with Let's Encrypt certs

## Performance Characteristics

### Throughput

- **Attestations**: ~1000/second per node
- **Transfers**: ~500/second per node
- **Balance queries**: ~10,000/second per node

### Latency

- **Attestation validation**: <100ms
- **Transfer confirmation**: <50ms
- **Balance lookup**: <10ms
- **Bridge (RTC → wRTC)**: 5-10 minutes

### Storage

- **Ledger size**: ~10GB per year
- **Attestations**: ~50GB per year
- **Transactions**: ~5GB per year

## Scalability

### Horizontal Scaling

- Add more RPC nodes for API load
- Shard database by wallet ID prefix
- Regional node deployment

### Vertical Scaling

- Increase validator node resources
- Optimize database queries (indexes, caching)
- Use read replicas for balance lookups

## Comparison to Other Chains

| Feature | RustChain | Bitcoin | Ethereum | Solana |
|---------|-----------|---------|----------|---------|
| Consensus | PoA (RIP-200) | PoW | PoS | PoH + PoS |
| TPS | 500+ | 7 | 15-30 | 2000+ |
| Fees | Free | High | Variable | Low |
| Finality | Instant | 60 min | 15 min | 400ms |
| Mining | 1 CPU = 1 Vote | ASIC | N/A | N/A |
| Vintage HW Bonus | Yes (2.5x) | No | No | No |

## Future Roadmap

### Phase 1: Mainnet Launch (Q1 2026)
-  RIP-200 consensus
-  Basic miner and node software
-  Solana bridge (wRTC)
-  Raydium DEX listing

### Phase 2: Decentralization (Q2 2026)
- [ ] 100+ validator nodes
- [ ] Geographic distribution
- [ ] Governance module
- [ ] Staking for validators

### Phase 3: DeFi Integration (Q3 2026)
- [ ] Liquidity pools on Solana
- [ ] Lending/borrowing protocols
- [ ] RTC-backed stablecoins
- [ ] Cross-chain bridges (Ethereum, BSC)

### Phase 4: Ecosystem Growth (Q4 2026)
- [ ] Mobile wallets (iOS, Android)
- [ ] Web wallet with dApp connector
- [ ] Smart contract layer
- [ ] Developer grants program

## References

- [RIP-200 Specification](https://github.com/rustchain/rips/blob/main/rip-200.md)
- [Whitepaper](https://rustchain.org/whitepaper.pdf)
- [Node Implementation](https://github.com/rustchain/node)
- [Bridge Contract Source](https://github.com/rustchain/bridge-contract)

## Next Steps

- [Node Operator Guide](node-operator-guide.md) - Run a node
- [API Reference](api-reference.md) - Build on RustChain
- [Contributing Guide](contributing-guide.md) - Contribute to the project
