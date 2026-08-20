# 🦞 RustChain Live Dashboard

A modern, feature-rich web dashboard for monitoring RustChain blockchain statistics in real-time.

## Features

- **Live Stats Cards**: Current epoch, slot, enrolled miners, total supply, epoch pot, blocks per epoch
- **Node Health Panel**: Version, uptime, backup age, DB status, tip age
- **Active Miners Table**: All miners ranked by antiquity multiplier, with hardware badges and attestation timestamps
- **Miner Distribution Chart**: Doughnut chart showing hardware type breakdown
- **Bridge & Swap Info**: RTC price, swap URL, network info
- **Auto-refresh**: Data updates automatically every 30 seconds
- **Mobile Responsive**: Fully responsive design for desktop, tablet, and mobile (375px breakpoint)
- **Dark Theme**: Premium dark gradient theme with glassmorphism cards
- **Zero Dependencies**: Single HTML file — open in browser, no build tools needed

## API Endpoints Used

| Endpoint | Data |
|----------|------|
| `GET /epoch` | Epoch, slot, enrolled miners, supply, epoch pot |
| `GET /api/miners` | Active miner list with hardware, multiplier, entropy |
| `GET /health` | Node health, version, uptime, DB status |
| `GET /wallet/swap-info` | RTC price, swap URL, network |

## Quick Start

```bash
# Open directly in browser
open index.html

# Or serve locally
python3 -m http.server 8080
# Then visit http://localhost:8080
```

## Screenshots

The dashboard displays:

1. **Header**: Connection status, auto-refresh timer, manual refresh button
2. **Stats Grid**: 6 stat cards with live data
3. **Node Health**: Detailed health metrics grid
4. **Miner Chart**: Doughnut chart of hardware distribution
5. **Miners Table**: Complete miner list with hardware badges and multipliers
6. **Swap Info**: RTC price and bridge details

## Technology

- HTML5
- CSS3 (Flexbox, Grid, animations, glassmorphism)
- Vanilla JavaScript (ES6+)
- Chart.js (CDN) for data visualization
- Fetch API for data retrieval

## File Structure

```
dashboard-1600/
├── index.html      # Main dashboard (single file)
├── README.md       # This file
└── wrtc-bridge-dashboard/  # wRTC bridge dashboard (sub-module)
```

## License

MIT — Built for RustChain Bounty #1600

---

**Bounty**: [#1600 — Build a web dashboard showing RustChain stats](https://github.com/Scottcjn/rustchain-bounties/issues/1600)
**Reward**: 5 RTC (+3 RTC for mobile responsive)