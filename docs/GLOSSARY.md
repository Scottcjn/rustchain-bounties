# RustChain Glossary

> Standard terms and definitions used in the RustChain ecosystem.
> Version: 2.2.1-rip200

---

## A

### Antiquity Multiplier
The reward multiplier assigned to a miner based on its hardware age. Older hardware = higher multipliers. Range: 0.8x (modern) to 3.5x+ (mythic/vintage).

### Antiquity Score
A 0.0-1.0 score produced by the PSE (Physical Signature Engine) that represents how authentically "vintage" the hardware is. Combined with era tables to produce the final antiquity_multiplier.

### Attestation
The process by which a miner submits its hardware fingerprint data to a RustChain attestation node for validation. Must be done before mining can begin.

### Attestation Node
A network node that receives and validates hardware attestation submissions. There are currently 3 active attestation nodes in the RustChain network.

---

## B

### Block Explorer
A web interface for browsing the RustChain blockchain. Available at `https://50.28.86.131/explorer`.

---

## D

### DePIN
Decentralized Physical Infrastructure Network. A category of crypto projects that coordinate physical infrastructure through token incentives. RustChain is a DePIN for vintage computing hardware. Other DePINs include Helium (networking), Filecoin (storage), and Render (GPU compute).

### Device Architecture
The specific CPU architecture of a miner's hardware (e.g., POWER8, x86-64, ARM64, Apple Silicon). Used in antiquity determination.

### Device Family
The broader CPU family classification (e.g., PowerPC, x86, ARM). Multiple architectures may belong to the same family.

---

## E

### Entropy Score
A float value (0.0-1.0) representing the randomness of a miner's work contribution. Higher entropy makes the reward distribution more unpredictable and resistant to gaming. See also: entropy_score in /api/miners.

### Epoch
The settlement period in RustChain (approximately 1 hour). At the end of each epoch, the attestation node aggregates all miner attestations and distributes RTC rewards proportional to (work × antiquity_multiplier × entropy_score).

### Ergo Anchoring
RustChain uses Ergo blockchain as an anchor chain for settlement. This provides additional security by committing RustChain state hashes to the Ergo chain periodically.

---

## G

### GitHub Bounties
The RustChain bounty program is hosted at `github.com/Scottcjn/rustchain-bounties`. Developers can earn RTC by resolving issues, writing documentation, or improving the protocol.

---

## M

### Miner
A participant in the RustChain network who contributes physical hardware to secure the network and earns RTC rewards. Miners must pass the 6+1 hardware fingerprint checks.

### Mining Multiplier
See **Antiquity Multiplier**.

---

## P

### PoA
Proof-of-Antiquity. See **RIP-200**.

### PSE
Physical Signature Engine. The AI/ML model that evaluates the 6 hardware fingerprint checks and produces an antiquity score. The final validation step in the attestation process.

### Proof-of-Antiquity
See **RIP-200**.

---

## R

### RIP-200
RustChain Improvement Proposal #200 — the formal name for RustChain's Proof-of-Antiquity consensus protocol. Defines:
- The 6 hardware fingerprint checks
- The PSE AI validation step
- The antiquity multiplier table
- Epoch settlement rules
- Reward distribution formula

### RTC
RustChain Token. The native cryptocurrency of the RustChain network. Used to pay for transaction fees and distributed as mining rewards. Can be bridged to Solana as wRTC.

---

## S

### Slot
A unit of time in the RustChain blockchain. Several slots make up an epoch. The `tip_age_slots` field in `/health` indicates chain synchronization status.

---

## T

### tip_age_slots
The number of slots between the current block and the chain tip. A value of 0 means the node is fully synchronized. Non-zero values indicate the node is behind.

---

## V

### Vintage Hardware
Computers and components manufactured 7-15 years ago. In RustChain, vintage hardware earns multipliers of 1.3x-1.8x. Examples: PowerPC G4/G5, early Intel Core series.

### VM Detection
One of the 6 hardware fingerprint checks. Detects whether the miner is running in a virtual machine (VM), which would disqualify them from earning full antiquity multipliers.

---

## W

### wRTC
Wrapped RTC. The Solana blockchain representation of RTC. Users can bridge RTC to Solana via the official bridge to use it in the broader DeFi ecosystem.

---

## Index

| Term | Section |
|------|---------|
| Antiquity Multiplier | A |
| Antiquity Score | A |
| Attestation | A |
| Attestation Node | A |
| Block Explorer | B |
| DePIN | D |
| Device Architecture | D |
| Device Family | D |
| Entropy Score | E |
| Epoch | E |
| Ergo Anchoring | E |
| GitHub Bounties | G |
| Miner | M |
| Mining Multiplier | M |
| PoA | P |
| PSE | P |
| Proof-of-Antiquity | P |
| RIP-200 | R |
| RTC | R |
| Slot | S |
| tip_age_slots | T |
| Vintage Hardware | V |
| VM Detection | V |
| wRTC | W |
