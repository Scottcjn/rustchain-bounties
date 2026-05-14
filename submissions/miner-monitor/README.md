# RustChain Miner Monitor

A lightweight Python script that monitors a RustChain node and tracks your wallet balance in real time.

## Features

- 🩺 **Node Health Check** – polls `/health` endpoint
- 📊 **Network Stats** – block height & peer count from `/api/stats`
- 🔄 **Epoch Tracking** – current epoch & block from `/epoch`
- 💰 **Balance Monitor** – watches `/balance/{wallet}`, detects changes
- 🔔 **Notifications** – shell command trigger on balance change
- 📝 **CSV Logging** – full history with timestamps for analysis

## Installation

```bash
cd submissions/miner-monitor
pip install -r requirements.txt
```

## Configuration

Edit `config.json` (auto-created on first run with defaults):

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `node_url` | string | `https://50.28.86.131` | RustChain node URL |
| `wallet` | string | `zp6` | Wallet address to monitor |
| `poll_interval_seconds` | int | `60` | Seconds between polls |
| `history_csv` | string | `history.csv` | CSV output file path |
| `log_level` | string | `INFO` | Python log level |
| `verify_ssl` | bool | `false` | Verify TLS certificates |
| `notify_command` | string | `""` | Shell command on balance change. Use `{msg}` placeholder. |

### Notification Example (macOS)

```json
{"notify_command": "osascript -e 'display notification \"{msg}\" with title \"RustChain\"'"}
```

### Notification Example (Linux)

```json
{"notify_command": "notify-send RustChain \"{msg}\""}
```

## Usage

```bash
python monitor.py
```

Press `Ctrl+C` to stop.

## Example Output

### Console

```
2026-05-15 00:30:00,123 [INFO] RustChain Miner Monitor started
2026-05-15 00:30:00,124 [INFO] Node: https://50.28.86.131  Wallet: zp6  Interval: 60s
2026-05-15 00:30:00,456 [INFO] Health=OK  Height=145023  Peers=42  Epoch=289  Balance=1250.5
2026-05-15 00:31:00,789 [INFO] 💰 Balance changed: 1250.5 → 1253.2
2026-05-15 00:31:00,790 [INFO] Health=OK  Height=145025  Peers=43  Epoch=289  Balance=1253.2
```

### CSV (history.csv)

```csv
timestamp,health_status,block_height,peers,epoch,epoch_block,balance,pending_balance
2026-05-15T00:30:00.123456+00:00,OK,145023,42,289,1024,1250.5,0.0
2026-05-15T00:31:00.789012+00:00,OK,145025,43,289,1026,1253.2,0.0
```

## Graceful Shutdown

The monitor handles `SIGINT` and `SIGTERM` for clean shutdown.

## Requirements

- Python 3.10+
- `requests` library

## License

MIT
