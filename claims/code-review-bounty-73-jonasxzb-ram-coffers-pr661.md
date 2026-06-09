# Code Review Bounty Claim - #73

Claimant: `jonasxzb`

Bounty: Scottcjn/rustchain-bounties#73

Wallet ID: `jonasxzb`

Status: submitted for maintainer assessment. The original #73 issue is not accepting new comments, so this PR records the claim.

## Review Submitted

### Scottcjn/ram-coffers#661 - Changes Requested

Review: https://github.com/Scottcjn/ram-coffers/pull/661#pullrequestreview-4397881373

Summary:

- Verified the PR with `git diff --check origin/main...HEAD`.
- Verified shell syntax with `bash -n benchmark_coffers_vs_llamacpp.sh`.
- Ran `./benchmark_coffers_vs_llamacpp.sh --dry-run` and inspected the generated report.
- Found a correctness blocker: the default "RAM Coffers" build path only copies Coffers headers into a cloned `llama.cpp` tree, but does not include, patch, define, or call the RAM Coffers integration code. The generated comparison therefore appears to measure stock `llama.cpp` with `numactl --interleave=all`, not RAM Coffers NUMA-aware inference.
- Requested that the default path either compile a real Coffers integration or require a verified hand-patched `--coffers-bin`, and that the report record resolved stock/coffers commit SHAs for reproducibility.

## Local Verification Evidence

Commands run:

```bash
git diff --check origin/main...HEAD
bash -n benchmark_coffers_vs_llamacpp.sh
./benchmark_coffers_vs_llamacpp.sh --dry-run
```

Dry-run report generated locally:

```text
benchmarks/out/coffers-vs-llamacpp-20260601-084810.md
```

## Reward Request

Please assess this under the #73 code review reward structure as one substantive changes-requested review.

Reference rate in #73: `1 RTC = $0.10 USD`. At the posted minimum of 5 RTC per accepted review, this claim requests 5 RTC / $0.50 equivalent.
