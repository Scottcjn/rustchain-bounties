# @elyan/staking

Typed JavaScript client for the open Elyan staking gate contract, built for bounty #14381.

The client mirrors the reference staking surface:

- `stake(input)`
- `submit(request)`
- `poll(attestationUrl)`
- `verify(response, request)`

It uses canonical JSON with sorted keys, sends the canonical request to a gate endpoint with a Bearer API key, verifies the Ed25519 signed verdict against the configured gate public key, and verifies the returned on-chain attestation hashes.

## Install Locally

```bash
cd submissions/14381-elyan-staking-sdk
node --test test/staking.test.mjs
```

This package is dependency-free and runs on Node 18+. If npm is available, `npm test` runs the same command.

## Example

```js
import { ElyanStakingClient } from "@elyan/staking";

const client = new ElyanStakingClient({
  gateUrl: "https://gate.example.com",
  apiKey: process.env.ELYAN_GATE_API_KEY,
  gatePublicKeyPem: process.env.ELYAN_GATE_PUBLIC_KEY_PEM,
});

const result = await client.stake({
  skill: "self-improve:lint",
  bondRtc: 3,
  agent: "my-agent",
  metadata: { repo: "owner/repo", run: "ci-123" },
});

console.log(result.verified);
```

## Verification Model

`submit()` sends this canonical request body:

```json
{
  "agent": "my-agent",
  "bond_rtc": 3,
  "created_at": "2026-06-26T00:00:00.000Z",
  "metadata": {},
  "nonce": "uuid",
  "skill": "self-improve:lint",
  "version": 1
}
```

The gate response must contain:

```json
{
  "verdict": {
    "verdict": { "passed": true, "request_hash": "..." },
    "public_key_pem": "-----BEGIN PUBLIC KEY-----...",
    "signature_algorithm": "Ed25519",
    "signature": "base64..."
  },
  "attestation": {
    "status": "confirmed",
    "tx_id": "rtc-tx",
    "request_hash": "...",
    "verdict_hash": "..."
  }
}
```

The SDK fails closed if:

- the gate rejects the Bearer API key
- the gate is unavailable
- the verdict signature is forged
- the verdict public key does not match the configured gate public key
- the attestation request or verdict hash does not match the verified payload

## Tests

```bash
node --test test/staking.test.mjs
```

Covered cases:

- happy path
- bad API key
- forged or mismatched gate public key
- gate-down fail-safe
- attestation hash mismatch
- canonical JSON byte ordering

Wallet ID for claim: `lxx197818`
