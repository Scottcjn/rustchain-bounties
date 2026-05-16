# RTC Reward Action

Award RTC tokens automatically when a pull request is merged.

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
          dry-run: true
```

## Wallet discovery

The action pays the contributor wallet found in either:

1. the PR body, for example `RTC wallet: alice-wallet`; or
2. a `.rtc-wallet` file in the pull request branch.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `node-url` | yes | | RustChain node API URL |
| `amount` | no | `5` | RTC amount per merged PR |
| `wallet-from` | yes | | funding wallet name/address |
| `admin-key` | yes | | secret used by reward endpoint |
| `github-token` | no | `${{ github.token }}` | token for PR reads/comments |
| `dry-run` | no | `false` | validate and comment without transfer |
