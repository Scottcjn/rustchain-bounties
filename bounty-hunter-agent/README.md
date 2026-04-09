# RustChain Autonomous Bounty Hunter Agent 🤖

> An AI agent that autonomously finds, evaluates, and claims RustChain bounties

## Overview

This is an **autonomous bounty hunter agent** that:
1. Fetches open RustChain bounties from GitHub
2. Evaluates difficulty and skill requirements
3. Forks repos and implements solutions
4. Submits clean PRs with bounty claims

## How It Works

```
┌─────────────────────────────────────────────┐
│  RustChain Bounty Hunter Agent              │
├─────────────────────────────────────────────┤
│  1. Fetch open bounties from GitHub API     │
│  2. Score by RTC value × difficulty         │
│  3. Fork repo & evaluate code              │
│  4. Implement fix/feature                   │
│  5. Submit PR with bounty claim             │
│  6. Track earnings in wallet                │
└─────────────────────────────────────────────┘
```

## Quick Start

```bash
# Set your GitHub token
export GITHUB_TOKEN=ghp_xxx

# Run the agent
python3 bounty_hunter.py your_wallet_name

# Or run the full autonomous version
python3 autonomous_hunter.py --wallet your_wallet --auto
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `ANTHROPIC_API_KEY` | For Claude | Claude API key for code generation |
| `OPENAI_API_KEY` | For GPT-4 | OpenAI API key for code generation |

## Features

### Bounty Evaluation
- Parses RTC amount from bounty title
- Assesses difficulty based on labels
- Matches required skills (Docker, GitHub Actions, etc.)
- Calculates priority score

### Autonomous PR Creation
- Forks repository automatically
- Creates feature branch
- Implements solution (with LLM assistance)
- Submits clean PR with description

### Wallet Tracking
- Maintains local wallet address
- Tracks earned RTC
- Reports earnings summary

## Architecture

```
bounty_hunter.py      # Main evaluation engine
├── fetches bounties via GitHub API
├── evaluates difficulty & skills
└── scores by RTC value

autonomous_hunter.py   # Full autonomous agent
├── uses Claude/ GPT-4 for code generation
├── implements fixes automatically
└── submits PRs
```

## Example Output

```
========================================
  RustChain Bounty Hunter Agent
  Wallet: shuziyoumin2_agent
========================================

[*] Fetching open bounties...
[+] Found 15 open bounties

[*] Top bounties by score:
  1. #2865 [15 RTC] Dockerize the RustChain Miner
     Difficulty: easy | Can do: ['docker']
  2. #2864 [20 RTC] Create a GitHub Action
     Difficulty: medium | Can do: ['github_action']
  3. #2868 [30 RTC] VS Code Extension
     Difficulty: medium | Can do: ['vscode']
```

## Requirements

- Python 3.8+
- `requests` library
- GitHub Personal Access Token
- Optional: Claude API key for autonomous code generation

## License

MIT
