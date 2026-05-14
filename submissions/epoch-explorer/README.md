# RustChain Epoch Explorer

A self-contained single-page web tool for monitoring RustChain epoch data, network statistics, and wallet balances.

## Features

- **Epoch Monitoring** — Real-time display of current epoch with countdown to the next
- **Network Stats** — Block height, transaction count, active miners, hashrate, peers
- **Wallet Lookup** — Search any wallet address for its balance
- **Epoch History** — Locally stored history table with CSV export
- **Auto Refresh** — Configurable polling interval (5s/10s/30s/60s)
- **Dark Theme** — Easy on the eyes, responsive design for mobile and desktop
- **Zero Dependencies** — Pure HTML/CSS/JS, just open in a browser

## Usage

1. Open `index.html` in any modern browser
2. If connecting to a node with a self-signed certificate, visit the API URL first and accept the certificate warning
3. Adjust the API base URL if needed (default: `https://50.28.86.131`)

## API Endpoints Used

| Endpoint | Description |
|---|---|
| `GET /epoch` | Current epoch info |
| `GET /api/stats` | Network statistics |
| `GET /balance/{wallet}` | Wallet balance |

## Technical Details

- Single HTML file, no build step required
- Uses `fetch()` for API calls
- History stored in `localStorage` (last 100 epochs)
- Responsive CSS grid layout
- ~16KB total, zero external dependencies

## License

MIT
