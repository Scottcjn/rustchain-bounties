# RTC Reward Action

GitHub Action that automatically awards RTC tokens when a pull request is merged. Turns any GitHub repo into a bounty platform with one YAML file.

## Usage

```yaml
# .github/workflows/rtc-reward.yml
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
          wallet-from: project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## How Contributors Set Their Wallet

Contributors add their RTC wallet address in the PR body:

```
Wallet: RTC99e36a40635b8527979fd1c4e6280fdfa176e715
```

Or the repo maintainer places a `.rtc-wallet` file in the repo root.

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `node-url` | Yes | — | RustChain node API URL |
| `amount` | Yes | — | RTC to award per merged PR |
| `wallet-from` | Yes | — | Source wallet for rewards |
| `admin-key` | Yes | — | Admin key for signing |
| `dry-run` | No | `false` | Log actions without sending transactions |
| `wallet-pattern` | No | `RTC[0-9a-fA-F]{36,44}` | Regex to find wallet in PR body |
| `comment-template` | No | Built-in | Template for reward comment |

## Outputs

| Output | Description |
|--------|-------------|
| `wallet-found` | `true` or `false` |
| `wallet` | The detected wallet address |
| `amount` | RTC amount awarded |
| `pr-number` | PR that triggered the reward |
