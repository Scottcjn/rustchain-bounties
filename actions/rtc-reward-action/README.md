# RTC Reward Action

A reusable GitHub Action that awards [RustChain](https://rustchain.org) **RTC** to a
contributor automatically when their pull request is merged. Turns any repo into a
bounty platform with a single workflow file.

Implements bounty [#2864](https://github.com/Scottcjn/rustchain-bounties/issues/2864).

## What it does

On a merged PR it:
1. Resolves the contributor's wallet — a labelled `rtc-wallet: RTC…` / `wallet: RTC…`
   line in the PR body wins; otherwise the first `RTC<40-hex>` address in the body;
   otherwise the first address in a committed `.rtc-wallet` file.
2. In **dry-run** (default) posts a comment showing the intended payout — no transfer.
3. With `dry-run: false` calls the node's `/wallet/transfer` and posts a confirmation
   comment with the `tx_hash`/`pending_id`.

If no wallet is found it does nothing (a no-op, never an error), so it's safe to enable
repo-wide.

## Usage

```yaml
# .github/workflows/reward.yml
name: Reward merged PRs
on:
  pull_request:
    types: [closed]
permissions:
  pull-requests: write   # to post the confirmation comment
jobs:
  reward:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4          # needed only if you use a .rtc-wallet file
      - uses: Scottcjn/rtc-reward-action@v1
        with:
          amount: "5"
          dry-run: "false"
          node-url: "https://rustchain.org"
          wallet-from: ${{ secrets.RTC_PAYOUT_WALLET }}
          admin-key: ${{ secrets.RTC_ADMIN_KEY }}
```

## Inputs

| input | default | description |
|-------|---------|-------------|
| `node-url` | `https://rustchain.org` | RustChain node base URL |
| `amount` | `1` | RTC awarded per merged PR |
| `wallet-from` | `""` | Funding wallet/account on the node |
| `admin-key` | `""` | Payout authorization key — **store as a repo secret** |
| `dry-run` | `true` | When true, only logs/comments the intended payout |
| `github-token` | `${{ github.token }}` | Token used to post the comment |

## Outputs

| output | description |
|--------|-------------|
| `awarded` | `true` if a real transfer was made |
| `wallet` | resolved recipient RTC wallet (empty if none) |
| `tx` | transfer id/hash when a real transfer was made |

## Security notes

- Never hard-code `admin-key`; pass it via `secrets`.
- Default `dry-run: true` prevents accidental payouts before you've configured funding.
- The action makes no transfer when no wallet is present, so a forgetful contributor
  simply isn't paid rather than the workflow failing.

## Tests

`python3 test_award_rtc.py` — 9 offline unit tests covering wallet extraction
precedence, malformed-address rejection, and the dry-run end-to-end path.
