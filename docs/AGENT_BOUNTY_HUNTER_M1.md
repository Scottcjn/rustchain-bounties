# AGENT_BOUNTY_HUNTER_M1

M1 skeleton implementation for bounty #34 (RustChain). This document provides quick usage and constraints.

## Files Added
- `scripts/agent_bounty_hunter.py`

## Purpose
Provide a machine-assisted but human-safe starting workflow:
1. scan open bounty issues,
2. filter by capability/risk and skip hardware-dependent items by default,
3. produce a simple implementation plan in JSON/Markdown for a selected bounty,
4. keep GitHub write actions in dry-run mode by default.

## Usage

### 1) Scan open bounties
```bash
python3 scripts/agent_bounty_hunter.py scan \
  --owner Scottcjn --repo rustchain-bounties
```

Options:
- `--min-capability` (float): minimum capability score.
- `--max-risk` (`low|medium|high`): risk threshold.
- `--include-hardware`: allow high-risk/hardware bounties.
- `--token`: optional GitHub token for API rate-limit/security.

### 2) Generate plan for one bounty
```bash
python3 scripts/agent_bounty_hunter.py plan --issue 34
python3 scripts/agent_bounty_hunter.py plan --issue 34 --format md
```

### 3) Post comment (dry-run default)
```bash
python3 scripts/agent_bounty_hunter.py post-comment \
  --issue 34 --body "Implementation plan ready"
```

Default is dry-run:
- `{"mode": "dry-run", "posted": false}`

To actually post:
```bash
python3 scripts/agent_bounty_hunter.py post-comment \
  --issue 34 \
  --body "..." \
  --no-dry-run \
  --token "$GITHUB_TOKEN"
```

## Constraints
- Remote call uses GitHub REST API v3 and `bounty` label filter.
- Hardware-related keywords (`hardware`, `arduino`, `raspberry`, `3d`, etc.) are treated as high risk and filtered out unless `--include-hardware`.
- This is a proof-of-progress skeleton (M1), not a full automation agent.

## Next Steps (M2)
- Add ranking strategy that balances reward vs risk and recent activity.
- Add per-bounty plan templating for language-specific tasks.
- Add richer test coverage with mocked GitHub responses.
- Add PR creation/helpful automation for claim/submission comments.
