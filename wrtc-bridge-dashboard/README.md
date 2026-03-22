# 🌉 wRTC Solana Bridge Dashboard

A real-time monitoring dashboard for the wRTC (wrapped RTC on Solana) bridge.

## 📊 Features

- **Total RTC Locked**: Shows total RTC locked in the bridge contract on RustChain
- **wRTC Circulating Supply**: Total wRTC tokens on Solana
- **Bridge Fee Revenue**: Total fees collected by the bridge
- **wRTC Price Chart**: Live price chart from Raydium via DexScreener
- **Recent Wrap Transactions**: RTC → wRTC conversions
- **Recent Unwrap Transactions**: wRTC → RTC conversions
- **Bridge Health Status**: Real-time health monitoring of both chains
- **Auto-Refresh**: Data updates automatically every 30 seconds

## 🚀 Quick Start

### Option 1: Open Directly

Simply open `index.html` in your browser:

```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

### Option 2: Local Server

For best experience, serve with a local web server:

```bash
# Using Python
python3 -m http.server 8080

# Using Node.js
npx serve .

# Using PHP
php -S localhost:8080
```

Then visit `http://localhost:8080`

## 🔧 Configuration

The dashboard is configured to work with:

- **RustChain API**: `https://api.rustchain.io`
- **RustChain RPC**: `https://50.28.86.131`
- **Solana RPC**: `https://api.mainnet-beta.solana.com`
- **DexScreener API**: `https://api.dexscreener.com/latest`

To use custom endpoints, edit the `CONFIG` object in `index.html`:

```javascript
const CONFIG = {
    RUSTCHAIN_API: 'https://your-rustchain-api.com',
    RUSTCHAIN_RPC: 'https://your-rustchain-rpc.com',
    SOLANA_RPC: 'https://your-solana-rpc.com',
    WRTC_MINT: 'YOUR_WRTC_MINT_ADDRESS',
    DEXSCREENER_API: 'https://api.dexscreener.com/latest',
    REFRESH_INTERVAL: 30000, // 30 seconds
};
```

## 📡 API Endpoints

The dashboard queries the following endpoints:

### RustChain API
- `GET /v1/bridge/stats` - Bridge statistics (locked RTC, fees)
- `GET /v1/bridge/transactions` - Recent wrap/unwrap transactions

### RustChain RPC
- `rustchain_getBridgeInfo` - Bridge information and stats

### Solana RPC
- `getTokenSupply` - wRTC total supply (requires mint address)

### DexScreener API
- `GET /dex/tokens/{tokenAddress}` - Token price and volume data

## 🎨 Design Features

- **Gradient Design**: Modern gradient background with Solana brand colors
- **Responsive Layout**: Works on desktop and mobile devices
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Health Monitoring**: Visual indicators for bridge health
- **Transaction History**: Detailed view of recent wrap/unwrap operations
- **Price Chart**: Interactive chart powered by Chart.js

## 🔄 Demo Mode

If the configured API endpoints are unavailable, the dashboard automatically falls back to demo mode with simulated data. This allows you to:

- Preview the dashboard interface
- Test the layout and design
- Understand the data structure

A "DEMO MODE" badge appears when using simulated data.

## 📦 Dependencies

- **Chart.js** (v4.4.0): For rendering the price chart (loaded via CDN)
- No other external dependencies required!

## 🏗️ Architecture

```
wrtc-bridge-dashboard/
├── index.html      # Single-file dashboard (HTML + CSS + JS)
└── README.md       # This file
```

The dashboard is implemented as a single HTML file for easy deployment and maintenance.

## 🚢 Deployment

The dashboard can be deployed to:

- **Static hosting** (GitHub Pages, Netlify, Vercel, Cloudflare Pages)
- **RustChain domain** (`rustchain.org/bridge`)
- **IPFS** (decentralized hosting)

Simply upload `index.html` to your hosting service.

## 🔐 Security

- **No server-side code**: Pure client-side application
- **No API keys required**: Uses public APIs
- **No sensitive data**: Only displays public blockchain data
- **CORS-friendly**: All APIs support CORS for browser requests

## 📊 Data Structure

### Bridge Stats
```json
{
  "rtcLocked": 1250000,
  "wrtcSupply": 1250000,
  "feeRevenue": 2500,
  "totalWraps": 5420,
  "totalUnwraps": 3210
}
```

### Transaction
```json
{
  "type": "wrap",
  "amount": 150,
  "fromAddress": "rN7v3...8xK2",
  "toAddress": "5F3dK...9xM2",
  "timestamp": 1711094400000,
  "txHash": "..."
}
```

## 🎯 Bounty Requirements

This dashboard satisfies all requirements from [Bounty #2303](https://github.com/Scottcjn/rustchain-bounties/issues/2303):

- ✅ Show total RTC locked in bridge
- ✅ Show total wRTC circulating on Solana
- ✅ Recent wrap transactions (RTC → wRTC)
- ✅ Recent unwrap transactions (wRTC → RTC)
- ✅ Bridge fee revenue
- ✅ Price chart: wRTC on Raydium
- ✅ Bridge health status (both sides)
- ✅ Auto-refresh every 30 seconds
- ✅ HTML/JS frontend (no framework required)
- ✅ Integrates RustChain API, Solana RPC, and DexScreener API

## 📝 License

MIT - Built for RustChain Bounty #2303

## 👤 Author

HuiNeng

**RTC Wallet Address**: `rN7v37Zp8nMqL5KdT9FwvC3eYbR2sX4hV8xK2mN6`

---

**Bounty**: #2303 - 60 RTC  
**Status**: ✅ Complete