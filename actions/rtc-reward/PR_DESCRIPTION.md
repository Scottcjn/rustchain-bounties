# RTC Reward Action PR

## Summary
This PR implements a GitHub Action that automatically awards RTC tokens when a PR is merged.

## Files Added
- `.github/actions/rtc-reward/action.yml` - Main action definition
- `.github/workflows/rtc-reward.yml` - Example workflow
- `README.md` - Documentation
- `LICENSE` - MIT License
- `CONTRIBUTING.md` - Contribution guidelines

## Features
- 🎯 **Auto-detect wallet**: Reads contributor's RTC wallet from PR body or `.rtc-wallet` file
- 💰 **Configurable rewards**: Set custom RTC amount per merge
- 🧪 **Dry-run mode**: Test without real transfers
- 💬 **Auto-comment**: Posts confirmation on PR after transfer
- 🔒 **Secure**: Admin key stored in GitHub Secrets

## Testing
- [ ] Dry-run mode tested
- [ ] Wallet detection verified
- [ ] Comment posting tested

## Bounty Claim
Claiming bounty from issue #2864

**Reward:** 20 RTC
**Wallet:** (to be provided after merge)

---
I received RTC compensation for this contribution.
