# RTC Reward GitHub Action 🎁

> Automatically award RTC tokens to contributors when their PRs are merged

## Setup

### 1. Add Secrets

In your GitHub repo, go to **Settings → Secrets** and add:

| Secret | Description |
|--------|-------------|
| `RTC_ADMIN_KEY` | Admin key for your project's funding wallet |

### 2. Add Workflow

Create `.github/workflows/rtc-reward.yml`:

```yaml
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
          node-url: 'https://50.28.86.131'
          amount: '5'
          wallet-from: 'your-project-wallet'
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

### 3. Contributors: Add Your Wallet

In your PR body, add:

```
RTC wallet: your_wallet_name
```

## Configuration

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `node-url` | No | `https://50.28.86.131` | RustChain node |
| `amount` | No | `5` | RTC per merge |
| `wallet-from` | **Yes** | - | Project wallet |
| `admin-key` | **Yes** | - | Admin key (secret) |
| `dry-run` | No | `false` | Test without sending |
| `min-pr-size` | No | `1` | Min lines to qualify |

## Example

```yaml
- uses: Scottcjn/rtc-reward-action@v1
  with:
    node-url: 'https://50.28.86.131'
    amount: '10'
    wallet-from: 'open-source-fund'
    admin-key: ${{ secrets.RTC_ADMIN_KEY }}
    dry-run: 'false'
    min-pr-size: '10'
```

## How It Works

1. PR is merged → Action triggers
2. Extracts contributor's wallet from PR body
3. Validates PR size meets minimum
4. Transfers RTC from project wallet
5. Posts confirmation comment on PR

## Publishing to Marketplace

```bash
git tag v1.0.0
git push origin v1.0.0
```

Then submit to GitHub Marketplace.

## License

MIT
