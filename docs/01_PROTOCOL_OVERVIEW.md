# RustChain Protocol Documentation

> Complete technical reference for the RustChain Proof-of-Antiquity blockchain.
> Last updated: 2026-04-09 | Protocol version: 2.2.1-rip200

---

## Table of Contents

1. [Overview](#overview)
2. [RIP-200: Proof-of-Antiquity Consensus](#rip-200-proof-of-antiquity-consensus)
3. [Antiquity Multipliers](#antiquity-multipliers)
4. [Hardware Fingerprinting](#hardware-fingerprinting)
5. [Token Economics](#token-economics)
6. [Network Architecture](#network-architecture)
7. [API Reference](./API_REFERENCE.md)
8. [Glossary](./GLOSSARY.md)

---

## Overview

**RustChain** is a DePIN (Decentralized Physical Infrastructure Network) blockchain that rewards the preservation and operation of vintage computing hardware. Unlike traditional PoW chains that reward speed and modern hardware, RustChain rewards longevity — older machines earn higher mining multipliers because they represent real, continuous physical presence.

### Key Properties

| Property | Value |
|----------|-------|
| Native Token | RTC (RustChain Token) |
| Consensus | RIP-200 Proof-of-Antiquity |
| Current Version | 2.2.1-rip200 |
| Active Miners | ~13 |
| Attestation Nodes | 3 |
| Hardware Architectures | 15+ (PowerPC, SPARC, MIPS, ARM, x86, RISC-V, 68K, etc.) |
| Explorer | https://50.28.86.131/explorer |

---

## RIP-200: Proof-of-Antiquity Consensus

RIP-200 is RustChain's consensus mechanism. It validates that:
1. A real physical machine is participating (not a VM, emulator, or rented instance)
2. The machine has been continuously online for a verifiable period
3. The hardware's age correlates with its antiquity multiplier

### The 6+1 Hardware Checks

RustChain uses **6 mandatory hardware fingerprint checks + 1 AI validation step**:

```
┌─────────────────────────────────────────────────────────────┐
│                 PROOF-OF-ANTIQUITY CHECKS                   │
├─────────────┬───────────────────────────────────────────────┤
│ Check 1     │ Clock Drift Analysis                          │
│             │ Measures oscillator drift over time. VMs       │
│             │ have near-zero drift. Real silicon drifts.    │
├─────────────┼───────────────────────────────────────────────┤
│ Check 2     │ Cache Timing Signature                        │
│             │ L1/L2/L3 cache latency patterns are unique   │
│             │ to each CPU model and age.                   │
├─────────────┼───────────────────────────────────────────────┤
│ Check 3     │ SIMD Instruction Set Identity                │
│             │ Detects available SIMD extensions (SSE,      │
│             │ AVX, NEON, AltiVec) as hardware fingerprint. │
├─────────────┼───────────────────────────────────────────────┤
│ Check 4     │ Thermal Entropy Measurement                   │
│             │ Real hardware has predictable thermal curves  │
│             │ under load. Emulators fake this poorly.       │
├─────────────┼───────────────────────────────────────────────┤
│ Check 5     │ Instruction Jitter Analysis                   │
│             │ Timing variations in instruction execution    │
│             │ reveal genuine CPU microarchitecture.         │
├─────────────┼───────────────────────────────────────────────┤
│ Check 6     │ Anti-Emulation Detection                     │
│             │ CPUID, MSRs, and hardware registers checked   │
│             │ for emulator signatures.                     │
├─────────────┼───────────────────────────────────────────────┤
│ AI Step     │ ML Model Validation (PSE)                    │
│             │ AI model evaluates all 6 checks and assigns   │
│             │ an antiquity score. Human review for edge     │
│             │ cases.                                       │
└─────────────┴───────────────────────────────────────────────┘
```

---

## Antiquity Multipliers

The core economic innovation: **older hardware = higher rewards**.

| Hardware Age / Era | Multiplier Range | Examples |
|--------------------|-----------------|----------|
| Modern (0-3 years) | 0.8x | Current-gen x86-64, M4 Mac |
| Recent (3-7 years) | 1.0x - 1.2x | Older x86, Apple Silicon M1-M3 |
| Vintage (7-15 years) | 1.3x - 1.8x | PowerPC G4/G5, early x86 |
| Ancient (15-25 years) | 1.8x - 2.2x | Power Mac G5, SPARC, early MIPS |
| Mythic (25+ years) | 2.5x - 3.5x+ | VAX-11/780, 486,68000 |

### Current Network Multipliers (Live Data)

```
miner                         | arch       | multiplier
------------------------------|------------|-----------
nox-ventures                 | x86-64     | 0.8x
power8-s824-sophia           | POWER8     | 2.0x   ← Vintage
m2-mac-mini-sophia           | AppleSilicon M4 | 1.2x
fraktaldefidao               | x86-64     | 0.8x
ForestLee                    | x86-64     | 0.8x
claw-jojo-51658              | aarch64    | 0.0005x ← Very low (ARM emulator?)
claw-qinlingrongdeMacBook-Pro| AppleSilicon M2 | 1.2x
tianlin-rtc                  | aarch64    | 0.0005x ← Very low (ARM emulator?)
```

> Note: Multipliers < 1.0x indicate the node's fingerprint checks failed or the hardware is emulated/modern with no antiquity.

---

## Epoch Flow

```
┌──────────┐     ┌───────────┐     ┌──────────┐     ┌───────────┐
│  MINER   │────▶│ ANTICITY  │────▶│  EPOCH   │────▶│ REWARD    │
│ Submits  │     │  CHECK    │     │ CLOSES   │     │ DISTRIB.  │
│ Attest.  │     │  (6+1)    │     │ (~1hr)   │     │ (RTC)     │
└──────────┘     └───────────┘     └──────────┘     └───────────┘
     │                 │                 │
     │  Hardware FP    │  Score + Multi  │  Proportional
     │  + Entropy      │  Submitted      │  to work done
     └─────────────────┴────────────────┘
```

1. **Miner submits attestation** — raw hardware data to the attestation node
2. **Antiquity check runs** — 6 hardware fingerprint checks + AI (PSE) validation
3. **Antiquity score calculated** — combines all checks into a 0.0-1.0 score
4. **Multiplier assigned** — score × era table = final mining multiplier
5. **Epoch closes** — node aggregates all attested miners
6. **Rewards distributed** — RTC distributed proportional to (work × multiplier)

---

## Token Economics

| Parameter | Value |
|-----------|-------|
| Token | RTC (RustChain Token) |
| Max Supply | Dynamic (inflation controlled by epoch rewards) |
| Distribution | Proportional to antiquity-weighted work |
| Bridge | Solana (wRTC) |

### Reward Formula

```
miner_reward = base_reward × antiquity_multiplier × entropy_score
```

- `base_reward` — fixed RTC per epoch per miner
- `antiquity_multiplier` — from hardware fingerprint (0.8x - 3.5x+)
- `entropy_score` — measure of contribution randomness (ensures anti-gaming)

---

## Network Architecture

```
                    ┌─────────────────────┐
                    │   Block Explorer     │
                    │  50.28.86.131/explorer│
                    └──────────┬────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐     ┌──────────┐     ┌──────────┐
        │ Attest.  │     │ Attest.  │     │ Attest.  │
        │ Node 1   │     │ Node 2   │     │ Node 3   │
        │(Primary) │     │          │     │          │
        └────┬─────┘     └──────────┘     └──────────┘
             │
    ┌────────┼────────────────────────────────────┐
    │        │         RustChain Network          │
    │   ┌────▼────┐                                │
    │   │ Ergo    │  (Anchor chain for settlement) │
    │   │Anchoring│                                │
    │   └────────┘                                │
    │                                              │
    ▼                                              ▼
  MINERS                                       MINERS
(13 active)                                  (worldwide)
```

### Node Health Check

```bash
curl -sk https://50.28.86.131/health
```

Response:
```json
{
  "ok": true,
  "backup_age_hours": 8.94,
  "db_rw": true,
  "tip_age_slots": 0,
  "uptime_s": 154336,
  "version": "2.2.1-rip200"
}
```

### Active Miners

```bash
curl -sk https://50.28.86.131/api/miners
```

Returns a paginated list of all active miners with their antiquity multipliers, hardware types, and attestation timestamps.

---

## Getting Started as a Miner

1. **Install the miner** — see [Install Miner guide]
2. **Run hardware checks** — the 6+1 fingerprint checks run automatically on startup
3. **Submit first attestation** — your hardware fingerprint is validated
4. **Receive antiquity score** — determines your multiplier
5. **Start earning RTC** — rewards arrive each epoch

---

## Glossary

See [Glossary](./GLOSSARY.md) for full term definitions.

| Term | Definition |
|------|------------|
| RIP-200 | RustChain's Proof-of-Antiquity consensus protocol |
| PSE | Physical Signature Engine — the AI model that validates hardware fingerprints |
| Entropy Score | A measure of work randomness that prevents gaming |
| Epoch | The settlement period (~1 hour) after which rewards are distributed |
| Attestation | The act of submitting your hardware fingerprint to the network |
| wRTC | Wrapped RTC — the Solana bridged version of the token |
