# Code review bounty claim: Scottcjn/Rustchain#6438

Bounty: Scottcjn/rustchain-bounties#2782

Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6438

Review: https://github.com/Scottcjn/Rustchain/pull/6438#pullrequestreview-4376993246

Issue claim: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4559758299

What I reviewed: `node/rustchain_v2_integrated_v2.2.1_rip200.py`, focusing on the `/api/miners` pagination response and the added current-epoch enrolled miner count.

Why I liked it: the patch keeps the existing active miner count backward-compatible while exposing a clearer `total_enrolled` value for clients comparing `/api/miners` with `/epoch` data.

I received RTC compensation for this review.
