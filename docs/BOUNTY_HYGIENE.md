# Bounty Hygiene and Research Rules

Last updated: 2026-02-19

This document defines the minimum quality and safety bar for RustChain/BoTTube bounties.
It exists to make submissions reproducible, auditable, and safe to review.

## 1) Required Bounty Metadata

Every new bounty issue should include:

- target repository (owner/repo)
- target branch or commit range
- in-scope and out-of-scope boundaries
- acceptance criteria (verifiable)
- payout amount and payout mode (single vs staged)
- disclosure expectations (for security work)

## 2) Supply-Chain Safety Requirements

Bounty submissions must avoid unsafe install/run patterns.

Do:

- pin dependencies when possible (version and/or digest)
- reference exact commit SHAs for external code
- provide checksums for downloaded artifacts
- use reproducible commands in README/PR body
- prefer reviewed package managers over random shell scripts

Do not:

- ask reviewers to run blind `curl | bash` commands
- require unpinned random packages without justification
- include secrets/tokens in code, scripts, or logs
- add compiled artifacts (`.pyc`, binaries) unless explicitly requested

## 3) Security Research Rules

For red-team/security bounties:

- follow `SECURITY.md` safe-harbor rules
- include clear reproduction steps and impact
- do not exfiltrate non-public data
- do not move funds you do not own
- coordinate disclosure before public posting

## 4) Payout Transparency

This project uses RTC-native payouts.

- no ICO claims and no guaranteed token value/liquidity
- utility coin and funding disclosure: `docs/UTILITY_COIN_POSITION.md`
- reward is for accepted shipped work
- payout queue/confirmation is logged in public ledger issue
- high-value bounties may use staged payout

Ledger reference:

- `https://github.com/Scottcjn/rustchain-bounties/issues/104`

## 5) Minimum PR Evidence

A bounty PR should include:

- linked bounty issue
- wallet ID
- test or verification evidence
- before/after summary
- quality self-score (Impact, Correctness, Evidence, Craft)
- supply-chain proof (if dependencies/artifacts changed)

## 6) Maintainer Rejection Triggers

A submission can be closed with no payout if it has:

- placeholder paths or non-runnable scaffolding
- unverifiable claims or missing proof
- duplicate/noise submissions
- unsafe install instructions
- unrelated or spammy changes
