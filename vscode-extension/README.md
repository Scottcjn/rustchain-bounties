# RustChain Development Tools — VS Code Extension

A VS Code extension for [RustChain](https://github.com/Scottcjn/RustChain) developers. Provides RTC balance monitoring, wallet dashboard view, miner listing, config file highlighting, and code snippets for the RIP-200 Proof-of-Attestation ecosystem.

**Bounty:** [#2868](https://github.com/Scottcjn/rustchain-bounties/issues/2868) · **Reward:** 30 RTC
**Wallet:** `RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5`

## Features

### RTC Balance Status Bar
- Displays your current RTC wallet balance in the VS Code status bar.
- Auto-refreshes on a configurable interval (default 120 s).
- Click the status-bar item to set or change your miner/wallet ID.

### Wallet Dashboard View
- Opens via **RustChain: Open Wallet Dashboard** command.
- Shows balance, node health, current epoch, and recent transactions.
- Quick action buttons for transfer, list miners, and claim bounty.
- Auto-refreshes with configurable interval.
- Includes mock API mode for development/demo when node is unreachable.

### Command Palette Commands
| Command | Description |
|---------|-------------|
| `RustChain: Refresh RTC Balance` | Manually refresh the balance display. |
| `RustChain: Set Miner/Wallet ID` | Configure which wallet to track. |
| `RustChain: Check Node Health` | Show node health + epoch info in a dialog. |
| `RustChain: Open Wallet Dashboard` | Open the full wallet dashboard view. |
| `RustChain: List Active Miners` | View all active miners on the network. |
| `RustChain: Transfer RTC` | Transfer RTC to another wallet. |
| `RustChain: View Transactions` | View recent transactions for your wallet. |
| `RustChain: Claim Bounty` | Claim a RustChain bounty by issue number. |

### Config File Highlighting
- Syntax highlighting for `rustchain.toml`, `rustchain.yaml`, and `rustchain.yml`.
- Highlights RustChain-specific keywords (`miner_id`, `attestation`, `epoch`, `RTC`, `RIP-200`, hardware tiers, etc.).

### Code Snippets
- **Python** — balance check, health check, epoch info, miner listing, attestation scaffold, epoch enrollment, full miner boilerplate.
- **Shell** — curl one-liners for every API endpoint, systemd unit template.
- **RustChain Config** — node config scaffold, miner section, Ergo anchoring section.

All snippet prefixes start with `rtc-` for easy discoverability.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `rustchain.nodeUrl` | `https://50.28.86.131` | RustChain node URL. |
| `rustchain.minerId` | `""` | Your miner/wallet ID. |
| `rustchain.balanceRefreshInterval` | `120` | Refresh interval in seconds (min 30). |
| `rustchain.showBalance` | `true` | Show/hide the balance status-bar item. |
| `rustchain.rejectUnauthorized` | `false` | Enforce TLS cert validation (default node uses self-signed). |
| `rustchain.useMockApi` | `true` | Use mock API responses when node is unreachable. |

## Installation

### From VS Code Marketplace
1. Open VS Code and go to Extensions (`Ctrl+Shift+X`)
2. Search for "RustChain"
3. Click Install

### From Source
```bash
cd vscode-extension
npm install
npm run compile
code --install-extension out/rustchain-dev-*.vsix
```

### Enable the Extension
1. Go to Settings (`Ctrl+,`)
2. Search for `rustchain.minerId`
3. Enter your RustChain miner/wallet ID (e.g., `RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5`)

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

## Mock API Mode

When `rustchain.useMockApi` is enabled (default), the extension will return realistic mock data when the RustChain node at `https://50.28.86.131:8099` is unreachable. This allows:

- Testing the extension without a live node connection
- Demo and development workflows
- UI development without blockchain dependency

Mock data includes:
- Fake balance: 100-1100 RTC based on miner ID
- Mock health status, epoch info, and miner list
- Simulated transactions

## Bounty Information

- **Issue:** [Scottcjn/rustchain-bounties#2868](https://github.com/Scottcjn/rustchain-bounties/issues/2868)
- **Reward:** 30 RTC
- **Payout Wallet:** `RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5`
- **Node API:** `https://50.28.86.131:8099` (may be unreachable — mock mode available)

## License

MIT — see the repository root `LICENSE` or individual SPDX headers.
