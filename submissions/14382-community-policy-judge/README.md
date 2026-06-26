# Community Policy Judge

Open Judge implementation for bounty #14382.

This judge is deliberately small and auditable. It implements the open interface:

```text
judge(request) -> (passed, reasons)
```

`judge(request)` returns the flat verdict shape with top-level `passed` and `reasons` fields. Use `judgeSigned(request)` or the HTTP gate adapter when a signed Ed25519 envelope is needed for downstream verification.

## What It Judges

The default policy checks that a proposed self-improvement request:

- has a non-trivial summary and a reviewable artifact (`diff`, `patch`, `repository`, or `artifact_url`)
- includes passing test or validation evidence
- avoids obvious secret leakage and unsafe execution patterns
- declares or implies a bounded improvement scope

This is meant for community-run gates that want a conservative "is this work reviewable and safe enough to advance?" check. It is not SophiaCore and does not attempt semantic code correctness beyond the policy checks above.

## Files

| File | Purpose |
| --- | --- |
| `policy-judge.mjs` | `CommunityPolicyJudge`, flat judge verdicts, canonical JSON, Ed25519 sign/verify helpers |
| `gate-server.mjs` | Minimal HTTP adapter exposing `POST /judge` for a reference gate |
| `test.mjs` | Node built-in test suite for passing, failing, and tampered verdicts |
| `package.json` | Local scripts, no external dependencies |

## Run

```bash
cd submissions/14382-community-policy-judge
npm test
node gate-server.mjs
```

Example request:

```bash
curl -sS http://127.0.0.1:8787/judge \
  -H 'content-type: application/json' \
  -d '{
    "summary": "Add typed validation around the gate request parser.",
    "scope": "code",
    "diff": "diff --git a/gate.js b/gate.js\n+ validate payload before submit",
    "tests": [{"name":"node --test","status":"passed"}]
  }'
```

## Key Handling

For demos and tests the judge generates an ephemeral Ed25519 key pair. For a persistent community gate, provide the key pair through environment variables:

```bash
JUDGE_PRIVATE_KEY_PEM="$(cat judge_private.pem)" \
JUDGE_PUBLIC_KEY_PEM="$(cat judge_public.pem)" \
node gate-server.mjs
```

`judge(request)` returns:

- `passed`
- `reasons`
- `checks`
- `request_hash`
- `issued_at`

`judgeSigned(request)` and `POST /judge` wrap that verdict in a signed envelope containing:

- `verdict.passed`
- `verdict.reasons`
- `verdict.request_hash`
- `public_key_pem`
- `signature_algorithm: Ed25519`
- `signature`

SDK verification succeeds by verifying the canonical envelope, excluding the `signature` field, with the pinned judge public key. The verifier must not trust a public key supplied only by an untrusted envelope.

## Limits

- This judge is a policy gate, not a deep theorem prover or full test runner.
- It cannot prove a diff is correct; it checks that the request is bounded, reviewable, tested, and free of obvious unsafe patterns.
- It is intentionally dependency-free so agents can run it inside constrained environments.

Wallet ID for claim: `lxx197818`
