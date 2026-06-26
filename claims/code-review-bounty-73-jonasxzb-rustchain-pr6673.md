# Code Review Bounty Claim - #73

Claimant: `jonasxzb`

Bounty: Scottcjn/rustchain-bounties#73

Wallet ID: `jonasxzb`

Status: submitted for maintainer assessment. The original #73 issue is not accepting new comments, so this PR records the claim.

## Review Submitted

### Scottcjn/Rustchain#6673 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/6673#pullrequestreview-4397908735

Summary:

- Reviewed the pending transaction ordering change.
- Verified the changed Python files compile.
- Reproduced that the PR's `created_at = int(time.time())` admission timestamp is only second-granular.
- Found that transactions accepted in the same second are ordered by `tx_hash`, not actual insertion/admission order.
- Requested a true admission-order tie-breaker, such as an autoincrement admission id/rowid ordering or high-resolution monotonic timestamp plus insertion-order tie-breaker.

## Local Verification Evidence

Commands run:

```bash
git diff --check origin/main...HEAD
python3 -m py_compile node/rustchain_tx_handler.py tests/test_tx_handler_pending_order.py
```

Focused direct `TransactionPool` probe with a mocked `rustchain_crypto` module:

```text
inserted_order ['z', 'a']
returned_order ['a', 'z']
```

The direct probe shows that two rows with the same integer `created_at` are returned by hash order, allowing a later admitted transaction with a lower hash to run before an earlier admitted transaction.

Note: invoking pytest for this file in the local checkout imported the repository-wide `tests/conftest.py` and failed because `flask` was not installed in the local Python environment, so the review relied on py_compile plus the focused pool probe above.

## Reward Request

Please assess this under the #73 code review reward structure as one substantive changes-requested review.

Reference rate in #73: `1 RTC = $0.10 USD`. At the posted minimum of 5 RTC per accepted review, this claim requests 5 RTC / $0.50 equivalent.
