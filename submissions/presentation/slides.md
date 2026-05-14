# RustChain — Proof of Antiquity Blockchain

---

## Slide 1: Title

# RustChain
## Proof of Antiquity Blockchain
### Where Vintage Hardware Mines Again

> *"Your 2005 laptop isn't e-waste. It's a mining rig."*

---

## Slide 2: What is RustChain?

A lightweight blockchain ecosystem written in **Rust** that rewards vintage hardware over modern silicon.

- **Anti-arms-race** by design
- **Ultra-low overhead** — runs on < 32 MB RAM
- **Hardware diversity** as a security model
- Written in Rust for memory safety and bare-metal performance

---

## Slide 3: The Problem

Modern blockchain has failed its original promise:

- 🔥 **E-waste skyrocketing** — perfectly functional hardware in landfills
- 🏭 **Centralization** — mining controlled by industrial farms
- 💰 **Priced out** — enthusiasts can't participate
- ⚡ **Energy waste** — ASICs consuming megawatts for trust

---

## Slide 4: The Solution — Reverse Proof-of-Work

RustChain **inverts** the incentive model:

| Traditional Blockchain | RustChain |
|----------------------|-----------|
| Newest hardware wins | Oldest hardware wins |
| Hash rate is king | Antiquity is king |
| $80,000 stake required | $20 eBay laptop |
| Centralized farms | Distributed enthusiasts |

---

## Slide 5: Consensus — Proof of Antiquity (PoA)

RustChain's consensus rewards the **age and authenticity** of physical hardware:

- **Hardware fingerprinting** — 6+1 cryptographic checks
- **Anti-emulation** — VMs and containers are rejected (0x multiplier)
- **Vintage multiplier** — older, rarer silicon earns more
- **Physical commitment** — SHA-256 hash of nonce + wallet + entropy data

---

## Slide 6: Hardware Fingerprinting (6+1 Checks)

| # | Check | What It Measures |
|---|-------|-----------------|
| 1 | Clock-Skew & Oscillator Drift | Timing variance from `rdtsc`/`mftb` |
| 2 | Cache Timing Fingerprint | L1/L2/L3 latency patterns |
| 3 | SIMD Unit Identity | SSE/AVX/AltiVec/NEON timing |
| 4 | Thermal Drift Entropy | Entropy across thermal states |
| 5 | Instruction Path Jitter | Cycle-level jitter across int/FP/branch |
| 6 | Anti-Emulation | VM/hypervisor detection |
| +1 | Physical Context | Hardware serials + MAC consistency |

---

## Slide 7: Hardware Certification Flow

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐     ┌──────────┐
│   Miner      │────▶│   Challenge   │────▶│   Fingerprint  │────▶│  Submit   │
│   Requests   │     │   (Nonce)     │     │   (6+1 checks) │     │  Report   │
│   Nonce      │     │   10-min TTL  │     │                │     │           │
└─────────────┘     └──────────────┘     └───────────────┘     └──────────┘
                                                                       │
                                                                       ▼
                                                              ┌──────────────┐
                                                              │   Node        │
                                                              │   Validation  │
                                                              │   ✓ Nonce     │
                                                              │   ✓ Commit    │
                                                              │   ✓ Fingerprint│
                                                              └──────────────┘
