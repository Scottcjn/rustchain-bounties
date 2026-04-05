#!/usr/bin/env python3
"""
RustChain Attestation Data Export Pipeline
Issue #2824 - Bounty: 25 RTC

Exports RustChain attestation and reward data in multiple formats:
- CSV
- JSON
- JSONL (JSON Lines)
- Parquet

Exported tables:
- miners
- epochs
- rewards
- attestations
- balances

Usage:
    python3 rustchain_export.py --format csv --output data/
    python3 rustchain_export.py --format json --output data/ --from 2025-12-01 --to 2026-02-01
    python3 rustchain_export.py --format jsonl --output data/ --api-only
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: 'requests' not installed. API-only mode will not work.")
    print("Install with: pip install requests")

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False
    print("Warning: 'pyarrow' not installed. Parquet export will not work.")
    print("Install with: pip install pyarrow")


# Configuration
RUSTCHAIN_NODE = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
TIMEOUT = 30


def fetch_api(endpoint: str) -> List[Dict]:
    """Fetch data from RustChain API."""
    if not HAS_REQUESTS:
        print(f"Error: requests library not available")
        return []
    
    url = f"{RUSTCHAIN_NODE}{endpoint}"
    try:
        resp = requests.get(url, timeout=TIMEOUT, verify=False)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
        return []


def export_csv(data: List[Dict], filepath: Path) -> int:
    """Export data to CSV format."""
    if not data:
        return 0
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    return len(data)


def export_json(data: List[Dict], filepath: Path) -> int:
    """Export data to JSON format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return len(data)


def export_jsonl(data: List[Dict], filepath: Path) -> int:
    """Export data to JSON Lines format."""
    with open(filepath, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    
    return len(data)


def export_parquet(data: List[Dict], filepath: Path) -> int:
    """Export data to Parquet format."""
    if not HAS_PYARROW:
        print(f"Error: pyarrow not available for {filepath}")
        return 0
    
    if not data:
        return 0
    
    table = pa.Table.from_pylist(data)
    pq.write_table(table, filepath)
    
    return len(data)


def export_data(
    data: List[Dict],
    output_dir: Path,
    table_name: str,
    format: str
) -> int:
    """Export data to specified format."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if format == 'csv':
        filepath = output_dir / f"{table_name}.csv"
        return export_csv(data, filepath)
    elif format == 'json':
        filepath = output_dir / f"{table_name}.json"
        return export_json(data, filepath)
    elif format == 'jsonl':
        filepath = output_dir / f"{table_name}.jsonl"
        return export_jsonl(data, filepath)
    elif format == 'parquet':
        filepath = output_dir / f"{table_name}.parquet"
        return export_parquet(data, filepath)
    else:
        print(f"Error: Unknown format '{format}'")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description='Export RustChain attestation data to CSV/JSON/Parquet'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['csv', 'json', 'jsonl', 'parquet'],
        default='csv',
        help='Output format (default: csv)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('data'),
        help='Output directory (default: data/)'
    )
    parser.add_argument(
        '--from',
        dest='from_date',
        type=str,
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--to',
        dest='to_date',
        type=str,
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Use API only, skip local database'
    )
    parser.add_argument(
        '--tables', '-t',
        nargs='+',
        choices=['miners', 'epochs', 'rewards', 'attestations', 'balances', 'all'],
        default=['all'],
        help='Tables to export (default: all)'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RustChain Attestation Data Export Pipeline")
    print("=" * 60)
    print(f"Format: {args.format}")
    print(f"Output: {args.output}")
    print(f"API: {RUSTCHAIN_NODE}")
    if args.from_date:
        print(f"From: {args.from_date}")
    if args.to_date:
        print(f"To: {args.to_date}")
    print()
    
    # Determine tables to export
    if 'all' in args.tables:
        tables = ['miners', 'epochs', 'rewards', 'attestations', 'balances']
    else:
        tables = args.tables
    
    # Export each table
    total_records = 0
    for table in tables:
        print(f"Exporting {table}...")
        
        # Fetch data from API
        endpoint = f"/api/{table}"
        data = fetch_api(endpoint)
        
        if not data:
            print(f"  No data found for {table}")
            continue
        
        # Apply date filtering if specified
        if args.from_date or args.to_date:
            filtered = []
            for record in data:
                # Try to find date field
                date_val = record.get('timestamp') or record.get('date') or record.get('created_at')
                if date_val:
                    try:
                        # Python 3.6 compatibility - use strptime instead of fromisoformat
                        if 'T' in date_val:
                            record_date = datetime.strptime(date_val.split('T')[0], '%Y-%m-%d').date()
                        else:
                            record_date = datetime.strptime(date_val, '%Y-%m-%d').date()
                        if args.from_date and record_date < datetime.strptime(args.from_date, '%Y-%m-%d').date():
                            continue
                        if args.to_date and record_date > datetime.strptime(args.to_date, '%Y-%m-%d').date():
                            continue
                    except:
                        pass  # Keep record if date parsing fails
                filtered.append(record)
            data = filtered
            print(f"  Filtered to {len(data)} records")
        
        # Export data
        count = export_data(data, args.output, table, args.format)
        total_records += count
        print(f"  Exported {count} records to {args.output}/{table}.{args.format}")
    
    print()
    print("=" * 60)
    print(f"Export complete: {total_records} total records")
    print(f"Output directory: {args.output}")
    print("=" * 60)


if __name__ == '__main__':
    main()
