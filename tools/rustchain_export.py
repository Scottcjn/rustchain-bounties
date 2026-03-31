#!/usr/bin/env python3
"""
RustChain Attestation Data Export Pipeline

Exports RustChain attestation and reward data into CSV, JSON, or JSONL formats.
Supports both live node API mode and local SQLite database mode.

Usage:
    python rustchain_export.py --format csv --output data/
    python rustchain_export.py --format json --output exports/
    python rustchain_export.py --from 2025-12-01 --to 2026-02-01 --format csv
    python rustchain_export.py --db-path ./rustchain.db --output exports/

Tables exported:
    - miners.csv(.json/.jsonl): Miner IDs, architectures, last attestation, total earnings
    - epochs.csv(.json/.jsonl): Epoch number, timestamp, pot size, settlement status
    - rewards.csv(.json/.jsonl): Per-miner per-epoch reward amounts
    - attestations.csv(.json/.jsonl): Attestation log (miner, timestamp, device info)
    - balances.csv(.json/.jsonl): Current RTC balances
"""

import argparse
import csv
import json
import sys
import os
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Any, Generator, Iterator, Optional

try:
    import requests
except ImportError:
    requests = None

# ─── Constants ────────────────────────────────────────────────────────────────

DEFAULT_NODE_BASE = "https://50.28.86.131"
API_MINERS = "/api/miners"
API_EPOCH = "/epoch"
API_BALANCE = "/wallet/balance"

# Table definitions
MINERS_TABLE = "miners"
EPOCHS_TABLE = "epochs"
REWARDS_TABLE = "rewards"
ATTESTATIONS_TABLE = "attestations"
BALANCES_TABLE = "balances"

ALL_TABLES = [MINERS_TABLE, EPOCHS_TABLE, REWARDS_TABLE, ATTESTATIONS_TABLE, BALANCES_TABLE]


# ─── Export Writers ────────────────────────────────────────────────────────────

def write_csv(rows: Iterator[dict], output_path: Path, fieldnames: list[str]) -> int:
    """Write rows to a CSV file. Returns row count."""
    count = 0
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            count += 1
    return count


def write_json(rows: Iterator[dict], output_path: Path, pretty: bool = True) -> int:
    """Write rows to a JSON file (array of objects). Returns row count."""
    data = list(rows)
    count = len(data)
    with open(output_path, "w", encoding="utf-8") as f:
        if pretty:
            json.dump(data, f, indent=2, default=str)
        else:
            json.dump(data, f, default=str)
    return count


def write_jsonl(rows: Iterator[dict], output_path: Path) -> int:
    """Write rows to a JSONL (JSON Lines) file. Returns row count."""
    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, default=str) + "\n")
            count += 1
    return count


# ─── Date Filtering ───────────────────────────────────────────────────────────

def parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {s!r}. Use YYYY-MM-DD.")


def in_date_range(row_timestamp: Any, from_date: Optional[date], to_date: Optional[date]) -> bool:
    """Check if a row's timestamp falls within the date range."""
    if not row_timestamp:
        return True
    if isinstance(row_timestamp, str):
        try:
            dt = datetime.fromisoformat(row_timestamp.replace("Z", "+00:00"))
            row_date = dt.date()
        except ValueError:
            try:
                row_date = datetime.strptime(str(row_timestamp)[:10], "%Y-%m-%d").date()
            except ValueError:
                return True
    elif isinstance(row_timestamp, datetime):
        row_date = row_timestamp.date()
    elif isinstance(row_timestamp, date):
        row_date = row_timestamp
    else:
        return True

    if from_date and row_date < from_date:
        return False
    if to_date and row_date > to_date:
        return False
    return True


# ─── API Fetcher ──────────────────────────────────────────────────────────────

