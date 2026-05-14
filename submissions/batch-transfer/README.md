# 💸 RustChain Batch Transfer Tool

Send RTC tokens to multiple addresses in one batch from a CSV file. Features progress tracking, dry-run mode, and transaction logging.

## Features

- **CSV import**: Load addresses and amounts from CSV
- **Dry-run mode**: Preview transfers without sending
- **Progress tracking**: Visual progress bar with persistence
- **Transaction log**: JSON log of all transfers
- **Memo support**: Add memos per transaction
- **Configurable delays**: Rate-limit between sends
- **Resume support**: Resume interrupted batches

## Quick Start

```bash
# Generate sample CSV
python batch.py --generate-sample

# Dry run (preview)
python batch.py --csv transfers.csv --dry-run

# Execute batch transfer
python batch.py --csv transfers.csv --from rtc1youraddress... --key YOUR_PRIVATE_KEY
```

## CSV Format

| address | amount | memo (optional) |
|---------|--------|-----------------|
| rtc1q... | 100 | Payment #1 |
| rtc1q... | 250.5 | Payment #2 |
| rtc1q... | 50 | |

```csv
address,amount,memo
rtc1qexample1...,100,Payment #1
rtc1qexample2...,250.5,Payment #2
rtc1qexample3...,50,
```

## Usage

### Generate Template
```bash
python batch.py -g
# Creates sample_transfers.csv
```

### Dry Run
```bash
python batch.py --csv transfers.csv --dry-run
```

### Live Transfer
```bash
python batch.py --csv transfers.csv --from rtc1sender... --key PRIVATE_KEY
```

### With Environment Variables
```bash
export RTC_SENDER=rtc1youraddress...
export RTC_PRIVATE_KEY=your_private_key
python batch.py --csv transfers.csv
```

### Custom RPC & Delay
```bash
python batch.py --csv transfers.csv --rpc https://my-rpcNode.com --delay 2.0
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--csv` | CSV file path | Required |
| `--from` | Sender address | Env: RTC_SENDER |
| `--key` | Private key | Env: RTC_PRIVATE_KEY |
| `--rpc` | RPC endpoint | `https://rpc.rustchain.io` |
| `--chain-id` | Chain ID | `rustchain-1` |
| `--dry-run` | Simulate only | false |
| `--delay` | Seconds between txs | 1.0 |
| `--log` | Log file path | batch_log.json |
| `--generate-sample` | Create sample CSV | - |

## Transaction Log

Each run creates a `batch_log.json` with full details:

```json
{
  "started": "2025-01-15T10:30:00",
  "total": 5,
  "completed": 4,
  "failed": 1,
  "transactions": [
    {
      "address": "rtc1q...",
      "amount": "100",
      "tx_hash": "ABC123...",
      "status": "success",
      "timestamp": "2025-01-15T10:30:01"
    }
  ]
}
```

## Security Notes

⚠️ **IMPORTANT**:
- Always run `--dry-run` first to verify your CSV
- Never share your private key
- Keep `batch_log.json` secure (contains transaction details)
- Use environment variables for keys when possible

## Dependencies

- Python 3.7+
- No external dependencies

## License

MIT License - Part of the RustChain Ecosystem
