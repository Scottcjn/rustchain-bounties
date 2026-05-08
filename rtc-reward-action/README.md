# RTC Reward GitHub Action

A GitHub Action that automatically awards RTC tokens when PRs are merged.

## Usage

```yaml
# .github/workflows/rtc-reward.yml
on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: AKIB473/rtc-reward-action@v1
        with:
          node-url: https://50.28.86.131
          amount: 5
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `node-url` | No | `https://50.28.86.131` | RustChain node URL |
| `amount` | No | `5` | RTC amount to award |
| `wallet-from` | No | `project-fund` | Source wallet name |
| `admin-key` | Yes | - | Admin key for RTC node |
| `dry-run` | No | `false` | Test mode without payment |

## How It Works

1. Triggers on PR merge
2. Extracts wallet from PR body (pattern: `RTC: walletname`) or `.rtc-wallet` file
3. Awards RTC to contributor's wallet
4. Posts confirmation comment on PR

## Wallet Discovery

The action looks for the wallet in this order:
1. PR body pattern: `RTC: your-wallet-name`
2. `.rtc-wallet` file in repository root

## Dry Run Mode

Set `dry-run: true` to test without actual payment.

## Publishing to GitHub Marketplace

1. Create release tag: `v1`
2. Action auto-publishes to marketplace

## Wallet Address

`miner-20260508-rustchain`