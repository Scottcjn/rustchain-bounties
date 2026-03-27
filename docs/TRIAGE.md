# Triage Workflow

This repo is the control plane for RTC bounties, claims, payout registration, and cross-repo routing.

## Routing Rules

Use `rustchain-bounties` for:
- new bounty definitions
- proof of completed bounty work
- merged PR payout requests
- social / campaign claims
- install report payouts
- wallet registration and payout targets
- payout ledger and fraud review

Use product repos for product work:
- `Scottcjn/Rustchain`: protocol, node, miner, wallet, explorer, security, API bugs
- `Scottcjn/bottube`: product, creator workflow, API, embeds, notifications, tips, SEO, moderation
- `Scottcjn/beacon-skill`: relay, identity, replay protection, install, packaging, docs bugs

## Recommended Project Columns

If you build a GitHub Project for this workflow, use these columns:
1. Inbox
2. Needs Routing
3. Ready to Spec
4. Ready for Contributors
5. In Progress
6. Needs Review
7. Needs Deploy / Payout
8. Done

## Suggested Fields

- Repo
- Type
- Area
- Severity
- ROI
- Owner
- Bounty RTC
- Needs Human Verify

## Type Values

- `bug`
- `feature`
- `security`
- `docs`
- `claim`
- `payout`
- `campaign`
- `ops`

## Severity Values

- `critical`
- `high`
- `medium`
- `low`

## ROI Heuristic

Use a simple 1-5 scale:
- `5`: trust, security, retention, payout integrity, or infra stability
- `4`: onboarding, SDKs, key product UX, distribution primitives
- `3`: useful but not urgent product or docs work
- `2`: niche improvements or low-leverage campaigns
- `1`: vanity work, duplicate work, or unclear impact

## Cleanup Rules

- Do not use product repos for wallet registration.
- Do not use product repos for payout or campaign proof.
- Close duplicate claim issues after payout is recorded in the ledger.
- Keep one payout ledger issue as the system of record.
- Route product bugs back to the product repo, even if a bounty exists here.
- Prefer issue forms over blank issues to keep review load bounded.

## Review Order

Review in this order:
1. Security and payout-integrity bugs
2. Reproducible product bugs blocking onboarding or retention
3. Merged PR payout requests waiting on verification
4. High-ROI product features
5. Campaign and proof-based claims
6. Low-signal growth or vanity tasks
