# RustChain Glossary of Terms

A comprehensive glossary of RustChain terminology, concepts, and technical definitions.

---

## A

### Antiquity Multiplier
A reward modifier (ranging from 1.0x to 2.5x) applied to mining rewards based on CPU age. Older hardware receives higher multipliers to incentivize preservation of vintage computing. The multiplier is subject to time decay for hardware older than 5 years.

### Attestation
The process of proving hardware authenticity to the RustChain network. Miners submit 6 hardware fingerprints that are validated against known profiles to prove they are running on physical, non-emulated hardware.

### Attestation Node
A trusted server that validates hardware fingerprints and enrolls miners into epochs. The primary node operates at `50.28.86.131`. This node is responsible for verifying attestation submissions and managing epoch enrollment.

### Epoch Pot
The RTC reward pool allocated for each epoch. Currently set at 1.5 RTC per epoch, distributed proportionally among enrolled miners based on their antiquity multipliers.

### Ergo Anchor
External blockchain (Ergo) where RustChain writes epoch settlement hashes for immutability and tamper-proof timestamps. Each epoch's settlement hash is stored in Ergo box registers R4-R9, providing cryptographic proof of RustChain state at a specific point in time.

### Ed25519
A modern elliptic curve signature scheme used by RustChain for all transaction signatures. Provides high security with compact key sizes. Miner IDs are derived from Ed25519 public keys.

---

## B

### Behavioral Heuristics
One of the 6 hardware fingerprint checks. Detects hypervisor signatures (VMware, QEMU, VirtualBox, etc.) via CPUID leaf inspection and MAC OUI pattern analysis. VMs typically expose hypervisor-specific CPUID flags that physical hardware does not.

### Base Reward
The standard mining reward before applying any multipliers. For RustChain, the base reward is calculated from the epoch pot divided by total network weight.

### Bridge
A mechanism to transfer RTC tokens between RustChain native chain and other blockchains. The BoTTube Bridge enables RTC ↔ wRTC conversion between RustChain and Solana/Base networks.

---

## C

### Cache Timing
One of the 6 hardware fingerprint checks. Profiles L1/L2/L3 cache latency curves to detect emulation. Emulators typically flatten cache hierarchy latency, making them detectable. Real hardware exhibits specific latency patterns based on cache architecture.

### Clock Skew
One of the 6 hardware fingerprint checks. Measures microscopic crystal oscillator imperfections unique to physical hardware. Every physical CPU has unique clock drift patterns (measured in ppm - parts per million) due to manufacturing variances and aging. VMs use the host clock, which appears "too perfect."

### Consensus
The mechanism by which RustChain nodes agree on the state of the blockchain. RustChain uses Proof-of-Antiquity (PoA) consensus via RIP-200 protocol, where each unique hardware device gets exactly 1 vote per epoch.

### CPUID
A processor instruction used to retrieve CPU identification and feature information. RustChain uses CPUID leaf inspection as part of behavioral heuristics to detect virtualization.

---

## D

### Decay Factor
The reduction applied to antiquity multipliers for hardware older than 5 years. Set at 15% per year beyond the 5-year threshold to prevent permanent advantage and reward early adoption.

**Formula:** `decay_factor = 1.0 - (0.15 × (age - 5) / 5)`

### DOS Mining
Mining RustChain on vintage DOS-compatible hardware (8086/286/386/486 systems). Currently experimental and eligible for commemorative badge rewards.

---

## E

### Epoch
A time period during which miners accumulate rewards. One epoch consists of 144 slots (~24 hours). At epoch end, the Epoch Pot is distributed among all enrolled miners.

### Epoch Lifecycle
The complete cycle of an epoch:
1. Epoch Start
2. Miners Submit Attestations
3. Fingerprints Validated
4. Miners Enrolled
5. Slot Counter (1-144)
6. Settlement at Slot 144
7. Distribute Epoch Pot
8. Anchor to Ergo
9. New Epoch Begins

### Ergo Blockchain
A UTXO-based smart contract platform that RustChain uses for anchoring epoch settlements. Provides immutable timestamping and external existence proof for RustChain state.

---

## F

### Fingerprint (Hardware)
A collection of 6 hardware measurements submitted during attestation:
1. **Clock Skew & Drift** - Crystal oscillator imperfections
2. **Cache Timing** - L1/L2/L3 latency curves
3. **SIMD Identity** - AltiVec/SSE/NEON pipeline biases
4. **Thermal Entropy** - CPU temperature changes under load
5. **Instruction Jitter** - Opcode execution time variance
6. **Behavioral Heuristics** - Hypervisor signature detection

### Flamekeeper
A community member who actively mines or contributes to RustChain. Named after the concept of keeping the "flame" of vintage computing alive.

