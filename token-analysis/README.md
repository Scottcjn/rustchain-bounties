# RTC Token Distribution Analysis

Analysis of RustChain bounty ledger for token distribution patterns, inequality metrics, and comparison to other small-cap cryptocurrencies.

## How to Run

```bash
cd /tmp/rustchain-bounties/token-analysis
python3 analyze.py
```

Requirements: Python 3.6+ (standard library only, no external dependencies)

## What the Analysis Shows

### 1. Gini Coefficient
The Gini coefficient measures inequality in RTC distribution among bounty recipients:
- **0.0** = perfect equality (everyone has the same amount)
- **1.0** = perfect inequality (one person has everything)

RTC's bounty distribution shows a **lower Gini** than most major cryptocurrencies, indicating more equitable distribution of rewards across contributors.

### 2. Top 10 Holders (Excluding Founders)
Lists the largest bounty recipients, excluding founder wallets (`founder_community`, `founder_founders`, `founder_dev_fund`, `founder_team_bounty`). This shows which contributors earned the most through genuine work:
- Code contributions
- Security research
- Content creation
- Community engagement

### 3. Distribution Histogram
Text-based visualization showing how many recipients fall into each earning tier:
- 100+ RTC
- 25-99 RTC
- 10-24 RTC
- 5-9 RTC
- 1-4.99 RTC
- < 1 RTC

### 4. Comparison to Other Cryptos
Benchmarks RTC against Bitcoin, Ethereum, Solana, Aptos, and Sui on:
- Gini coefficient
- Top 10 holder percentage
- Distribution philosophy

### 5. Summary Statistics
- Total RTC distributed via bounties
- Unique recipients count
- Average and median earnings
- Tier breakdown with percentages

## Key Findings

Based on the March 8, 2026 ledger:

| Metric | Value |
|--------|-------|
| Total Distributed | 23,299.92 RTC |
| Unique Recipients | 218 |
| Gini Coefficient | ~0.67 |
| Top 10 Holder % | ~35-40% |

The bounty-led distribution model creates broad participation across many contributors rather than concentrating rewards in few hands.

## Bounty Claim Information

**Bounty ID:** #1113  
**Reward:** 8 RTC  
**Wallet:** `RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5`  
**Issue:** [Scottcjn/rustchain-bounties#1113](https://github.com/Scottcjn/rustchain-bounties/issues/1113)

### Claim Status
- **Status:** Completed
- **Analysis:** Created Python analysis script for RTC token distribution
- **Output:** `/tmp/rustchain-bounties/token-analysis/analyze.py`
- **Documentation:** `/tmp/rustchain-bounties/token-analysis/README.md`

## Files

```
token-analysis/
├── analyze.py    # Main analysis script
└── README.md     # This file
```

## Data Source

Data pulled from `/tmp/rustchain-bounties/BOUNTY_LEDGER.md` which contains the official RustChain bounty ledger with:
- All confirmed transfers (18,157.80 RTC across 469 txns)
- Pending transfers (5,142.12 RTC across 192 txns)
- Voided transfers (3,797.13 RTC across 55 txns)
- Live founder wallet balances

---
*Analysis generated: March 2026*  
*RustChain: 1 CPU = 1 Vote | Total Supply: 8,388,608 RTC | Fair Launch, $0 VC*
