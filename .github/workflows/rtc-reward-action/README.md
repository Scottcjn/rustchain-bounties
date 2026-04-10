# RTC Reward GitHub Action

Automatically award RTC tokens when PRs are merged in any GitHub repository.

## 🚀 Features

- ✅ Automatic RTC token awards on PR merge
- ✅ Configurable reward amount per merge
- ✅ Reads contributor wallet from PR body or uses GitHub username
- ✅ Posts confirmation comment on PR
- ✅ Dry-run mode for testing
- ✅ GitHub Marketplace ready

## 📖 Usage

Add this workflow to your repository:

```yaml
name: Auto Reward RTC

on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: 'Award RTC'
        uses: your-username/rtc-reward-action@v1
        with:
          node-url: https://50.28.86.131
          amount: 5
          wallet-from: bounty-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## ⚙️ Configuration

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| node-url | Yes | - | RustChain node URL |
| amount | Yes | 5 | RTC amount per merge |
| wallet-from | Yes | - | Project wallet name |
| admin-key | Yes | - | Admin private key |
| dry-run | No | false | Test mode |
| comment-message | No | - | Custom reward message |

## 🔐 Security

- Store admin key in GitHub Secrets
- Use separate wallet for rewards
- Enable dry-run mode for testing
