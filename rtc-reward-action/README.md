# RTC Reward GitHub Action

Automatically award RTC tokens when PRs are merged.

## Features

- ✅ Configurable RTC amount
- ✅ Reads contributor wallet from PR body
- ✅ Posts confirmation comment
- ✅ Dry-run mode support

## Usage

```yaml
name: Auto Reward

on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: your-username/rtc-reward-action@v1
        with:
          node-url: https://50.28.86.131
          amount: 5
          wallet-from: project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Configuration

| Input | Required | Description |
|-------|----------|-------------|
| node-url | Yes | RustChain node URL |
| amount | Yes | RTC amount per merge |
| wallet-from | Yes | Project wallet |
| admin-key | Yes | Admin key |
| dry-run | No | Test mode |
