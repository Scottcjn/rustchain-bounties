# RTC Reward Action

Automatically award RTC tokens when a PR is merged. Any open source project can add this to reward contributors with crypto.

## Usage

```yaml
name: RTC Rewards
on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: chenzhizhuan/rtc-reward-action@v1
        with:
          node-url: http://50.28.86.153:8099
          amount: 5
          wallet-from: your-project-wallet
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Features

- **Configurable RTC amount** - Set reward per merge
- **Wallet extraction** - Reads contributor wallet from PR body
- **PR Comment** - Posts reward confirmation on the PR
- **Dry-run mode** - Test without actual transactions

## Configuration

| Input | Description | Default |
|-------|-------------|---------|
| `node-url` | RustChain node URL | `http://50.28.86.153:8099` |
| `amount` | RTC to award per PR | `5` |
| `wallet-from` | Source wallet ID | - |
| `admin-key` | Admin key for transactions | - |
| `dry-run` | Test without transactions | `false` |

## Contributor Setup

Contributors include their RTC wallet in the PR body:

```
## RTC Wallet
wallet: my-rtc-wallet
```

Or any format containing `wallet: <id>`.

## Example

```yaml
on:
  pull_request:
    types: [closed]

jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: chenzhizhuan/rtc-reward-action@v1
        with:
          amount: 10
          wallet-from: project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## License

MIT
