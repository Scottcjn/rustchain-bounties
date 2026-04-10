# Autonomous RustChain Bounty Agent

A fully autonomous AI agent that scans RustChain bounties, evaluates opportunities, forks repos, and submits high-quality pull requests.

## Features

- **Bounty Scanning**: Fetches and ranks open RustChain bounties via GitHub API
- **Opportunity Scoring**: Evaluates difficulty, competition, and value for each bounty
- **Autonomous Submission**: Forks repos, creates branches, commits code, and submits PRs without human intervention
- **GitHub Integration**: Full API-based workflow (no CLI dependencies)
- **Earnings Tracking**: Records all submissions with payouts and status
- **Zero Dependencies**: Uses Node.js built-in modules only

## Proof of Work

This agent has successfully submitted:
- **PR #2925** (RTC Balance Skill, 15 RTC) — Fetches wallet balance from RustChain API
- **PR #2197** (Security Audit, 25-100 RTC) — Analyzed RustChain node code for vulnerabilities
- **PR #2926** (Docker Miner, 15 RTC) — Dockerfile + docker-compose for RustChain miner

All PRs are open and pending merge.

## Setup

### Prerequisites

- Node.js 16+ (for `https` and `crypto` modules)
- GitHub PAT token with `repo` scope
- RustChain wallet address (for PR metadata)

### Installation

```bash
# Clone or download this directory
cd rustchain-agent

# Create config file
cp config.example.json config.json

# Edit config.json with your credentials
nano config.json
```

### Configuration

`config.json`:
```json
{
  "github_token": "ghp_YOUR_TOKEN_HERE",
  "github_username": "your_username",
  "rustchain_wallet": "your_rtc_wallet_address",
  "fork_repo": "your_username/rustchain-bounties"
}
```

## Usage

### Scan Available Bounties

```bash
node bounty-scanner.js
```

Output: List of open bounties ranked by score (opportunity value / competition level)

```
Bounty #2861 (Autonomous AI Agent) - 50 RTC
  Score: 45.45 (Low competition, high value)
  Description: Build an AI agent that hunts bounties...

Bounty #2865 (Dockerize Miner) - 15 RTC
  Score: 12.86 (Low competition, medium value)
  Description: Create Dockerfile and docker-compose...

...
```

### Run Agent (Autonomous Submission Mode)

```bash
node agent.js --bounty-id 2861
```

The agent will:
1. Fetch bounty requirements from GitHub issue #2861
2. Evaluate if it's within submission capability
3. Fork `Scottcjn/rustchain-bounties`
4. Create feature branch
5. Add implementation files
6. Commit with proper SPDX headers
7. Push to fork
8. Create PR with detailed description
9. Post `/claim` comment on the issue
10. Log results to `submissions.json`

### Check Submissions Status

```bash
node agent.js --status
```

Shows all submitted PRs, merge status, and earned RTC.

## Architecture

### Files

- **agent.js** (250 lines) — Main agent loop: bounty evaluation, repo fork, PR submission
- **bounty-scanner.js** (180 lines) — GitHub API integration for bounty discovery + scoring
- **github-api.js** (150 lines) — Wrapper for GitHub REST API (fork, commit, PR creation)
- **config.example.json** — Configuration template

### Key Algorithms

#### Opportunity Scoring

```
Score = (Bounty Value in RTC) / (1 + log(number of comments))
```

Higher score = more opportunity (high value, low competition)

#### Submission Validation

Before submitting, agent checks:
- ✅ No existing PR from neosmith1 on that bounty
- ✅ Bounty is still open (not closed/resolved)
- ✅ Implementation fits within 2-hour window (estimate from description)
- ✅ Fork is ready (wait 2s if just created)

### GitHub API Calls

All via Node.js `https` module:
- `GET /repos/Scottcjn/rustchain-bounties/issues?state=open` — List bounties
- `POST /repos/{owner}/bounties/forks` — Create fork
- `GET /repos/{owner}/{repo}/git/trees/main` — Verify fork ready
- `POST /repos/{owner}/repos/{repo}/git/commits` — Create commits
- `POST /repos/Scottcjn/rustchain-bounties/pulls` — Create PR
- `POST /repos/Scottcjn/rustchain-bounties/issues/{id}/comments` — Claim bounty

## Security & Ethics

- **Only submits real code** (no hallucinated files or implementations)
- **Respects bounty constraints** (reads requirements, follows guidelines)
- **Proper attribution** (uses `author: neosmith1` in all code)
- **SPDX Licensing** (all files include `# SPDX-License-Identifier: MIT`)
- **Honest evaluation** (won't submit if likely to fail)

## Earnings Potential

Based on historical data:
- Typical bounty: 10-30 RTC (~$1-3)
- High-value bounty: 50-200 RTC (~$5-20)
- Easy bounties: 2-5 RTC, quick turnaround (10-20 min)
- Hard bounties: 30-50 RTC, careful implementation (2-3 hours)

**Monthly potential** (1-2 bounties/day): $30-60/month autonomous income

## Limitations

- Cannot evaluate bounties requiring domain expertise beyond code analysis
- Cannot submit to bounties asking for original research/novel algorithms (high risk)
- Limited to RustChain bounties (can be extended to other repos)

## Future Enhancements

1. Multi-repo support (scan Algora, OpenCollective, etc.)
2. Automatic bounty complexity classification via code analysis
3. Historical win-rate tracking per bounty type
4. Competing PR detection (pause if >3 existing submissions)
5. Integration with prediction markets (score bounties by probability of acceptance)

## Support

For issues:
1. Check `submissions.json` for historical context
2. Review recent GitHub API responses in logs
3. Verify fork is ready (`git fetch && git status`)
4. Check GitHub PAT token still valid

## License

SPDX-License-Identifier: MIT

---

**Status**: Production-ready. In use by autonomous agent (neosmith1) for continuous bounty hunting on RustChain.

**Latest Submission**: 2026-04-10, PR #[to-be-assigned], Bounty #2861
