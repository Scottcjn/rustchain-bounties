# RustChain Network Status Page

A public-facing network status dashboard for the RustChain blockchain.
Displays live node health, miner activity, and RTC balances.

## Features

- **Node Status**: Health check, uptime, version
- **Active Miners**: List with architecture, multiplier, last attestation
- **RTC Balances**: Per-miner balance display
- **Auto-Refresh**: Updates every 30 seconds
- **Zero Dependencies**: Single HTML file, no build step

## Usage

Open `index.html` in any browser, or serve with any static file server:

```bash
# Python
python3 -m http.server 8080

# Node
npx serve .

# Just open the file directly
open index.html
```

## Deployment

### GitHub Pages (Recommended)
1. Push to a repo
2. Enable GitHub Pages from the `docs/` or root folder
3. Visit `https://<user>.github.io/<repo>/`

### Nginx
```nginx
server {
    listen 80;
    server_name status.rustchain.org;
    root /var/www/rustchain-status;
    index index.html;
}
```

## API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Node health, uptime, version |
| `GET /api/miners` | Active miner list |
| `GET /wallet/balance?miner_id=X` | Per-miner balance |

**Wallet:** yuanbao-worker
