# Code Review Bounty Claim - #73

Claimant: `jonasxzb`

Bounty: Scottcjn/rustchain-bounties#73

Wallet ID: `jonasxzb`

Status: submitted for maintainer assessment. The original #73 issue is not accepting new comments, so this PR records the claim.

## Review Submitted

### Scottcjn/Rustchain#6666 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/6666#pullrequestreview-4397950852

Summary:

- Re-reviewed the current data custody proof head after duplicate-offset and piece-hash follow-ups.
- Verified the duplicate-offset blocker is addressed: impossible coverage requests now raise `ValueError sample_count exceeds distinct sample windows`.
- Verified the forged `piece_hash` blocker is addressed: `verify_custody_proof()` now rejects mismatched full-piece hashes when `piece_hash` is present.
- Confirmed focused custody tests pass on the current head.

## Local Verification Evidence

Commands run:

```bash
git diff --check origin/main...HEAD -- node/data_custody.py node/tests/test_data_custody.py
python3 -m py_compile node/data_custody.py node/tests/test_data_custody.py
PYTHONPATH=. python3 -m pytest -q node/tests/test_data_custody.py --tb=short --noconftest -o addopts=''
```

Focused pytest result:

```text
8 passed in 0.04s
```

Focused previous-blocker probe result:

```text
duplicate-offset guard ValueError sample_count exceeds distinct sample windows
{'valid': False, 'slashable': True, 'reason': 'piece_hash_mismatch', 'checked_samples': 0, 'failed_offsets': []}
```

## Reward Request

Please assess this under the #73 code review reward structure as one substantive approval review.

Reference rate in #73: `1 RTC = $0.10 USD`. At the posted minimum of 5 RTC per accepted review, this claim requests 5 RTC / $0.50 equivalent.