### Fleet Detection
A security mechanism that identifies multiple wallets operating from the same physical hardware. Each hardware fingerprint is bound to one wallet to prevent Sybil attacks.

---

## G

### G3 (PowerPC G3)
IBM/Motorola PowerPC processor (1997-2003). Receives 1.8x antiquity multiplier. Known for efficient performance and used in early iMac and PowerBook systems.

### G4 (PowerPC G4)
IBM/Motorola PowerPC processor (1999-2005). Receives the highest 2.5x antiquity multiplier. Features AltiVec (Velocity Engine) SIMD unit. Highly sought after for RustChain mining.

### G5 (PowerPC G5)
IBM PowerPC processor (2003-2006). Receives 2.0x antiquity multiplier. Used in Power Mac G5 systems. Features advanced thermal management and 64-bit architecture.

### Governance
RustChain's on-chain voting system for protocol changes. Requirements:
- Proposal creation: wallet must hold >10 RTC
- Voting eligibility: must be an active miner
- Vote weight: 1 RTC = 1 base vote × antiquity multiplier
- Pass condition: yes_weight > no_weight
- Proposal lifecycle: Draft → Active (7 days) → Passed/Failed

---

## H

### Hardware Fingerprinting
The core security mechanism of RustChain. Six independent checks that uniquely identify physical hardware and detect emulation attempts.

### Hardware Heuristics
See **Behavioral Heuristics**.

---

## I

### Instruction Jitter
One of the 6 hardware fingerprint checks. Measures nanosecond-scale execution time variance of specific opcodes. Real silicon exhibits random jitter due to thermal noise and manufacturing variances. VMs are "too clean" with deterministic execution times.

### Instruction Set
The set of basic commands a CPU can execute. RustChain tracks SIMD instruction sets (AltiVec, SSE, NEON) as part of hardware identity.

---

## L

### Loyalty Bonus
A bonus multiplier for modern CPUs (≤5 years old) that maintain continuous uptime. Earns +15% multiplier per year of uptime, capped at +50%.

**Formula:** `loyalty_bonus = min(0.5, uptime_years × 0.15)`

### Ledger Integrity
A security audit category for RustChain bounties. Ensures the accuracy and immutability of reward distribution records.

---

## M

### Miner
A participant running the RustChain client on qualifying hardware. Miners submit attestations to earn RTC tokens.

### Miner ID
Unique identifier/wallet address for a miner. Derived from Ed25519 public key. Example format: `abc123RTC`

### Mining
The process of running RustChain client software to earn RTC rewards. Unlike traditional PoW mining, RustChain mining does not require intensive computation—instead, it proves hardware authenticity and age.

### Multiplier (Antiquity)
See **Antiquity Multiplier**.

---

## N

### Node
A server participating in the RustChain network. Types include:
- **Attestation Node**: Validates hardware fingerprints
- **Ergo Anchor Node**: Writes settlements to Ergo blockchain
- **Explorer Node**: Provides block explorer interface

### NUMA (Non-Uniform Memory Access)
A computer memory design used in multi-processor systems. Relevant for POWER8 systems running RustChain, where memory access times vary based on memory location relative to the processor.

---

## P

### PoA (Proof-of-Antiquity)
RustChain's consensus mechanism. Rewards older hardware with higher multipliers. **Not to be confused with Proof-of-Authority.** Core principle: 1 CPU = 1 Vote, weighted by hardware antiquity.

### PowerPC
IBM/Motorola CPU architecture (1991-2006). Used in Apple Macintosh computers and IBM servers. G4 and G5 processors receive the highest RustChain multipliers (2.5x and 2.0x respectively).

### POWER8
IBM server processor architecture (2014). Supported by RustChain with 1.5x multiplier. Features 128 threads and large memory capacity (up to 768GB RAM).

### Premine
The initial allocation of RTC tokens before public mining began. RustChain premined 75,000 RTC for development and bounties out of 8,000,000 total supply.

### Proposal
A formal suggestion for protocol changes submitted through RustChain governance. Requires >10 RTC in wallet to create.

---

## R

### RIP-200 (RustChain Iterative Protocol)
The consensus mechanism defining how attestations are validated and rewards distributed. Current version: RIP-200 v2.2.1.

### RTC (RustChain Token)
Native cryptocurrency of RustChain. Key metrics:
- **Total Supply:** 8,000,000 RTC
- **Reference Rate:** 1 RTC = $0.10 USD
- **Epoch Pot:** 1.5 RTC
- **Token Mint (Solana):** `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`

### Rust
In RustChain context, refers to literal iron oxide on vintage hardware—not the Rust programming language. The name celebrates that corroding vintage hardware still has computational value and dignity.

---

## S

