# RustChain Bounty Hunter — Autonomous AI Agent

> An autonomous AI agent that finds, evaluates, and claims RustChain bounties on GitHub.
> Built for Issue #2861 — **50 RTC bounty**.

## What It Does

```
1. Fetch open bounties from rustchain-bounties GitHub repo
2. Score by feasibility (AI-powered evaluation)
3. Pick highest-value doable bounty
4. Fork repo → implement → submit PR
5. Track earnings in local wallet
```

## Architecture

```
bounty-hunter/
├── agent.py          # Main orchestrator
├── github_client.py  # GitHub API wrapper (fork, branch, file, PR)
├── bounty_scorer.py  # AI-powered bounty evaluation
├── wallet_tracker.py # Track earnings
├── skills/           # Domain-specific implementations
│   ├── docker_skill.py
│   ├── telegram_skill.py
│   ├── vscode_skill.py
│   └── article_skill.py
├── CLAUDE.md         # Agent instructions
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."
export GH_TOKEN="ghp_..."  # optional, for higher rate limits

# Hunt for bounties
python agent.py --wallet my-wallet

# Target a specific bounty
python agent.py --wallet my-wallet --bounty-id 2863
```

## Agent Loop

```
┌─────────────────────────────────────────┐
│  FETCH  → GitHub API: open bounties     │
└────────────────┬──────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  SCORE  → AI eval (feasibility/RTC)     │
└────────────────┬──────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  PICK  → Top-ranked doable bounty       │
└────────────────┬──────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  FORK  → Create feature branch          │
└────────────────┬──────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  BUILD → Implement the bounty           │
└────────────────┬──────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  PR   → Submit clean PR + bounty link   │
└────────────────┬──────────────────────┘
                 ▼
┌─────────────────────────────────────────┐
│  TRACK → Log wallet + earnings          │
└─────────────────────────────────────────┘
```

## Bounty Scoring Matrix

| Signal | Score Impact | Rationale |
|--------|-------------|-----------|
| Docker | +20 | Standardized, testable |
| Telegram Bot | +20 | Self-contained |
| GitHub Action | +25 | Clear spec |
| VSCode Extension | +20 | Well-defined API |
| Script/Tool | +15 | Quick win |
| Docs/Readme | +10 | Low complexity |
| Article | +25 | Just writing |
| Security Audit | -30 | Needs expertise |
| Full Agent | -20 | High complexity |

## AI Evaluation

Uses Claude API to assess:
1. Is the bounty clearly specified?
2. Can I complete it with available tools?
3. Estimated time to complete?
4. Risk of rejection?

```python
# Example AI evaluation output
"BOUNTY #2863 Dev.to Article: Score 88/100
 Confident I can write 800+ word technical article.
 Tech stack: markdown only. Low risk. Proceed."
```

## Wallet Integration

- Wallet address stored in `wallet.json`
- All PRs include wallet in body for RTC rewards
- Tracks history of submitted PRs and earnings

## GitHub Etiquette

- Respects rate limits (polite delays between API calls)
- No spam — only submits high-quality PRs
- Clean commit messages following conventional commits
- Meaningful PR descriptions with proof of work

## Requirements

- Python 3.10+
- `requests` library
- `anthropic` SDK (for AI evaluation)
- `PyGithub` (optional, for higher-level GitHub API)
- GitHub token (optional but recommended)

## Deploy as Claude Code Skill

```bash
# Add as a Claude Code custom command
mkdir -p ~/.claude/commands
cp CLAUDE.md ~/.claude/commands/bounty-hunter.md

# Now in Claude Code:
# /bounty-hunter Find and claim a RustChain bounty
```

## Proof of Work

This agent has been tested on:
- ✅ Bounty #2869: Telegram Bot (10 RTC) — PR#2928
- ✅ Bounty #2864: GitHub Action (20 RTC) — PR#2927
- ✅ Bounty #2868: VSCode Extension (30 RTC) — PR#2930
- ✅ Bounty #2924: Docker Miner (15+5 RTC) — PR#2924

Total claimed: 80+ RTC across 4 PRs

## License

MIT
