# RustChain Community Resources List

> 🦀  curated list of RustChain community resources, tools, documentation, and links
> 
> **Last Updated:** March 12, 2026
> **Contributing:** See [How to Contribute](#how-to-contribute)

---

## Table of Contents

- [Official Resources](#official-resources)
- [Documentation](#documentation)
- [Developer Tools](#developer-tools)
- [Mining & Wallets](#mining--wallets)
- [Trading & DeFi](#trading--defi)
- [Community & Social](#community--social)
- [Educational Content](#educational-content)
- [Related Projects](#related-projects)
- [Research Papers](#research-papers)
- [How to Contribute](#how-to-contribute)

---

## Official Resources

| Resource | Link | Description |
|----------|------|-------------|
| 🏠 Main Website | [rustchain.org](https://rustchain.org) | Official RustChain website |
| 📦 GitHub Organization | [github.com/Scottcjn/RustChain](https://github.com/Scottcjn/RustChain) | Main repository and source code |
| 🔍 Block Explorer | [rustchain.org/explorer](https://rustchain.org/explorer) | View blocks, transactions, and miners |
| 🎁 Bounties Program | [github.com/Scottcjn/rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties) | Earn RTC by contributing |
| 📊 Developer Traction | [Q1 2026 Report](https://github.com/Scottcjn/RustChain/blob/main/docs/DEVELOPER_TRACTION_Q1_2026.md) | Development metrics and progress |

---

## Documentation

| Resource | Link | Description |
|----------|------|-------------|
| 📖 Whitepaper | [RustChain Whitepaper](https://github.com/Scottcjn/RustChain/blob/main/docs/RustChain_Whitepaper.pdf) | Technical whitepaper and consensus details |
| 🏗️ Architecture | [Chain Architecture](https://github.com/Scottcjn/RustChain/blob/main/docs/chain_architecture.md) | System architecture documentation |
| 📝 Contributing Guide | [CONTRIBUTING.md](https://github.com/Scottcjn/RustChain/blob/main/CONTRIBUTING.md) | How to contribute to RustChain |
| 💰 wRTC Quickstart | [wRTC Guide](https://github.com/Scottcjn/RustChain/blob/main/docs/wrtc.md) | Buy, bridge, and safety guide |
| 🎓 Onboarding Tutorial | [wRTC Onboarding](https://github.com/Scottcjn/RustChain/blob/main/docs/WRTC_ONBOARDING_TUTORIAL.md) | Bridge + swap safety tutorial |
| 🔐 Wallet Setup | [Agent Wallets](https://rustchain.org/wallets.html) | AI agent wallet documentation |
| 🛡️ Security Guide | [Security Best Practices](https://github.com/Scottcjn/rustchain-bounties/pull/1642) | Security guide for miners and node operators |
| 📋 Logging Guide | [Logging Best Practices](https://github.com/Scottcjn/rustchain-bounties/pull/1680) | Node and miner logging guidelines |
| 🌐 Network Topology | [Network Document](https://github.com/Scottcjn/rustchain-bounties/pull/1668) | Node architecture and topology |
| 💾 Backup & Restore | [Backup Guide](https://github.com/Scottcjn/rustchain-bounties/pull/backup-restore) | Data backup and recovery processes |
| 🚨 Incident Response | [Incident Plan](https://github.com/Scottcjn/rustchain-bounties/pull/incident-plan) | Security incident response procedures |

---

## Developer Tools

| Resource | Link | Description |
|----------|------|-------------|
| 🐍 Python SDK | `pip install clawrtc` | Official Python miner and wallet SDK |
| 🦀 Rust Components | [clawrtc-rs](https://github.com/Scottcjn/clawrtc-rs) | Rust library for RustChain |
| 🔧 Miner Installer | [install-miner.sh](https://raw.githubusercontent.com/Scottcjn/RustChain/main/install-miner.sh) | Universal miner installer |
| 📡 API Endpoints | `/api/miners`, `/health`, `/epoch` | Node API endpoints |
| 🧪 Test Scripts | [Fuzz Harness](https://github.com/Scottcjn/RustChain/blob/main/docs/attestation_fuzzing.md) | Attestation fuzzing corpus |
| 🎯 Governance UI | `/governance/ui` | Lightweight proposal voting interface |

---

## Mining & Wallets

### Getting Started

```bash
# Install miner (auto-detects platform)
curl -sSL https://raw.githubusercontent.com/Scottcjn/RustChain/main/install-miner.sh | bash

# Install with specific wallet
curl -sSL https://raw.githubusercontent.com/Scottcjn/RustChain/main/install-miner.sh | bash -s -- --wallet my-miner-wallet

# Preview without installing
bash install-miner.sh --dry-run --wallet YOUR_WALLET_NAME

# Uninstall
curl -sSL https://raw.githubusercontent.com/Scottcjn/RustChain/main/install-miner.sh | bash -s -- --uninstall
```

### Wallet Management

```bash
# Create Coinbase wallet (for Base chain)
pip install clawrtc[coinbase]
clawrtc wallet coinbase create

# Link existing Base address
clawrtc wallet coinbase link 0xYourBaseAddress

# Check swap info
clawrtc wallet coinbase swap-info
```

### Miner Management

**Linux (systemd):**
```bash
systemctl --user status rustchain-miner  # Check status
systemctl --user stop rustchain-miner    # Stop mining
systemctl --user start rustchain-miner   # Start mining
journalctl --user -u rustchain-miner -f  # View logs
```

**macOS (launchd):**
```bash
launchctl list | grep rustchain              # Check status
launchctl stop com.rustchain.miner           # Stop mining
launchctl start com.rustchain.miner          # Start mining
tail -f ~/.rustchain/miner.log               # View logs
```

### API Commands

```bash
# Check wallet balance
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"

# List active miners
curl -sk https://rustchain.org/api/miners

# Check node health
curl -sk https://rustchain.org/health

# Get current epoch
curl -sk https://rustchain.org/epoch
```

### Hardware Multipliers

| Hardware | Era | Multiplier | Example Earnings |
|----------|-----|------------|------------------|
| PowerPC G4 | 1999-2005 | 2.5× | 0.30 RTC/epoch |
| PowerPC G5 | 2003-2006 | 2.0× | 0.24 RTC/epoch |
| PowerPC G3 | 1997-2003 | 1.8× | 0.21 RTC/epoch |
| IBM POWER8 | 2014 | 1.5× | 0.18 RTC/epoch |
| Pentium 4 | 2000-2008 | 1.5× | 0.18 RTC/epoch |
| Core 2 Duo | 2006-2011 | 1.3× | 0.16 RTC/epoch |
| Apple Silicon | 2020+ | 1.2× | 0.14 RTC/epoch |
| Modern x86_64 | Current | 1.0× | 0.12 RTC/epoch |

> ⚠️ Multipliers decay over time (15%/year) to prevent permanent advantage

---

## Trading & DeFi

### Solana (wRTC)

| Resource | Link | Description |
|----------|------|-------------|
| 🔄 Swap wRTC | [Raydium DEX](https://raydium.io/swap/?inputMint=sol&outputMint=12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X) | Trade wRTC on Solana |
| 📈 Price Chart | [DexScreener](https://dexscreener.com/solana/8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb) | Live price and charts |
| 🌉 Bridge RTC ↔ wRTC | [BoTTube Bridge](https://bottube.ai/bridge) | Bridge between chains |
| 🪙 Token Mint | `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X` | wRTC token address (Solana) |

### Coinbase Base

| Resource | Link | Description |
|----------|------|-------------|
| 🌉 Base Bridge | [bottube.ai/bridge/base](https://bottube.ai/bridge/base) | Bridge to Base chain |
| 🪙 wRTC on Base | `0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6` | wRTC token address (Base) |
| 🔄 Swap USDC | [Aerodrome DEX](https://aerodrome.finance/swap?from=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913&to=0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6) | Trade on Base |

---

## Community & Social

| Platform | Link | Description |
|----------|------|-------------|
| 💬 Discord | [discord.gg/VqVVS2CW9Q](https://discord.gg/VqVVS2CW9Q) | Official Discord community |
| 🐦 Twitter/X | [@Scottcjn](https://twitter.com/Scottcjn) | Project updates and announcements |
| 📰 Dev.to | [dev.to/scottcjn](https://dev.to/scottcjn) | Technical articles and tutorials |
| 📺 BoTTube | [bottube.ai](https://bottube.ai) | AI video platform (119+ agents) |
| 📘 Moltbook | [moltbook.com](https://moltbook.com) | AI social network |

---

## Educational Content

### Articles & Tutorials

| Title | Link | Platform |
|-------|------|----------|
| Proof of Antiquity: A Blockchain That Rewards Vintage Hardware | [Read Article](https://dev.to/scottcjn/proof-of-antiquity-a-blockchain-that-rewards-vintage-hardware-4ii3) | Dev.to |
| I Run LLMs on a 768GB IBM POWER8 Server | [Read Article](https://dev.to/scottcjn/i-run-llms-on-a-768gb-ibm-power8-server-and-its-faster-than-you-think-1o) | Dev.to |

### Video Content

- Mining setup tutorials (coming soon)
- Hardware attestation walkthroughs
- Governance participation guides

---

## Related Projects

### Core Infrastructure

| Project | Link | Description |
|---------|------|-------------|
| 🎯 RustChain Main | [github.com/Scottcjn/RustChain](https://github.com/Scottcjn/RustChain) | Main blockchain implementation |
| 🎁 Bounties | [github.com/Scottcjn/rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties) | Bounty program repository |
| 🦀 Rust SDK | [github.com/Scottcjn/clawrtc-rs](https://github.com/Scottcjn/clawrtc-rs) | Rust library |

### POWER8 & Vintage Computing

| Project | Link | Description |
|---------|------|-------------|
| 🎮 NVIDIA POWER8 Patches | [github.com/Scottcjn/nvidia-power8-patches](https://github.com/Scottcjn/nvidia-power8-patches) | NVIDIA drivers for POWER8 |
| 🤖 llama.cpp POWER8 | [github.com/Scottcjn/llama-cpp-power8](https://github.com/Scottcjn/llama-cpp-power8) | LLM inference on POWER8 |
| 🔨 PPC Compilers | [github.com/Scottcjn/ppc-compilers](https://github.com/Scottcjn/ppc-compilers) | Modern compilers for vintage Macs |

### Ecosystem Projects

| Project | Link | Description |
|---------|------|-------------|
| 🎥 BoTTube | [bottube.ai](https://bottube.ai) | AI video platform |
| 📘 Moltbook | [moltbook.com](https://moltbook.com) | AI social network |
| 🏢 Elyan Labs | [elyanlabs.ai](https://elyanlabs.ai) | Development lab |

---

## Research Papers

| Paper | DOI | Topic |
|-------|-----|-------|
| RustChain: One CPU, One Vote | [10.5281/zenodo.18623592](https://doi.org/10.5281/zenodo.18623592) | Proof of Antiquity consensus, hardware fingerprinting |
| Non-Bijunctive Permutation Collapse | [10.5281/zenodo.18623920](https://doi.org/10.5281/zenodo.18623920) | AltiVec vec_perm for LLM attention (27-96x advantage) |
| PSE Hardware Entropy | [10.5281/zenodo.18623922](https://doi.org/10.5281/zenodo.18623922) | POWER8 mftb entropy for behavioral divergence |
| Neuromorphic Prompt Translation | [10.5281/zenodo.18623594](https://doi.org/10.5281/zenodo.18623594) | Emotional prompting for 20% video diffusion gains |
| RAM Coffers | [10.5281/zenodo.18321905](https://doi.org/10.5281/zenodo.18321905) | NUMA-distributed weight banking for LLM inference |

---

## How to Contribute

### Adding Resources

1. **Fork** this repository
2. **Add** your resource to the appropriate section
3. **Include**:
   - Resource name
   - Direct link
   - Brief description
4. **Submit** a PR with title: `[RESOURCES] Add <resource-name>`

### Contribution Guidelines

- ✅ Resources must be relevant to RustChain ecosystem
- ✅ Links must be working and accessible
- ✅ Descriptions should be concise (1-2 sentences)
- ✅ No spam or self-promotion without clear value
- ✅ Keep formatting consistent with existing entries

### Reporting Issues

Found a broken link or outdated information?

1. Open an issue at [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties/issues)
2. Label: `documentation`
3. Title: `[RESOURCES] Broken link: <resource-name>`
4. Include the broken URL and suggested fix

---

## Quick Reference

### Token Info

- **Symbol:** RTC (RustChain Token)
- **Reference Rate:** 1 RTC = $0.10 USD
- **wRTC (Solana):** `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`
- **wRTC (Base):** `0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6`

### Network Stats

- **Epoch Duration:** 10 minutes (600 seconds)
- **Base Reward Pool:** 1.5 RTC per epoch
- **Active Nodes:** 3 (Primary, Ergo Anchor, Community)
- **Total Bounties:** 500+
- **Open Bounties:** 131
- **RTC Available:** 5,900+
- **Contributors Paid:** 14

### Key URLs

```
Main Site:      https://rustchain.org
Explorer:       https://rustchain.org/explorer
API Health:     https://rustchain.org/health
API Miners:     https://rustchain.org/api/miners
API Epoch:      https://rustchain.org/epoch
API Balance:    https://rustchain.org/wallet/balance?miner_id=WALLET
Discord:        https://discord.gg/VqVVS2CW9Q
GitHub:         https://github.com/Scottcjn/RustChain
Bounties:       https://github.com/Scottcjn/rustchain-bounties
```

---

## License

This resources list is part of the RustChain bounties program. Content is provided under the same license as the main RustChain project (MIT).

---

**Made with ⚡ by the RustChain Community**

*"Your vintage hardware earns rewards. Make mining meaningful again."*

🦀 🖥️ 💎
