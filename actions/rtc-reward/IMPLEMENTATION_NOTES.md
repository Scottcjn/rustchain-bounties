# GitHub Action: Auto-Award RTC on PR Merge

## Implementation Complete ✅

### What Was Built
A reusable GitHub Action (`rtc-reward-action`) that automatically awards RTC tokens to contributors when their PR is merged.

### Files Created
```
rtc-reward-action/
├── action.yml              # Main action (Composite action)
├── README.md               # Documentation
├── LICENSE                 # MIT License
├── CONTRIBUTING.md         # Contribution guidelines
└── examples/
    └── workflow-example.yml # Example workflow
```

### Key Features
- **Auto-detect wallet**: Reads contributor's RTC wallet from PR body or `.rtc-wallet` file
- **Configurable rewards**: Set custom RTC amount per merge (default: 5 RTC)
- **Dry-run mode**: Test without real transfers
- **Auto-comment**: Posts confirmation on PR after transfer
- **Secure**: Admin key stored in GitHub Secrets

### Technical Details
- Action type: Composite (uses Python + GitHub Script)
- Inputs: node-url, amount, wallet-from, admin-key, dry-run, min-commits
- Outputs: tx-hash, recipient-wallet, status

### Bounty Information
- **Bounty Issue:** #2864
- **Reward:** 20 RTC (~$2.00 USD)
- **Status:** Code complete, network issue blocking push

### Network Issue
GitHub connection (port 443) is timing out. The code is ready but cannot be pushed.
Workaround: Will retry connection or ask user to manually create repo.

### Next Steps
1. Push code to GitHub repo
2. Create PR to Scottcjn/Rustchain or publish to GitHub Marketplace
3. Comment on bounty issue to claim

---
Generated: 2026-06-12 05:11 GMT+8
