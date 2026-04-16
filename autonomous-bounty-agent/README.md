# Autonomous Bounty Agent

An autonomous AI agent that scans, claims, and submits PRs for RustChain bounties.

## Overview

This agent autonomously:
1. Scans the [RustChain Bounties](https://github.com/Scottcjn/rustchain-bounties) repository for open bounty issues
2. Filters for agent-appropriate bounties (documentation, propagation, content, standard issues)
3. Claims suitable bounties via GitHub comments
4. Generates implementation files
5. Submits pull requests with solutions
6. Tracks earnings and PR status

## Project Structure

```
autonomous-bounty-agent/
├── agent.py              # Main agent orchestrator
├── github_scanner.py    # GitHub API scanner for bounties
├── pr_builder.py        # Fork, branch, commit, and PR submission
├── earnings_tracker.py  # Track claims, PRs, and earnings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set required environment variables:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx  # Required
export RTC_WALLET=RTCxxxxxxxxxxxxxxxxxxxxxxxx  # Optional, for real payouts
```

Or pass them as command-line arguments.

## Usage

```bash
# Target a specific bounty
python agent.py --bounty 2861 --token ghp_xxx

# Work on up to 3 bounties
python agent.py --max 3 --token ghp_xxx

# Full options
python agent.py \
  --token ghp_xxxxx \
  --wallet RTCxxxxx \
  --bounty 2861 \
  --max 1 \
  --delay 5
```

## How It Works

### 1. GitHub Scanner (`github_scanner.py`)
- Fetches open bounty issues from `Scottcjn/rustchain-bounties`
- Filters by agent-appropriate labels: `good first issue`, `standard`, `propagation`, `content`, `documentation`
- Skips hardware, red-team, and critical bounties

### 2. PR Builder (`pr_builder.py`)
- Forks the target repository
- Creates a dedicated branch
- Commits solution files
- Creates a pull request

### 3. Earnings Tracker (`earnings_tracker.py`)
- Records all claimed bounties with timestamps
- Tracks PR submission status
- Persists data to JSON

### 4. Agent Orchestrator (`agent.py`)
- Coordinates all modules
- Generates solution content based on bounty category
- Produces final earnings summary

## Requirements Met for Bounty #2861

- `github_scanner.py`: Scans and filters open bounties
- `pr_builder.py`: Full fork -> branch -> commit -> PR workflow
- `earnings_tracker.py`: Persistent tracking of claims and earnings
- `agent.py`: Complete orchestrator with CLI interface
- `requirements.txt`: All dependencies
- `README.md`: Documentation
