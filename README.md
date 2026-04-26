// File: README.md
# RTC Reward Action

A GitHub Action that automatically awards RTC tokens when a pull request is merged.

## Usage

Create a workflow file (e.g., `.github/workflows/rtc-reward.yml`):

```yaml
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

## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `node-url` | RustChain node URL | No | `https://50.28.86.131` |
| `amount` | Amount of RTC to award per merge | No | `5` |
| `wallet-from` | Sender wallet name | Yes | - |
| `admin-key` | Private key for sender wallet (secret) | Yes | - |
| `dry-run` | Enable dry-run mode (no actual transaction) | No | `false` |

## How it works

1. When a PR is merged, the action triggers.
2. It attempts to find the contributor's wallet in this order:
   - From the PR body (look for `Wallet: <wallet_address>`)
   - From a `.rtc-wallet` file in the PR's head commit
3. If a wallet is found, it sends the specified amount of RTC from the `wallet-from` to the contributor's wallet.
4. It posts a comment on the PR confirming the transaction (or dry-run notice).

## Example PR Body

```
Thanks for reviewing my PR!

Wallet: rtc1qdgff5l5q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q
```

## Example .rtc-wallet File

```
rtc1qdgff5l5q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q55q
```

## License

MIT