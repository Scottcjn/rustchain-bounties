# Diff-Bounds Judge

A community gate for the open **Judge** interface (`judge(request) -> (passed, reasons)`)
on the staking self-improvement rails. Submitted for **Bounty #14382** (multi-claim).

This is a **distinct, non-overlapping** judge. It judges *only the geometry and
containment of a self-improvement diff* — not its content, not its lint quality,
and it does not run the test suite. It is meant to run **alongside** the other
community judges:

| Judge | What it checks | This one? |
|-------|----------------|-----------|
| Policy judge | configurable content rules (secrets, shape, scope) | ❌ different |
| Test-runner judge | runs the suite, passes iff green | ❌ different |
| Static-analysis judge | lint / AST checks on the code | ❌ different |
| **Diff-Bounds judge** | **size limits + anti-test-deletion + protected paths** | ✅ |

## Why this judge exists

An autonomous agent that stakes RTC to "self-improve" has an incentive to *game*
the gate — e.g. delete the failing tests, strip assertions, quietly disable CI,
or dump an unreviewably huge change. A content/lint/test judge does not catch any
of those by itself. The Diff-Bounds judge closes that gap by reasoning about the
**shape of the change**.

## What it checks

Given a request carrying a unified `diff` (or `patch`), it runs four checks:

1. **parseable** — the request actually contains a well-formed unified diff.
2. **size** — the change stays within bounds: `maxFiles` (25), `maxAddedLines`
   (800), `maxRemovedLines` (600). All configurable.
3. **test_integrity** — the diff does **not** delete a test file and does **not**
   net-remove test assertions (`assert*`, `expect`, `it(`, `test(`, `self.assert*`).
   This is the anti-gaming guard.
4. **protected_paths** — the diff does not silently edit CI config (`.github/`) or
   lockfiles (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `Cargo.lock`,
   `poetry.lock`). An explicit `allow_protected: ["path", ...]` in the request
   whitelists intended changes.

The verdict is signed with the judge's own **Ed25519** key in the same canonical
JSON envelope used across the staking rails (sorted keys, no whitespace), so the
open SDK's signature verification passes byte-for-byte.

## Interface compatibility

`createJudge(options).judge(request)` returns a signed verdict envelope:

```json
{
  "verdict": { "judge_id": "...", "passed": true, "reasons": [], "checks": [...], "stats": {...} },
  "signature_algorithm": "Ed25519",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...",
  "signature": "<base64>"
}
```

`judge.verify(signedVerdict)` re-derives the canonical payload and checks the
signature against the embedded public key — identical to what the SDK does
against the gate pubkey. Tampering with any field, or substituting a forged key,
fails verification (covered by tests).

It plugs into the reference gate server **unmodified**: the included
`gate-server.mjs` exposes `POST /judge` (request → signed verdict) and
`GET /health`, the same surface the other community judges use.

## Run it

```bash
# Generate a key pair (optional — omit to auto-generate an ephemeral one):
node -e 'import("./diff-bounds-judge.mjs").then(m=>{const k=m.generateJudgeKeyPair();console.log(k.privateKeyPem);console.error(k.publicKeyPem)})'

# Serve the gate:
JUDGE_PRIVATE_KEY_PEM="$(cat key.pem)" PORT=8788 node gate-server.mjs

# Judge a diff:
curl -s -X POST http://127.0.0.1:8788/judge \
  -H 'content-type: application/json' \
  -d '{"summary":"harden add()","diff":"diff --git a/s.js b/s.js\n--- a/s.js\n+++ b/s.js\n@@ -1 +1 @@\n-x\n+y"}'
```

Programmatic:

```js
import { createJudge } from "./diff-bounds-judge.mjs";

const judge = createJudge({ limits: { maxFiles: 10, maxAddedLines: 200 } });
const signed = judge.judge({ summary: "...", diff: unifiedDiffText });
if (!signed.verdict.passed) console.log(signed.verdict.reasons);
console.log("signature ok:", judge.verify(signed));
```

## Tests

```bash
node --test     # 12 tests: happy path, oversize, too-many-files,
                # test-deletion, assertion-stripping, protected paths,
                # tamper detection, forged-key rejection, canonical determinism
```

## Limits

- It analyses diff **geometry**, not semantics: it cannot tell whether a same-size
  change is a *good* change (that is the test-runner / static-analysis judge's job).
- Assertion counting is heuristic (regex over added/removed lines) and language-
  agnostic; it is a guard against blatant test-gaming, not a coverage tool.
- It trusts that the supplied diff matches what was actually applied; pairing it
  with the on-chain attestation of the artifact closes that loop.

Add your RTC wallet to the claim. — MIT licensed.
