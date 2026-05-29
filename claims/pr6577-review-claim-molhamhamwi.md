# Code review bounty claim — RustChain PR #6577

Bounty: Scottcjn/rustchain-bounties#2782

## Review

- Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6577
- Review: https://github.com/Scottcjn/Rustchain/pull/6577#pullrequestreview-4388657448
- Claim comment: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4573780461
- Reviewed head: `65d7aa81380171e33a47f7c99a2d06bf0b1aa36b`
- Reviewer: @MolhamHamwi

## Substantive observations

1. `node/coalition.py` now makes the non-hex miner-id path fail closed by default and only restores readable test miner names when `RUSTCHAIN_TEST_ALLOW_UNSIGNED_COALITION_MINERS` is explicitly enabled. That closes the previous production bypass because arbitrary names no longer skip signature verification.
2. `node/tests/test_coalition.py` adds a direct regression for `/api/coalition/create` using `miner_id: "alice"` with the test-bypass env var removed, and the surrounding read requests include `ADMIN_HEADERS` where the hardened endpoints require admin authentication.

## Disclosure

I received RTC compensation for this review.
