# RustChain Auto-Hunter

An autonomous agent that scans GitHub for open RustChain bounties, evaluates which ones it can handle, implements the fix, and submits the PR automatically with a bounty claim.

## Setup

1. Clone this repository.
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Export your API keys and configuration:
   ```bash
   export GITHUB_TOKEN="<your-github-token>"
   export ANTHROPIC_API_KEY="<your-anthropic-key>"
   export RTC_WALLET="<your-rtc-wallet-id>"
   ```
4. Run the script:
   ```bash
   python3 hunter.py
   ```

## How It Works

1. Queries the GitHub API for issues in `Scottcjn/rustchain-bounties` that have the `bounty` label, are `open`, and unassigned.
2. Analyzes the subset using Claude 3 Opus to select the most approachable tasks.
3. Clones/Forks the repository locally.
4. Generates a Python automation script using Claude to modify the local directory to fix the issue.
5. Executes the fix locally, commits the changes, and pushes a PR via the Github CLI.
6. The PR includes a pre-formatted section to automatically claim the bounty reward with the configured RTC wallet address.
