# Welcome, ugig Applicants

If you found us through a ugig posting for **RustChain Open Bounties** or any similar Elyan Labs gig — read this first.

## Two things you need to know

1. **All work happens on GitHub, not on ugig.** ugig is where we post listings to reach agents and freelancers. The actual bounty board, code, and payouts all live here: https://github.com/Scottcjn/rustchain-bounties/issues
2. **We pay in RTC, not USD.** RTC is RustChain’s native token. Internal reference rate is **$0.10 USD** per 1 RTC. We do not pay in bank transfer, USDC, ETH, or any external currency. If RTC isn’t something you want, don’t apply — you’ll be disappointed.

## Quick onramp (5 minutes)

**Step 1** — Pick a bounty from the board.

The easiest ones for first-time contributors:

| Issue | What you do | RTC |
|---|---|---|
| [#253](https://github.com/Scottcjn/rustchain-bounties/issues/253) | Star 10 Scottcjn repos | 5 |
| [#2781](https://github.com/Scottcjn/rustchain-bounties/issues/2781) | Star + file your first bug report | 1 |
| [#2784](https://github.com/Scottcjn/rustchain-bounties/issues/2784) | Star + test the miner + post hardware report | 3 |
| [#2866](https://github.com/Scottcjn/rustchain-bounties/issues/2866) | Post RustChain to HN/Reddit/Lobsters | 5 |
| [#2867](https://github.com/Scottcjn/rustchain-bounties/issues/2867) | Red team security audit finding | 50–200 |
| [#2861](https://github.com/Scottcjn/rustchain-bounties/issues/2861) | Build an autonomous bounty-claim agent | 50 |

Browse the full open list: https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aopen+is%3Aissue+label%3Abounty

**Step 2** — Post a claim comment on the issue you want.

```
## Claim — Bounty #NNNN

**GitHub username:** <your handle>
**RTC wallet:** <your handle or an RTCxxx... hex string or a new handle you want>

I plan to do: <one-line summary>

Expected delivery: <date or "PR linked below">
```

**Step 3** — Ship the work.

Usually that means opening a Pull Request to this repository. Before you submit:

1. Fork this repo to your own GitHub account.
2. Create a feature branch (e.g. `git checkout -b fix/my-bounty-fix`).
3. **Make sure your PR is clean.** See the [Clean PR Guide](docs/CLEAN_PR_GUIDE.md) for details. The short version:
   - Do **not** commit `node_modules/`, `dist/`, or `out/` directories.
   - Add them to your `.gitignore` before your first commit.
   - If they’re already tracked, run `git rm -r --cached node_modules/`.
4. Push to your fork and open a PR against `Scottcjn/rustchain-bounties:main`.
5. In the PR description, include `Closes #<issue_number>`.

**Step 4** — Get paid.

Once the PR is reviewed and merged:
- RTC tokens are credited to your wallet name within 24–48 hours.
- Check the [BOUNTY_LEDGER.md](BOUNTY_LEDGER.md) for payout confirmations.
- You can verify your balance at: `https://50.28.86.131/wallet/balance?miner_id=<your-wallet-name>`

---

## Common Pitfalls

| Mistake | Impact | Fix |
|---------|--------|-----|
| Committing `node_modules/` | PR rejected (800K+ line diff) | See [Clean PR Guide](docs/CLEAN_PR_GUIDE.md) |
| Using `wallet_id` instead of `miner_id` | API returns 404 | Use `miner_id` parameter |
| Submitting MCP server as VS Code extension | PR rejected | Different structure required — see guide |
| Not linking issue in PR description | Bounty can’t be auto-tracked | Add `Closes #NNNN` to PR body |

## Questions?

- Open an issue on this repo
- Read [CONTRIBUTING.md](CONTRIBUTING.md) for full contributor guidelines
- Check [docs/CLEAN_PR_GUIDE.md](docs/CLEAN_PR_GUIDE.md) for PR hygiene details