### Settlement
End-of-epoch process where the Epoch Pot is distributed among enrolled miners based on their antiquity multipliers. The settlement hash is then anchored to the Ergo blockchain.

### SIMD (Single Instruction, Multiple Data)
Processor instructions that perform the same operation on multiple data points simultaneously. RustChain checks for SIMD identity (AltiVec/SSE/NEON) as part of hardware fingerprinting.

### Slot
A time unit within an epoch. 144 slots = 1 epoch (~24 hours). Each slot represents approximately 10 minutes.

### Sybil Attack
An attack where a single adversary controls multiple network identities. RustChain prevents this through hardware-bound identity—each physical device can only enroll one wallet.

---

## T

### Thermal Entropy
One of the 6 hardware fingerprint checks. Measures CPU temperature changes under load. Real hardware exhibits thermal variance; VMs report static temperatures or pass through host temperatures without load correlation.

### Time Decay
The reduction of antiquity bonus for vintage hardware older than 5 years. Set at 15% per year beyond the 5-year threshold.

**Example:** A 24-year-old G4 (base 2.5x):
- Vintage bonus: 1.5 (2.5 - 1.0)
- Decay: 1.0 - (0.15 × 19/5) = 0.43
- Final multiplier: 1.0 + (1.5 × 0.43) = **1.645x**

### Tokenomics
The economic model of RTC token:
- **Supply:** 8,000,000 RTC (capped)
- **Distribution:** 1.5 RTC per epoch via mining
- **Premine:** 75,000 RTC (development/bounties)
- **Reference Value:** $0.10 USD

---

## V

### Vintage Hardware
CPUs older than 5 years that qualify for antiquity bonuses. Examples:
- PowerPC G3/G4/G5
- Pentium III/4
- Core 2 Duo
- IBM POWER8

### Validator
A node that validates blocks and attestations. In RustChain, the primary attestation node serves as the validator.

### VM Detection
The process of identifying virtual machines and emulators. RustChain uses 6 independent checks to detect VMs, which receive 1 billionth of normal rewards if detected.

### Vote Weight
In RustChain governance, vote weight equals RTC held × antiquity multiplier. This gives vintage hardware miners proportionally more governance power.

### wRTC (Wrapped RTC)
RTC token wrapped for use on other blockchains:
- **Solana:** `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`
- **Base:** `0x5683C10596AaA09AD7F4eF13CAB94b9b74A669c6`

---

## X

### x402 Protocol
HTTP 402 Payment Required protocol implementation for AI agent machine-to-machine payments. RustChain agents can use x402 for automated micropayments.

---

## Reference Tables

### Antiquity Multipliers by Hardware

| Hardware | Era | Base Multiplier | Example Earnings/Epoch |
|----------|-----|-----------------|------------------------|
| PowerPC G4 | 1999-2005 | 2.5× | 0.30 RTC |
| PowerPC G5 | 2003-2006 | 2.0× | 0.24 RTC |
| PowerPC G3 | 1997-2003 | 1.8× | 0.21 RTC |
| IBM POWER8 | 2014 | 1.5× | 0.18 RTC |
| Pentium 4 | 2000-2008 | 1.5× | 0.18 RTC |
| Core 2 Duo | 2006-2011 | 1.3× | 0.16 RTC |
| Apple Silicon | 2020+ | 1.2× | 0.14 RTC |
| Modern x86_64 | Current | 1.0× | 0.12 RTC |

### Hardware Fingerprint Checks

| # | Check | Detects |
|---|-------|---------|
| 1 | Clock Skew & Drift | VMs use host clock (too perfect) |
| 2 | Cache Timing | Emulators flatten cache hierarchy |
| 3 | SIMD Identity | Different timing in emulation |
| 4 | Thermal Entropy | VMs report static temperatures |
| 5 | Instruction Jitter | Real silicon has nanosecond jitter |
| 6 | Behavioral Heuristics | Detects VMware, QEMU, etc. |

### Bounty Tiers

| Tier | Reward (RTC) | Examples |
|------|--------------|----------|
| Micro | 1-10 | Typo fix, small docs, simple test |
| Standard | 20-50 | Feature, refactor, new endpoint |
| Major | 75-100 | Security fix, consensus improvement |
| Critical | 100-150 | Vulnerability patch, protocol upgrade |

---

## Related Resources

- [Protocol Specification](./PROTOCOL.md) - Full RIP-200 technical details
- [Tokenomics](./tokenomics_v1.md) - RTC supply and distribution
- [API Reference](./API.md) - All endpoints with examples
- [Hardware Fingerprinting](./hardware-fingerprinting.md) - Deep dive on 6 checks
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to RustChain

---

*Last updated: March 2026*
*Protocol version: RIP-200 v2.2.1*
