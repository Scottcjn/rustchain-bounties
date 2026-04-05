#!/usr/bin/env python3
"""
Automated Backup Verification Script for RustChain DB Backups

This script verifies the integrity of RustChain database backups:
1. Finds the latest backup file
2. Runs SQLite integrity check
3. Verifies key tables exist and have data
4. Compares row counts against the live DB

Usage:
    python3 verify_backup.py [--backup-dir PATH] [--live-db PATH]

Payout: 10 RTC for working verification script
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/755
"""

import argparse
import os
import sys
import glob
import tempfile
import shutil
import sqlite3
import re
from datetime import datetime
from pathlib import Path


# Key tables to verify
KEY_TABLES = [
    'balances',
    'miner_attest_recent',
    'headers',
    'ledger',
    'epoch_rewards'
]


def find_latest_backup(backup_dir: str) -> str:
    """Find the most recent backup file."""
    if not os.path.exists(backup_dir):
        raise FileNotFoundError(f"Backup directory not found: {backup_dir}")
    
    # Look for common backup patterns
    patterns = [
        'rustchain_v2.db.bak',
        'rustchain_v2_*.db',
        'rustchain*.bak',
        '*.db.bak'
    ]
    
    backup_files = []
    for pattern in patterns:
        backup_files.extend(glob.glob(os.path.join(backup_dir, pattern)))
    
    if not backup_files:
        raise FileNotFoundError(f"No backup files found in {backup_dir}")
    
    # Sort by modification time, newest first
    backup_files.sort(key=os.path.getmtime, reverse=True)
    return backup_files[0]


def check_integrity(backup_path: str) -> bool:
    """Run SQLite integrity check on the backup."""
    conn = sqlite3.connect(backup_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()
        conn.close()
        
        return result[0] == 'ok'
    except Exception as e:
        conn.close()
        raise Exception(f"Integrity check failed: {e}")


def get_table_info(db_path: str) -> dict:
    """Get row counts for key tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    table_info = {}
    try:
        for table in KEY_TABLES:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                table_info[table] = count
            except sqlite3.OperationalError:
                table_info[table] = -1  # Table doesn't exist
    finally:
        conn.close()
    
    return table_info


def verify_backup(backup_path: str, live_db_path: str = None) -> dict:
    """
    Verify backup integrity and compare with live DB.
    
    Returns a dict with verification results.
    """
    results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'backup_path': backup_path,
        'integrity_ok': False,
        'tables': {},
        'live_tables': {},
        'differences': {},
        'pass': False
    }
    
    # Create temp copy for non-destructive testing
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        tmp_path = tmp.name
    
    try:
        shutil.copy2(backup_path, tmp_path)
        
        # Run integrity check
        results['integrity_ok'] = check_integrity(tmp_path)
        
        # Get table info from backup
        results['tables'] = get_table_info(tmp_path)
        
        # Compare with live DB if provided
        if live_db_path and os.path.exists(live_db_path):
            results['live_tables'] = get_table_info(live_db_path)
            
            for table in KEY_TABLES:
                backup_count = results['tables'].get(table, 0)
                live_count = results['live_tables'].get(table, 0)
                
                if backup_count >= 0 and live_count >= 0:
                    # Allow up to 1 epoch behind (approximately 1000 rows for ledger)
                    diff = live_count - backup_count
                    results['differences'][table] = {
                        'backup': backup_count,
                        'live': live_count,
                        'diff': diff,
                        'ok': diff <= 1000 or table != 'ledger'
                    }
        
        # Determine pass/fail
        results['pass'] = (
            results['integrity_ok'] and
            all(results['tables'].get(t, -1) > 0 for t in KEY_TABLES if t != 'epoch_rewards') and
            all(v.get('ok', False) for v in results['differences'].values())
        )
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    return results


def print_results(results: dict):
    """Print verification results in a readable format."""
    print(f"[{results['timestamp']}] Backup: {results['backup_path']}")
    
    integrity_status = "PASS" if results['integrity_ok'] else "FAIL"
    print(f"[{results['timestamp']}] Integrity: {integrity_status}")
    
    for table, count in results['tables'].items():
        status = "✅" if count > 0 else "❌"
        if results.get('live_tables'):
            live_count = results['live_tables'].get(table, 'N/A')
            diff_info = f" (live: {live_count})"
            if table in results['differences']:
                diff_ok = results['differences'][table]['ok']
                status = "✅" if diff_ok else "⚠️"
            print(f"[{results['timestamp']}] {table}: {count} rows{diff_info} {status}")
        else:
            print(f"[{results['timestamp']}] {table}: {count} rows {status}")
    
    result_status = "PASS" if results['pass'] else "FAIL"
    print(f"[{results['timestamp']}] RESULT: {result_status}")
    
    return 0 if results['pass'] else 1


def main():
    parser = argparse.ArgumentParser(
        description='Verify RustChain database backup integrity'
    )
    parser.add_argument(
        '--backup-dir',
        default='/root/rustchain/backups',
        help='Directory containing backup files'
    )
    parser.add_argument(
        '--live-db',
        default='/root/rustchain/rustchain_v2.db',
        help='Path to live database'
    )
    parser.add_argument(
        '--find-only',
        action='store_true',
        help='Only find and display the latest backup file'
    )
    
    args = parser.parse_args()
    
    try:
        # Find latest backup
        backup_path = find_latest_backup(args.backup_dir)
        print(f"Found backup: {backup_path}", file=sys.stderr)
        
        if args.find_only:
            return 0
        
        # Verify backup
        results = verify_backup(backup_path, args.live_db)
        
        # Print results and return exit code
        return print_results(results)
        
    except FileNotFoundError as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {e}", file=sys.stderr)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] RESULT: FAIL", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: {e}", file=sys.stderr)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] RESULT: FAIL", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())