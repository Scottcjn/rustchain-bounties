# JUnit Artifact Judge

This is a community implementation of the open `Judge` interface for bounty
#14382. It judges submitted JUnit XML test artifacts rather than executing
untrusted code.

## What It Judges

- Accepts legacy `junit_xml` payloads and nested `test_artifacts.junit_xml`.
- Passes only when at least one test is reported and there are zero failures
  and zero errors.
- Returns `(passed, reasons)` through the exported `judge(request)` function.
- Provides a small `POST /judge` adapter for reference gate servers that call a
  local HTTP judge.
- Signs verdict envelopes with an Ed25519 key using Node's built-in `crypto`
  module.

## Run

```bash
node community/judges/junit-artifact-judge/test.mjs
```

To run the HTTP adapter, provide a PEM-encoded Ed25519 private key:

```bash
export JUNIT_JUDGE_PRIVATE_KEY_PEM="$(cat ed25519-private.pem)"
node community/judges/junit-artifact-judge/judge.mjs
```

Then post:

```json
{
  "junit_xml": "<testsuite tests=\"1\" failures=\"0\" errors=\"0\"><testcase name=\"ok\"/></testsuite>"
}
```

## Limits

This judge does not execute tests, inspect source code, or verify that the XML
artifact came from a trusted CI system. It is intentionally narrow: use it only
as a gate for already-produced test result artifacts, and combine it with CI
provenance checks when the source of the artifact matters.

## Wallet

RTC payout wallet: qiann0512-gif
