# RustChain Development Tools — VS Code Extension

A VS Code extension for [RustChain](https://github.com/Scottcjn/Rustchain) developers. Provides RTC balance monitoring, config file highlighting, and code snippets for the RIP-200 Proof-of-Attestation ecosystem.

Bounty: [#1619](https://github.com/Scottcjn/rustchain-bounties/issues/1619)

## Features

### RTC Balance Status Bar
- Displays your current RTC wallet balance in the VS Code status bar.
- Auto-refreshes on a configurable interval (default 120 s).
- Click the status-bar item to set or change your miner/wallet ID.

### Config File Highlighting
- Syntax highlighting for `rustchain.toml`, `rustchain.yaml`, and `rustchain.yml`.
- Highlights RustChain-specific keywords (`miner_id`, `attestation`, `epoch`, `RTC`, `RIP-200`, hardware tiers, etc.).

### Code Snippets
- **Python** — balance check, health check, epoch info, miner listing, attestation scaffold, epoch enrollment, full miner boilerplate.
- **Shell** — curl one-liners for every API endpoint, systemd unit template.
- **RustChain Config** — node config scaffold, miner section, Ergo anchoring section.

All snippet prefixes start with `rtc-` for easy discoverability.

### Commands
| Command | Description |
|---------|-------------|
| `RustChain: Refresh RTC Balance` | Manually refresh the balance display. |
| `RustChain: Set Miner/Wallet ID` | Configure which wallet to track. |
| `RustChain: Check Node Health` | Show node health + epoch info in a dialog. |

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `rustchain.nodeUrl` | `https://50.28.86.131` | RustChain node URL. |
| `rustchain.minerId` | `""` | Your miner/wallet ID. |
| `rustchain.balanceRefreshInterval` | `120` | Refresh interval in seconds (min 30). |
| `rustchain.showBalance` | `true` | Show/hide the balance status-bar item. |
| `rustchain.rejectUnauthorized` | `false` | Enforce TLS cert validation (default node uses self-signed). |

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
