# Code review claim for bounty #73

Reviewer: @qingfeng312
RTC wallet/miner ID: `qingfeng312-codex`

Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/5944
Review: https://github.com/Scottcjn/Rustchain/pull/5944#pullrequestreview-4329583161
Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/73

Summary: requested changes because PR #5944 fixes parsing of `amount_rtc`, but the default verifier configuration still points to the raw IP `https://50.28.86.131`. With default TLS verification and no local node certificate, a clean install fails certificate validation before the new `amount_rtc` parsing path can run. I verified the same balance endpoint works through the TLS-valid hostname `https://rustchain.org/wallet/balance?miner_id=davidtang-codex`, and requested switching the default endpoint or adding a default-install regression path.

Result: CHANGES_REQUESTED review submitted for bounty accounting. Maintainer award/payment is not assumed until confirmed.
