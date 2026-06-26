# Dependency Policy Judge

**Bounty:** [#14382](https://github.com/Scottcjn/rustchain-bounties/issues/14382) (75 RTC, multi-claim)

This is a community gate for the open `Judge` interface:

```python
judge(request) -> (passed: bool, reasons: list[str])
```

It is a distinct judge from static analysis and test-running gates. It checks
dependency manifests before a self-improvement request is accepted, then signs
the verdict with an Ed25519 key so clients can verify that the result came from
this gate.

## What It Judges

Given a request with `files` or `manifests`, the judge inspects:

- `package.json`
- `requirements*.txt`
- `pyproject.toml`

The default policy rejects:

- NPM lifecycle install scripts: `preinstall`, `install`, `postinstall`,
  `prepare`.
- Floating or broad dependency versions such as `latest`, `*`, `^1.2.3`,
  `~1.2.3`, `>=1.2.3`, and wildcard ranges.
- URL, Git, GitHub, and local file dependency specs.
- Python requirements that are not pinned with `==`.
- Python requirements that use editable installs, extra package indexes, URLs,
  or VCS dependencies.

These checks are deterministic and do not install, import, or execute any
submitted package.

## Interface

```python
from judge import DependencyPolicyJudge

judge = DependencyPolicyJudge()
passed, reasons = judge.judge({
    "files": {
        "package.json": '{"dependencies": {"left-pad": "1.3.0"}}'
    }
})

envelope = judge.sign_verdict({"files": {"package.json": "{}"}})
assert DependencyPolicyJudge.verify(envelope)
```

## Plugging Into the Reference Gate

The judge only needs to be registered wherever the reference gate accepts an
object implementing `judge(request) -> (passed, reasons)`:

```python
from judge import DependencyPolicyJudge

gate_server.register_judge(DependencyPolicyJudge())
```

No reference server code changes are required.

## Tests

```bash
pip install -r integrations/dependency-policy-judge/requirements.txt
pytest integrations/dependency-policy-judge/test_judge.py -q
```

The tests cover accepted manifests, rejected NPM and Python dependency patterns,
the open Judge interface, signed verdict verification, and tamper detection.

## RTC Wallet

Payout identifier: `qingfeng312-codex`

## License

MIT (SPDX-License-Identifier: MIT)
