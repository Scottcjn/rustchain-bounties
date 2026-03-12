# RustChain One-Pager

## 🚀 What is RustChain?

**RustChain** is a **Proof-of-Antiquity blockchain** that flips crypto mining upside-down: instead of rewarding the fastest hardware, it rewards the **oldest hardware**. Your vintage PowerPC G4, DOS machine, or retro computer earns **higher mining rewards** than modern rigs.

> *"Your vintage hardware earns rewards. Make mining meaningful again."*

---

## 💰 Token: RTC (RustChain Token)

| Metric | Value |
|--------|-------|
| **Reference Rate** | 1 RTC = $0.10 USD |
| **Token on Solana** | wRTC: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` |
| **Token on Base** | `0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6` |
| **Swap** | [Raydium (Solana)](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) \| [Aerodrome (Base)](https://aerodrome.finance/swap?from=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&to=0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6) |
| **Bridge** | [BoTTube Bridge](https://bottube.ai/bridge) |

---

## 🎯 Core Innovation: Proof-of-Antiquity

### Hardware Rewards Multiplier

| Hardware | Era | Multiplier | Earnings/Epoch |
|----------|-----|------------|----------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC |
| **Modern x86_64** | Current | **1.0×** | 0.12 RTC |

*Multipliers decay 15%/year to prevent permanent advantage.*

---

## 🔒 Security: Hardware Fingerprinting

Every miner must prove their hardware is **real, not emulated**. RustChain uses **6 hardware checks**:

1. **Clock-Skew & Oscillator Drift** ← Silicon aging patterns
2. **Cache Timing Fingerprint** ← L1/L2/L3 latency signatures
3. **SIMD Unit Identity** ← AltiVec/SSE/NEON bias
4. **Thermal Drift Entropy** ← Heat curves are unique
5. **Instruction Path Jitter** ← Microarchitecture jitter maps
6. **Anti-Emulation Checks** ← Detect VMs/emulators

> **VMs receive 1 billionth of normal rewards** — real vintage silicon has unique aging patterns that can't be faked.

---

## ⛓️ Consensus: One CPU, One Vote

Unlike PoW where hash power = votes, RustChain uses **round-robin consensus**:

- Each unique hardware device gets **exactly 1 vote per epoch**
- Rewards split equally among all voters, then multiplied by antiquity
- No advantage from running multiple threads or faster CPUs

**Epoch Duration:** 10 minutes (600 seconds)  
**Base Reward Pool:** 1.5 RTC per epoch

---

## 🛠️ Getting Started

### Install Miner (1 command)

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

### Or via Python

```bash
pip install clawrtc
clawrtc mine --dry-run
```

### Check Balance

```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"
```

### Network Health

```bash
curl -sk https://rustchain.org/health
curl -sk https://rustchain.org/epoch
curl -sk https://rustchain.org/api/miners
```

---

## 🌐 Ecosystem

| Project | Description | Link |
|---------|-------------|------|
| **RustChain** | Proof-of-Antiquity blockchain | [rustchain.org](https://rustchain.org) |
| **BoTTube** | AI video platform (119+ agents) | [bottube.ai](https://bottube.ai) |
| **Moltbook** | AI social network | [moltbook.com](https://moltbook.com) |
| **Block Explorer** | View blocks & transactions | [rustchain.org/explorer](https://rustchain.org/explorer) |

---

## 🎁 Earn RTC: Bounties & Contributions

Contribute to earn RTC tokens. All work is paid:

| Tier | Reward | Examples |
|------|--------|----------|
| **Micro** | 1-10 RTC | Typo fix, small docs, simple test |
| **Standard** | 20-50 RTC | Feature, refactor, new endpoint |
| **Major** | 75-100 RTC | Security fix, consensus improvement |
| **Critical** | 100-150 RTC | Vulnerability patch, protocol upgrade |

**Browse bounties:** [github.com/Scottcjn/rustchain-bounties/issues](https://github.com/Scottcjn/rustchain-bounties/issues)

---

## 📚 Resources

| Resource | Link |
|----------|------|
| **GitHub** | [github.com/Scottcjn/RustChain](https://github.com/Scottcjn/RustChain) |
| **Whitepaper** | [DOI: 10.5281/zenodo.18623592](https://doi.org/10.5281/zenodo.18623592) |
| **Discord** | [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q) |
| **Price Chart** | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) |
| **Dev Traction Report** | [Q1 2026](https://github.com/Scottcjn/RustChain/blob/main/docs/DEVELOPER_TRACTION_Q1_2026.md) |

---

## 🏆 Badges & Achievements

Earn commemorative badges for mining milestones:

- 🔥 **Bondi G3 Flamekeeper** — Mine on PowerPC G3 (Rare)
- ⚡ **QuickBasic Listener** — Mine from DOS machine (Legendary)
- 🛠️ **DOS WiFi Alchemist** — Network DOS machine (Mythic)
- 🏛️ **Pantheon Pioneer** — First 100 miners (Limited)

---

## 🎯 Why RustChain?

| Traditional PoW | RustChain |
|-----------------|-----------|
| Rewards fastest hardware | Rewards **oldest** hardware |
| Newer = Better | **Older = Better** |
| Wasteful energy consumption | **Preserves computing history** |
| Race to the bottom | **Rewards digital preservation** |

**Core Principle:** Authentic vintage hardware that has survived decades deserves recognition. RustChain flips mining upside-down.

> The name comes from a literal 486 laptop with oxidized serial ports that still boots to DOS and mines RTC. *"Rust"* here means iron oxide on 30-year-old silicon — not the programming language.

---

## 📞 Contact & Community

- **Discord:** [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q)
- **GitHub:** [github.com/Scottcjn](https://github.com/Scottcjn)
- **Website:** [rustchain.org](https://rustchain.org)

---

**Made with ⚡ by [Elyan Labs](https://elyanlabs.ai)**  
*License: MIT*

---

*Last updated: March 2026*
