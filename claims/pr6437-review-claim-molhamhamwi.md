# Code review bounty claim: Scottcjn/Rustchain#6437

Bounty: Scottcjn/rustchain-bounties#2782

Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/6437

Review: https://github.com/Scottcjn/Rustchain/pull/6437#pullrequestreview-4377007185

Issue claim: https://github.com/Scottcjn/rustchain-bounties/issues/2782#issuecomment-4559769446

What I reviewed: `node/test_legacy_sig_fee.py`, focusing on the legacy signature fee manipulation demonstrator.

Why I liked it: the PR clearly shows that the legacy signed payload excludes `fee_rtc`, making the fee-tampering risk easy to understand; I also pointed out how to turn it from a demonstrator into a production-path regression test.

I received RTC compensation for this review.