```

---

## Slide 8: Attestation Payload

```json
{
  "miner": "WALLET_ADDRESS",
  "miner_id": "my-powerbook-g4",
  "nonce": "SERVER_PROVIDED_NONCE",
  "report": {
    "commitment": "sha256(nonce + wallet + entropy_data)",
    "entropy_score": 0.0045
  },
  "device": {
    "family": "PowerPC",
    "arch": "g4",
    "model": "PowerMac3,6",
    "serial": "CK245..."
  },
  "fingerprint": {
    "all_passed": true
  }
}
```

---

## Slide 9: Antiquity Multipliers

| Tier | Multiplier | Examples |
|------|-----------|---------|
| **Legendary** | 4.0x | Intel 386, Motorola 68000, MIPS R2000 |
| **Epic** | 2.5x | PowerPC G4, 486, Pentium I |
| **Rare** | 2.0x | PowerPC G5, DEC Alpha, SPARC |
| **Common** | 0.8x–1.0x | Modern x86_64 (Skylake+, Zen 3+) |
| **Flagged** | 0x | VMs, Emulators |

A 2003 PowerPC G4 iBook earns **2.5x** more than a modern Threadripper.

---

## Slide 10: Multiplier Formula

### Time Decay (Vintage Hardware)
```
decay_factor = 1.0 - (0.15 × years_since_genesis)
final_multiplier = 1.0 + (vintage_bonus × decay_factor)
```
Vintage bonus decays 15% per year from chain genesis (2025).

### Loyalty Bonus (Modern Hardware)
```
+15% per year of uptime, capped at +50% (1.5x total)
```

### Server Hardware Bonus
```
Xeon / EPYC / Opteron → flat +10%
```

---

## Slide 11: Token Economics

- **Token**: RTC (RustChain Token)
- **Reference rate**: $0.10 USD
- **No ICO, no presale, no VC funding** — fully self-funded by Elyan Labs
- **Distribution**: 100% via mining and bounty rewards
- **Epoch**: ~10 minutes (144 blocks/day)
- **Reward model**: Proportional to attestation weight

```
Reward_miner = (Weight_miner / Σ Weight_all) × TotalEpochPot
```

---

## Slide 12: Epoch Reward Mechanism

```
┌─────────────────────────────────────────────────┐
│                 EPOCH (~10 min)                   │
│                                                   │
│  Miners enroll → Attest → Submit fingerprints    │
│                                                   │
│  At epoch end:                                    │
│  1. Sum all attestation weights                   │
│  2. Calculate each miner's share                  │
│  3. Distribute RTC proportionally                 │
│                                                   │
│  Next epoch begins...                             │
└─────────────────────────────────────────────────┘
```

---

## Slide 13: vs Bitcoin PoW

| Aspect | Bitcoin PoW | RustChain PoA |
|--------|------------|---------------|
| Consensus | SHA-256 hash race | Hardware antiquity verification |
| Hardware | ASIC miners ($10K+) | Vintage Mac ($20-100) |
| Energy | ~150 TWh/year | Negligible |
| Sybil resistance | Computational cost | Physical hardware identity |
| E-waste | Generates massive e-waste | Repurposes existing hardware |
| Entry cost | Thousands of dollars | A trip to eBay |

---

## Slide 14: vs Ethereum PoS

| Aspect | Ethereum PoS | RustChain PoA |
|--------|-------------|---------------|
| Stake required | 32 ETH (~$80,000+) | Physical hardware |
| Barrier to entry | Financial capital | A vintage computer |
| Finality | ~12.8 min (2 epochs) | Per-block confirmation |
| Sybil resistance | Economic slashing | Hardware fingerprinting |
| Centralization risk | Lido controls ~30% | No stake pooling needed |
| Validator hardware | Modern server required | 256 MB RAM sufficient |

---

## Slide 15: Security Model

### Multi-layered Defense

1. **Nonce-based replay protection** — short-lived challenges (10-min TTL)
2. **6+1 fingerprint checks** — VM/emulator detection
3. **No mock signatures** — mandatory admin key
4. **Validated JSON** — strict schema enforcement
5. **Hardware serial verification** — manufacturing database cross-check
6. **Antiquity multiplier** — disincentivizes modern hardware farms

### Chain Security Features
- `no_mock_sigs`
- `mandatory_admin_key`
- `replay_protection`
- `validated_json`

---

## Slide 16: Developer Tools

| Tool | Description |
|------|-------------|
| **Rust Miner** | Native Rust binary — cross-platform (x86_64, ARM, PowerPC, RISC-V) |
| **Apple II Miner** | 6502 assembly — 4.0x multiplier on real Apple II hardware |
| **Python SDK** | `pip install clawrtc` — miner, BCOS scanning, wallet management |
| **MCP Server** | Model Context Protocol server for AI agent integration |
| **VS Code Extension** | Syntax highlighting and wallet integration |
| **Grafana Dashboards** | Real-time monitoring for miners and nodes |
| **Prometheus Metrics** | Standard `/metrics` endpoint for observability |

---

## Slide 17: API Reference

**Base URL**: `https://50.28.86.131` (self-signed TLS)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | System statistics (block time, epoch, miners) |
| `/health` | GET | Node health check |
| `/epoch` | GET | Current epoch information |
| `/balance/{miner}` | GET | Miner balance lookup |
| `/attest/challenge` | POST | Request attestation nonce |
| `/attest/submit` | POST | Submit attestation report |
| `/epoch/enroll` | POST | Enroll in current epoch |
| `/withdraw/*` | POST/GET | Withdrawal management |
| `/metrics` | GET | Prometheus metrics |

