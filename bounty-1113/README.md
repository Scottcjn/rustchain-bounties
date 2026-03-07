# Bounty #1113: RTC Token Distribution Analysis

A comprehensive analysis of RustChain's RTC token distribution using the explorer API.

## Features

📊 **Distribution Metrics**
- Total wallets and non-zero wallets
- Total supply calculation
- Mean, median, min, max balances

📈 **Inequality Analysis**
- Gini coefficient calculation (0.8012 - highly concentrated)
- Top 10 holder concentration
- Bottom 50% wealth share

📉 **Visualizations**
- ASCII histogram of balance distribution
- Lorenz curve showing wealth inequality
- Comparison to other cryptocurrencies

## Results Summary

| Metric | Value |
|--------|-------|
| Total Wallets | 13 |
| Non-Zero Wallets | 10 |
| Total Supply | 3,431.81 RTC |
| Gini Coefficient | **0.8012** |
| Mean Balance | 263.99 RTC |
| Median Balance | 7.83 RTC |

### Top 5 Holders

| Rank | Wallet | Balance | % of Supply |
|------|--------|---------|-------------|
| 1 | RTC1d48d... | 1,900.24 RTC | 55.37% |
| 2 | frozen-factorio-ryan | 785.97 RTC | 22.90% |
| 3 | modern-sophiacore-3a168058 | 409.49 RTC | 11.93% |
| 4 | victus-x86-scott | 281.67 RTC | 8.21% |
| 5 | fraktaldefidao | 25.83 RTC | 0.75% |

### Key Findings

1. **Highly Concentrated**: Gini coefficient of 0.80 indicates significant wealth concentration
2. **Top Heavy**: Top 3 wallets control ~90% of the supply
3. **Early Stage**: Distribution typical of new blockchain projects
4. **Comparison**: More concentrated than Bitcoin (~0.65-0.85) and Ethereum (~0.70-0.90)

## Usage

```bash
# Install dependencies
pip install requests

# Run analysis
python3 token_analysis.py
```

## Files

- `token_analysis.py` - Main analysis script
- `token_distribution_report.json` - Detailed JSON report
- `README.md` - This file

## API Endpoints Used

- `GET /api/miners` - List all miners
- `GET /wallet/balance?miner_id={id}` - Get wallet balance

## Wallet for RTC Payout

**sovereign-agent**
