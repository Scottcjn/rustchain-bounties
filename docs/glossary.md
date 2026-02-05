# RustChain Glossary

A comprehensive glossary of terms used in the RustChain ecosystem.

---

## A

### Antiquity Multiplier
A bonus factor applied to mining rewards based on the age and type of hardware. Older hardware (like PowerPC G4) receives higher multipliers (up to 2.5x) compared to modern hardware (0.8x).

### Attestation
The process by which a miner proves their hardware is real and active. Attestations are submitted periodically and include a hardware fingerprint that is validated by the network.

### API (Application Programming Interface)
The HTTP endpoints exposed by RustChain nodes that allow external applications to interact with the network.

---

## B

### Balance
The amount of RTC tokens held in a wallet. Balances are stored as 64-bit integers representing micro-RTC (1 RTC = 1,000,000 micro-RTC).

### Block
A unit of data in the blockchain containing attestations and transactions. Blocks are produced approximately every 10 minutes.

### Block Time
The target interval between blocks. RustChain targets 600 seconds (10 minutes) per block.

### Bounty
A reward offered for completing a specific task or contribution to the RustChain ecosystem. Bounties are paid in RTC.

---

## C

### Chain ID
A unique identifier for a blockchain network. RustChain's mainnet uses `rustchain-mainnet-v2`.

### Consensus
The mechanism by which network participants agree on the state of the ledger. RustChain uses Proof-of-Attestation (RIP-200).

### CPU Fingerprint
A component of hardware fingerprinting that identifies the processor model, features, and characteristics.

---

## D

### Device Architecture
The CPU instruction set architecture (e.g., x86_64, ARM, PowerPC). Different architectures receive different antiquity multipliers.

### Device Family
A grouping of hardware types (e.g., PowerPC, Apple Silicon, x86_64).

---

## E

### Emulation Detection
Security mechanisms that identify software emulation of hardware, preventing fake mining.

### Entropy Score
A measure of randomness in hardware characteristics, used to detect spoofed fingerprints.

### Epoch
A period of 144 blocks (~24 hours) during which attestations are collected and rewards are calculated.

### Epoch Pot
The total RTC reward distributed to miners at the end of an epoch. Currently set at 1.5 RTC per epoch.

---

## F

### Feeless
RustChain transactions do not require gas or transaction fees. Transfers are completely free.

### Fingerprint
A unique identifier generated from hardware characteristics used to verify the authenticity of mining hardware.

### Fork
A divergence in the blockchain where two competing chains exist. RustChain uses the longest chain rule to resolve forks.

---

## G

### Genesis
The first block of the blockchain, containing the initial state and distribution.

### G3, G4, G5
Generations of PowerPC processors from Apple. G4 (2.5x multiplier) and G5 (2.0x multiplier) receive bonus rewards in RustChain.

---

## H

### Hardware Fingerprinting
The process of collecting unique identifiers from a computer's hardware to verify its authenticity.

### Health Check
An API endpoint (`/health`) that returns the operational status of a RustChain node.

### Hash
A cryptographic function that produces a fixed-size output from variable input. Used for verification and identification.

---

## I

### i64 (Integer 64)
A 64-bit signed integer. RTC balances are stored as i64 values representing micro-RTC.

---

## L

### Ledger
The complete record of all transactions and balances on the RustChain network.

### Longest Chain Rule
The consensus rule that the valid chain with the most blocks is considered the canonical chain.

---

## M

### Mainnet
The primary production network for RustChain (`rustchain-mainnet-v2`).

### Micro-RTC
The smallest unit of RTC. 1 RTC = 1,000,000 micro-RTC.

### Miner
A participant who runs hardware to submit attestations and earn RTC rewards.

