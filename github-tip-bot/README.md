# GitHub Tip Bot for RTC

A GitHub Action that enables tipping RTC to contributors directly in GitHub issues and PR comments.

## Features

- `/tip @user AMOUNT RTC [memo]` - Tip a contributor
- `/balance` - Check your RTC balance
- `/leaderboard` - Top tipped contributors this month
- `/register WALLET_NAME` - Register your wallet

## Setup

### 1. Create a GitHub App or Use This Action

This bot can be deployed as a GitHub Action using repository dispatch events.

### 2. Configure the Action

Add `.github/workflows/tip-bot.yml`:

```yaml
name: RTC Tip Bot
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  tip:
    runs-on: ubuntu-latest
    steps:
      - name: Handle tip commands
        uses: Scottcjn/rustchain-bounties/actions/tip-bot@main
        with:
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
          rpc-url: https://50.28.86.131
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Set Up Secrets

- `RTC_ADMIN_KEY` - Admin key for RTC transfers (contact bounty owner)
- `GITHUB_TOKEN` - Auto-provided by GitHub Actions

## Commands

| Command | Description |
|---------|-------------|
| `/tip @user 5 RTC Great work!` | Tip 5 RTC to user with memo |
| `/balance` | Check your RTC balance |
| `/leaderboard` | Show top tippees this month |
| `/register mywallet` | Register wallet name |

## Usage Example

```
/tip @contributor 10 RTC Thanks for the amazing PR!
```

Bot responds:
```
✅ Queued: 10 RTC → contributor-wallet
From: tipper-user | Memo: Thanks for the amazing PR!
Status: Pending (confirms in 24h)
```

## Rate Limits

- 1 tip per comment
- 10 tips per hour per user

## License

MIT
