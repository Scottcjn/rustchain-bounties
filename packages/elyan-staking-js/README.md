<!-- SPDX-License-Identifier: MIT -->
# @elyan/staking

Typed JS/TS client for the Elyan staking gate. Implements the open contract:
`stake()` / `submit()` / `poll()` / `verify()`. Verifies the gate's Ed25519
signed verdict and the on-chain attestation. Fail-safe: any verification
failure throws — the caller never sees an untrusted payload.

Closes #14381.

## Install

```bash
npm install @elyan/staking
```

Node 18+ required (uses global `fetch` and `node:crypto` Ed25519). No third-party
runtime dependencies.

## Quick start

```ts
import { StakingClient } from "@elyan/staking";

const client = new StakingClient({
  gateUrl: "https://gate.elyan.example",
  apiKey: process.env.ELYAN_API_KEY!,
  // Gate's Ed25519 public key, 32 bytes hex.
  gatePublicKey: process.env.ELYAN_GATE_PUBKEY!,
});

const result = await client.stake({
  agentId: "agent-42",
  amount: "10",
  purpose: "self-improvement-cycle",
});

console.log("verified payload:", result.payload);
console.log("attestation tx:", result.attestationTxHash);
```

`stake()` is `submit()` → poll-until-ready → `verify()`. Call the individual
methods if you need finer control.

## Canonical JSON

Requests and verdict payloads are serialized with sorted keys and no extra
whitespace (matching Python's `json.dumps(sort_keys=True, separators=(",",":"))`)
so signatures match byte-for-byte with the Python reference SDK.

## Errors

| Error | When |
|---|---|
| `UnauthorizedError` | gate returned 401/403 (bad API key) |
| `SignatureError` | Ed25519 signature does not verify against `gatePublicKey` |
| `AttestationError` | on-chain attestation check failed |
| `GateUnavailableError` | network error, 5xx, or poll timeout |
| `StakingError` | base class for all of the above |

## Custom attestation verification

Replace the default verifier (which only requires a non-empty `txHash`) with
chain-aware logic — e.g. fetch the transaction from an RPC endpoint and confirm
it commits the verdict hash.

```ts
const client = new StakingClient({
  gateUrl, apiKey, gatePublicKey,
  attestationVerifier: {
    async verify(verdict) {
      // ...look up verdict.attestation.txHash on chain and compare digest...
      return true;
    },
  },
});
```

## Tests

```bash
npm test
```

Covers: happy path, bad API key, forged/mismatched pubkey, tampered payload,
gate-down, gate-5xx, failed attestation.
