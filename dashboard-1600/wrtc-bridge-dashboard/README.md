# wRTC Solana Bridge Dashboard

Real-time monitoring dashboard for the wRTC ↔ Solana cross-chain bridge.

## Features

- **Total RTC Locked in Bridge** — Live count of RTC locked via deposit transactions
- **Total wRTC Circulating on Solana** — Real-time supply tracked via Solana RPC
- **Recent Wrap Transactions (RTC → wRTC)** — Last 20 deposit bridge transfers
- **Recent Unwrap Transactions (wRTC → RTC)** — Last 20 withdrawal bridge transfers
- **Bridge Fee Revenue** — Cumulative fees collected by the bridge
- **wRTC Price Chart (Raydium)** — Live price chart via DexScreener API
- **Bridge Health Status** — Operational status for both RustChain and Solana sides
- **Auto-refresh every 30 seconds**

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JS (no build step required)
- **APIs**:
  - RustChain API — bridge state, locked RTC, transactions
  - Solana RPC — wRTC token supply
  - DexScreener API — wRTC price/volume data
- **Deployment**: Serve `index.html` on any static host or open directly in browser

## File Structure

```
dashboard-1600/wrtc-bridge-dashboard/
├── README.md       — This file
└── index.html      — Self-contained dashboard (all JS/CSS inline)
```

## Configuration

The dashboard auto-detects the following config from `window.BRIDGE_CONFIG`:

```js
window.BRIDGE_CONFIG = {
  // RustChain API endpoint (leave empty for auto-detect)
  rustchainApi: '',
  // Solana RPC endpoint
  solanaRpc: 'https://api.mainnet-beta.solana.com',
  // wRTC mint address on Solana
  wrtcMint: 'YOUR_WRTC_MINT_ADDRESS',
  // Solana explorer base URL
  explorer: 'https://solscan.io',
  // Refresh interval in ms (default: 30000)
  refreshMs: 30000
};
```

## Open in Browser

Simply open `index.html` directly or serve via any static HTTP server:

```bash
# Python
python -m http.server 8080

# Node.js
npx serve .

# Docker
docker run -p 8080:80 -v $(pwd):/usr/share/nginx/html nginx:alpine
```

## Related

- Bridge API specs: `docs/protocol/API_SPEC.md`
- wRTC onboarding: `docs/wrtc-onboarding/`
- Bridge tests: `tests/test_bridge_lock_ledger.py`
