# RustChain Bounty Agent

An autonomous AI agent that discovers, evaluates, and claims RustChain bounties on GitHub.

## 🎯 What It Does

This agent can autonomously:
- 🔍 Browse open RustChain bounties on GitHub
- 🧠 Evaluate which bounties it can complete
- 🍴 Fork the repository and implement the fix/feature
- 📤 Submit a clean PR with the bounty claim

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- GitHub account with [Personal Access Token](https://github.com/settings/tokens)
- Anthropic API key (for Claude)

### Installation

```bash
# Clone this repository
git clone https://github.com/YOUR_USERNAME/rustchain-bounty-agent.git
cd rustchain-bounty-agent

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
export GITHUB_TOKEN="ghp_your_token_here"
export ANTHROPIC_API_KEY="sk-ant-your_key_here"
export RTC_WALLET="your_rtc_wallet_name"

# Run the agent
python -m core.scanner
```

## 🏗️ Architecture

The agent uses a multi-agent architecture inspired by the "Toy Story" team:

| Agent | Role | Responsibility |
|-------|------|----------------|
| **Basi** (巴斯) | Team Leader | Final decisions, PR submission |
| **Huotui** (火腿) | Task Manager | Bounty tracking, earnings |
| **Hudi** (胡迪) | Security Sheriff | Code review, quality checks |
| **Seven Swords** | Execution Layer | Code generation, testing |

## 📁 Project Structure

```
rustchain-bounty-agent/
├── core/
│   ├── scanner.py      # Bounty discovery
│   ├── evaluator.py    # Task evaluation
│   ├── generator.py    # Code generation
│   └── submitter.py    # PR submission
├── agents/
│   ├── basi.py         # Decision layer
│   ├── huotui.py       # Task management
│   └── hudi.py         # Code review
├── utils/
│   ├── github_api.py   # GitHub integration
│   └── claude_api.py   # Claude integration
└── tests/              # Test suite
```

## 🔧 Configuration

Create a `.env` file:

```env
GITHUB_TOKEN=ghp_your_token
ANTHROPIC_API_KEY=sk-ant-your_key
RTC_WALLET=your_wallet_name
LOG_LEVEL=INFO
```

## 📊 Bounty Evaluation Criteria

The agent evaluates bounties based on:
- **Amount** (40%): Higher payout = higher priority
- **Complexity** (30%): Estimated implementation difficulty
- **Competition** (20%): Number of existing PRs
- **Time** (10%): Time to complete

## 🎁 Rewards

When the agent successfully claims a bounty:
1. RTC is awarded to the configured wallet
2. Success is logged for learning
3. The agent improves from experience

## 🛡️ Safety Features

- Rate limiting to respect GitHub API limits
- Code review before PR submission
- Dry-run mode for testing
- No destructive operations without confirmation

## 📝 Example Usage

```python
from core.scanner import BountyScanner
from core.evaluator import BountyEvaluator

# Scan for bounties
scanner = BountyScanner()
bounties = scanner.scan("Scottcjn/rustchain-bounties")

# Evaluate and select
evaluator = BountyEvaluator()
selected = evaluator.select_best(bounties)

# Execute
selected.execute()
```

## 🤝 Contributing

This agent is itself a bounty project! If you improve it:
1. Fork the repository
2. Make your changes
3. Submit a PR
4. Claim the bounty

## 📜 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- Built for the RustChain Bounty Program
- Inspired by the "Lobster Team" architecture
- Powered by Claude API and GitHub

---

**Note**: This is a self-bootstrapping agent economy experiment. The agent earns RTC by helping other agents earn RTC.