def fetch_json(url: str, timeout: int = 30) -> Any:
    """Fetch JSON from a URL. Returns None on failure."""
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def fetch_api_data(
    base_url: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> dict:
    """
    Fetch all data from the live node REST API.
    Returns a dict with keys: miners, epochs, rewards, attestations, balances.
    """
    miners = fetch_json(f"{base_url}{API_MINERS}") or []
    epoch_data = fetch_json(f"{base_url}{API_EPOCH}") or {}
    balance_data = fetch_json(f"{base_url}{API_BALANCE}") or {}

    # Normalize miners
    if isinstance(miners, list):
        miner_list = miners
    elif isinstance(miners, dict) and "miners" in miners:
        miner_list = miners["miners"]
    else:
        miner_list = [miners] if miners else []

    # Normalize epoch info
    if isinstance(epoch_data, dict) and "epochs" in epoch_data:
        epoch_list = epoch_data["epochs"]
    elif isinstance(epoch_data, list):
        epoch_list = epoch_data
    else:
        epoch_list = [epoch_data] if epoch_data else []

    # Build attestations from miner data
    attestations = []
    for miner in miner_list:
        if not isinstance(miner, dict):
            continue
        attestations.append({
            "miner_id": miner.get("miner_id") or miner.get("id") or miner.get("address", ""),
            "timestamp": miner.get("last_attestation") or miner.get("last_attest") or miner.get("attestation_time", ""),
            "architecture": miner.get("architecture") or miner.get("arch", ""),
            "device_info": miner.get("device_info") or miner.get("device", "") or miner.get("fingerprint", ""),
            "status": miner.get("status", "active"),
        })

    # Build rewards from epoch data
    rewards = []
    for epoch in epoch_list:
        if not isinstance(epoch, dict):
            continue
        epoch_num = epoch.get("epoch") or epoch.get("epoch_number", 0)
        pot_size = epoch.get("pot_size") or epoch.get("reward_pool", 0)
        for miner in miner_list:
            if not isinstance(miner, dict):
                continue
            miner_id = miner.get("miner_id") or miner.get("id") or miner.get("address", "")
            # Proportional reward based on pot size divided among miners
            reward = float(pot_size) / max(len(miner_list), 1)
            rewards.append({
                "miner_id": miner_id,
                "epoch": epoch_num,
                "reward": reward,
                "timestamp": epoch.get("timestamp") or epoch.get("time", ""),
            })

    # Build miners summary
    miners_out = []
    for miner in miner_list:
        if not isinstance(miner, dict):
            continue
        miner_id = miner.get("miner_id") or miner.get("id") or miner.get("address", "")
        miners_out.append({
            "miner_id": miner_id,
            "architecture": miner.get("architecture") or miner.get("arch", ""),
            "last_attestation": miner.get("last_attestation") or miner.get("last_attest", ""),
            "total_earnings": miner.get("total_earnings") or miner.get("earnings", 0),
            "status": miner.get("status", "active"),
        })

    # Build epochs
    epochs_out = []
    for epoch in epoch_list:
        if not isinstance(epoch, dict):
            continue
        if not in_date_range(epoch.get("timestamp"), from_date, to_date):
            continue
        epochs_out.append({
            "epoch": epoch.get("epoch") or epoch.get("epoch_number", ""),
            "timestamp": epoch.get("timestamp") or epoch.get("time", ""),
            "pot_size": epoch.get("pot_size") or epoch.get("reward_pool", 0),
            "settlement_status": epoch.get("settlement_status") or epoch.get("settled", "pending"),
        })

    # Build balances
    balances_out = []
    if isinstance(balance_data, dict) and "balances" in balance_data:
        bal_list = balance_data["balances"]
    elif isinstance(balance_data, list):
        bal_list = balance_data
    else:
        bal_list = []
        for miner in miner_list:
            if not isinstance(miner, dict):
                continue
            miner_id = miner.get("miner_id") or miner.get("id") or miner.get("address", "")
            bal_list.append({"miner_id": miner_id, "balance": miner.get("balance", 0)})

    for bal in bal_list:
        if not isinstance(bal, dict):
            continue
        balances_out.append({
            "miner_id": bal.get("miner_id") or bal.get("id") or "",
            "balance": bal.get("balance") or bal.get("rtc_balance", 0),
            "last_updated": bal.get("last_updated") or bal.get("timestamp", ""),
        })

    # Filter by date range
    miners_out = [m for m in miners_out if in_date_range(m.get("last_attestation"), from_date, to_date)]
    attestations = [a for a in attestations if in_date_range(a.get("timestamp"), from_date, to_date)]
    rewards = [r for r in rewards if in_date_range(r.get("timestamp"), from_date, to_date)]

    return {
        "miners": miners_out,
        "epochs": epochs_out,
        "rewards": rewards,
        "attestations": attestations,
        "balances": balances_out,
    }


# ─── Database Fetcher ─────────────────────────────────────────────────────────

def fetch_db_data(
    db_path: str,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> dict:
    """
    Fetch all data from a local SQLite database.
    Falls back to sample/seed data if tables don't exist (for demo purposes).
    """
    if not os.path.exists(db_path):
        print(f"  [WARN] Database not found: {db_path}. Using seed data.", file=sys.stderr)
        return generate_seed_data(from_date, to_date)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ── Miners ─────────────────────────────────────────────────────────────────
    miners_out = []
    try:
        cur.execute("SELECT * FROM miners LIMIT 1000")
        cols = [d[0] for d in cur.description]
        for row in cur.fetchall():
            r = dict(zip(cols, row))
            if in_date_range(r.get("last_attestation"), from_date, to_date):
                miners_out.append({
                    "miner_id": r.get("miner_id") or r.get("id") or r.get("address", ""),
                    "architecture": r.get("architecture") or r.get("arch", ""),
                    "last_attestation": r.get("last_attestation") or r.get("last_attest", ""),
                    "total_earnings": r.get("total_earnings") or r.get("earnings", 0),
                    "status": r.get("status", "active"),
                })
    except sqlite3.OperationalError:
        pass

    # ── Epochs ─────────────────────────────────────────────────────────────────
    epochs_out = []
    for table_name in ["epoch_state", "epochs"]:
        try:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 5000")
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                r = dict(zip(cols, row))
                ts = r.get("timestamp") or r.get("time") or r.get("created_at", "")
                if in_date_range(ts, from_date, to_date):
                    epochs_out.append({
                        "epoch": r.get("epoch") or r.get("epoch_number", ""),
                        "timestamp": ts,
                        "pot_size": r.get("pot_size") or r.get("reward_pool", 0),
                        "settlement_status": r.get("settlement_status") or r.get("settled", "pending"),
                    })
            break
        except sqlite3.OperationalError:
            continue

    # ── Rewards ────────────────────────────────────────────────────────────────
    rewards_out = []
    for table_name in ["epoch_rewards", "rewards"]:
        try:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 10000")
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                r = dict(zip(cols, row))
                ts = r.get("timestamp") or r.get("time", "")
                if in_date_range(ts, from_date, to_date):
                    rewards_out.append({
                        "miner_id": r.get("miner_id") or r.get("id") or r.get("address", ""),
                        "epoch": r.get("epoch") or r.get("epoch_number", ""),
                        "reward": r.get("reward") or r.get("amount", 0),
                        "timestamp": ts,
                    })
            break
        except sqlite3.OperationalError:
            continue

    # ── Attestations ───────────────────────────────────────────────────────────
    attestations_out = []
    for table_name in ["miner_attest_recent", "attestations"]:
        try:
            cur.execute(f"SELECT * FROM {table_name} LIMIT 10000")
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                r = dict(zip(cols, row))
                ts = r.get("timestamp") or r.get("attestation_time") or r.get("time", "")
                if in_date_range(ts, from_date, to_date):
                    attestations_out.append({
                        "miner_id": r.get("miner_id") or r.get("id") or r.get("address", ""),
                        "timestamp": ts,
                        "architecture": r.get("architecture") or r.get("arch", ""),
                        "device_info": r.get("device_info") or r.get("fingerprint", "") or r.get("device", ""),
                        "status": r.get("status", "active"),
                    })
            break
        except sqlite3.OperationalError:
            continue

    # ── Balances ───────────────────────────────────────────────────────────────
    balances_out = []
    try:
        cur.execute("SELECT * FROM balances LIMIT 5000")
        cols = [d[0] for d in cur.description]
        for row in cur.fetchall():
            r = dict(zip(cols, row))
            balances_out.append({
                "miner_id": r.get("miner_id") or r.get("id") or r.get("address", ""),
                "balance": r.get("balance") or r.get("rtc_balance", 0),
                "last_updated": r.get("last_updated") or r.get("timestamp", ""),
            })
    except sqlite3.OperationalError:
        pass

    conn.close()

    # Fall back to seed data if nothing found
    if not any([miners_out, epochs_out, rewards_out, attestations_out, balances_out]):
        print(f"  [WARN] No known tables found in {db_path}. Using seed data.", file=sys.stderr)
        return generate_seed_data(from_date, to_date)

    return {
        "miners": miners_out,
        "epochs": epochs_out,
        "rewards": rewards_out,
        "attestations": attestations_out,
        "balances": balances_out,
    }


# ─── Seed / Demo Data ──────────────────────────────────────────────────────────

def generate_seed_data(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> dict:
    """Generate realistic seed data for demo/testing when no data source is available."""

    def make_date(d: str) -> str:
        return d

    epochs_data = [
        {"epoch": 1000, "timestamp": "2025-12-01T00:00:00Z", "pot_size": 500.0, "settlement_status": "settled"},
        {"epoch": 1001, "timestamp": "2025-12-02T00:00:00Z", "pot_size": 520.0, "settlement_status": "settled"},
        {"epoch": 1002, "timestamp": "2025-12-03T00:00:00Z", "pot_size": 480.0, "settlement_status": "settled"},
        {"epoch": 1003, "timestamp": "2025-12-15T00:00:00Z", "pot_size": 610.0, "settlement_status": "settled"},
        {"epoch": 1004, "timestamp": "2026-01-01T00:00:00Z", "pot_size": 750.0, "settlement_status": "settled"},
        {"epoch": 1005, "timestamp": "2026-01-15T00:00:00Z", "pot_size": 820.0, "settlement_status": "settled"},
        {"epoch": 1006, "timestamp": "2026-02-01T00:00:00Z", "pot_size": 900.0, "settlement_status": "settled"},
        {"epoch": 1007, "timestamp": "2026-02-15T00:00:00Z", "pot_size": 870.0, "settlement_status": "settled"},
        {"epoch": 1008, "timestamp": "2026-03-01T00:00:00Z", "pot_size": 950.0, "settlement_status": "settled"},
        {"epoch": 1009, "timestamp": "2026-03-15T00:00:00Z", "pot_size": 1010.0, "settlement_status": "settled"},
    ]

    miners_data = [
        {
            "miner_id": "0xAa1f2d3E4b5C6e7F8a9B0c1D2e3F4a5B6c7D8e9F",
            "architecture": "PowerPC G5", "last_attestation": "2026-03-30T12:00:00Z",
            "total_earnings": 2450.75, "status": "active",
        },
        {
            "miner_id": "0xBb2e3F4a5B6c7D8e9F0a1B2c3D4e5F6a7B8c9D0e",
            "architecture": "SPARC v9", "last_attestation": "2026-03-29T18:30:00Z",
            "total_earnings": 1890.30, "status": "active",
        },
        {
            "miner_id": "0xCc3f4A5b6C7d8E9f0A1b2C3d4E5f6A7b8C9d0E1f",
            "architecture": "68K Mac II", "last_attestation": "2026-03-28T09:15:00Z",
            "total_earnings": 3201.50, "status": "active",
        },
        {
            "miner_id": "0xDd4a5B6c7D8e9F0a1B2c3D4e5F6a7B8c9D0e1F2a",
            "architecture": "PowerPC G4", "last_attestation": "2026-03-27T22:45:00Z",
            "total_earnings": 980.20, "status": "active",
        },
        {
            "miner_id": "0xEe5b6C7d8E9f0A1b2C3d4E5f6A7b8C9d0E1f2A3b",
            "architecture": "x86_64", "last_attestation": "2026-03-26T14:00:00Z",
            "total_earnings": 450.10, "status": "active",
        },
        {
            "miner_id": "0xFf6c7D8e9F0a1B2c3D4e5F6a7B8c9D0e1F2a3B4c",
            "architecture": "ARM64", "last_attestation": "2026-03-25T11:30:00Z",
            "total_earnings": 320.80, "status": "active",
        },
        {
            "miner_id": "0x11Aa7B8c9D0e1F2a3B4c5D6e7F8a9B0c1D2e3F4",
            "architecture": "PowerPC G4", "last_attestation": "2026-03-24T16:00:00Z",
            "total_earnings": 712.60, "status": "active",
        },
        {
            "miner_id": "0x22Bb8C9d0E1f2A3b4C5d6E7f8A9b0C1d2E3f4A5b",
            "architecture": "68K Quadra", "last_attestation": "2026-03-23T08:20:00Z",
            "total_earnings": 550.40, "status": "active",
        },
        {
            "miner_id": "0x33Cc9D0e1F2a3B4c5D6e7F8a9B0c1D2e3F4a5B6c",
            "architecture": "RISC-V", "last_attestation": "2026-03-22T19:10:00Z",
            "total_earnings": 185.30, "status": "active",
        },
    ]

    # Filter by date
    filtered_epochs = [e for e in epochs_data if in_date_range(e["timestamp"], from_date, to_date)]
    filtered_miners = [m for m in miners_data if in_date_range(m["last_attestation"], from_date, to_date)]

    # Build rewards
    rewards_data = []
    for epoch in filtered_epochs:
        pot = epoch["pot_size"]
        n = len(filtered_miners)
        for miner in filtered_miners:
            multiplier = 2.0 if "PowerPC" in miner["architecture"] or "68K" in miner["architecture"] or "SPARC" in miner["architecture"] else 1.0
            reward = round((pot / n) * multiplier, 4)
            rewards_data.append({
                "miner_id": miner["miner_id"],
                "epoch": epoch["epoch"],
                "reward": reward,
                "timestamp": epoch["timestamp"],
            })

    # Build attestations
    attestations_data = []
    for miner in filtered_miners:
        attestations_data.append({
            "miner_id": miner["miner_id"],
            "timestamp": miner["last_attestation"],
            "architecture": miner["architecture"],
            "device_info": f"fingerprint:{miner['miner_id'][:16]}",
            "status": miner["status"],
        })

    # Build balances
    balances_data = [
        {"miner_id": m["miner_id"], "balance": round(m["total_earnings"], 4), "last_updated": m["last_attestation"]}
        for m in filtered_miners
    ]

    return {
        "miners": filtered_miners,
        "epochs": filtered_epochs,
        "rewards": rewards_data,
        "attestations": attestations_data,
        "balances": balances_data,
    }


# ─── Table Field Definitions ───────────────────────────────────────────────────

FIELD_DEFINITIONS = {
    MINERS_TABLE: ["miner_id", "architecture", "last_attestation", "total_earnings", "status"],
    EPOCHS_TABLE: ["epoch", "timestamp", "pot_size", "settlement_status"],
    REWARDS_TABLE: ["miner_id", "epoch", "reward", "timestamp"],
    ATTESTATIONS_TABLE: ["miner_id", "timestamp", "architecture", "device_info", "status"],
    BALANCES_TABLE: ["miner_id", "balance", "last_updated"],
}


# ─── Streaming Row Iterator ────────────────────────────────────────────────────

def iter_rows(data: list) -> Generator[dict, None, None]:
    yield from data


# ─── Main Export ──────────────────────────────────────────────────────────────

def run_export(
    tables: list[str],
    output_dir: Path,
    fmt: str,
    mode: str,
    node_url: str,
    db_path: Optional[str],
    from_date: Optional[date],
    to_date: Optional[date],
) -> dict:
    """Run the export and return stats."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Fetch data
    if mode == "api":
        data = fetch_api_data(node_url, from_date, to_date)
        source = f"API ({node_url})"
    elif mode == "db":
        data = fetch_db_data(db_path, from_date, to_date)
        source = f"DB ({db_path})"
    else:
        # Auto: try API first, fall back to DB, then seed
        data = fetch_api_data(node_url, from_date, to_date)
        if not any(data.values()):
            data = fetch_db_data(db_path, from_date, to_date)
        if not any(data.values()):
            data = generate_seed_data(from_date, to_date)
        source = "auto (API→DB→seed)"

    print(f"Data source: {source}", file=sys.stderr)

    stats = {}
    for table in tables:
        rows = data.get(table, [])
        fieldnames = FIELD_DEFINITIONS.get(table, list(rows[0].keys()) if rows else [])

        if fmt == "csv":
            out_path = output_dir / f"{table}.csv"
            count = write_csv(iter_rows(rows), out_path, fieldnames)
        elif fmt == "json":
            out_path = output_dir / f"{table}.json"
            count = write_json(iter_rows(rows), out_path)
        elif fmt == "jsonl":
            out_path = output_dir / f"{table}.jsonl"
            count = write_jsonl(iter_rows(rows), out_path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

        stats[table] = count
        print(f"  [OK] {out_path} ({count} rows)")

    return stats


# ─── CLI ──────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RustChain Attestation Data Export Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rustchain_export.py --format csv --output data/
  python rustchain_export.py --format json --output exports/ --node-url https://50.28.86.131
  python rustchain_export.py --from 2025-12-01 --to 2026-02-01 --format csv --output data/
  python rustchain_export.py --db-path ./rustchain.db --output exports/
  python rustchain_export.py --tables miners epochs --format jsonl --output data/
        """,
    )
    parser.add_argument(
        "--format", "-f", choices=["csv", "json", "jsonl"], default="csv",
        help="Output format (default: csv)",
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=Path("."),
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--node-url", type=str, default=DEFAULT_NODE_BASE,
        help=f"Node API base URL (default: {DEFAULT_NODE_BASE})",
    )
    parser.add_argument(
        "--mode", "-m", choices=["api", "db", "auto"], default="auto",
        help="Data source mode: api (live node), db (local SQLite), auto (default)",
    )
    parser.add_argument(
        "--db-path", type=str, default="rustchain.db",
        help="Path to local SQLite database (for db mode)",
    )
    parser.add_argument(
        "--from", dest="from_date", type=str, default=None,
        help="Start date (YYYY-MM-DD), inclusive",
    )
    parser.add_argument(
        "--to", dest="to_date", type=str, default=None,
        help="End date (YYYY-MM-DD), inclusive",
    )
    parser.add_argument(
        "--tables", "-t", nargs="+",
        choices=ALL_TABLES + ["all"],
        default=["all"],
        help="Tables to export (default: all)",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    from_date = parse_date(args.from_date)
    to_date = parse_date(args.to_date)

    if from_date and to_date and from_date > to_date:
        print("Error: --from date must be before --to date", file=sys.stderr)
        sys.exit(1)

    tables = ALL_TABLES if "all" in args.tables else args.tables

    # Validate tables
    invalid = set(tables) - set(ALL_TABLES)
    if invalid:
        print(f"Error: Unknown tables: {invalid}. Valid: {ALL_TABLES}", file=sys.stderr)
        sys.exit(1)

    print(f"RustChain Export — format={args.format} mode={args.mode}")
    if from_date:
        print(f"  Date range: {from_date}", end="")
        print(f" to {to_date}" if to_date else " to today")
    print(f"  Tables: {', '.join(tables)}")
    print(f"  Output: {args.output.absolute()}")
    print()

    stats = run_export(
        tables=tables,
        output_dir=args.output,
        fmt=args.format,
        mode=args.mode,
        node_url=args.node_url,
        db_path=args.db_path,
        from_date=from_date,
        to_date=to_date,
    )

    total = sum(stats.values())
    print(f"\nExport complete: {total} total rows across {len(stats)} files.")


if __name__ == "__main__":
    main()
