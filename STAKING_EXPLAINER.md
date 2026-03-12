# RustChain Staking Explainer

## Overview

RustChain uses a **Proof-of-Antiquity (PoA)** consensus mechanism, which is fundamentally different from traditional Proof-of-Stake (PoS) or Proof-of-Work (PoW) systems. This document explains how the RustChain staking/mining mechanism works, reward structures, and associated risks.

> **Note:** While commonly referred to as "staking," RustChain technically uses **mining with hardware attestation**. You stake your vintage hardware's computational capacity rather than locking up tokens.

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [Staking/Mining Mechanism](#stakingmining-mechanism)
3. [Reward Structure](#reward-structure)
4. [Hardware Multipliers](#hardware-multipliers)
5. [Risks](#risks)
6. [Getting Started](#getting-started)
7. [FAQ](#faq)

---

## How It Works

RustChain flips traditional mining on its head: **older hardware earns higher rewards**. The protocol validates that you're running on genuine physical hardware (not emulated) and rewards you based on your hardware's age and rarity.

### Core Principle: 1 CPU = 1 Vote

Each miner gets one vote weighted by hardware antiquity. The older and rarer your hardware, the higher your reward multiplier.

```
┌─────────────────────────────────────────────────────────────┐
│                    RustChain Epoch Cycle                    │
├─────────────────────────────────────────────────────────────┤
│  1. Miner submits hardware attestation                      │
│  2. Network validates fingerprint (6 checks)                │
│  3. Miner enrolled in current epoch with multiplier         │
│  4. Epoch runs for 144 slots (~24 hours)                    │
│  5. Settlement: rewards distributed by weight               │
│  6. Hash anchored to Ergo blockchain                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Staking/Mining Mechanism

### Step 1: Hardware Attestation

Every miner must prove their hardware is real through **6 hardware fingerprint checks**:

| # | Check | Purpose | VM Detection |
|---|-------|---------|--------------|
| 1 | **Clock Skew** | Crystal oscillator imperfections | VMs use host clock (too perfect) |
| 2 | **Cache Timing** | L1/L2/L3 latency curves | Emulators flatten cache hierarchy |
| 3 | **SIMD Identity** | AltiVec/SSE/NEON biases | Different timing in emulation |
| 4 | **Thermal Entropy** | CPU temp under load | VMs report static temps |
| 5 | **Instruction Jitter** | Opcode execution variance | Real silicon has nanosecond jitter |
| 6 | **Behavioral Heuristics** | Hypervisor signatures | Detects VMware, QEMU, etc. |

### Step 2: Enrollment

Once validated, your miner is enrolled in the current epoch with a **multiplier** based on your hardware type.

### Step 3: Epoch Settlement

Every 144 slots (~24 hours), the epoch pot (1.5 RTC) is distributed proportionally:

```
miner_reward = epoch_pot × (miner_multiplier / total_weight)
```

**Example:**
- G4 miner: 2.5x weight
- x86 miner: 1.0x weight
- Total weight: 3.5

**G4 receives:** 1.5 × (2.5/3.5) = **1.07 RTC**
**x86 receives:** 1.5 × (1.0/3.5) = **0.43 RTC**

---

## Reward Structure

### Token Supply

| Metric | Value |
|--------|-------|
| **Total Supply** | 8,000,000 RTC |
| **Premine** | 75,000 RTC (dev/bounties) |
| **Epoch Pot** | 1.5 RTC / epoch |
| **Epoch Duration** | ~24 hours (144 slots) |
| **Reference Rate** | 1 RTC = $0.10 USD |

### Distribution Model

- **Mining Rewards:** ~99% of tokens distributed through PoA mining
- **Development/Bounties:** Premined allocation for ecosystem growth
- **No Transfer Fees:** RustChain aims for fee-free transfers

---

## Hardware Multipliers

### Base Multipliers by Hardware Era

| Hardware | Era | Base Multiplier | Example Earnings/epoch |
|----------|-----|-----------------|------------------------|
| **PowerPC G4** | 1999-2005 | **2.5×** | 0.30 RTC |
| **PowerPC G5** | 2003-2006 | **2.0×** | 0.24 RTC |
| **PowerPC G3** | 1997-2003 | **1.8×** | 0.21 RTC |
| **IBM POWER8** | 2014 | **1.5×** | 0.18 RTC |
| **Pentium 4** | 2000-2008 | **1.5×** | 0.18 RTC |
| **Core 2 Duo** | 2006-2011 | **1.3×** | 0.16 RTC |
| **Apple Silicon** | 2020+ | **1.2×** | 0.14 RTC |
| **Modern x86_64** | Current | **1.0×** | 0.12 RTC |

### Decay Mechanism

Vintage hardware (>5 years) experiences **15% annual decay** to prevent permanent advantage:

```
decay_factor = 1.0 - (0.15 × (age - 5) / 5)
final_multiplier = 1.0 + (vintage_bonus × decay_factor)
```

**Example: G4 (24 years old, base 2.5x)**
- Vintage bonus: 1.5 (2.5 - 1.0)
- Decay: 1.0 - (0.15 × 19/5) = 0.43
- **Final: 1.0 + (1.5 × 0.43) = 1.645x**

### Loyalty Bonus

Modern hardware earns **+15%/year uptime** (capped at +50%):

```
loyalty_bonus = min(0.5, uptime_years × 0.15)
final = base + loyalty_bonus
```

---

## Risks

### 1. Hardware Risk

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Hardware Failure** | Vintage hardware may fail unexpectedly | Maintain backups, monitor temps |
| **Power Consumption** | Old hardware less energy efficient | Calculate ROI including electricity |
| **Parts Scarcity** | Replacement parts hard to find | Stock spare parts if possible |

### 2. Economic Risk

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Token Price Volatility** | RTC price may fluctuate | Only invest what you can afford to lose |
| **Multiplier Decay** | Vintage bonus decreases over time | Factor decay into ROI calculations |
| **Network Participation** | More miners = lower individual rewards | Early participation advantageous |

### 3. Technical Risk

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Attestation Failure** | Fingerprint checks may fail | Ensure genuine hardware, no VMs |
| **Network Connectivity** | Requires stable internet | Use wired connection if possible |
| **Software Updates** | Protocol may evolve | Stay updated with latest miner version |

### 4. Security Risk

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Private Key Loss** | No recovery mechanism | Backup wallet keys securely |
| **Wallet Address Errors** | Typos in wallet ID | Double-check before transactions |
| **Phishing** | Fake nodes/websites | Only use official rustchain.org domains |

---

## Getting Started

### Prerequisites

- Physical hardware (not VM/emulator)
- Python 3.10+
- Internet connection
- Wallet ID (miner_id)

### Quick Start

```bash
# 1. Install miner
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash

# 2. Check balance
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_WALLET_NAME"

# 3. Monitor miner status
curl -sk https://rustchain.org/api/miners
```

### Platform-Specific Commands

**Linux (systemd):**
```bash
systemctl --user status rustchain-miner
journalctl --user -u rustchain-miner -f
```

**macOS (launchd):**
```bash
launchctl list | grep rustchain
tail -f ~/.rustchain/miner.log
```

---

## FAQ

### Q: Can I run on a VM?
**A:** No. The 6-check fingerprint system will detect and reject VMs/emulators.

### Q: How much can I earn?
**A:** Depends on your hardware multiplier and total network participation. A G4 might earn ~0.30 RTC/epoch (~$0.03/day at reference rate).

### Q: Do I need to lock up RTC tokens?
**A:** No. Unlike traditional staking, you're staking hardware capacity, not tokens.

### Q: What if my hardware fails?
**A:** Simply re-attest with new hardware. Your wallet ID remains the same.

### Q: Can I run multiple miners?
**A:** Yes, but each must be on separate physical hardware. Running multiple on same machine will be detected.

### Q: How do I cash out?
**A:** RTC can be bridged to wRTC on Solana and swapped on DEXes like Raydium. See [wRTC Quickstart](docs/wrtc.md).

---

## Resources

- **GitHub:** https://github.com/Scottcjn/Rustchain
- **Block Explorer:** https://50.28.86.131/explorer
- **Discord:** https://discord.gg/VqVVS2CW9Q
- **Whitepaper:** https://github.com/Scottcjn/Rustchain/tree/main/docs/whitepaper
- **API Docs:** https://github.com/Scottcjn/Rustchain/blob/main/docs/API.md

---

## License

This document is licensed under the same terms as the RustChain project (MIT License).

**Last Updated:** March 2026
**Protocol Version:** RIP-200 v2.2.1
