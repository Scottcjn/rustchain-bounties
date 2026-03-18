# RustChain On-Chain Governance System

Implementation of the RustChain on-chain governance system for decentralized decision-making.

## Overview

This system allows RTC holders to propose and vote on network changes including:
- New RIPs (RustChain Improvement Proposals)
- Bounty funding
- Parameter changes
- Feature activations
- Emergency actions

## Features

### Core Functionality
- **Proposal Creation**: Any wallet with >10 RTC can create a proposal
- **Voting**: 1 RTC = 1 vote, weighted by hardware antiquity multiplier
- **Hardware-Weighted Voting**: Votes are weighted by the miner's hardware antiquity (G4 = 2.5x, G5 = 2.5x, SPARC = 2.5x-2.9x)
- **7-Day Voting Window**: All proposals have a 7-day voting period
- **Quorum Requirement**: 33% of active miners must vote for a proposal to pass

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/governance/propose` | POST | Create a new proposal |
| `/governance/proposals` | GET | List all proposals |
| `/governance/proposal/<id>` | GET | Get proposal details + votes |
| `/governance/vote` | POST | Cast a vote |
| `/governance/results/<id>` | GET | Get proposal results |
| `/governance/stats` | GET | Governance statistics |
| `/governance` | GET | Web UI |

### Hardware Multipliers

| Hardware | Multiplier |
|----------|------------|
| Intel 386 | 3.0x |
| Intel 486 | 2.8-2.9x |
| Motorola 68000 | 2.2-3.0x |
| MIPS R-series | 2.3-3.0x |
| PowerPC G4/G5 | 2.5x |
| SPARC V7-V9 | 2.5-2.9x |
| Retro Consoles | 2.3-2.8x |

## Installation

### Prerequisites
- Python 3.8+
- Flask
- SQLite3

### Setup

1. Copy `governance.py` to your RustChain node:
   ```bash
   cp governance/governance.py /path/to/RustChain/node/
   ```

2. Register the blueprint in your Flask app:
   ```python
   from governance import create_governance_blueprint, create_governance_ui, init_governance_db

   # Initialize database
   init_governance_db("rustchain.db")

   # Register blueprints
   app.register_blueprint(create_governance_blueprint("rustchain.db"))
   app.register_blueprint(create_governance_ui("rustchain.db"))
   ```

3. Ensure required tables exist in your database (schema included in governance.py)

## API Usage

### Create Proposal

```bash
curl -X POST http://localhost:5000/governance/propose \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": "your_wallet_address",
    "title": "Increase Block Reward",
    "proposal_type": "parameter_change",
    "description": "Proposal to increase block reward from 10 to 15 RTC",
    "parameter_key": "block_reward",
    "parameter_value": "15"
  }'
```

### Cast Vote

```bash
curl -X POST http://localhost:5000/governance/vote \
  -H "Content-Type: application/json" \
  -d '{
    "wallet": "your_wallet_address",
    "proposal_id": 1,
    "vote": "for"
  }'
```

### List Proposals

```bash
curl http://localhost:5000/governance/proposals
```

### Get Proposal Details

```bash
curl http://localhost:5000/governance/proposal/1
```

## Database Schema

The governance system uses two main tables:

### governance_proposals

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Proposal title |
| description | TEXT | Full description |
| proposal_type | TEXT | RIP/bounty/parameter_change/feature_activation/emergency |
| proposer_wallet | TEXT | Wallet address of creator |
| proposer_stake | REAL | RTC balance at creation |
| created_at | INTEGER | Unix timestamp |
| expires_at | INTEGER | Unix timestamp (7 days) |
| status | TEXT | active/passed/failed/expired |
| parameter_key | TEXT | Optional parameter to change |
| parameter_value | TEXT | New parameter value |
| votes_for | REAL | Weighted votes for |
| votes_against | REAL | Weighted votes against |
| votes_abstain | REAL | Weighted votes abstain |
| quorum_met | INTEGER | 1 if quorum reached |

### governance_votes

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| proposal_id | INTEGER | Foreign key to proposals |
| voter_wallet | TEXT | Wallet address |
| voter_hardware | TEXT | Hardware type |
| vote | TEXT | for/against/abstain |
| weight | REAL | Weighted vote value |
| signature | TEXT | Optional Ed25519 signature |
| voted_at | INTEGER | Unix timestamp |

## Web UI

Access the governance UI at `/governance` endpoint to:
- View all active proposals
- Create new proposals
- Cast votes
- View governance statistics

## Security

- Proposals require minimum 10 RTC stake to create
- Voters must have active attestation (within 48 hours)
- Optional Ed25519 signature verification for votes
- Founder veto capability for security-critical changes (first 2 years)

## Integration Notes

This implementation integrates with the existing RustChain node:
- Uses existing `attestations` table for active miner detection
- Uses existing `miners` table for hardware type
- Uses existing `balances` table for RTC stake checking

## License

Apache 2.0

## Author

AI Agent (Bounty #50) - 2026-03-17
