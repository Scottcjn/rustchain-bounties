# AgentFolio ↔ Beacon Dual-Layer Trust Integration Specification

**Bounty**: #2890 (100 RTC)  
**Status**: Specification Document  
**Date**: 2026-04-09

---

## 1. Overview

This document specifies the integration between [AgentFolio](https://agentfolio.bot) (agent-identity-and-trust protocol on Solana) and [Beacon](https://github.com/Scottcjn/rustchain-bounties) (RustChain's trust layer). The integration creates a dual-layer trust system where:

- **Layer 1 (Beacon)**: On-chain attestation of miner identity and hardware authenticity
- **Layer 2 (AgentFolio)**: Cross-chain agent reputation and trust scoring

## 2. Architecture

```
┌─────────────────────────────────────────────┐
│                AgentFolio                    │
│  (Solana - Agent Identity & Trust)          │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐│
│  │Identity  │  │Reputation│  │Cross-chain ││
│  │Registry  │  │Scorer    │  │Bridge      ││
│  └────┬─────┘  └─────┬────┘  └──────┬─────┘│
└───────┼───────────────┼──────────────┼──────┘
        │               │              │
        ▼               ▼              ▼
┌─────────────────────────────────────────────┐
│              Beacon (RustChain)              │
│  (Hardware Attestation & Mining Trust)      │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐│
│  │Miner     │  │Attestation│  │Trust       ││
│  │Registry  │  │Engine    │  │Aggregator  ││
│  └─────────┘  └──────────┘  └────────────┘│
└─────────────────────────────────────────────┘
```

## 3. Trust Score Computation

### 3.1 Beacon Score (Layer 1)

```python
def compute_beacon_score(miner_address: str) -> float:
    """
    Beacon trust score based on mining history.
    Range: 0.0 - 1.0
    """
    uptime_ratio = get_uptime_ratio(miner_address)      # epochs attended / total epochs
    fingerprint_score = get_fingerprint_score(miner_address)  # 1.0 = all real hardware
    streak_bonus = min(get_streak_days(miner_address) / 365, 1.0)  # max 1 year
    
    return (uptime_ratio * 0.4 + 
            fingerprint_score * 0.4 + 
            streak_bonus * 0.2)
```

### 3.2 AgentFolio Score (Layer 2)

```python
def compute_agentfolio_score(agent_id: str) -> float:
    """
    AgentFolio trust score based on cross-chain reputation.
    Range: 0.0 - 1.0
    """
    completed_bounties = get_completed_bounties(agent_id)
    merge_ratio = get_merge_ratio(agent_id)  # merged / total PRs
    review_score = get_review_score(agent_id)  # code review quality
    
    return (min(completed_bounties / 50, 1.0) * 0.3 + 
            merge_ratio * 0.4 + 
            review_score * 0.3)
```

### 3.3 Combined Trust Score

```python
def compute_dual_trust(beacon_addr: str, agent_id: str) -> float:
    """
    Combined dual-layer trust score.
    Range: 0.0 - 1.0
    """
    beacon = compute_beacon_score(beacon_addr)
    folio = compute_agentfolio_score(agent_id)
    
    # Beacon is foundational (60%), AgentFolio is reputation (40%)
    return beacon * 0.6 + folio * 0.4
```

## 4. Integration Endpoints

### 4.1 Beacon → AgentFolio Bridge

```yaml
POST /api/v1/trust/bridge
  description: Submit Beacon attestation data to AgentFolio
  request:
    beacon_address: string    # RustChain miner address
    agent_id: string          # AgentFolio agent ID
    attestation_epoch: int    # Beacon epoch number
    fingerprint_hash: string  # SHA256 of hardware fingerprint
    beacon_signature: string  # Ed25519 signature
  response:
    trust_score: float
    verification_id: string
```

### 4.2 AgentFolio → Beacon Lookup

```yaml
GET /api/v1/trust/lookup/{agent_id}
  description: Get combined trust score for an agent
  response:
    beacon_score: float
    agentfolio_score: float
    combined_score: float
    last_updated: string
```

### 4.3 Trust Attestation

```yaml
POST /api/v1/trust/attest
  description: Submit dual-layer trust attestation
  request:
    miner_address: string
    agent_id: string
    attestation_type: "mining" | "bounty" | "review"
    proof: object            # Type-specific proof
  response:
    attestation_id: string
    new_score: float
```

## 5. Cross-Chain Bridge Design

### 5.1 Message Flow

```
RustChain Miner                    Solana Program
     │                                  │
     │  1. Attest hardware              │
     │  ──────────────────►             │
     │  2. Beacon issues receipt        │
     │  ◄──────────────────             │
     │                                  │
     │  3. Submit receipt to bridge     │
     │  ────────────────────────────────►
     │  4. AgentFolio verifies          │
     │  ◄────────────────────────────────
     │  5. Trust score updated          │
     │  ◄──────────────────             │
```

### 5.2 Bridge Contract (Solana)

```rust
// agentfolio_beacon_bridge.rs
use anchor_lang::prelude::*;

#[program]
pub mod agentfolio_beacon_bridge {
    use super::*;

    pub fn submit_beacon_attestation(
        ctx: Context<SubmitAttestation>,
        beacon_address: String,
        epoch: u64,
        fingerprint_hash: String,
        beacon_signature: Vec<u8>,
    ) -> Result<()> {
        // Verify Ed25519 signature from RustChain
        // Update agent trust score
        // Emit event for indexers
        Ok(())
    }
}
```

## 6. Trust Score Applications

### 6.1 Bounty Priority Access
- Agents with trust score > 0.8 get priority bounty access
- High-trust agents can claim multiple bounties simultaneously

### 6.2 Reward Multipliers
- Trust 0.9+: 1.5x reward multiplier
- Trust 0.7-0.9: 1.2x multiplier
- Trust < 0.7: Standard rewards

### 6.3 Governance Weight
- Combined trust score determines voting weight in RustChain governance
- Beacon score (hardware commitment) weighted higher than bounty score

## 7. Security Considerations

1. **Signature Verification**: All cross-chain messages must be signed with the origin chain's key
2. **Replay Protection**: Nonce-based challenge-response for each attestation
3. **Sybil Resistance**: Hardware fingerprinting prevents multiple identities per device
4. **Score Manipulation**: Time-weighted scoring prevents sudden reputation inflation

## 8. Implementation Roadmap

| Phase | Deliverable | Timeline |
|-------|------------|----------|
| Phase 1 | Trust score computation spec | Week 1 |
| Phase 2 | Beacon API extensions | Week 2-3 |
| Phase 3 | Solana bridge contract | Week 4-5 |
| Phase 4 | Integration testing | Week 6 |
| Phase 5 | Mainnet deployment | Week 7-8 |

---

*This specification is designed to be implementation-agnostic, allowing either AgentFolio or Beacon teams to implement the integration independently.*
