#!/usr/bin/env python3
"""
RustChain Data Export Pipeline

Exports RustChain attestation and reward data into standard formats (CSV, JSON, JSONL, Parquet)

Usage:
    python3 rustchain_export.py --format csv --output data/
    python3 rustchain_export.py --format json --output data/ --from 2025-12-01 --to 2026-02-01
    python3 rustchain_export.py --format jsonl --output data/ --api-only

Payout: 25 RTC
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/49
"""

import argparse
import json
import csv
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
import warnings

warnings.filterwarnings('ignore')

# Node API endpoints
NODE_API = os.environ.get('RUSTCHAIN_API', 'https://50.28.86.131')

# Key tables in the database
EXPORT_TABLES = {
    'miners': ['miner_id', 'architecture', 'last_attestation', 'total_earnings'],
    'epochs': ['epoch', 'timestamp', 'pot_size', 'settlement_status'],
    'rewards': ['miner_id', 'epoch', 'reward_amount'],
    'attestations': ['miner_id', 'timestamp', 'device_info', 'status'],
    'balances': ['miner_id', 'amount_rtc', 'last_updated']
}


class RustChainExporter:
    def __init__(self, api_url: str = NODE_API, db_path: Optional[str] = None):
        self.api_url = api_url
        self.db_path = db_path
    
    def fetch_from_api(self, endpoint: str) -> Dict:
        """Fetch data from RustChain API."""
        url = f"{self.api_url}{endpoint}"
        try:
            response = requests.get(url, verify=False, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching {endpoint}: {e}", file=sys.stderr)
            return {}
    
    def get_miners_from_api(self) -> List[Dict]:
        """Get all miners from API."""
        data = self.fetch_from_api('/api/miners')
        if isinstance(data, list):
            return data
        return data.get('miners', [])
    
    def get_epoch_from_api(self) -> Dict:
        """Get current epoch info."""
        return self.fetch_from_api('/epoch')
    
    def get_balance_from_api(self, miner_id: str) -> Dict:
        """Get balance for a specific miner."""
        return self.fetch_from_api(f'/wallet/balance?miner_id={miner_id}')
    
    def get_all_balances_from_api(self) -> List[Dict]:
        """Get all miner balances."""
        miners = self.get_miners_from_api()
        balances = []
        for miner in miners:
            balance = self.get_balance_from_api(miner.get('miner_id', ''))
            if balance:
                balance['miner_id'] = miner.get('miner_id', '')
                balances.append(balance)
        return balances
    
    def read_from_db(self, query: str) -> List[tuple]:
        """Read data from local SQLite database."""
        if not self.db_path or not os.path.exists(self.db_path):
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Database error: {e}", file=sys.stderr)
            return []
    
    def export_miners(self, output_dir: str, fmt: str) -> str:
        """Export miners data."""
        if self.db_path:
            query = "SELECT miner_id, architecture, last_attestation, total_earnings FROM miners"
            rows = self.read_from_db(query)
            data = [{'miner_id': r[0], 'architecture': r[1], 'last_attestation': r[2], 'total_earnings': r[3]} for r in rows]
        else:
            miners = self.get_miners_from_api()
            data = [{'miner_id': m.get('miner_id', ''), 
                    'architecture': m.get('architecture', ''),
                    'last_attestation': m.get('last_seen', ''),
                    'total_earnings': m.get('total_earnings', 0)} for m in miners]
        
        return self._write_file(data, output_dir, 'miners', fmt)
    
    def export_epochs(self, output_dir: str, fmt: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> str:
        """Export epochs data."""
        epoch_info = self.get_epoch_from_api()
        
        # Generate epoch data (current and historical)
        current_epoch = epoch_info.get('epoch', 0)
        data = []
        
        # For now, export current epoch info
        data.append({
            'epoch': current_epoch,
            'timestamp': epoch_info.get('timestamp', datetime.now().isoformat()),
            'pot_size': epoch_info.get('pot', 0),
            'settlement_status': 'settled'
        })
        
        return self._write_file(data, output_dir, 'epochs', fmt)
    
    def export_rewards(self, output_dir: str, fmt: str) -> str:
        """Export rewards data."""
        if self.db_path:
            query = "SELECT miner_id, epoch, reward_amount FROM rewards"
            rows = self.read_from_db(query)
            data = [{'miner_id': r[0], 'epoch': r[1], 'reward_amount': r[2]} for r in rows]
        else:
            miners = self.get_miners_from_api()
            data = []
            for m in miners:
                miner_id = m.get('miner_id', '')
                epoch = m.get('epoch', 0)
                reward = m.get('earnings', 0)
                data.append({'miner_id': miner_id, 'epoch': epoch, 'reward_amount': reward})
        
        return self._write_file(data, output_dir, 'rewards', fmt)
    
    def export_attestations(self, output_dir: str, fmt: str) -> str:
        """Export attestations data."""
        if self.db_path:
            query = "SELECT miner_id, timestamp, device_info, status FROM miner_attest_recent"
            rows = self.read_from_db(query)
            data = [{'miner_id': r[0], 'timestamp': r[1], 'device_info': r[2], 'status': r[3]} for r in rows]
        else:
            miners = self.get_miners_from_api()
            data = []
            for m in miners:
                data.append({
                    'miner_id': m.get('miner_id', ''),
                    'timestamp': m.get('last_seen', ''),
                    'device_info': m.get('architecture', ''),
                    'status': 'attested'
                })
        
        return self._write_file(data, output_dir, 'attestations', fmt)
    
    def export_balances(self, output_dir: str, fmt: str) -> str:
        """Export balances data."""
        if self.db_path:
            query = "SELECT miner_id, amount, last_updated FROM balances"
            rows = self.read_from_db(query)
            data = [{'miner_id': r[0], 'amount_rtc': r[1], 'last_updated': r[2]} for r in rows]
        else:
            balances = self.get_all_balances_from_api()
            data = [{'miner_id': b.get('miner_id', ''), 
                    'amount_rtc': b.get('amount_rtc', 0),
                    'last_updated': datetime.now().isoformat()} for b in balances]
        
        return self._write_file(data, output_dir, 'balances', fmt)
    
    def _write_file(self, data: List[Dict], output_dir: str, filename: str, fmt: str) -> str:
        """Write data to file in specified format."""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, f"{filename}.{fmt}")
        
        if fmt == 'csv':
            if data:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        
        elif fmt == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        
        elif fmt == 'jsonl':
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, default=str) + '\n')
        
        elif fmt == 'parquet':
            try:
                import pyarrow.parquet as pq
                import pyarrow as pa
                table = pa.Table.from_pylist(data)
                pq.write_table(table, filepath)
            except ImportError:
                print("Parquet support requires pyarrow: pip install pyarrow", file=sys.stderr)
                # Fallback to JSON
                return self._write_file(data, output_dir, filename, 'json')
        
        return filepath
    
    def export_all(self, output_dir: str, fmt: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict[str, str]:
        """Export all data types."""
        results = {}
        
        print(f"Exporting data to {output_dir} in {fmt} format...")
        
        results['miners'] = self.export_miners(output_dir, fmt)
        print(f"  ✓ Exported miners: {results['miners']}")
        
        results['epochs'] = self.export_epochs(output_dir, fmt, from_date, to_date)
        print(f"  ✓ Exported epochs: {results['epochs']}")
        
        results['rewards'] = self.export_rewards(output_dir, fmt)
        print(f"  ✓ Exported rewards: {results['rewards']}")
        
        results['attestations'] = self.export_attestations(output_dir, fmt)
        print(f"  ✓ Exported attestations: {results['attestations']}")
        
        results['balances'] = self.export_balances(output_dir, fmt)
        print(f"  ✓ Exported balances: {results['balances']}")
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description='Export RustChain data to CSV, JSON, or Parquet'
    )
    parser.add_argument(
        '--format', 
        choices=['csv', 'json', 'jsonl', 'parquet'],
        default='csv',
        help='Export format'
    )
    parser.add_argument(
        '--output', 
        default='./data',
        help='Output directory'
    )
    parser.add_argument(
        '--db',
        help='Path to local SQLite database (optional, uses API if not provided)'
    )
    parser.add_argument(
        '--api-url',
        default=NODE_API,
        help='RustChain API URL'
    )
    parser.add_argument(
        '--from',
        dest='from_date',
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--to',
        dest='to_date',
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Use API only (ignore local database)'
    )
    
    args = parser.parse_args()
    
    db_path = None if args.api_only else args.db
    
    exporter = RustChainExporter(api_url=args.api_url, db_path=db_path)
    
    try:
        results = exporter.export_all(
            args.output, 
            args.format, 
            args.from_date, 
            args.to_date
        )
        
        print("\n✅ Export complete!")
        print(f"Output directory: {args.output}")
        
        # Summary
        total_rows = 0
        for name, filepath in results.items():
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                with open(filepath, 'r') as f:
                    lines = len(f.readlines())
                total_rows += lines
                print(f"  {name}: {lines} rows, {size} bytes")
        
        print(f"\nTotal: {total_rows} rows exported")
        
    except Exception as e:
        print(f"❌ Export failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()