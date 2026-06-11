# RTC Reward GitHub Action

Automatically award RTC tokens to contributors when their pull requests are merged.

## Features

- ✅ Configurable RTC amount per merge
- ✅ Reads contributor wallet from PR body or `.rtc-wallet` file
- ✅ Posts confirmation comment on PR
- ✅ Dry-run mode for testing
- ✅ Ready for GitHub Marketplace

## Usage

Create `.github/workflows/rtc-reward.yml` in your repository:

```yaml
name: RTC Reward on PR Merge

on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: foreverzyf/rtc-reward-action@v1
        with:
          node-url: https://50.28.86.131
          amount: 5
          wallet-from: project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `node-url` | Yes | `https://50.28.86.131` | RustChain node URL |
| `amount` | Yes | `5` | RTC amount to award |
| `wallet-from` | Yes | - | Source wallet for sending |
| `admin-key` | Yes | - | Admin private key (use GitHub Secret) |
| `dry-run` | No | `false` | Test mode (no transactions) |

## How Contributors Add Their Wallet

Contributors can add their RTC wallet in two ways:

1. **In PR description**: Include `RTC...` address anywhere in the PR body
2. **`.rtc-wallet` file**: Add a `.rtc-wallet` file to the repo root with their address

## Example PR Description

```markdown
## Changes
Fixed bug in validator...

## Wallet
My RTC wallet: RTCa1b2c3d4e5f6...
```

## License

MIT
