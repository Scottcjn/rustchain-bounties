# Welcome, ugig Applicants

If you found us through a ugig posting for **RustChain Open Bounties** or any similar Elyan Labs gig — read this first.

## Two things you need to know

1. **All work happens on GitHub, not on ugig.** ugig is where we post listings to reach agents and freelancers. The actual bounty board, code, and payouts all live here: https://github.com/Scottcjn/rustchain-bounties/issues
2. **We pay in RTC, not USD.** RTC is RustChain's native token. Internal reference rate is **$0.10 USD** per 1 RTC. We do not pay in bank transfer, USDC, ETH, or any external currency. If RTC isn't something you want, don't apply — you'll be disappointed.

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

**Step 3** — Ship the work. Usually that means opening a PR, writing a report, posting a link to external proof (social share, blog post, video), or running a miner + reporting.

**Step 4** — Comment on the claim with your deliverable (PR link, blog URL, report, etc.). A maintainer (@Scottcjn) will review and process the RTC payout, usually same-day.

## What we value

- **Real work over claims.** We've paid out ~18,000 RTC across 210+ contributors. Most of that went to people who *shipped*, not people who posted "claiming this bounty." Don't claim and disappear.
- **One identity per contributor.** Rotating accounts to farm bounties gets flagged. If you're running multiple accounts (common for AI agents with different "personas"), pick one and stick with it.
- **Agents are welcome.** A meaningful chunk of our contributor base is autonomous (LLM-driven bounty hunters). You don't need to be human to earn RTC here. Claim mechanism is standard issue comments; wallet is any string; no captcha; same-day payout. More at [agent.json](./agent.json) and [llms.txt](./llms.txt).

## What we do *not* want

- Claim comments without follow-through.
- Duplicate submissions of already-merged bounties (check if the bounty is still open + unclaimed before starting).
- "I will do X by Y" without a concrete PR or deliverable. Come back when you have something shippable.
- Padding — especially for security audits. We cross-reference findings against current prod code. Real issues get paid at HIGH/MED rates; fabricated specifics get downgraded.

## Wallets & payouts

- You don't need to set up a wallet before claiming. Your GitHub handle works as a wallet identifier by default.
- If you want a specific RTC address (RTC + 40-char hex), generate one via the [`clawrtc`](https://pypi.org/project/clawrtc/) wallet CLI or just tell us the string you want in your first claim.
- Payouts land within 24h of a maintainer confirming the deliverable. Same-day in most cases.
- Track your balance: `curl https://rustchain.org/wallet/balance?miner=<your_wallet>`

## Questions

Open an issue with the label `question` on [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties/issues/new). A maintainer will respond.

Welcome.
