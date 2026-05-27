# RTC Reward Action

GitHub Action that auto-awards RTC tokens when a PR is merged.

## How It Works

1. Triggers on `pull_request` closed event
2. Checks if PR was actually merged
3. Extracts contributor wallet from PR body or `.rtc-wallet` file
4. Calls RustChain API to transfer RTC tokens
5. Posts a comment confirming the payment

## Inputs

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `node-url` | Yes | - | RustChain node URL |
| `amount` | Yes | - | Amount of RTC tokens to reward |
| `wallet-from` | Yes | - | Source wallet address |
| `admin-key` | Yes | - | Admin key for signing transfers |
| `wallet-field` | No | `wallet` | Field name in PR body |
| `dry-run` | No | `false` | Simulate without sending tokens |

## Outputs

| Output | Description |
|--------|-------------|
| `recipient` | Wallet address that received the reward |
| `tx-status` | Transaction status (sent, dry-run, skipped) |
| `amount` | Amount awarded |

## Setup

### 1. Add Secrets

Go to repo Settings > Secrets:
- `RTC_ADMIN_KEY` - Admin key for RustChain
- `RTC_WALLET_FROM` - Your funding wallet address

### 2. Create Workflow

`.github/workflows/reward.yml`:
```yaml
name: RTC Reward

on:
  pull_request:
    types: [closed]

jobs:
  reward:
    runs-on: ubuntu-latest
    if: github.event.pull_request.merged == true
    steps:
      - uses: actions/checkout@v4

      - name: Award RTC
        uses: your-org/rtc-reward-action@v1
        with:
          node-url: 'https://rustchain.org'
          amount: '100'
          wallet-from: ${{ secrets.RTC_WALLET_FROM }}
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 3. PR Body Format

Contributors add wallet address to PR body:
```markdown
## Description
Fixed the bug in auth module

wallet: 0x1234567890abcdef1234567890abcdef12345678
```

Or create `.rtc-wallet` file in repo root:
```
0x1234567890abcdef1234567890abcdef12345678
```

## Dry Run Mode

Test without sending tokens:
```yaml
- uses: your-org/rtc-reward-action@v1
  with:
    dry-run: 'true'
    # ... other inputs
```

## Development

```bash
npm install
npm test
```

## License

MIT
