# RTC Balance Query — GitHub Action

> **Read-only** GitHub Action that queries RustChain (RTC) wallet balance and posts the result as a PR comment.  
> ⛔ **No transfer / send functionality.** This action will never move funds.

## Features

- 🔍 Queries wallet balance via RustChain API (`GET /wallet/balance?miner_id=WALLET`)
- 💬 Posts a formatted comment on the PR with balance info
- 📁 Reads wallet address from action input, `.rtc-wallet` file, or PR body
- 🏷️ Supports **dry-run** mode (log only, no comment)
- ⚙️ Fully configurable via `action.yml` inputs/outputs

## Usage

```yaml
name: RTC Balance Check

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-balance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Query RTC Balance
        uses: legendhy/rustchain-bounties/rtc-github-action@main
        with:
          wallet-address: ''           # Optional: override auto-detection
          query-amount: '20'           # Informational display amount
          api-base-url: 'https://rustchain.org'
          github-token: ${{ secrets.GITHUB_TOKEN }}
          dry-run: 'false'             # Set true to skip posting comment
```

## Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `wallet-address` | Wallet to query (overrides auto-detection) | No | `''` |
| `query-amount` | Informational RTC amount to display | No | `'20'` |
| `api-base-url` | RustChain API base URL | No | `'https://rustchain.org'` |
| `github-token` | Token for posting PR comments | Yes | — |
| `dry-run` | Log results without posting comment | No | `'false'` |

## Outputs

| Output | Description |
|---|---|
| `balance` | Wallet balance from RustChain API |
| `wallet-address` | The wallet address that was queried |
| `status` | `success` or `error` |

## Wallet Address Resolution (priority order)

1. **`wallet-address` input** — explicit parameter
2. **`.rtc-wallet` file** — single-line file in repo root
3. **PR body** — line matching `RTC Wallet: <address>` or `Wallet: <address>`

## Security

This action is **strictly read-only**. It:
- ✅ Only calls `GET /wallet/balance`
- ❌ Never calls any wallet/send/transfer API
- ❌ Never possesses private keys or seed phrases

## License

MIT
