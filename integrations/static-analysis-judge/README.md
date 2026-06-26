# Static-Analysis Judge

**Bounty:** [#14382](https://github.com/Scottcjn/rustchain-bounties/issues/14382) (75 RTC, multi-claim)

A community implementation of the open `Judge` interface — an *alternative*
gate to SophiaCore, suitable for code self-improvement requests where the
gate needs a fast, deterministic, no-execution check.

## Interface

```python
judge(request) -> (passed: bool, reasons: list[str])
```

The `StaticAnalysisJudge` class implements this contract and exposes
`sign_verdict()` / `verify()` for Ed25519-signed envelopes that any SDK
verifying signed Beacon-style envelopes can authenticate.

## What it judges

Given a request of the form `{"files": {"path.py": "<source>", ...}}`,
the judge passes iff **every** file:

1. Parses as valid Python (no `SyntaxError`).
2. Contains no calls to `eval`, `exec`, `compile`, or `__import__`.
3. Imports none of `os.system`, `subprocess`, `pickle`, `marshal`.
4. Stays under the configured per-function and per-file line caps
   (defaults: 200 / 2000).

All rules run on the AST — **no submitted code is ever executed**.

## Limits

This is intentionally a narrow gate. It does **not**:

- Run, import, or sandbox the submitted code.
- Catch semantic bugs, races, or logic errors.
- Replace a full linter, type checker, or security scanner.
- Judge non-Python files (they are ignored).
- Cover dynamic shell-outs via `os.popen`, `ctypes`, attribute-based
  `getattr(__builtins__, 'eval')` tricks, etc. Adversarial code can
  bypass static analysis; this judge is designed for honest
  self-improvement requests, not adversarial review.

For richer policy, compose this judge with a test-runner judge or a
configurable policy judge.

## Usage

```python
from judge import StaticAnalysisJudge

j = StaticAnalysisJudge()
passed, reasons = j.judge({"files": {"patch.py": open("patch.py").read()}})

# Signed verdict envelope (Ed25519)
envelope = j.sign_verdict({"files": {"patch.py": "..."}})
assert StaticAnalysisJudge.verify(envelope)
```

## Plugging into the reference gate server

Because the gate server consumes anything matching the open `Judge`
interface, instantiation alone is enough:

```python
from judge import StaticAnalysisJudge
gate_server.register_judge(StaticAnalysisJudge())
```

No reference-server code is modified.

## Tests

```bash
pip install cryptography pytest
pytest integrations/static-analysis-judge/test_judge.py -q
```

Twelve tests cover the interface contract, every rule, the signature
roundtrip, and tamper detection.

## RTC wallet

Payout wallet: _to be added by maintainer of this fork on claim._

## License

MIT (SPDX-License-Identifier: MIT).
