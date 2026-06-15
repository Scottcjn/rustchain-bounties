# RustChain Data Export Pipeline

A standalone tool that extracts RustChain attestation and reward data into standard formats (CSV, JSON, JSONL) for analysis, reporting, and compliance.

## Features

- **Multiple export formats**: CSV, JSON array, JSON Lines
- **Date range filtering**: `--from` and `--to` flags
- **API-only mode**: Works remotely against any RustChain node
- **SQLite fallback**: Use local database when API is unavailable
- **Data validation**: Row counts and manifest generation
- **Memory efficient**: Streaming/pagination ready for large datasets

## Installation

```bash
cd tools/
pip install -r requirements.txt  # needs requests
```

## Usage

```bash
# CSV export (default)
python rustchain_export.py --format csv --output data/

# JSON export with date range
python rustchain_export.py --format json --from 2025-12-01 --to 2026-02-01

# JSON Lines export
python rustchain_export.py --format jsonl --output exports/

# Custom node URL
python rustchain_export.py --node-url https://my-rustchain.local --format csv

# SQLite fallback mode
python rustchain_export.py --sqlite /path/to/rustchain.db --format csv
```

## Output Files

| File | Description |
|------|-------------|
| `miners.csv` | All miner IDs, architectures, last attestation, total earnings |
| `epochs.csv` | Epoch number, timestamp, pot size, settlement status |
| `rewards.csv` | Per-miner per-epoch reward amounts |
| `attestations.csv` | Attestation log (miner, timestamp, device info) |
| `balances.csv` | Current RTC balances |
| `manifest.json` | Export metadata and row counts |

## API Endpoints Used

- `GET /api/miners` — Active miner list
- `GET /wallet/balance?miner_id=X` — Per-miner balance
- `GET /health` — Node health check

## Bounty

Implements [Issue #49](https://github.com/Scottcjn/rustchain-bounties/issues/49) — Attestation Data Export Pipeline (25 RTC reward).

## License

MIT — same as rustchain-bounties repository.
