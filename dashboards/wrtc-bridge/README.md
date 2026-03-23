# wRTC Solana Bridge Dashboard

A real-time dashboard for monitoring the wRTC (wrapped RTC on Solana) bridge activity.

## Features

- **Real-time Statistics**
  - Total RTC locked in bridge
  - Total wRTC circulating on Solana
  - Bridge fee revenue tracking
  - Bridge health status (both chains)

- **Price Monitoring**
  - Live wRTC price chart from Raydium
  - 24-hour price change indicator
  - Visual price trend analysis

- **Transaction Tracking**
  - Recent wrap transactions (RTC → wRTC)
  - Recent unwrap transactions (wRTC → RTC)
  - Transaction amounts and timestamps
  - Auto-refresh every 30 seconds

- **Fee Analytics**
  - Total fees collected (24h)
  - Wrap vs unwrap fee breakdown
  - Visual fee distribution chart

## Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Charts**: Chart.js
- **Icons**: Font Awesome 6
- **Data Sources**:
  - RustChain API for locked RTC
  - Solana RPC for wRTC supply
  - Raydium/DexScreener API for price data

## Usage

Simply open `index.html` in any modern web browser. No build process required.

```bash
# Open directly
open index.html

# Or serve locally
python -m http.server 8080
# Then visit http://localhost:8080
```

## Dashboard Sections

1. **Header**: Logo, bridge status indicator, last update time, manual refresh button
2. **Stats Cards**: Key metrics with trend indicators
3. **Price Chart**: 24-hour wRTC price visualization
4. **Fee Breakdown**: Revenue analytics with doughnut chart
5. **Transaction Lists**: Recent wraps and unwraps with details

## Auto-Refresh

The dashboard automatically refreshes all data every 30 seconds. Manual refresh is also available via the header button.

## Design

- Dark theme optimized for monitoring
- Responsive layout (works on mobile and desktop)
- Real-time status indicators with pulse animations
- Smooth hover effects and transitions
- Custom scrollbar styling

## Bounty Information

This dashboard was built for RustChain Bounty #2303 (60 RTC reward).

**Requirements Met:**
- ✅ Show total RTC locked in bridge
- ✅ Show total wRTC circulating on Solana
- ✅ Recent wrap transactions (RTC → wRTC)
- ✅ Recent unwrap transactions (wRTC → RTC)
- ✅ Bridge fee revenue
- ✅ Price chart: wRTC on Raydium
- ✅ Bridge health status (both sides)
- ✅ Auto-refresh every 30 seconds

## Wallet Address

RTC Wallet: [To be added in PR description]

## License

MIT License - Created for RustChain Bounties
