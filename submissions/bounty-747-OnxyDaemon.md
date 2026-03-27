@Scottcjn Claiming the **Bounty Verification Bot** bounty (#747).

I have built a fully functional GitHub Action bot that automates the verification of bounty claims, specifically designed for the RustChain ecosystem.

### ✅ Implemented Features (75/75 RTC Potential)
1. **GitHub Star/Follow Verification** (30 RTC): Automatically checks if a user follows you and counts stars on your repos via GitHub API.
2. **Wallet Existence Check** (10 RTC): Queries the RustChain node API (50.28.86.131) to verify wallet existence and current balance.
3. **Article/URL Verification** (10 RTC): Checks if Article/Medium/dev.to links are live and provides a rough word count.
4. **Dev.to Article Quality Check** (10 RTC): Rough word count and content verification.
5. **Duplicate Claim Detection** (15 RTC): Scans the issue comment history for previous PAID markers by the same user.

### 🚀 Implementation Details
- **Repository:** https://github.com/OnxyDaemon/bounty-verification-bot
- **Workflow:** Included GitHub Action (.github/workflows/verify-bounties.yml) that can run on a schedule (every 30 mins) or manual trigger.
- **Reporting:** Posts a clean markdown table back to the issue with a PASS/FAIL summary and suggested payout calculation.
- **Configurable:** Easy to adjust RTC rates, follow multipliers, and target node URLs.

### 👛 Wallet Address
RTC8e94b315106322cd5d3680682b3dcb9f984e386c (OnyxDaemon)

Ready for review and deployment!
