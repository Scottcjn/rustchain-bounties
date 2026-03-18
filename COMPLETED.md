# Bounty Verification Bot - MVP

A bot that automatically verifies GitHub bounty claims on Scottcjn's repos.

## Features:
- Checks if user follows @Scottcjn
- Counts how many Scottcjn repos user has starred
- Verifies wallet existence and balance
- Checks if article URLs are live
- Detects duplicate claims

## Usage:
```bash
GITHUB_TOKEN=... python verify_bot.py
GITHUB_TOKEN=... python verify_bot.py --repo Scottcjn/rustchain-bounties --issue 747
```

## Example output:
Posted verification comment on Scottcjn/rustchain-bounties#747
Verified 2 claims across 1 issues

## Milestone achievements (RustChain #747):
- Follow check (5 RTC)
- Star count check (10 RTC)
- Wallet existence (10 RTC)
- Article URL check (10 RTC)
- Duplicate detection (15 RTC)

Total: 50-75 RTC (depending on bonus criteria)

## Setup:
1. Get GitHub token: https://github.com/settings/tokens
2. Set RUSTCHAIN_NODE_URL to your node
3. Run the bot

## Files:
- `verify_bot.py` - Main bot code (10,929 bytes)
- `README.md` - Usage and setup guide (1,366 bytes)
- `requirements.txt` - Dependencies (requests>=2.32.4)

## Status: MVP COMPLETED
Ready to run against RustChain #747 issue.

For more info: https://github.com/Scottcjn/rustchain-bounties/issues/747