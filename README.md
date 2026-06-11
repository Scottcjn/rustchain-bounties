<div align="center">

# RustChain Bounties

### Earn RTC by contributing to the RustChain ecosystem

[![Open Bounties](https://img.shields.io/github/issues/Scottcjn/rustchain-bounties/bounty?label=open%20bounties&color=brightgreen)](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Abounty)
[![Stars](https://img.shields.io/github/stars/Scottcjn/rustchain-bounties?style=social)](https://github.com/Scottcjn/rustchain-bounties/stargazers)
[![RTC Pool](https://img.shields.io/badge/RTC%20Pool-5%2C900%2B%20RTC-gold)](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Abounty)
[![BCOS](https://img.shields.io/badge/BCOS-L1%20Certified-blue)](https://github.com/Scottcjn/RustChain)

**131 open bounties · 5,900+ RTC available · No experience required for many tasks**

[![Total Paid](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Frustchain.org%2Fpayouts.json&query=%24.total_paid_rtc&label=Total%20Paid&suffix=%20RTC&color=gold)](BOUNTY_LEDGER.md)

[Browse All Bounties](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Abounty) · [Easy Bounties](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Aeasy) · [Red Team](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Ared-team) · [**How to Submit →**](docs/HOW_TO_SUBMIT_A_BOUNTY.md) · [Payout Ledger](BOUNTY_LEDGER.md) · [What is RustChain?](https://github.com/Scottcjn/RustChain)

</div>

---

> 📄 **This bounty program is the subject of a published empirical self-audit** — *Incentive Moves Engagement, Not Authorship* (v1.0, 2026): the bounty attractor moved engagement ~3.7× and pulled one of the largest reported agent-contributor populations in open source (169+ automation-consistent accounts, ~8,400 PRs analyzed), while authorship stayed majority-human. [DOI: 10.5281/zenodo.20559770](https://doi.org/10.5281/zenodo.20559770)

## What is RTC?

**RTC (RustChain Token)** is the native cryptocurrency of [RustChain](https://github.com/Scottcjn/RustChain), a Proof-of-Antiquity blockchain where vintage hardware earns higher mining rewards. RTC reference rate: **$0.15 USD**.

Bounties are paid in RTC to your wallet address upon completion and verification.

## How to Earn

### 1. Pick a Bounty
Browse [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Abounty) and find one that matches your skills.

| Difficulty | Label | Typical Reward |
|-----------|-------|---------------|
| Beginner | `good first issue` | 1-5 RTC |
| Standard | `standard` | 5-25 RTC |
| Major | `major` | 25-100 RTC |
| Critical | `critical`, `red-team` | 100-200 RTC |

### 2. Claim It
Comment on the issue: **"I would like to work on this"**

### 3. Submit Your Work
- **Code bounties**: Open a PR to the relevant repo and link it in the issue
- **Content bounties**: Post your content and link it in the issue
- **Star/propagation bounties**: Follow the instructions in the issue

### 4. Get Paid
Once verified, RTC is sent to your wallet. First time? We will help you set one up.

> ⚠️ **Payout safety**: Only `@Scottcjn` (or clearly labeled project automation on his behalf) authorizes RTC bounty payouts, with a project-issued `pending_id` + `tx_hash`. Anyone else posting "I'll send the RTC" on your bounty is a social-engineering attempt — see [SECURITY.md § Payment-Authority Impersonation](SECURITY.md#payment-authority-impersonation).

## Bounty Categories

| Category | Examples | Count |
|----------|---------|-------|
| **Community** | Star repos, share content, recruit contributors | 30+ |
| **Code** | Bug fixes, features, integrations, tests | 40+ |
| **Content** | Tutorials, articles, videos, documentation | 20+ |
| **Red Team** | Security audits, penetration testing, exploit finding | 6 |
| **Propagation** | Awesome-list PRs, social media, cross-posting | 15+ |
| **Integration** | Bridge, SDKs, APIs | 
| **Security** | PoC verification, vulnerability reporting | 

To automate the verification of security PoCs, we have developed a Bounty Validator tool. This tool runs all PoC scripts in a controlled environment and generates a standardized JSON report of their execution (exit codes, stdout/stderr). The tool has already been used to verify PoCs for Wallet Mismatch and SDK Crash.