---

## Slide 18: BoTTube Integration

RustChain's built-in video platform for the community:

- 📺 **Embedded player** — lightweight HTML5 video player
- 🎬 **Content bounties** — earn RTC for tutorial videos
- 🔗 **API-driven** — `/api/videos/{id}/stream`
- 🤖 **BoTTube Upload Bot** — automated video submission pipeline

```html
<!-- Embed anywhere -->
<iframe src="https://rustchain.org/bottube/{video_id}"></iframe>
```

---

## Slide 19: Roadmap

| Phase | Timeline | Goals |
|-------|----------|-------|
| **Phase 1** | ✅ Complete | Core chain, Rust miner, Apple II miner, BCOS certification |
| **Phase 2** | 🔄 In Progress | 500+ stars, exchange listings, DEX pools, dual-mining |
| **Phase 3** | 📋 Planned | Cross-chain bridges, mobile wallet, DAO governance |
| **Phase 4** | 🔮 Future | Museum partnerships, hardware certification program, global retro-computing network |

### Active Initiatives
- Warthog dual-mining integration
- Ledger integrity red team (200 RTC bounty)
- Consensus attack red team (200 RTC bounty)
- Multi-language documentation (DE, ES, FR, PT, ZH)

---

## Slide 20: Supported Architectures

| CPU | Family | Arch | Multiplier |
|-----|--------|------|-----------|
| PowerPC 7450 | PowerPC | g4 | **2.5x** |
| PowerPC 970 | PowerPC | g5 | **2.0x** |
| PowerPC 750 | PowerPC | g3 | **1.8x** |
| Intel Core 2 | x86_64 | core2duo | 1.3x |
| Apple M1/M2/M3 | ARM | apple_silicon | 1.2x |
| StarFive JH7110 | RISC-V | starfive | 1.1x |
| Modern x86_64 | x86_64 | modern | 1.0x |
| **Apple II (6502)** | 6502 | apple2 | **4.0x** ⭐ |

---

## Slide 21: Get Started

```bash
# 1. Clone the miner
git clone https://github.com/Scottcjn/RustChain.git
cd rustchain-miner

# 2. Build
cargo build --release

# 3. Start mining
./target/release/rustchain-miner --wallet YOUR_WALLET

# 4. Check your balance
curl -sk https://50.28.86.131/balance/YOUR_WALLET
```

### Or earn via bounties:
Browse 131 open bounties → [github.com/Scottcjn/rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties)

---

## Slide 22: Community & Links

| Resource | Link |
|----------|------|
| **RustChain** | [github.com/Scottcjn/RustChain](https://github.com/Scottcjn/RustChain) |
| **Block Explorer** | [50.28.86.131/explorer](https://50.28.86.131/explorer) |
| **Discord** | [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q) |
| **Bounties** | [github.com/Scottcjn/rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties) |
| **BCOS** | [rustchain.org/bcos/](https://rustchain.org/bcos/) |
| **Traction Report** | Q1 2026 Developer Traction Report |

---

## Slide 23: Q&A

# Questions?

**RustChain** — We put the power back in the old circuits. ⚡

- ⭐ Star us: [github.com/Scottcjn/RustChain](https://github.com/Scottcjn/RustChain)
- 💬 Discord: [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q)
- 📧 Contribute: 131 open bounties, 5,900+ RTC available

---

## Appendix: Stats

- **Total bounties created**: 500+
- **Open bounties**: 131
- **RTC available**: 5,900+
- **Contributors paid**: 14
- **Total paid out**: 22,756 RTC
- **Chain version**: 2.2.1-security-hardened
- **Active features**: RIP-0005, RIP-0008, RIP-009, RIP-0142, RIP-0143, RIP-0144
- **1,882 commits · 97 repos · 1,334 stars**
