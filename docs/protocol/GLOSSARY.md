# Glossary of Terms

This glossary defines key technical terms used within the RustChain ecosystem and the RIP-200 protocol.

| Term | Definition |
| :--- | :--- |
| **Antiquity** | The historical value assigned to a piece of computing hardware based on its age, architecture rarity, and preservation difficulty. |
| **Antiquity Multiplier** | A numeric coefficient (e.g., 2.5x) applied to a miner's attestation weight to determine their share of epoch rewards. |
| **Attestation** | The process by which a physical device proves its hardware characteristics and integrity to a RustChain node. |
| **Commitment** | A cryptographic hash (`sha256(nonce + wallet + entropy)`) that ensures the reported timing entropy was collected during the current challenge window. |
| **Epoch** | A fixed period of time (approximately 10 minutes or 1 block) during which miner attestations are collected and rewards are settled. |
| **Ergo Anchoring** | The process of recording a cryptographic summary (root hash) of the RustChain state onto the Ergo blockchain for long-term immutability. |
| **Fingerprint** | A collection of unique hardware identifiers (MACs, Serial Numbers, CPU flags) used to identify a specific physical machine. |
| **Nonce** | A unique, single-use number provided by the node to ensure the freshness of an attestation and prevent replay attacks. |
| **PoA (Proof-of-Antiquity)** | The consensus mechanism that prioritizes older, rarer hardware over raw modern hashing power. |
| **PSE (Physical Signature Entropy)** | The measurement of hardware-specific timing variations used as a secondary signal of physical silicon presence. |
| **RIP-200** | RustChain Improvement Proposal #200, the foundational standard for the modern Proof-of-Antiquity protocol and hardware fingerprinting. |
| **RTC** | RustChain Token, the native utility token of the network. |
| **Slot** | The smallest unit of time in the RustChain ledger, currently synchronized with epoch progress. |
| **Vintage Bonus** | The additional multiplier granted to hardware older than 5 years, which decays slowly over time to reward early network participants. |

---
*Back to [Overview](./OVERVIEW.md).*
