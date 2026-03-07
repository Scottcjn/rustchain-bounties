# RTC Token Distribution Analysis

**Bounty #1113** - Analysis of RTC token distribution patterns on RustChain

## Overview

This project provides a comprehensive analysis of the RustChain Token (RTC) distribution across the bounty program, examining concentration metrics, funding sources, and contributor patterns.

## Key Findings

### 📊 Program Scale
- **Total Paid**: 22,756.62 RTC (~$2,275.66 USD)
- **Recipients**: 214 unique wallets
- **Transactions**: 641 total payouts
- **Average Payout**: 35.50 RTC per transaction

### 💰 Funding Distribution
| Source | RTC Paid | % of Total | Purpose |
|--------|----------|------------|---------|
| Community Fund | 18,425.12 | 81.0% | Content, engagement, stars |
| Team Bounty | 3,561.50 | 15.6% | Code, PRs, integrations |
| Dev Fund | 770.00 | 3.4% | Security, audits |

### 📉 Concentration Metrics
- **Top 1**: 3.92% of all payouts
- **Top 5**: 17.05% of all payouts  
- **Top 10**: 22.75% of all payouts
- **Gini Coefficient**: 0.147 (moderate equality)

### 🏦 Treasury Health
- **Remaining**: 185,017.26 RTC (~$18,500)
- **Spent**: 11.0% of treasury
- **Runway**: ~8x historical payout volume remaining

## Files

- `rtc_distribution_analysis.py` - Main analysis script
- `rtc_analysis.json` - Exported data in JSON format
- `README.md` - This file

## Usage

```bash
python3 rtc_distribution_analysis.py
```

## Insights & Recommendations

1. **Healthy Distribution**: Top 10 control only 22.75% - good decentralization
2. **Dev Fund Underutilized**: Only 2.9% spent - increase security investments
3. **Team Fund Depleted**: 71.5% spent - may need replenishment soon
4. **Strong Retention**: 3.0 transactions per recipient average

## Data Source

Analysis based on [RustChain Bounty Ledger](https://github.com/Scottcjn/rustchain-bounties/blob/main/BOUNTY_LEDGER.md) as of March 7, 2026.

---

**Wallet for RTC payout**: sovereign-agent
