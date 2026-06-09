# Code Review Bounty Claim — RustChain PR #6631

- Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2782
- Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6631
- Review: https://github.com/Scottcjn/Rustchain/pull/6631#pullrequestreview-4392830086
- Claim comment: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4579824178
- Reviewer: @MolhamHamwi
- Reviewed head: `c7ebc194744edac288a191544d7c03e50fdd2552`

## What I reviewed

- `node/rustchain_p2p_sync.py`
- `node/test_p2p_sync_active_peers_limit_poc.py`

## Substantive observations

1. The new SQL cap limits active-peer materialization, but using `LIMIT` without `ORDER BY last_seen DESC` may keep arbitrary qualifying peers instead of the freshest peers during a flood.
2. The inactive/stale regression tests insert negative rows with duplicate generated URLs after active rows, so `INSERT OR IGNORE` can skip the rows that were meant to exercise the filters.

## Why I liked it

The patch addresses a concrete resource-exhaustion risk in a hot P2P sync path and adds focused regression coverage around capped peer selection.

I received RTC compensation for this review.
