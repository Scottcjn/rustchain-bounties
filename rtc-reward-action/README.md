# RTC Reward Action

Automatically award RTC tokens to contributors when their PR is merged.

## Usage

Add this to your workflow:

`yaml
name: RTC Reward

on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: Scottcjn/rustchain-bounties/rtc-reward-action@v1
        with:
          node-url: https://50.28.86.131
          amount: 5
          wallet-from: your-project-fund-wallet
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
`

## Setup

1. Go to your repository Settings > Secrets
2. Add RTC_ADMIN_KEY with your RTC node admin key
3. Add the workflow file to .github/workflows/rtc-reward.yml

## Contributor Wallet

Contributors should add their wallet address in the PR body:

`
Wallet: your-wallet-address
`

Or simply include the address anywhere in the PR description.

## Dry Run Mode

For testing without sending real transactions:

`yaml
with:
  dry-run: true
`

## License

MIT