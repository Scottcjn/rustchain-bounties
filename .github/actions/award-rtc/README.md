# Auto-Award RTC on PR Merge

GitHub Action that automatically awards RTC tokens to contributors when their PR is merged.

## Usage

Add to `.github/workflows/award-rtc.yml`:

```yaml
name: Award RTC on PR Merge
on:
  pull_request_target:
    types: [closed]

jobs:
  award-rtc:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Award RTC
        uses: Scottcjn/rustchain-bounties/.github/actions/award-rtc@main
        with:
          reward_rtc: '''10'''
        env:
          RUSTCHAIN_ADMIN_KEY: ${{ secrets.RUSTCHAIN_ADMIN_KEY }}
```

## Required Secrets

| Secret | Description |
|--------|-------------|
| `RUSTCHAIN_ADMIN_KEY` | Admin key for the RustChain node |

## Inputs

| Input | Default | Description |
|-------|---------|-------------|
| `reward_rtc` | `10` | Amount of RTC to award per merged PR |
| `node_url` | `https://50.28.86.131` | RustChain node URL |

## Bounty

- **Issue**: [#2864](https://github.com/Scottcjn/rustchain-bounties/issues/2864)
- **Reward**: 20 RTC (~.00 USD)
- **Author**: 大鹏 (YPC0813)
