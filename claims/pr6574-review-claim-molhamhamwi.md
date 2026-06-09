# Code review bounty claim — RustChain PR #6574

Bounty: Scottcjn/rustchain-bounties#2782

## Review

- Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6574
- Review: https://github.com/Scottcjn/Rustchain/pull/6574#pullrequestreview-4388667442
- Claim comment: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4573799457
- Reviewed head: `963e926c6774ad817044939de8d375270dc0eb0e`
- Reviewer: @MolhamHamwi

## Substantive observations

1. `explorer/enhanced-explorer.html` now uses `window.location.origin` instead of a hard-coded IP address, which avoids deployed frontend/API host mismatches and CORS failures.
2. `web/hall-of-fame/index.html` now loads the leaderboard from `/hall/leaderboard`, matching the existing `/hall/stats` route family.
3. The review also flagged a follow-up risk: using `.toFixed(2)` directly on miner earnings can throw if the API serializes the value as a string; the existing `formatNumber(..., 2)` path is safer.

## Disclosure

I received RTC compensation for this review.
