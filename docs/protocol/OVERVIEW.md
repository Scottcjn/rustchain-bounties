# RustChain Protocol Overview: RIP-200

## Introduction
RustChain is a decentralized blockchain network built on the **Proof-of-Antiquity (PoA)** consensus mechanism. Unlike Proof-of-Work (which rewards raw compute power) or Proof-of-Stake (which rewards capital), PoA rewards the **preservation and utilization of computing history**.

The network is governed by the **RIP-200 (RustChain Improvement Proposal #200)**, which defines the modernized attestation flow, hardware fingerprinting, and the antiquity-based reward distribution system.

## Core Philosophy: The Antiquity Premium
In RustChain, "antiquity" refers to the historical and preservation value of computing hardware. The protocol is designed to:
1. **Incentivize Hardware Preservation**: Higher rewards are given to vintage architectures (e.g., 68K Macs, PowerPC G4/G5, early x86) that are difficult to maintain.
2. **Prevent Hardware Centralization**: By penalizing cheap, mass-produced modern hardware (like ARM SBC clusters) and completely barring Virtual Machines, RustChain ensures a fair distribution based on unique physical devices.
3. **Proof of Physical Presence**: Using 6+1 hardware fingerprint checks to ensure that miners are running on real, documented hardware rather than emulators.

## Consensus Mechanism: Proof-of-Attestation (PoA)
RustChain does not require energy-intensive hashing. Instead, miners participate in "Attestation Cycles":

1. **Challenge**: The miner requests a unique nonce from the node.
2. **Fingerprint & Entropy**: The miner collects hardware identifiers (serial numbers, MACs, CPU flags) and measures CPU timing jitters (entropy).
3. **Submission**: The miner signs and submits an attestation report.
4. **Validation**: The node verifies the fingerprint against known architectural signatures and stores the record.
5. **Enrollment**: Once attested, the miner enrolls in the current **Epoch** to become eligible for block rewards.

## Network Architecture
- **Attestation Nodes**: Maintain the ledger, verify hardware signatures, and anchor the state to the **Ergo Blockchain** for immutable security.
- **Miners**: Physical hardware devices running the RustChain miner client.
- **Beacon Service**: An optional coordination layer for AI agents and distributed miners to sync status.

## Workflow Diagram
```mermaid
sequence_client-server
    participant Miner
    participant Node
    participant Ergo

    Miner->>Node: POST /attest/challenge
    Node-->>Miner: Returns unique Nonce
    Miner->>Miner: Collect Hardware Fingerprint & Entropy
    Miner->>Node: POST /attest/submit (Report + Commitment)
    Node->>Node: Verify 6+1 Fingerprint Checks
    Node-->>Miner: Success (Valid for ~10 mins)
    Miner->>Node: POST /epoch/enroll
    Node->>Node: Record for Block Reward Settlement
    Node->>Ergo: Anchor Epoch State (Periodically)
```

---
*Next: See [Attestation Details](./ATTESTATION.md) for technical validation logic.*
