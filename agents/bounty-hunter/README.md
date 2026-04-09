# RustChain Autonomous Bounty Hunter Agent

Self-bootstrapping agent that earns RTC by completing bounties.

## Setup
```bash
pip install -r requirements.txt
export GITHUB_TOKEN=your_token
python agent.py
```

## Workflow
1. Scan open RustChain bounties via GitHub API
2. Evaluate difficulty and feasibility  
3. Fork repo, implement solution
4. Submit clean PR with bounty claim
