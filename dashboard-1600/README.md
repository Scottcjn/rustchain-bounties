# 🦞 RustChain Dashboard

A simple, elegant web dashboard for monitoring RustChain blockchain statistics.

## Features

- **Live Stats**: View current epoch, active miner count, total supply, and published payout transaction count
- **Active Miners**: First 10 miners reported by the node, with hardware, multiplier, and last attestation
- **Payout Summary**: Published RTC payout totals, recipient count, feed timestamp, and methodology
- **Auto-refresh**: Data updates automatically every 30 seconds
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Easy on the eyes with a modern gradient background

## Quick Start

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

## API Configuration

The dashboard uses the public REST API at `https://rustchain.org`. Requests
time out after 10 seconds. Failed refreshes show an error and mark previously
loaded data stale; no demo values are generated. A missing payout feed does
not prevent epoch, miner, or supply updates.

To use your own CORS-enabled node, edit `API_BASE` in `index.html`:

```javascript
const API_BASE = 'https://your-node.com';
```

## Supported API Endpoints

The dashboard makes read-only GET requests:

| Endpoint | Description |
|--------|-------------|
| `/epoch` | Epoch, slot, enrolled miners, and total RTC supply |
| `/api/miners` | Active miner details and total count from pagination |
| `/payouts.json` | Published payout transaction count and summary (optional) |

The transaction card counts **published payouts**, not 24-hour or all-network
transactions. The feed currently includes confirmed and pending transfers from
founder payout wallets to external recipients, excluding voids and internal
pools. Its timestamp and methodology are displayed alongside the totals.
The public `/api/transactions` endpoint is unavailable, so individual transaction
rows are not fabricated. Supply is the reported total, not a circulating estimate.

## Verification

From the repository root, using Node.js 18 or newer:

```bash
node --test dashboard-1600/dashboard.test.mjs
```

Run the optional live integration check in PowerShell:

```powershell
$env:RUSTCHAIN_LIVE='1'; node --test dashboard-1600/dashboard.test.mjs
```

The tests execute the page's actual JavaScript and cover live-response mapping,
missing payout data, stale-data recovery, empty miner lists, HTML escaping, and
30-second refresh scheduling. No dependencies or build step are required.

## Screenshots

The dashboard displays:

1. **Status Bar**: Connection status and last update time
2. **Stats Cards**: Epoch, miners, supply, transactions
3. **Miners Table**: Up to 10 active miners with hardware and attestation details
4. **Payout Summary**: Published transaction totals and their scope

## Technologies

- HTML5
- CSS3 (Flexbox, Grid, animations)
- Vanilla JavaScript (no frameworks)
- Fetch API for data retrieval

## File Structure

```
rustchain-dashboard/
├── index.html      # Main dashboard (single file)
└── README.md       # This file
```

## License

MIT - Built for RustChain Bounty #1600

## Author

Lobster Bot / 花猫 (Flower Cat)

---

**Bounty**: #1600 - 5 RTC  
**Status**: ✅ Complete
