# wRTC Solana Bridge Dashboard

Real-time dashboard for monitoring the wRTC (wrapped RTC on Solana) bridge activity, built for [Bounty #2303](https://github.com/Scottcjn/rustchain-bounties/issues/2303).

## Features

All requirements from the bounty fulfilled:

| Requirement | Status |
|---|---|
| Show total RTC locked in bridge | Done |
| Show total wRTC circulating on Solana | Done |
| Recent wrap transactions (RTC -> wRTC) | Done |
| Recent unwrap transactions (wRTC -> RTC) | Done |
| Bridge fee revenue | Done |
| Price chart: wRTC on Raydium | Done |
| Bridge health status (both sides) | Done |
| Auto-refresh every 30 seconds | Done |

## Architecture

### Data Sources

- **RustChain API** (`https://50.28.86.131`) - Bridge ledger, locked RTC, node health
- **Solana RPC** (`mainnet-beta`) - wRTC token supply, holder accounts, slot
- **DexScreener API** - wRTC/USD price, volume, liquidity, 24h change
- **Jupiter API** - Price fallback

### Tech Stack

- **Frontend**: Single-file HTML + vanilla JavaScript (zero dependencies)
- **Charts**: Custom canvas-based price chart with gradient fill
- **Layout**: CSS Grid, fully responsive (mobile/tablet/desktop)

### Key Token Addresses

- **wRTC Mint**: `12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X`
- **Raydium Pool**: `8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb`

## Dashboard Panels

1. **Stats Grid** (6 cards):
   - RTC Locked in Bridge (with USD value)
   - wRTC Circulating Supply (with holder count)
   - wRTC Price (with 24h change)
   - Bridge Volume 24h (with tx count)
   - Bridge Fee Revenue (all-time)
   - Peg Ratio (1:1 health indicator)

2. **Bridge Health**: Dual-panel showing RustChain and Solana side status, latency, epoch/slot, node info

3. **Price Chart**: 24h wRTC/USD canvas chart with gradient fill and time labels

4. **Recent Wraps**: Latest RTC -> wRTC transactions with address, amount, and time

5. **Recent Unwraps**: Latest wRTC -> RTC transactions with address, amount, and time

6. **Fee Revenue**: 24h / 7d / All-time fee breakdown with wrap vs unwrap volume bars

## Running

Open `index.html` directly in any browser, or serve via HTTP:

```bash
# Python
python3 -m http.server 8000

# Node.js
npx serve .
```

No build step required. No npm install. Zero dependencies.

## Deploy Target

This dashboard can be deployed to `rustchain.org/bridge` as specified in the bounty, or served standalone on any static hosting (GitHub Pages, Netlify, Vercel, etc.).

## Offline / Demo Mode

When the RustChain or Solana APIs are unreachable (e.g., local development), the dashboard automatically generates realistic demo data for preview purposes. Real API data takes priority whenever available.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT
