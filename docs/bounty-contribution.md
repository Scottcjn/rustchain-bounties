Looking at this issue, I need to create a policy document that addresses the RTC wallet deduplication requirement. The issue specifies a forensic audit found 5 contributors with conflicting wallet/account mappings. Let me write a clear, actionable policy.

---

# Policy: One Canonical RTC Wallet Per Contributor Identity

**Effective:** 2026-04-27  
**Deadline:** 2026-05-11 (14 days)  
**Scope:** All contributors with RTC payout history or pending bounties

## Background

A forensic audit on 2026-04-27 identified 5 contributors with inconsistent wallet-to-account mappings:

- Multiple GitHub accounts claiming payouts to the same RTC wallet
- Single GitHub accounts listing multiple RTC wallets across different bounties

This creates ambiguity in payout routing and makes it impossible to accurately track per-contributor RTC totals.

## The Rule

Each natural person contributing to RustChain Bounties must declare exactly **one canonical RTC wallet** that will receive all future payouts. This wallet is bound to your primary GitHub account.

**You are affected if any of the following apply:**

1. You control two or more GitHub accounts that have cited the same RTC wallet in bounty claims
2. Your single GitHub account has cited two or more different RTC wallets across different bounty issues or PRs
3. You have ever changed your payout wallet address without notifying the maintainers

## How to Declare

1. Open a new issue in this repository using the **"Canonical Wallet Declaration"** template
2. Fill in:
   - Your primary GitHub username
   - The single RTC wallet address you want to use going forward
   - Any secondary GitHub accounts you control (if applicable)
   - Any old wallet addresses you've used before (if applicable)

**Template URL:** `https://github.com/Scottcjn/rustchain-bounties/issues/new?template=canonical_wallet.md`

## What Happens If You Don't Declare

If we receive no declaration by 2026-05-11 23:59 UTC:

- Payouts will be made **per-PR basis** using the wallet address cited in each individual bounty claim
- No consolidation or cross-referencing will be attempted
- You forfeit the ability to dispute routing errors after payout

## For the 5 Identified Contributors

You will receive a direct mention in a comment on your most recent bounty issue within 48 hours. The comment will link back to this policy. You do not need to wait for that mention — you can declare immediately.

## Enforcement After Deadline

Starting 2026-05-12, any PR or bounty claim that cites a wallet different from your declared canonical wallet will be rejected at review. No exceptions.

## Questions

Comment on this issue or ping `@Scottcjn` in the RustChain Discord `#bounties` channel.