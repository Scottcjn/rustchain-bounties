# RustChain Attestation Data Export Pipeline

Export RustChain attestation and reward data into **CSV**, **JSON**, or **JSONL** formats for analysis, tax reporting, and compliance.

## Features

- ✅ Exports all 5 data types: `miners`, `epochs`, `rewards`, `attestations`, `balances`
- ✅ Date range filtering (`--from` / `--to`)
- ✅ Multiple output formats: CSV, JSON, JSONL
- ✅ Works with **live node API** or **local SQLite** database
- ✅ Streaming writes (memory-efficient for large datasets)
- ✅ Seed/demo data when no data source is available

## Quick Start

```bash
# CSV export (all tables, current directory)
python tools/rustchain_export.py --format csv --output data/

# JSON export with date filter
python tools/rustchain_export.py --format json --output exports/ \
    --from 2025-12-01 --to 2026-02-01

# JSONL export from live node API
python tools/rustchain_export.py --format jsonl --output data/ \
    --node-url https://50.28.86.131

# Export specific tables only
python tools/rustchain_export.py --format csv --output data/ \
    --tables miners rewards

# Use local SQLite database
python tools/rustchain_export.py --format csv --output data/ \
    --mode db --db-path ./rustchain.db
```

## Output Files

| File | Description |
|------|-------------|
| `miners.csv` | Miner IDs, architectures, last attestation, total earnings, status |
| `epochs.csv` | Epoch number, timestamp, pot size, settlement status |
| `rewards.csv` | Per-miner per-epoch reward amounts and timestamps |
| `attestations.csv` | Attestation log (miner, timestamp, architecture, device info) |
| `balances.csv` | Current RTC balances per miner |

## Command-Line Options

| Flag | Description |
|------|-------------|
| `--format`, `-f` | Output format: `csv`, `json`, `jsonl` (default: `csv`) |
| `--output`, `-o` | Output directory (default: current directory) |
| `--node-url` | Live node API base URL (default: `https://50.28.86.131`) |
| `--mode`, `-m` | Data source: `api`, `db`, `auto` (default: `auto`) |
| `--db-path` | Path to local SQLite database (for `--mode db`) |
| `--from` | Start date (YYYY-MM-DD), inclusive |
| `--to` | End date (YYYY-MM-DD), inclusive |
| `--tables`, `-t` | Which tables to export: `miners`, `epochs`, `rewards`, `attestations`, `balances`, or `all` |

## Date Filtering

Filter exports by date range using `--from` and `--to`:

```bash
# Export December 2025 data only
python tools/rustchain_export.py --format csv --output data/ \
    --from 2025-12-01 --to 2025-12-31

# Export Q1 2026
python tools/rustchain_export.py --format json --output data/ \
    --from 2026-01-01 --to 2026-03-31
```

## Data Source Modes

### API Mode (`--mode api`)
Connects to the live RustChain node REST API. Works remotely, ideal for most use cases.

```bash
python tools/rustchain_export.py --mode api \
    --node-url https://50.28.86.131 \
    --format csv --output data/
```

### DB Mode (`--mode db`)
Reads directly from a local SQLite database. Requires SSH access to the node for full data.

```bash
python tools/rustchain_export.py --mode db \
    --db-path ./rustchain.db \
    --format csv --output data/
```

### Auto Mode (`--mode auto`)
Tries API first, falls back to DB, then to built-in seed data if neither is available.

```bash
python tools/rustchain_export.py --mode auto --format csv --output data/
```

## CSV Format

All CSV files include headers and proper escaping:

```csv
miner_id,architecture,last_attestation,total_earnings,status
0xAa1f2d3E...,PowerPC G5,2026-03-30T12:00:00Z,2450.75,active
0xBb2e3F4a...,SPARC v9,2026-03-29T18:30:00Z,1890.30,active
```

## JSON Format

```json
[
  {
    "miner_id": "0xAa1f2d3E...",
    "architecture": "PowerPC G5",
    "last_attestation": "2026-03-30T12:00:00Z",
    "total_earnings": 2450.75,
    "status": "active"
  }
]
```

## JSONL Format (Streaming)

Each line is a valid JSON object — ideal for large datasets:

```jsonl
{"miner_id": "0xAa1f2d3E...", "architecture": "PowerPC G5", ...}
{"miner_id": "0xBb2e3F4a...", "architecture": "SPARC v9", ...}
```

## Requirements

```bash
pip install requests
```

## Node API Endpoints Used

- `GET /api/miners` — List all miners
- `GET /epoch` — Epoch information
- `GET /wallet/balance` — Balance information

## Database Tables (DB Mode)

The tool auto-detects these tables in the local SQLite database:

- `miners` / `miner_attest_recent`
- `epoch_state` / `epochs`
- `epoch_rewards` / `rewards`
- `balances`

---

**Bounty**: 25 RTC · Issue [#49](https://github.com/Scottcjn/rustchain-bounties/issues/49)
