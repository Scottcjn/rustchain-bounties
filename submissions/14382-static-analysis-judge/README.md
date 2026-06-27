# Static Analysis Judge

Open Judge implementation for bounty #14382.

This judge performs **static analysis** on submitted code artifacts. It is an alternative to the closed SophiaCore judge and the community policy judge — it focuses on **code quality** rather than policy review.

## Interface

```text
judge(request) -> (passed, reasons)
```

The returned verdict is wrapped in an Ed25519 signed envelope so a staking SDK or gate server can verify that the verdict was produced by this judge's key.

## What It Judges

The static analysis judge checks submitted code for:

| Check | Description |
| --- | --- |
| **Syntax** | Validates syntax via language-specific compilers/interpreters (Python, JavaScript, Rust, Go) |
| **Line length** | Flags lines exceeding a configurable max (default 120 chars) |
| **Trailing whitespace** | Detects trailing whitespace on any line |
| **Documentation** | Ensures functions and classes have docstrings (Python) or JSDoc (JS/TS) |
| **Unused imports** | Detects Python imports that are never referenced |
| **Hardcoded secrets** | Flags API keys, passwords, and private key patterns |

A submission **passes** only if all enabled checks pass.

## Files

| File | Purpose |
| --- | --- |
| `static-judge.mjs` | `StaticAnalysisJudge` class, canonical JSON, Ed25519 sign/verify helpers |
| `gate-server.mjs` | Minimal HTTP adapter exposing `POST /judge` for a reference gate |
| `test.mjs` | Node built-in test suite for pass, fail, and tampered verdict cases |
| `package.json` | Local scripts, no external dependencies |

## Run

```bash
cd submissions/14382-static-analysis-judge
npm test
node gate-server.mjs
```

Example request:

```bash
curl -sS http://127.0.0.1:8788/judge \
  -H 'content-type: application/json' \
  -d '{
    "summary": "Refactor the request parser to use typed validation.",
    "language": "python",
    "code": "def parse(request):\n    \"\"\"Parse and validate a request.\"\"\"\n    return request\n",
    "filename": "parser.py"
  }'
```

## Request Format

The judge accepts any of these fields to identify code:

- `code` — full source code
- `diff` — unified diff text
- `patch` — patch text
- `source` — alias for code

Language detection uses (in priority order):
1. `language` field (explicit)
2. `filename` extension
3. Heuristic pattern matching on the code content

## Key Handling

For demos and tests the judge generates an ephemeral Ed25519 key pair. For a persistent community gate, provide the key pair through environment variables:

```bash
JUDGE_PRIVATE_KEY_PEM="$(cat judge_private.pem)" \
JUDGE_PUBLIC_KEY_PEM="$(cat judge_public.pem)" \
node gate-server.mjs
```

The response includes:

- `verdict.passed`
- `verdict.reasons`
- `verdict.language_detected`
- `verdict.checks` (detailed per-check results)
- `verdict.request_hash`
- `public_key_pem`
- `signature_algorithm: Ed25519`
- `signature`

SDK verification succeeds by verifying the canonical envelope, excluding the `signature` field, with `public_key_pem`.

## Configuration

The judge accepts a `config` object with:

| Option | Default | Description |
| --- | --- | --- |
| `maxLineLength` | 120 | Maximum line length before flagging |
| `requireDocstrings` | true | Require docstrings on functions/classes |
| `checkUnusedImports` | true | Detect unused Python imports |
| `checkSecrets` | true | Detect hardcoded secrets |
| `checkTrailingWhitespace` | true | Detect trailing whitespace |

## Limits

- Syntax checking requires the relevant compiler/interpreter (`python3`, `node`, `rustc`/`gofmt`) to be installed and on PATH.
- This judge checks **static code quality** — it does not execute code or run test suites.
- Language detection is heuristic; explicitly setting `language` or `filename` improves accuracy.
- "Unused import" detection is currently Python-only.
- This judge is **distinct from the community policy judge**: it focuses on code linting/reviewability rather than policy/process checks.

Wallet ID for claim: `OWL-Agent`
