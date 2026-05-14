# RustChain Architecture Overview

High-level system design of the RustChain Proof of Antiquity blockchain.

## Network Topology

```
┌─────────────────────────────────────────────────┐
│                  RustChain Mainnet               │
│              (v2.2.1-security-hardened)          │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Node 1  │  │  Node 2  │  │  Node 3  │      │
│  │50.28.86  │  │ (future) │  │ (future) │      │
│  │  .131    │  │          │  │          │      │
│  └────┬─────┘  └──────────┘  └──────────┘      │
│       │                                         │
│  ┌────┴──────────────────────────────────┐      │
│  │         Shared Ledger State            │      │
│  │  Epoch 162 | Slot 23403               │      │
│  │  661 miners | 8,388,608 RTC supply    │      │
│  └───────────────────────────────────────┘      │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Core Components

### 1. Node Layer
- **REST API** (HTTPS, self-signed cert) at `https://50.28.86.131`
- Endpoints: `/health`, `/api/stats`, `/epoch`, `/balance/{id}`, `/metrics`
- JSON responses, Prometheus metrics at `/metrics`

### 2. Consensus: Proof of Antiquity (RIP-200)
- Miners attest real hardware via challenge-response
- Epochs: 144 blocks per epoch (~24 hours at 600s block time)
- Reward pot per epoch: 1.5 RTC
- No mining in the traditional sense — attestation-based

### 3. Miner Layer
- Python-based miner scripts (Linux, macOS, Windows)
- Hardware attestation via challenge/submit flow
- Enrollment required per epoch to receive rewards

### 4. Agent Economy
- Job marketplace for on-chain tasks
- Escrow-based payment in RTC
- Jobs posted and fulfilled by network agents

### 5. Security Features (v2.2.1)
- No mock signatures (`no_mock_sigs`)
- Mandatory admin key (`mandatory_admin_key`)
- Replay protection (`replay_protection`)
- Validated JSON (`validated_json`)

## Data Flow

```
Miner → POST /attest/challenge → Node
Miner ← Challenge response ← Node
Miner → POST /attest/submit → Node
Node → Verify hardware attestation
Node → Record on ledger
Node → POST /epoch/enroll → Miner enrolled
```

## Key Metrics (Live as of Epoch 162)

| Metric | Value |
|--------|-------|
| Total supply | 8,388,608 RTC |
| Active miners | 661 |
| Enrolled this epoch | 13 |
| Block time | 600 seconds |
| Epoch reward pot | 1.5 RTC |

## Links

- **Explorer:** https://explorer.rustchain.org/
- **GitHub:** https://github.com/Scottcjn/Rustchain
- **Bounties:** https://github.com/Scottcjn/rustchain-bounties
- **Node API:** https://50.28.86.131 (self-signed cert)
