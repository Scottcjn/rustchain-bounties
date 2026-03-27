# 🦞 RustChain Dashboard

A simple, elegant web dashboard for monitoring RustChain blockchain statistics.

## Features

- **Real-time Stats**: View current epoch, active miners, total supply, and transaction volume
- **Miner Leaderboard**: Top 10 miners by blocks mined
- **Recent Transactions**: Live feed of recent blockchain transactions
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

The dashboard is configured to work with:

- **REST API**: `https://api.rustchain.io`
- **RPC Node**: `https://50.28.86.131`

If these endpoints are unavailable, the dashboard automatically falls back to demo mode with mock data.

To use your own node, edit the `API_BASE` and `RPC_NODE` constants in `index.html`:

```javascript
const API_BASE = 'https://your-node.com';
const RPC_NODE = 'https://your-rpc-node.com';
```

## Supported API Endpoints

The dashboard queries the following RustChain RPC methods:

| Method | Description |
|--------|-------------|
| `rustchain_getEpoch` | Get current epoch information |
| `rustchain_getMiners` | Get list of active miners |
| `rustchain_getLedger` | Get recent transactions |

## Screenshots

The dashboard displays:

1. **Status Bar**: Connection status and last update time
2. **Stats Cards**: Epoch, miners, supply, transactions
3. **Miners Table**: Top 10 miners with rankings
4. **Transactions Table**: Recent blockchain activity

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
