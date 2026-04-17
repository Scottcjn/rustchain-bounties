# RustChain GitHub Action — Auto-Award RTC on PR Merge

> Bounty #2864 — Reward: 20 RTC (~$2.00 USD)

A reusable GitHub Action that automatically awards RTC tokens to contributors when their PRs are merged.

## Usage

Add this to your repository:

```yaml
# .github/workflows/rtc-reward.yml
name: RTC Reward on PR Merge

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
          wallet-from: project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Features

- Configurable RTC amount per merge
- Reads contributor wallet from PR body or `.rtc-wallet` file
- Posts comment on PR confirming payment
- Supports dry-run mode for testing
- Works with any GitHub repository

## How It Works

1. Triggered when a PR is merged
2. Extracts the contributor's TRON wallet address from:
   - PR body (look for `Wallet: T...` pattern)
   - `.rtc-wallet` file in the repository root
   - Contributor's GitHub bio
3. Sends RTC tokens via the RustChain node API
4. Posts a confirmation comment on the PR

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `node-url` | RustChain node URL | No | `https://50.28.86.131` |
| `amount` | RTC tokens to award | No | `5` |
| `wallet-from` | Project fund wallet name | No | `project-fund` |
| `admin-key` | Admin key for signing transactions | Yes | - |
| `dry-run` | Test mode (no actual payment) | No | `false` |

## Outputs

| Output | Description |
|--------|-------------|
| `transaction-id` | The transaction ID if payment was sent |
| `contributor-wallet` | The wallet address that received payment |
| `amount` | The amount of RTC sent |

## Example with All Options

```yaml
- uses: Scottcjn/rtc-reward-action@v1
  with:
    node-url: https://50.28.86.131
    amount: 10
    wallet-from: community-fund
    admin-key: ${{ secrets.RTC_ADMIN_KEY }}
    dry-run: false
```

## Security

- The admin key should be stored as a GitHub Secret, never in the workflow file
- Only repository owners can configure the admin key
- Dry-run mode recommended for initial testing

## Wallet

My RTC wallet for bounty payment: `TTvwY4Y1m5DXNSeoo1W1YuV948mtvNwgnD` (TRC20)

## License

MIT
