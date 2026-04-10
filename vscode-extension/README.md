# RustChain Dashboard - VS Code Extension

**Bounty: #2868 - 30 RTC**

A VS Code extension that displays your RustChain wallet balance, miner status, and bounty board directly in your IDE.

## Features

### 1. Wallet Balance (Status Bar)
- Shows your RTC balance in the VS Code status bar
- Real-time updates every 60 seconds
- Click to refresh

### 2. Miner Status
- Green indicator when your miner is actively attesting
- Red indicator when offline or not mining

### 3. Bounty Browser (Sidebar)
- Browse all open RustChain bounties
- Click to open bounty in browser
- Quick claim functionality

### 4. Epoch Timer
- Shows current epoch and countdown
- Tracks mining schedule

### 5. Quick Actions
- "Claim Bounty" button opens PR template
- Direct links to bounty board

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties/vscode-extension

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Package the extension
npx vsce package

# Install (in VS Code)
# Extensions view -> ... -> Install from VSIX
```

### VS Code Marketplace (after publishing)

```bash
code --install-extension shuziyoumin2.rustchain-dashboard
```

## Configuration

Add to your VS Code settings (`.vscode/settings.json`):

```json
{
  "rustchain.walletName": "your_wallet_name",
  "rustchain.nodeUrl": "https://50.28.86.131",
  "rustchain.refreshInterval": 60
}
```

### Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `rustchain.walletName` | string | "" | Your RustChain wallet name |
| `rustchain.nodeUrl` | string | "https://50.28.86.131" | RustChain node URL |
| `rustchain.refreshInterval` | number | 60 | Auto-refresh interval in seconds |

## Usage

### Status Bar
- Shows ◎ XX.XX RTC when connected
- Shows ❌ Offline when connection fails
- Click to manually refresh

### Bounty Browser
1. Open the RustChain sidebar (🦀 icon in Activity Bar)
2. View all open bounties
3. Click any bounty to open in GitHub
4. Use "Claim Bounty" command to start working

### Commands

Open Command Palette (Ctrl/Cmd + Shift + P):

- `RustChain: Refresh` - Manually refresh dashboard
- `RustChain: Claim Bounty` - Open bounty by number

## API Endpoints

This extension uses the following RustChain API endpoints:

```
GET https://50.28.86.131/health
GET https://50.28.86.131/wallet/balance?wallet_id={name}
GET https://50.28.86.131/epoch
GET https://50.28.86.131/api/miners
```

## Development

### Prerequisites

- Node.js 16+
- VS Code 1.75+
- npm 8+

### Setup

```bash
npm install
npm run watch  # For development with hot reload
```

### Testing

```bash
# Run extension in VS Code Extension Development Host
F5 in VS Code

# Or test manually
npx vscode-test-host
```

## Compatibility

- ✅ VS Code 1.75+
- ✅ Cursor (MCP compatible)
- ✅ Windsurf
- ✅ VSCodium

## Extension Size

< 5MB (meets requirement)

## File Structure

```
vscode-extension/
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript configuration
├── README.md             # This file
├── media/
│   └── icon.png          # Extension icon
└── src/
    └── extension.ts      # Main extension code
```

## Publishing

```bash
# Login to VS Code Marketplace
npx vsce login shuziyoumin2

# Publish
npx vsce publish

# Or package for manual installation
npx vsce package
```

## License

MIT - Same as RustChain project

## Wallet for RTC Rewards

shuziyoumin2_bot

---

**Earn RTC by contributing to RustChain!**
