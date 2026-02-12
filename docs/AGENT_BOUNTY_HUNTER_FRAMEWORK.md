# Agent Bounty Hunter Framework (Issue #34)

This document describes a practical AI-agent bounty framework that is already used in production-style runs.

## What Is Included

- `scripts/agent_bounty_hunter.py`
  - `scan`: fetch/rank open bounty leads
  - `claim-template`: generate claim comment text
  - `submit-template`: generate submission update text
  - `monitor`: monitor issue/PR pairs for payout readiness
- `data/agent_monitor_targets.json`
  - Sample monitoring targets covering real completed submissions
- `data/agent_execution_log_2026-02-12.json`
  - Real end-to-end execution log from this agent run

## Human-in-the-Loop Safety

The framework prepares actions but does not auto-merge or auto-pay:

1. Agent ranks and prepares candidates.
2. Agent drafts claim/submission content.
3. Human/operator performs final submit click (or explicit CLI post).
4. Agent monitors PR state and payout readiness.

## Real End-to-End Evidence

The following bounties were completed and queued by this agent run:

- #123: `Rustchain #115` accepted, payout queued (40 RTC)
- #72: `Rustchain #117` + `#118` accepted, payout queued (50 RTC)
- #122: `bottube #94` + `Rustchain #116` content + `ram-coffers #1` accepted, payout queued (25 RTC)
- #100: starter discovery accepted, payout queued (2 RTC)

Ledger reference:
- `rustchain-bounties#104` comment with pending ids 30-33.

## Quick Usage

```bash
# 1) Scan top candidates
python3 scripts/agent_bounty_hunter.py scan --top 10 --min-usd 10

# 2) Generate claim template for issue 34
python3 scripts/agent_bounty_hunter.py claim-template \
  --issue 34 \
  --wallet davidtang-codex \
  --handle David-code-tang

# 3) Generate submission template
python3 scripts/agent_bounty_hunter.py submit-template \
  --wallet davidtang-codex \
  --handle David-code-tang \
  --summary "Delivered docs + validation evidence." \
  --pr https://github.com/Scottcjn/Rustchain/pull/115

# 4) Monitor active issue/PR pairs
python3 scripts/agent_bounty_hunter.py monitor \
  --targets-json data/agent_monitor_targets.json
```

## Limitations

- Reward extraction is heuristic from title/body text.
- Difficulty scoring is heuristic and should be tuned per repo.
- External platform constraints still require maintainer review and payout timing.
