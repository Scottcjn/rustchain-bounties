# Secret-Leak Judge

A community gate for the open **Judge** interface (`judge(request) -> (passed, reasons)`)
on the staking self-improvement rails. Submitted for **Bounty #14382** (multi-claim).

This is a **distinct, non-overlapping** judge. It judges *only one thing*: whether
a self-improvement diff **introduces a hardcoded secret in its added lines**. It is
meant to run **alongside** the other community judges, not replace them:

| Judge | What it checks | This one? |
|-------|----------------|-----------|
| Diff-bounds judge | size limits + anti-test-deletion + protected paths | ❌ different |
| Test-runner judge | runs the suite, passes iff green | ❌ different |
| Static-analysis judge | lint / AST checks on the code | ❌ different |
| Dependency-policy judge | allowed/blocked dependency sets | ❌ different |
| **Secret-Leak judge** | **no hardcoded keys / tokens / credentials in added lines** | ✅ |

## Why this judge exists

An autonomous agent that stakes RTC to "self-improve" rewrites its own source. One
careless edit and a private key, an AWS secret, a vendor token or a password literal
lands in the repo — and from there into git history forever, where rotation is the
only remedy. A size judge, a lint judge or a test-runner judge will happily pass such
a change: the code still builds, still lints, still goes green. This judge closes that
gap by scanning the **content that was added**.

It only inspects **added (`+`) lines** — *removing* a secret (e.g. replacing a
hardcoded password with `os.environ[...]`) is exactly what you want and passes.

## What it checks

Given a request carrying a unified `diff` (or `patch`), it runs two checks:

1. **parseable** — the request actually contains a well-formed unified diff (a file
   header **and** at least one `@@` hunk). Header-only/empty input is rejected so it
   can never trivially "pass" with nothing scanned.
2. **no_hardcoded_secrets** — none of the added lines match a high-confidence secret
   rule. The rules are vendor-anchored or structurally specific to keep false
   positives low:

   | rule | catches |
   |------|---------|
   | `private_key_block` | `-----BEGIN ... PRIVATE KEY-----` (RSA/EC/OpenSSH/PGP/…) |
   | `aws_access_key_id` | `AKIA…` / `ASIA…` access key ids |
   | `github_token` | `ghp_…`, `gho_…`, `github_pat_…` |
   | `slack_token` | `xoxb-…`, `xoxp-…`, `xoxa/r/s-…` |
   | `google_api_key` | `AIza…` |
   | `stripe_secret_key` | `sk_live_…`, `rk_live_…`, `sk_test_…` |
   | `openai_key` | `sk-…`, `sk-proj-…`, `sk-ant-…` |
   | `basic_auth_url` | `scheme://user:password@host` |
   | `hardcoded_credential_assignment` | `password`/`secret`/`api_key`/`token`/… `= "literal"` |

### False-positive guards

The credential-assignment and URL rules **do not** fire when the value is:

- a placeholder — `changeme`, `<your-api-key>`, `xxxxxxxx`, `${VAULT_SECRET}`,
  `{{ ... }}`, `example`, `dummy`, `redacted`, …
- an environment / config reference — `process.env.X`, `os.environ[...]`,
  `getenv(...)`, `config.*`, `vault.*`, `${ENV_VAR}`, …

An explicit `allow_secrets: ["path/to/file", "substring", ...]` in the request
whitelists an intended addition (e.g. a **public** test fixture or a key the
project genuinely ships). An entry matches either the file path or a substring of
the offending line.

The verdict never echoes a live secret back: any long token in a finding's
`snippet` is **redacted** (`ghp_…cd[redacted 40 chars]`).

## Interface compatibility

`createJudge(options).judge(request)` returns a signed verdict envelope in the same
canonical JSON shape (sorted keys, no whitespace) used across the staking rails, so
the open SDK's Ed25519 verification passes byte-for-byte:

```json
{
  "verdict": {
    "judge_id": "secret-leak-judge-v1",
    "interface": "Judge.judge(request)->(passed,reasons)",
    "passed": false,
    "reasons": ["added lines introduce 1 hardcoded secret(s): AWS access key id in deploy.sh (+line 1)"],
    "checks": [ ... ],
    "findings": [{ "rule": "aws_access_key_id", "label": "AWS access key id", "path": "deploy.sh", "added_line": 1, "snippet": "..." }],
    "stats": { "files": 1, "added_lines": 1, "secrets_found": 1 }
  },
  "signature_algorithm": "Ed25519",
  "public_key_pem": "-----BEGIN PUBLIC KEY-----\n...",
  "signature": "<base64>"
}
```

`judge.verify(signedVerdict)` re-derives the canonical payload and checks the
signature against the embedded public key — identical to what the SDK does against
the gate pubkey. Tampering with any field, or substituting a forged key, fails
verification (fail-safe against MITM/forgery).

### Keys

Configure the gate with **only** a private key — the advertised public key is
*derived* from it (`crypto.createPublicKey`), so the documented `JUDGE_PRIVATE_KEY_PEM`-only
server flow is always self-consistent:

```bash
JUDGE_PRIVATE_KEY_PEM="$(cat judge.key)" node gate-server.mjs
```

With no key configured, a fresh Ed25519 pair is generated at startup (handy for
local/dev). Supplying only a public key gives a verify-only instance.

## Run it

```bash
node --test          # 19 tests: happy path, each detector, placeholder/env guards,
                     # removal-is-ok, allow_secrets, redaction, forged-key, reproducibility
node gate-server.mjs # POST /judge -> signed verdict; GET /health
```

```bash
curl -s -X POST http://127.0.0.1:8789/judge -H 'content-type: application/json' \
  -d '{"summary":"add deploy key","diff":"diff --git a/deploy.sh b/deploy.sh\n--- a/deploy.sh\n+++ b/deploy.sh\n@@ -1,1 +1,2 @@\n #!/bin/sh\n+export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE\n"}'
# -> verdict.passed = false, findings[0].rule = "aws_access_key_id"
```

## Limits (honest scope)

- It is a **lexical** scanner over added diff lines, not a data-flow analysis. It
  targets *committed* secrets (the common, high-impact mistake), not secrets that are
  computed/assembled at runtime.
- High-confidence rules favour precision over recall: a bespoke in-house token format
  with no recognizable prefix and a generic variable name may pass. It is a gate
  against the **obvious, irreversible** leak, complementary to the other judges — not
  a replacement for a full secret-scanning product.
- Dependency-free, Node ≥ 16 (`node:crypto` Ed25519). MIT.

— submitted by `@Vyacheslav-Tomashevskiy`
