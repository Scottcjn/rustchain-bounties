# RTC GitHub Tip Bot

**Bounty Issue:** #1153  
**Reward:** 25-40 RTC

## Overview

A GitHub Action that enables RTC tipping directly in GitHub comments.

## How It Works

```
/tip @username 5 RTC Great PR!
```

Bot responds:
```
✅ Queued: 5 RTC → username
From: tipper | Memo: Great PR!
Status: Pending (confirms in 24h)
```

## Features

### Required (25 RTC)
- ✅ `/tip @user AMOUNT RTC [memo]` - Send tips
- ✅ Validates sender is repo maintainer
- ✅ Validates recipient has registered wallet
- ✅ Calls RustChain `/wallet/transfer` API
- ✅ Posts confirmation comment

### Bonus (40 RTC)
- `/balance` - Check your RTC balance
- `/leaderboard` - Top tippers this month
- `/register WALLET_NAME` - Register wallet
- Daily digest of tips

## Setup

### Option 1: GitHub Action (Recommended)

1. Copy `.github/workflows/tip-bot.yml` to your repo
2. Add these secrets:
   - `GITHUB_TOKEN` - Auto-generated
   - `NODE_URL` - RustChain node (e.g., `50.28.86.131`)
   - `ADMIN_WALLET` - Wallet for transfers
   - `ADMIN_KEY` - Admin key for API

### Option 2: Python Bot (Standalone)

See `tip-bot.py` for standalone version.

## Commands

| Command | Description |
|---------|-------------|
| `/tip @user 5 RTC Thanks!` | Tip 5 RTC |
| `/balance` | Check your balance |
| `/register mywallet` | Register wallet |

## Security

- Only repo maintainers can tip
- Rate limited: 1 tip/comment, 10 tips/hour
- Memo is required for audit trail

## License

MIT
