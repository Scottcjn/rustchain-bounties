# Policy: One Canonical RTC Wallet per Contributor Identity

**Effective Date:** 2026-04-27  
**Compliance Deadline:** 2026-05-11  

## Overview

This policy addresses inconsistencies identified during a forensic audit of contributor payout wallets associated with the RustChain Bounties program. The audit, conducted on 2026-04-27, revealed **5 contributors** with ambiguous wallet-to-identity mappings:

- Multiple GitHub accounts citing the same RTC wallet address
- Multiple RTC wallet addresses cited from the same GitHub account

To ensure accurate, fair, and auditable payout distribution, each contributor must declare **one canonical RTC wallet** per unique contributor identity.

## Policy Statement

**Effective immediately**, all contributors who exhibit any of the following conditions must declare a single canonical payout wallet:

1. **One GitHub account, multiple RTC wallets** — A single GitHub account references more than one distinct RTC wallet address across any combination of PRs, issues, or bounty claims.

2. **One RTC wallet, multiple GitHub accounts** — The same RTC wallet address is cited by two or more different GitHub accounts.

### Deadline

All declarations must be submitted **by 2026-05-11 23:59 UTC**.

### Consequences of Non-Compliance

If no declaration is received by the deadline, the RustChain Bounties program will **infer per-PR wallet assignment** based on the wallet address most recently associated with each individual pull request. This may result in:

- Split payouts across multiple wallets for the same contributor
- Delayed payment processing
- Potential loss of unclaimed bounties

## How to Declare Your Canonical Wallet

### Option 1: Via GitHub Issue (Recommended)

Create a new issue in the [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties) repository using the following template:

```markdown
### Canonical Wallet Declaration

**Contributor GitHub Username:** [your primary GitHub username]

**Canonical RTC Wallet Address:** `0x[your-rtc-wallet-address]`

**Affected Accounts/Wallets (list all):**
- GitHub account(s): [list all GitHub accounts you control]
- RTC wallet(s): [list all RTC wallet addresses previously used]

**Declaration:**
I confirm that the above canonical wallet address is the sole payout destination for all my contributions to RustChain Bounties, past and future.

**Signed:** [your GitHub username]
**Date:** YYYY-MM-DD
```

### Option 2: Via Pull Request Comment

If you have an open PR, you may add a comment to that PR with the same information as above. The comment must be visible and unambiguous.

## Verification Process

After submission, the RustChain Bounties team will:

1. Verify that the declared wallet address is valid on the RustChain network
2. Cross-reference the declared wallet against the audit findings
3. Update internal records within 5 business days
4. Confirm receipt by replying to your declaration issue or PR comment

## Example Scenarios

### Scenario A: One GitHub Account, Multiple Wallets

**Current state:**
- GitHub user `@alice_dev` has PR #42 citing wallet `0xabc...`
- Same user has PR #58 citing wallet `0xdef...`

**Required action:** `@alice_dev` must declare one canonical wallet (e.g., `0xabc...`) and explain the discrepancy.

### Scenario B: One Wallet, Multiple GitHub Accounts

**Current state:**
- Wallet `0x123...` is cited by GitHub user `@bob_coder` in PR #15
- Same wallet is cited by GitHub user `@bob_alt` in PR #27

**Required action:** The contributor must declare which GitHub account is primary and confirm that both accounts belong to the same individual.

## Technical Background

The forensic audit was performed using the following methodology:

1. **Wallet extraction:** All RTC wallet addresses were extracted from PR descriptions, issue comments, and bounty claim forms in the `rustchain-bounties` repository.

2. **Identity mapping:** Each wallet address was mapped to the GitHub account that cited it, using the `author` field of the relevant GitHub object.

3. **Conflict detection:** A script identified cases where:
   - One GitHub account → multiple wallet addresses
   - One wallet address → multiple GitHub accounts

The audit script (Python) is available for transparency:

```python
# audit_wallet_mapping.py
import json
from collections import defaultdict

def audit_wallet_mapping(records):
    """
    records: list of dicts with keys 'github_user', 'wallet_address', 'pr_number'
    Returns: dict with 'multiple_wallets_per_user' and 'multiple_users_per_wallet'
    """
    user_to_wallets = defaultdict(set)
    wallet_to_users = defaultdict(set)
    
    for record in records:
        user_to_wallets[record['github_user']].add(record['wallet_address'])
        wallet_to_users[record['wallet_address']].add(record['github_user'])
    
    conflicts = {
        'multiple_wallets_per_user': {
            user: list(wallets) 
            for user, wallets in user_to_wallets.items() 
            if len(wallets) > 1
        },
        'multiple_users_per_wallet': {
            wallet: list(users) 
            for wallet, users in wallet_to_users.items() 
            if len(users) > 1
        }
    }
    
    return conflicts

# Example usage
sample_records = [
    {'github_user': 'alice_dev', 'wallet_address': '0xabc', 'pr_number': 42},
    {'github_user': 'alice_dev', 'wallet_address': '0xdef', 'pr_number': 58},
    {'github_user': 'bob_coder', 'wallet_address': '0x123', 'pr_number': 15},
    {'github_user': 'bob_alt', 'wallet_address': '0x123', 'pr_number': 27},
]

print(json.dumps(audit_wallet_mapping(sample_records), indent=2))
```

## Support

For questions or assistance with the declaration process, please:

- Open a support issue in the [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties/issues) repository with the label `wallet-declaration`
- Contact the program administrators via the repository's discussion board

---

*This policy is effective as of 2026-04-27 and supersedes any prior informal agreements regarding wallet assignment.*