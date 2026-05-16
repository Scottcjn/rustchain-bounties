# rtc-reward-action

Automatically awards **RTC tokens** when a pull request is merged. Any open source project can add this to reward contributors with cryptocurrency — zero backend required.

---

## Usage

### Add to any repo with one YAML file

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
          node-url: https://rustchain.org
          amount: 5
          wallet-from: your-project-fund
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

### Settings

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `node-url` | No | `https://rustchain.org` | RustChain node URL |
| `amount` | No | `5` | RTC per merged PR |
| `wallet-from` | **Yes** | — | Source wallet name |
| `admin-key` | **Yes** | — | Admin key (store in GitHub Secret) |
| `dry-run` | No | `false` | Test without sending RTC |
| `min-pr-body-length` | No | `10` | Minimum PR body chars to extract wallet |

---

## How It Works

1. Triggers when any PR is **merged**
2. Parses the PR body for a **wallet name** (supports EVM addresses, wallet names, `wallet_name:` patterns)
3. Calls RustChain `/wallet/send` API to transfer RTC
4. Posts a **confirmation comment** on the PR

---

## Wallet Extraction

The action looks for the contributor's wallet in the PR body in this order:

1. **EVM address** — `0x...` (40 hex chars)
2. **Backtick-wrapped** — `` `wallet_name` ``
3. **Keyed pattern** — `wallet: name` or `rtc_wallet: name`
4. **Plain wallet name** — lowercase with underscores

Example valid PR body:
```
## My Contribution

Implemented the new feature.

**Wallet:** founder_community
```

---

## Publish to GitHub Marketplace

1. Create a **public repo** named `rtc-reward-action`
2. Add this action to `.github/actions/rtc-reward-action/`
3. Tag a release: `git tag v1 && git push --tags`
4. Go to **GitHub Marketplace** → **Publish** → select your repo
5. Users can now reference it as `owner/rtc-reward-action@v1`

---

## Security

- **Never** commit `admin-key` — use `${{ secrets.RTC_ADMIN_KEY }}`
- Use `dry-run: true` to test before enabling real payments
- The action only triggers on **merged** PRs, not opened/closed (unmerged)

---

## License

MIT
