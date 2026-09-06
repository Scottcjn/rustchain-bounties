# Bounty Hygiene and Research Rules

Last updated: 2026-09-02

This document defines the minimum quality and safety bar for RustChain/BoTTube bounties.
It exists to make submissions reproducible, auditable, safe to review, and less likely to waste contributor or maintainer time on work that could never qualify.

## 1) Required Bounty Metadata

Every new bounty issue should include:

- target repository (owner/repo)
- target branch or commit range
- in-scope and out-of-scope boundaries
- acceptance criteria (verifiable)
- payout amount and payout mode (single vs staged)
- cap, slot, per-person, or first-accepted limits when applicable
- the accepted submission route (`PR`, issue comment, email fallback, public repo, external proof URL, etc.)
- any external proof dependency such as hardware, publication, account age, live URL, or third-party acceptance
- disclosure expectations (for security work)

If the title, body, machine-readable bounty spec, or later maintainer clarification disagree about reward or eligibility, contributors should record the conflict and use the most recent explicit maintainer rule rather than silently choosing the larger value.

## 2) Pre-Build Viability Gate

Before substantial implementation starts, verify all of the following from the live authoritative issue and current repository state:

1. The bounty is still open and payable.
2. The stated reward and payout mode are current.
3. Any pool, cap, slot, or per-claimant allowance still has room.
4. No competing claim, PR, or already-merged equivalent has consumed the deliverable.
5. The requested source gap still exists on the current target branch.
6. Every required acceptance criterion can be demonstrated honestly.
7. The required submission route is actually executable by the contributor.
8. Any required external proof can really be produced; screenshots, publication, hardware runs, users, transactions, or third-party approvals must never be invented.

If one of these gates fails, stop before building and either choose another bounty or wait for the specific condition to change. A large headline reward does not make an ineligible or unsubmittable task valuable.

## 3) Submission Route Integrity

A completed artifact is not a valid claim until it is submitted through a route the bounty accepts.

- Prefer the route stated in the live bounty issue or its machine-readable `bounty-spec`.
- A `403 Resource not accessible by integration` is a tool/permission failure, not maintainer acceptance and not permission to invent a substitute route.
- Use email fallback only when the bounty, project documentation, or maintainer explicitly authorizes it.
- If a bounty requires an upstream PR, a private fork or unrelated public repository does not satisfy that requirement by itself.
- If a bounty requires a merged PR, a merely opened PR is still incomplete unless the live bounty explicitly says otherwise.
- Keep repairs and additional evidence in the original claim thread whenever possible. Do not create duplicate economic claims for the same underlying work.

## 4) Supply-Chain Safety Requirements

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

## 5) Security Research Rules

For red-team/security bounties:

- follow `SECURITY.md` safe-harbor rules
- include clear reproduction steps and impact
- do not exfiltrate non-public data
- do not move funds you do not own
- coordinate disclosure before public posting

## 6) Payout Transparency and Claim Stages

This project uses RTC-native payouts.

- no ICO claims and no guaranteed token value/liquidity
- utility coin and funding disclosure: `docs/UTILITY_COIN_POSITION.md`
- reward is for accepted shipped work
- payout queue/confirmation is logged in public ledger issue
- high-value bounties may use staged payout

Do not collapse claim stages. Treat them separately:

`BUILT -> SUBMITTED -> ACCEPTED/QUEUED -> PENDING ON-CHAIN -> RECEIVED`

- `BUILT` means the artifact exists.
- `SUBMITTED` means it reached an authorized claim route.
- `ACCEPTED/QUEUED` requires maintainer evidence.
- `PENDING ON-CHAIN` requires a pending/transaction reference or equivalent authoritative transfer evidence.
- `RECEIVED` requires wallet/ledger confirmation.

Requested, estimated, duplicate, superseded, cap-overflow, or conditional rewards are not received revenue.

Ledger reference:

- `https://github.com/Scottcjn/rustchain-bounties/issues/104`

## 7) Minimum PR Evidence

A bounty PR should include:

- linked bounty issue
- wallet ID
- test or verification evidence
- before/after summary
- quality self-score (Impact, Correctness, Evidence, Craft)
- supply-chain proof (if dependencies/artifacts changed)
- any cap/slot or competing-claim check that materially affects eligibility

## 8) Recheck Instead of Rebuilding

When a candidate is currently blocked, record the condition that would make it actionable again rather than repeatedly rebuilding or resubmitting it. Useful triggers include:

- submission route becomes available
- occupying PR closes or is rejected
- maintainer changes the reward, cap, or acceptance criteria
- required external account/hardware/publication route becomes available
- a maintainer requests a concrete revision

Terminal conditions such as an awarded one-winner bounty, expired deadline, consumed cap, or permanently ineligible deliverable should not be repeatedly rescanned without new authoritative evidence.

## 9) Maintainer Rejection Triggers

A submission can be closed with no payout if it has:

- placeholder paths or non-runnable scaffolding
- unverifiable claims or missing proof
- duplicate/noise submissions
- unsafe install instructions
- unrelated or spammy changes
- knowingly unavailable submission or proof routes presented as completed
- cap/slot overflow represented as payable work
