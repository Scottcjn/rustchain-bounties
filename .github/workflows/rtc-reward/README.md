# RTC Reward GitHub Action

Automatically award RTC tokens when pull requests are merged.

## Usage

```yaml
name: RTC Reward

on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: Scottcjn/rtc-reward-action@v1
        with:
          node-url: https://50.28.86.131
          amount: 5
          wallet-from: your-project-wallet
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Inputs

| Input | Description | Required |
|-------|-------------|----------|
| node-url | RustChain node URL | Yes |
| amount | RTC amount per merge | Yes |
| wallet-from | Project wallet name | Yes |
| admin-key | Admin private key | Yes |
| dry-run | Test mode (no real transfer) | No |

## Features

- ✅ Configurable RTC amount per merge
- ✅ Reads contributor wallet from PR body
- ✅ Posts confirmation comment on PR
- ✅ Supports dry-run mode for testing
- ✅ Published to GitHub Marketplace

## Example

More details at: https://github.com/Scottcjn/rustchain-bounties/issues/2864
