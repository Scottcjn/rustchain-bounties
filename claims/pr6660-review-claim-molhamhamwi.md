# Code Review Bounty Claim — RustChain PR #6660

- Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2782
- Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6660
- Review: https://github.com/Scottcjn/Rustchain/pull/6660#pullrequestreview-4395770879
- Claim comment: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4583815022
- Reviewer: @MolhamHamwi
- Reviewed head: `113925d35450a9cae8e7df6348c7a3b24629612d`

## What I reviewed

- `sdk/rustchain/client.py`
- `sdk/tests/test_client_unit.py`
- `sdk/README.md`
- `tests/test_bridge_lock_ledger.py`

## Substantive observations

1. `_request()` retries only transient connection/timeout failures and 429/5xx responses, while non-transient 4xx responses still raise immediately so SDK callers keep crisp validation feedback.
2. `retry_count = max(1, retry_count)` and `retry_backoff = max(0.0, retry_backoff)` make the new constructor options safe for zero/negative inputs, and the tests patch `time.sleep` to verify retry backoff without adding real delay.
3. `check_eligibility()` follows the existing `balance()` validation style and the unit test asserts both the `/lottery/eligibility` URL and `miner_id` query params.
4. The bridge lock-ledger tests now provide the admin key/header so malformed-query assertions run after the admin gate rather than failing early on authentication.

## Validation

- `python3 -m py_compile sdk/rustchain/client.py sdk/tests/test_client_unit.py tests/test_bridge_lock_ledger.py`
- `python -m pytest tests/test_client_unit.py -q` — 30 passed

## Why I liked it

The patch adds SDK reliability and a useful mining eligibility helper while keeping retry behavior narrow and covered by focused tests.

I received RTC compensation for this review.
