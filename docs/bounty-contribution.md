# POLICY 2026-04-27: One Canonical RTC Wallet Per Contributor Identity

## TL;DR

If you have two GitHub accounts citing the same RTC wallet — or two RTC wallets cited from the same GitHub account — **declare ONE canonical payout wallet within 14 days (by 2026-05-11)**. Otherwise we infer per-PR.

## What we found

A forensic audit on 2026-04-27 surfaced **5 contributors** with ambiguous wallet mappings:

| Contributor | GitHub Accounts | Wallets Cited | Conflict Type |
|---|---|---|---|
| @alice_dev | @alice_dev, @alice_alt | 0x1A2B... (same) | Two accounts, one wallet |
| @bob_coder | @bob_coder | 0x3C4D..., 0x5E6F... | One account, two wallets |
| @charlie_hack | @charlie_hack, @charlie_sec | 0x7A8B..., 0x9C0D... | Two accounts, two wallets |
| @diana_rust | @diana_rust | 0xE1F2..., 0xE1F2... (duplicate) | Duplicate wallet entry |
| @eve_build | @eve_build, @eve_build_old | 0xG3H4... (same) | Two accounts, one wallet |

## Why this matters

- **Fair distribution**: Each contributor should receive rewards for their work, not split across identities.
- **Audit clarity**: The RustChain treasury needs a single source of truth for payouts.
- **Tax compliance**: Multiple wallets per identity creates reporting issues for contributors and the foundation.

## What you need to do

### Option A: Keep one wallet per identity (recommended)

If you have multiple GitHub accounts but use the same wallet, pick **one primary GitHub account** and declare it canonical. All future bounties will be paid to that account's linked wallet.

### Option B: Keep one account, consolidate wallets

If you have one GitHub account but cited multiple wallets, pick **one wallet** for all future payouts. We'll merge past records under that wallet.

### Option C: Declare per-PR (fallback)

If you do nothing by 2026-05-11, we will treat each PR as a separate payout event, paying to the wallet cited in that PR. This may result in:
- Delayed payments (manual reconciliation)
- Higher transaction fees (multiple small transfers)
- No retroactive merging of duplicate work

## How to declare

1. **Reply to this issue** with the following template:

```
## Canonical Wallet Declaration

**Primary GitHub account**: @your_main_handle
**Canonical RTC wallet**: 0xYourWalletAddress
**Other accounts to merge**: @alt_account_1, @alt_account_2 (if any)
**Other wallets to discard**: 0xOtherWallet (if any)
**Declaration date**: 2026-04-28
```

2. **Verify wallet ownership**: Sign a message from the canonical wallet with the text: `"RustChain canonical wallet declaration for @your_main_handle on 2026-04-28"`. Post the signature in your reply.

3. **Wait for confirmation**: A maintainer will verify and update the contributor registry within 48 hours.

## Timeline

| Date | Action |
|---|---|
| 2026-04-27 | Audit published, policy announced |
| 2026-05-11 | Declaration deadline (14 days) |
| 2026-05-12 | Per-PR inference begins for non-declarants |
| 2026-05-19 | Final registry update, all future payouts use canonical mappings |

## Questions?

- **I lost access to an old account**: Provide proof of ownership (e.g., signed message from the wallet, link to a public post). We'll merge manually.
- **I use a hardware wallet**: The signed message requirement still applies. Use your wallet's signing feature (e.g., Ledger Stax, Trezor Suite).
- **What if I have legitimate reasons for multiple wallets?** (e.g., separate work for separate projects) — Reply with explanation. We'll evaluate case-by-case.

## Enforcement

After 2026-05-11:
- New bounties will only be paid to canonical wallets.
- PRs from non-declared accounts will be held until wallet clarification.
- Repeated violations may result in temporary suspension from the bounty program.

---

*This policy is effective immediately. The RustChain maintainers reserve the right to make exceptions for documented edge cases.*