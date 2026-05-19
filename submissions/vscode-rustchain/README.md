# RustChain Wallet & Miner Dashboard — VS Code Extension

A VS Code extension that brings the RustChain blockchain experience directly into your editor. Monitor your wallet balance, track miner status, and view network information without leaving VS Code.

## Features

### 💰 Wallet Balance
- View your RTC token balance in the status bar
- Click to open the full dashboard panel
- Quick command to check balance via notification

### ⛏️ Miner Dashboard
- Real-time miner status (active/inactive)
- Hashrate monitoring
- Active worker count

### 🌐 Network Status
- Current epoch number
- Block height
- Connected peers
- Total supply information

### 🔄 Auto-Refresh
- Configurable auto-refresh interval
- Manual refresh command
- Data updates in both status bar and dashboard

## Commands

| Command | Description |
|---------|-------------|
| `RustChain: Show Wallet Balance` | Display wallet balance in a notification |
| `RustChain: Show Network Status` | Display network info in a notification |
| `RustChain: Open Dashboard` | Open the full WebView dashboard panel |
| `RustChain: Refresh Data` | Manually refresh all data |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `rustchain.apiUrl` | `https://api.rustchain.xyz` | RustChain API base URL |
| `rustchain.walletAddress` | `""` | Your RustChain wallet address |
| `rustchain.refreshInterval` | `60` | Auto-refresh interval in seconds (0 to disable) |

## Getting Started

1. Install the extension
2. Open VS Code Settings and set your `rustchain.walletAddress`
3. The status bar will show your balance automatically
4. Use `Ctrl+Shift+P` → `RustChain: Open Dashboard` for the full view

## Architecture

```
vscode-rustchain/
├── extension.js          # Extension entry point
├── src/
│   ├── apiClient.js      # RustChain API HTTP client
│   ├── statusBar.js      # Status bar item management
│   └── walletPanel.js    # WebView dashboard panel
├── package.json          # Extension manifest
├── .vscodeignore         # Packaging exclusions
└── README.md             # This file
```

## API Endpoints Used

- `GET /wallet/:address/balance` — Wallet balance
- `GET /miner/:address/status` — Miner status
- `GET /network/status` — Network status
- `GET /wallet/:address/transactions` — Recent transactions

## Bounty

This extension was built for **RustChain Bounty #2868**: Build a VS Code Extension — RustChain Wallet & Miner Dashboard (30 RTC).

## License

MIT
