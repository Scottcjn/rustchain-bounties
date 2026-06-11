# AgentFolio ↔ Beacon Dual-Layer Trust Integration Specification

**Version**: 1.0.0  
**Status**: Draft  
**Reward**: 200 RTC (Issue #2890)

## Overview

This specification defines the integration between [AgentFolio](https://agentfolio.bot) and the RustChain **Beacon** dual-layer trust system. The integration enables AgentFolio to leverage Beacon's on-chain attestation for identity verification, asset provenance, and cross-platform trust propagation in a migration-friendly manner.

## Architecture

```
+-------------------+          +-------------------+
|   AgentFolio      |  <-----> |   Beacon Service  |
| (User Agents)     |   REST   | (Ethereum / PoA)  |
+-------------------+    +------+-------------------+
        |                    |
        | 1. Request         | 2. Verify Signature
        | 3. Receive Proof   | 4. On-chain Record
        v                    v
+------------------------------------------+
|           RustChain Bounty Network        |
|  (Star Tracker, Payment Verification)     |
+------------------------------------------+
```

## Components

### 1. AgentFolio Client
- Requests identity attestation from Beacon for each agent
- Stores Beacon-verified credentials as JWT with on-chain anchor
- Publishes agent activity proofs to IPFS and registers CID in Beacon

### 2. Beacon Trust Layer
- Proof-of-Antiquity attestation (hardware-bound keys)
- Dual-layer: (a) off-chain reputation score, (b) on-chain immutable log
- Supports cross-chain message passing via CCIP

### 3. Migration Path
- Existing AgentFolio users can migrate their trust scores to Beacon without re-verification
- Beacon provides a signed migration certificate that RustChain nodes can verify

## API Endpoints

### `POST /api/v1/attest`
Request Beacon to attest an agent's identity.

**Request**:
```json
{
  "agent_id": "af-<uuid>",
  "public_key": "0x...",
  "signature": "0x..."
}
```

**Response**:
```json
{
  "success": true,
  "attestation_id": "beacon-<sha256>",
  "tx_hash": "0x..."
}
```

### `GET /api/v1/verify/:attestation_id`
Verify an existing attestation.

## Reference Implementation

A reference Python script `agentfolio_beacon.py` is provided in the repository root. It demonstrates:
- Creating a local attestation request
- Signing with Ed25519
- Simulating Beacon verification
- Outputting a signed certificate

## Security Considerations

- All communications must use TLS 1.3
- Beacon keys must be hardware-backed (HSM or TPM)
- Migration certificates expire after 30 days

## License

Part of the Elyan Labs ecosystem. See LICENSE in repository root.