### Miner ID
See [Wallet ID](#wallet-id).

### Multiplier
See [Antiquity Multiplier](#antiquity-multiplier).

---

## N

### Node
A computer running the RustChain software that validates transactions and maintains the ledger.

### Nonce
A number used once to prevent replay attacks. Each transaction includes a nonce that must be unique for the sending wallet.

---

## P

### Proof-of-Attestation (PoA)
RustChain's consensus mechanism (RIP-200) where miners prove they control real hardware rather than solving computational puzzles.

### Proof-of-Stake (PoS)
A consensus mechanism (not used by RustChain) where validators stake tokens to participate.

### Proof-of-Work (PoW)
A consensus mechanism (not used by RustChain) where miners solve computational puzzles.

### PowerPC
A CPU architecture developed by IBM, Motorola, and Apple. PowerPC hardware receives bonus multipliers in RustChain.

### Public Key
The public half of a cryptographic key pair, used to verify signatures and identify wallets.

---

## R

### Replay Attack
An attack where a valid transaction is re-submitted. RustChain prevents this with nonce-based replay protection (RIP-0143).

### Replay Protection
Security mechanism that prevents transaction replay using unique nonces.

### RIP (RustChain Improvement Proposal)
A formal proposal for changes to the RustChain protocol. Examples include:
- **RIP-0005**: Hardware fingerprinting
- **RIP-0008**: Antiquity multipliers
- **RIP-0009**: Epoch-based rewards
- **RIP-0142**: Signed transfers
- **RIP-0143**: Replay protection
- **RIP-0144**: Admin key validation
- **RIP-200**: Proof-of-Attestation consensus

### RTC (RustChain Token)
The native cryptocurrency of the RustChain network.

---

## S

### Signature
A cryptographic proof that a message was created by the holder of a private key. RustChain uses Ed25519 signatures.

### Signed Transfer
A transfer transaction that includes a cryptographic signature proving the sender authorized it (RIP-0142).

### Slot
A subdivision of an epoch. Each epoch contains multiple slots.

### Supply
The total amount of RTC in existence. Current circulating supply is approximately 200,000 RTC.

### Sybil Attack
An attack where an adversary creates multiple fake identities. RustChain's hardware fingerprinting prevents this.

---

## T

### Testnet
A test network for development and experimentation (separate from mainnet).

### Timestamp
A record of when an event occurred, used in attestations and transactions.

### Transaction
A transfer of RTC from one wallet to another.

### Transfer
See [Transaction](#transaction).

---

## U

### Uptime
The duration a node has been running continuously, reported in seconds by the health endpoint.

### UUID
Universally Unique Identifier. Part of the hardware fingerprint used to verify real hardware.

---

## V

### Validator
A node that validates transactions and attestations. In RustChain, all nodes are validators.

### Vintage Hardware
Older computer hardware (pre-2010) that receives bonus multipliers for mining.

### VM (Virtual Machine)
Software that emulates computer hardware. VMs are detected and rejected by RustChain's attestation system.

### VM Detection
Security mechanisms that identify when mining software runs inside a virtual machine.

---

## W

### Wallet
A digital container for holding RTC tokens, identified by a unique wallet ID.

### Wallet ID
A unique identifier for a wallet. Can be any string on testnet, but production wallets should use secure identifiers.

### Withdrawal
The process of moving RTC from the network (planned feature for cross-chain bridges).

---

## X

### x86_64
A 64-bit processor architecture commonly used in modern computers. Modern x86_64 receives a 0.8x multiplier.

---

## Numbers

### 1 CPU = 1 Vote
The core principle of RustChain that each real CPU has equal voting power, regardless of computational speed.

### 144 Blocks per Epoch
The number of blocks in each epoch (~24 hours at 10-minute blocks).

### 600 Seconds
Target block time (10 minutes).

### 1.5 RTC per Epoch
The reward pool distributed to active miners each epoch.

---

## Symbols

### RTC
Symbol for RustChain Token.

### µRTC (Micro-RTC)
One millionth of an RTC (1 RTC = 1,000,000 µRTC).

---

*This glossary is updated as new terms are introduced to the RustChain ecosystem.*
