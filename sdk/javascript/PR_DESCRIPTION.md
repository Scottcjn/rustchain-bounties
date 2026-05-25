# PR: Add `sdk/javascript/` — Official JavaScript / Node.js SDK

## What does this PR do?

Adds a new, focused JavaScript / Node.js SDK package under `sdk/javascript/`. It mirrors the
endpoint set of the existing `sdk/python/` SDK so apps and agents can be written in JS against
the real RustChain node without protocol guesswork.

**Files added (all under `sdk/javascript/`):**

- `README.md`               — install + quick start + API reference
- `LICENSE`                 — MIT
- `package.json`            — ESM-first, Node ≥ 18, zero runtime deps
- `.gitignore`
- `src/index.js`            — public exports (ESM)
- `src/index.cjs`           — CJS shim
- `src/client.js`           — `RustChainClient` (health, epoch, miners, balance, history,
                              bounties, epoch rewards, explorer blocks, attest challenge)
- `src/errors.js`           — `RustChainError` hierarchy (mirrors the Python SDK)
- `test/client.test.js`     — uses Node's built-in `node:test`; injects a fake `fetch` so the
                              suite is hermetic
- `examples/health-check.js` — runnable demo of `/health`, `/epoch`, `/miners`
- `examples/balance.js`     — runnable demo of `/wallet/balance`

## Why?

The `sdk/` tree only ships Python today. A JS SDK is the highest-leverage missing piece for
front-end dashboards, Telegram/Discord bots, VS Code extensions, and any browser-side tool that
wants to talk to a RustChain node.

## How to test?

```bash
cd sdk/javascript
node --test test/
# expected: all tests pass on Node ≥ 18 with no installs
```

Optional live smoke-tests (require network to the real node):

```bash
node examples/health-check.js
node examples/balance.js zxy0314-work
```

## Acceptance criteria checklist (from `docs/HOW_TO_SUBMIT_A_BOUNTY.md`)

- [x] **Real node URL only** — `https://50.28.86.131` is the single base URL in the SDK; verified
      against `docs/HOW_TO_SUBMIT_A_BOUNTY.md`. No `api.rustchain.io` or other hallucinated URLs.
- [x] **No invented files referenced** — the SDK references only its own files. The
      cross-reference in the README points at `sdk/python/README.md` which actually exists.
- [x] **One bounty, one PR** — all 11 new files live under `sdk/javascript/`. Nothing outside
      that directory is touched.
- [x] **Repo root README untouched** — the bounty board landing page is preserved.
- [x] **No `node_modules/`, `__pycache__/`, `.pyc`, `.DS_Store` in the diff** — `.gitignore`
      added; package has zero runtime deps so there's nothing to bundle.
- [x] **Code actually runs** — the test suite uses only Node's built-in `node:test` +
      `node:assert/strict` (Node ≥ 18) and an injected fake `fetch`, so it's reproducible in CI
      with `node --test test/`.
- [x] **Documentation matches the actual codebase** — every method in the README's API table
      corresponds to a method exported by `src/client.js`.

## Related Issues

This PR claims a JavaScript/Node SDK bounty (clear gap in the `sdk/` tree). Wallet for payout:
`zxy0314-work`.
