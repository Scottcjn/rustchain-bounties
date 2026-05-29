# Code Review Bounty Claim: RustChain PR #6622

- Bounty issue: https://github.com/Scottcjn/rustchain-bounties/issues/2782
- Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6622
- Review: https://github.com/Scottcjn/Rustchain/pull/6622#pullrequestreview-4390440588
- Claim comment: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4578816404
- Reviewed head: `586be6ab59212c04adbb78f39dc73abb0e41e989`
- Decision: Commented with one minor wording/maintainability note

## What I reviewed

- `node/utxo_db.py`
- `node/test_utxo_db.py`

## Substantive observations

1. `mempool_get_block_candidates` now maintains separate selected spend-input and selected data-input sets, so a candidate batch cannot include one transaction that spends a box another selected transaction only reads as a data input.
2. The regression test exercises sequential block application behavior: the read-only transaction is valid alone, but is excluded once the oracle box has already been selected for spending in the same candidate batch.
3. I verified the focused UTXO candidate tests locally from `node/`: `Ran 3 tests in 0.051s - OK`.

## Disclosure

I received RTC compensation for this review.
