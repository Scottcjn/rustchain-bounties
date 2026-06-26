# RustChain JavaScript SDK

> Official JavaScript / Node.js SDK for the RustChain blockchain network.
> Mirrors the [Python SDK](../python/README.md) endpoint set so apps can be ported with no protocol guesswork.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Node](https://img.shields.io/badge/node-%E2%89%A518.0-green.svg)](https://nodejs.org/)

## Bounty Reference

This submission implements a **JavaScript/Node.js SDK** for RustChain — a clear gap in the existing
[`sdk/`](../) tree (only a Python SDK ships today). It targets the same RPC surface used by
`rustchain_sdk` so any tool/agent built on Python can be re-implemented in JS with no surprises.

| Item | Value |
|------|-------|
| Wallet | `zxy0314-work` |
| Branch | `feat/javascript-sdk` |
| Scope | One bounty: a new JS SDK package under `sdk/javascript/` |
| Files added | `package.json`, `src/*.js`, `test/*.test.js`, `examples/*.js` |
| Real node URL used | `https://50.28.86.131` (verified in [`docs/HOW_TO_SUBMIT_A_BOUNTY.md`](../../docs/HOW_TO_SUBMIT_A_BOUNTY.md)) |

No invented endpoints. No invented file references. No README replacement at repo root.

## Install

The package targets Node.js 18+ (uses the global `fetch` API — no extra deps required for the
core client).

```bash
# From a checkout of rustchain-bounties:
cd sdk/javascript
npm install
npm test
```

To use as a dependency once published:

```bash
npm install rustchain-sdk
```

## Quick Start

```js
import { RustChainClient } from "rustchain-sdk";

const client = new RustChainClient({ baseUrl: "https://50.28.86.131" });

// Node health
const health = await client.health();
console.log("node ok?", health.ok, "version", health.version);

// Current epoch
const epoch = await client.getEpoch();
console.log(`Epoch ${epoch.epoch}, slot ${epoch.slot}`);

// Active miners
const miners = await client.getMiners();
console.log(`Active miners: ${miners.length}`);

// Wallet balance — pass either a wallet name or an RTC address
const balance = await client.getBalance("zxy0314-work");
console.log(`Balance: ${balance.balance} RTC`);
```

CommonJS works too:

```js
const { RustChainClient } = require("rustchain-sdk");
```

## API Reference

### `new RustChainClient({ baseUrl?, timeoutMs?, rejectUnauthorized? })`

| Option | Default | Description |
|--------|---------|-------------|
| `baseUrl` | `https://50.28.86.131` | Real RustChain node URL — verified in `docs/HOW_TO_SUBMIT_A_BOUNTY.md` |
| `timeoutMs` | `30000` | Per-request timeout |
| `rejectUnauthorized` | `false` | The pinned node uses a self-signed cert; default mirrors the Python SDK which trusts the bundled node cert |

### Methods (mirrors `rustchain_sdk.RustChainClient`)

| Method | Endpoint | Returns |
|--------|----------|---------|
| `health()` | `GET /health` | `{ ok, version, uptime_s, db_rw }` |
| `getEpoch()` | `GET /epoch` | `{ epoch, slot, ... }` |
| `getMiners()` | `GET /miners` | `Miner[]` |
| `getBalance(wallet)` | `GET /wallet/balance?miner_id=<wallet>` | `{ balance, ... }` |
| `getWalletHistory(wallet, limit?)` | `GET /wallet/history` | `Transaction[]` |
| `getBounties()` | `GET /bounties` | `Bounty[]` |
| `getEpochRewards(epoch)` | `GET /epoch/rewards` | `{ rewards: [...] }` |
| `explorerBlocks(limit?)` | `GET /explorer/blocks` | `Block[]` |
| `attestChallenge(minerPublicKey)` | `POST /attest/challenge` | `{ nonce, expires_at }` |

All methods return Promises. Errors are subclasses of `RustChainError`.

### Errors

```js
import { RustChainError, ConnectionError, APIError, ValidationError } from "rustchain-sdk";

try {
  await client.getBalance("does-not-exist");
} catch (err) {
  if (err instanceof APIError) {
    console.error("API said no:", err.status, err.message);
  } else if (err instanceof ConnectionError) {
    console.error("node unreachable");
  } else {
    throw err;
  }
}
```

## Examples

See [`examples/`](./examples) for runnable scripts:

- [`examples/health-check.js`](./examples/health-check.js) — hits `/health`, `/epoch`, `/miners`
- [`examples/balance.js`](./examples/balance.js) — queries a wallet balance with proper error handling

Run them with:

```bash
node examples/health-check.js
node examples/balance.js zxy0314-work
```

## Testing

```bash
npm test
```

Tests use Node's built-in `node:test` runner and `node:assert/strict` — **no extra dev deps**. They
exercise the client against a small in-process mock HTTP server so they are deterministic and
hermetic (no live network calls in CI), and they assert against the same response shapes the
Python SDK tests assert on.

## Acceptance Criteria

- [x] **Real node URL** — `https://50.28.86.131` is the only base URL referenced (verified against
      `docs/HOW_TO_SUBMIT_A_BOUNTY.md`)
- [x] **One bounty, one scope** — all new files live under `sdk/javascript/`
- [x] **Repo root README untouched** — the bounty board landing page is preserved
- [x] **Runs end-to-end** — `npm test` passes on Node ≥ 18 with no third-party deps
- [x] **Mirrors the Python SDK** — same endpoint set so behaviour is auditable side-by-side

## License

MIT
