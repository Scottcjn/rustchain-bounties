# RustChain RTC Reward Action

A GitHub Action that automatically awards **RTC tokens** to contributors when their pull request is merged.

Any open-source project can add one YAML file and start rewarding contributors with crypto — zero backend required.

## Quick Start

```yaml
# .github/workflows/rtc-reward.yml
name: Award RTC on PR Merge

on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: Scottcjn/rustchain-bounties/github-action@main
        with:
          amount: 5
          wallet-from: my-project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## How It Finds the Recipient Wallet

The action searches for the recipient wallet in this order:

1. **PR body** — scans for a line matching `Wallet: <wallet-id>` (customizable regex)
2. **`.rtc-wallet` file** — reads from the repo root
3. **GitHub username** — falls back to the PR author's GitHub login

### PR Body Example

Contributors add their wallet to the PR description:

```
## Changes

Added feature X and fixed bug Y.

Wallet: my-wallet-name
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `node-url` | No | `https://50.28.86.131` | RustChain node URL |
| `amount` | No | `5` | RTC to award per merged PR |
| `wallet-from` | **Yes** | — | Sender wallet ID |
| `admin-key` | **Yes** | — | Admin key (store in Secrets) |
| `wallet-pattern` | No | `wallet[\s:]+(\S+)` | Regex to find recipient wallet in PR body |
| `dry-run` | No | `false` | Simulate without real transfer |
| `comment-on-pr` | No | `true` | Post confirmation comment |
| `require-label` | No | _(any PR)_ | Only award if PR has this label |

## Outputs

| Output | Description |
|--------|-------------|
| `awarded` | `"true"` if RTC was sent |
| `recipient-wallet` | Wallet that received the RTC |
| `tx-id` | RustChain transaction ID |
| `amount-rtc` | Amount awarded |

## Features

- **Zero npm dependencies** — pure Node.js built-ins, fast cold start
- **Dry-run mode** — test your setup before going live
- **Label filtering** — award only bounty-labelled PRs
- **Auto-fallback** — GitHub username if no wallet found
- **PR comments** — automatic confirmation with transaction ID
- **Self-signed cert support** — works with the default RustChain node

## Security

- Store `admin-key` in **GitHub Secrets**, never in workflow files
- The action only posts comments if `GITHUB_TOKEN` is provided
- TLS verification can be enforced by removing `rejectUnauthorized: false`

## Bounty

Built for RustChain bounty [#2864](https://github.com/Scottcjn/rustchain-bounties/issues/2864).

**Wallet:** 暖暖
