# RustChain Web Dashboard

A single-page web dashboard for monitoring the RustChain blockchain network in real-time.

## Features

- **Live Epoch Number** - Current blockchain epoch
- **Active Miner Count** - Number of miners currently participating
- **Total RTC Supply** - Total tokens in circulation
- **Network Hashrate** - Current mining hashrate
- **Recent Transactions** - Latest blockchain transactions with type, amount, and details
- **Auto-Refresh** - Updates every 30 seconds automatically

## How to Run

### Option 1: Direct Open (Simplest)
Simply open `index.html` in any modern web browser:
```bash
# On Linux/macOS
xdg-open index.html
open index.html

# On Windows (from the directory)
start index.html
```

### Option 2: Local HTTP Server (Recommended for Development)
```bash
# Python 3
python -m http.server 8080

# Then open http://localhost:8080 in your browser
```

### Option 3: Using Node.js
```bash
npx serve .
```

## Bounty Information

| Item | Details |
|------|---------|
| **Bounty ID** | #1600 |
| **Reward** | 5 RTC |
| **Issue** | [Scottcjn/rustchain-bounties#1600](https://github.com/Scottcjn/rustchain-bounties/issues/1600) |
| **Wallet** | `RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5` |

## API Connection

The dashboard attempts to connect to the RustChain node at `https://50.28.86.131:8099`. If the node is unreachable, it automatically falls back to realistic mock data so you can see how the dashboard would look with live data.

### Endpoints Used
- `GET /api/epoch` - Current epoch number
- `GET /api/stats` - Network statistics (miners, supply, hashrate)
- `GET /api/transactions?limit=N` - Recent transactions

## Screenshots

### Dashboard Layout
The dashboard features:
- **Header** with RustChain branding and live connection status indicator
- **4-Stat Grid** showing Epoch, Active Miners, Total Supply, and Network Hashrate
- **Transactions Table** with hash, type badges, addresses, amounts, and epoch
- **Footer** with bounty information and claim link

### Status Indicator
- 🟢 **Green pulsing** - Connected to live node
- 🔴 **Red** - Using mock data (node unreachable)
- 🟡 **Yellow** - Refreshing data

### Transaction Types
- **Reward** (green badge) - Block reward payouts to miners
- **Transfer** (blue badge) - Token transfers between addresses
- **Stake** (yellow badge) - Staking pool deposits

## Technical Details

- **Pure HTML/CSS/JS** - No frameworks, single file, maximum compatibility
- **CSS Grid & Flexbox** - Responsive layout that works on mobile
- **Fetch API** - Modern async data loading with timeout handling
- **Mock Data Fallback** - Realistic simulated data when node is unreachable
- **Auto-Refresh** - 30-second refresh interval with visual status

## File Structure

```
web-dashboard/
├── index.html   # Complete dashboard (HTML + CSS + JS)
└── README.md    # This file
```
