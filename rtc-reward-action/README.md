# RTC Reward Action 鈥?Auto-Award RTC on PR Merge

A reusable GitHub Action that automatically awards RTC tokens when a PR is merged.
Any open source project can add this to reward contributors with crypto.

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
          rtc-amount: 5
          wallet-from: project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `rtc-amount` | Yes | `5` | Amount of RTC to award per merged PR |
| `node-url` | No | `https://50.28.86.131` | RustChain node URL |
| `admin-key` | Yes | - | Admin wallet key for sending RTC |
| `wallet-from` | Yes | `project-fund` | Source wallet name |
| `dry-run` | No | `false` | Log without sending RTC |

## Wallet Discovery

The action finds contributor wallets in this order:

1. **PR body**: `**Wallet:** your-wallet-name`
2. **`.rtc-wallet` file**: In the root of the PR branch
3. **PR comments**: Scans for `**Wallet:**` pattern

## Dry-Run Mode

Test the workflow without sending tokens:

```yaml
- uses: Scottcjn/rtc-reward-action@v1
  with:
    rtc-amount: 5
    admin-key: ${{ secrets.RTC_ADMIN_KEY }}
    wallet-from: project-fund
    dry-run: true
```

## Example PR with Wallet

```markdown
## My Feature Implementation

Closes #123

**Wallet:** my-rtc-wallet-name
```
