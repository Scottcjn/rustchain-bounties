#!/usr/bin/env python3
"""
RustChain Automated Backup Verification Script
Issue #2823 - Bounty: 10 RTC

Verifies backup integrity and completeness:
- Finds latest backup file
- Runs SQLite integrity check
- Verifies key tables exist with data
- Compares row counts with live DB
- Non-destructive testing
- Proper exit codes for cron alerting

Usage:
    python3 verify_backup.py --backup-dir /root/rustchain/backups --live-db /root/rustchain/rustchain_v2.db
"""

import os
import sys
import argparse
import sqlite3
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple, Dict


# Key tables to verify
KEY_TABLES = [
    'balances',
    'miner_attest_recent',
    'headers',
    'ledger',
    'epoch_rewards',
]

# Allow backup to be up to 1 epoch behind
MAX_EPOCH_LAG = 1


def find_latest_backup(backup_dir: Path) -> Optional[Path]:
    """Find the most recent backup file in directory."""
    if not backup_dir.exists():
        return None
    
    # Common backup file patterns
    patterns = [
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        'rustchain*.db',
        'backup*.db',
    ]
    
    backup_files = []
    for pattern in patterns:
        backup_files.extend(backup_dir.glob(pattern))
    
    if not backup_files:
        return None
    
    # Sort by modification time, newest first
    backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    
    return backup_files[0]


def check_integrity(db_path: Path) -> Tuple[bool, str]:
    """Run SQLite integrity check on database."""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        
        if result == 'ok':
            return True, "PASS"
        else:
            return False, f"FAIL: {result}"
    except Exception as e:
        return False, f"ERROR: {e}"


def get_table_counts(db_path: Path) -> Dict[str, int]:
    """Get row counts for all key tables."""
    counts = {}
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        for table in KEY_TABLES:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = -1  # Table doesn't exist
        
        conn.close()
    except Exception as e:
        print(f"Error reading {db_path}: {e}")
        return {}
    
    return counts


def verify_backup(backup_path: Path, live_db_path: Optional[Path] = None) -> bool:
    """
    Verify backup integrity and completeness.
    
    Returns True if verification passes, False otherwise.
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Backup: {backup_path}")
    
    # Check backup exists
    if not backup_path.exists():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Backup file not found")
        return False
    
    # Create temp copy for non-destructive testing
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)
    
    try:
        shutil.copy2(str(backup_path), temp_path)
        temp_db = Path(temp_path)
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Failed to copy backup: {e}")
        return False
    
    all_pass = True
    
    # 1. Run integrity check
    integrity_ok, integrity_msg = check_integrity(temp_db)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Integrity: {integrity_msg}")
    if not integrity_ok:
        all_pass = False
    
    # 2. Check key tables exist and have data
    backup_counts = get_table_counts(temp_db)
    
    if not backup_counts:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: Could not read backup tables")
        os.unlink(temp_path)
        return False
    
    # 3. Compare with live DB if available
    live_counts = {}
    if live_db_path and live_db_path.exists():
        live_counts = get_table_counts(live_db_path)
    
    # 4. Report results
    for table in KEY_TABLES:
        backup_count = backup_counts.get(table, -1)
        live_count = live_counts.get(table, None)
        
        if backup_count < 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {table}: MISSING ❌")
            all_pass = False
        elif backup_count == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {table}: EMPTY ⚠️")
            # Empty table might be OK depending on table
        elif live_count is not None:
            # Compare with live DB
            if backup_count >= live_count - 100:  # Allow some lag
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {table}: {backup_count} rows (live: {live_count}) ✅")
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {table}: {backup_count} rows (live: {live_count}) ⚠️ STALE")
                # Don't fail for staleness, just warn
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {table}: {backup_count} rows ✅")
    
    # Cleanup
    os.unlink(temp_path)
    
    # Final result
    result = "PASS" if all_pass else "FAIL"
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] RESULT: {result}")
    
    return all_pass


def main():
    parser = argparse.ArgumentParser(
        description='Verify RustChain backup integrity and completeness'
    )
    parser.add_argument(
        '--backup-dir',
        type=Path,
        default=Path('/root/rustchain/backups'),
        help='Directory containing backup files'
    )
    parser.add_argument(
        '--live-db',
        type=Path,
        default=None,
        help='Path to live database for comparison'
    )
    parser.add_argument(
        '--backup-file',
        type=Path,
        default=None,
        help='Specific backup file to verify (default: latest in backup-dir)'
    )
    
    args = parser.parse_args()
    
    # Find backup file
    if args.backup_file:
        backup_path = args.backup_file
    else:
        backup_path = find_latest_backup(args.backup_dir)
    
    if not backup_path:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR: No backup found in {args.backup_dir}")
        sys.exit(1)
    
    # Run verification
    success = verify_backup(backup_path, args.live_db)
    
    # Exit code for cron alerting
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
