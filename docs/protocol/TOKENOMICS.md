# Token Economics & Antiquity Multipliers

## RTC Token Distribution
The native token of RustChain is **RTC (RustChain Token)**. It is distributed via Proof-of-Attestation (PoA) rewards at the end of every **Epoch** (approximately every 10 minutes, or 144 blocks per day).

## Reward Calculation Model
Rewards are calculated proportionally based on a miner's **Attestation Weight** relative to the total weight of all enrolled miners in that epoch.

$$Reward_{miner} = \frac{Weight_{miner}}{\sum Weight_{all}} \times TotalEpochPot$$

### The Multiplier Formula
A miner's weight is determined by their hardware's **Antiquity Multiplier**, which consists of a Base Multiplier, Time Decay, and optional bonuses.

#### 1. Base Multiplier (Preservation Tiers)
Rewards are based on **rarity + preservation value**, not just raw age.

| Tier | Base Multiplier | Examples |
| :--- | :--- | :--- |
| **Legendary** | 3.0x | Intel 386, Motorola 68000, MIPS R2000 |
| **Epic** | 2.5x | PowerPC G4, 486, Pentium I |
| **Rare** | 2.0x | PowerPC G5, DEC Alpha, SPARC, POWER8 |
| **Common** | 0.8x - 1.0x | Modern x86_64 (Skylake+, Zen 3+) |
| **Cheap** | 0.0005x | ARM (Raspberry Pi, cheap SBCs) |
| **Flagged** | 0x | VMs, Emulators (failed fingerprints) |

#### 2. Time Decay (For Vintage Hardware)
To reward early adoption of specific vintage architectures, the "vintage bonus" (anything above 1.0x) decays at **15% per year** starting from the chain genesis (2025).

**Formula:**
`decay_factor = 1.0 - (0.15 * years_since_genesis)`
`final_multiplier = 1.0 + (vintage_bonus * decay_factor)`

#### 3. Loyalty Bonus (For Modern Hardware)
Modern hardware (≤ 5 years old) that might have a lower base multiplier can earn a loyalty bonus of **15% per year of uptime**, capped at a maximum of **+50%** (1.5x total).

#### 4. Server hardware Bonus
Enterprise-class CPUs (Intel Xeon, AMD EPYC/Opteron) receive a flat **+10% bonus** on top of their final calculated multiplier.

## Rationale
- **ARM Penalty**: Raspberry Pis and cheap ARM chips are penalized (0.0005x) to prevent "mining farms" that would centralize the network.
- **VM/Emulator Exclusion**: VMs receive 0x rewards because they do not contribute to the preservation of physical computing history.
- **Fairness**: By prioritizing unique hardware serials and antiquity, the network remains accessible to enthusiasts rather than just those with massive capital.

---
*Next: See [API Specification](./API_SPEC.md).*
