# RustChain Development Tools — VS Code Extension

A VS Code extension for [RustChain](https://github.com/Scottcjn/Rustchain) developers. Provides RTC wallet balance monitoring, miner status indicators, epoch countdown, bounty browser, config file highlighting, and code snippets for the RIP-200 Proof-of-Attestation ecosystem.

Bounty: [#2868](https://github.com/Scottcjn/rustchain-bounties/issues/2868)

## Features

### 💰 RTC Balance Status Bar
- Displays your current RTC wallet balance in the VS Code status bar.
- Auto-refreshes on a configurable interval (default 120 s).
- Click the status-bar item to set or change your miner/wallet ID.

### ⛏️ Miner Status Indicator
- Green/red status bar indicator showing whether your miner is actively attesting.
- Polls the `/api/miners` endpoint to check miner activity.
- Click to view full node health and miner details.

### ⏱️ Epoch Countdown Timer
- Shows time remaining until the next epoch settlement in the status bar.
- Displays current epoch, slot progress, enrolled miners count.
- Updates automatically every minute.

### 🎯 Bounty Browser
- Browse all open RustChain bounties directly from VS Code.
- Filter by tier (Critical, Standard, Easy) or category (Integration, Good First Issue, etc.).
- Click any bounty to open it on GitHub.
- Quick action button to claim a bounty and open the PR template.

### Config File Highlighting
- Syntax highlighting for `rustchain.toml`, `rustchain.yaml`, and `rustchain.yml`.
- Highlights RustChain-specific keywords (`miner_id`, `attestation`, `epoch`, `RTC`, `RIP-200`, hardware tiers, etc.).

### Code Snippets
- **Python** — balance check, health check, epoch info, miner listing, attestation scaffold, epoch enrollment, full miner boilerplate.
- **Shell** — curl one-liners for every API endpoint, systemd unit template.
- **RustChain Config** — node config scaffold, miner section, Ergo anchoring section.

All snippet prefixes start with `rtc-` for easy discoverability.

## Commands

| Command | Description |
|---------|-------------|
| `RustChain: Open Bounty Browser` | Open the bounty browser panel. |
| `RustChain: Claim Bounty` | Open bounty browser + PR template for quick submission. |
| `RustChain: Refresh RTC Balance` | Manually refresh all status-bar items. |
| `RustChain: Set Miner/Wallet ID` | Configure which wallet to track. |
| `RustChain: Check Node Health` | Show node health + epoch info in a dialog. |
| `RustChain: Show Epoch Info` | Focus the output panel for epoch details. |
| `RustChain: Open Miner Status` | View full miner status details. |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `rustchain.nodeUrl` | `https://50.28.86.131` | RustChain node URL. |
| `rustchain.minerId` | `""` | Your miner/wallet ID. |
| `rustchain.balanceRefreshInterval` | `120` | Balance refresh interval in seconds (min 30). |
| `rustchain.showBalance` | `true` | Show/hide the balance status-bar item. |
| `rustchain.showMinerStatus` | `true` | Show/hide the miner status indicator. |
| `rustchain.showEpochTimer` | `true` | Show/hide the epoch countdown timer. |
| `rustchain.rejectUnauthorized` | `false` | Enforce TLS cert validation (default node uses self-signed). |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Node health status |
| `GET /wallet/balance?miner_id={id}` | Wallet balance for a miner |
| `GET /epoch` | Current epoch information |
| `GET /api/miners` | List of active miners |

## Development

```bash
cd vscode-extension
npm install
npm run compile
# Press F5 in VS Code to launch the Extension Development Host
```

## Testing

```bash
# TypeScript tests (requires VS Code test runner)
npm test

# Python structural tests (from repo root)
python -m pytest tests/test_vscode_extension.py -v
```

## License

MIT — see the repository root `LICENSE` or individual SPDX headers.
