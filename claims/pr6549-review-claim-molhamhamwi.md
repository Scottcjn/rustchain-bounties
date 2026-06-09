# Code Review Bounty Claim: Scottcjn/Rustchain#6549

- Bounty issue: https://github.com/Scottcjn/rustchain-bounties/issues/2782
- Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6549
- Review: https://github.com/Scottcjn/Rustchain/pull/6549#pullrequestreview-4386032325
- Claim comment: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4569786574
- Head reviewed: `415276f806c0597c5fac922a0a863ca83c31d8ff`

## What I reviewed

`node/anti_double_mining.py` and `node/tests/test_anti_double_mining.py` for epoch-weight-aware representative miner selection.

## Why I liked it

The patch applies epoch enrollment weight before entropy/timestamp tie-breakers only when an epoch is provided, so same-machine aliases cannot displace the enrolled high-weight representative while no-epoch callers keep the old deterministic fallback behavior. The focused regression test directly covers a lower-entropy but higher-enrolled-weight miner beating a fresher/higher-entropy alias.

## Verification

- `python3 -m py_compile node/anti_double_mining.py node/tests/test_anti_double_mining.py`
- `PYTHONPATH=node python3 -m pytest node/tests/test_anti_double_mining.py -q` → 22 passed

I received RTC compensation for this review.
