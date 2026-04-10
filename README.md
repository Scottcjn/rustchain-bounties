# RTC Reward GitHub Action

Automatically award RTC tokens when PRs are merged.

## Features
- Configurable RTC amount
- Reads wallet from PR body
- Dry-run mode

## Usage
```yaml
- uses: Scottcjn/rtc-reward-action@v1
  with:
    node-url: https://50.28.86.131
    amount: 5
    wallet-from: bounty-fund
    admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```
