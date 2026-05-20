# RustChain Notification Bot

Real-time monitoring bot for RustChain — get alerts on balance changes and epoch transitions via Telegram or Discord.

## Features

- 🔍 **Balance Monitoring** — track wallet balance changes with configurable thresholds
- 🔄 **Epoch Tracking** — get notified on epoch transitions
- 📢 **Multi-channel** — Telegram bot + Discord webhook support
- ⚙️ **Configurable Rules** — set thresholds, enable/disable channels per rule
- 🔁 **Polling** — configurable poll interval with graceful error handling

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and edit config
cp config.example.json config.json
# Edit config.json with your API URL, wallet addresses, and bot tokens

# Run
python bot.py -c config.json

# One-shot mode (single check, for testing)
python bot.py -c config.json --once
```

## Configuration

Copy `config.example.json` to `config.json` and fill in:

| Field | Description |
|---|---|
| `api.base_url` | RustChain REST API base URL |
| `api.timeout` | Request timeout in seconds (default: 15) |
| `poll_interval_seconds` | Seconds between check cycles (default: 30) |
| `wallets` | List of wallet addresses to monitor |
| `channels.telegram` | Telegram bot token + chat ID |
| `channels.discord` | Discord webhook URL |
| `rules.balance_change.threshold` | Minimum balance delta to trigger notification (0 = any change) |

## Notification Rules

### Balance Change
Triggers when a wallet's balance changes by at least the configured threshold. Set `threshold: 0` to alert on any change.

### Epoch Change
Triggers on every epoch transition with full epoch metadata.

### Error Alerts
Sends error notifications when API calls fail. Disable with `rules.errors.enabled: false`.

## Architecture

```
bot.py
├── RustChainClient   — API wrapper (balance, epoch, network info)
├── Notifier          — Rule engine + multi-channel dispatch
├── run_monitor()     — Main polling loop with state tracking
└── CLI               — argparse entry point
```

## Dependencies

- `requests` — HTTP client for API calls and webhook delivery

## License

MIT
