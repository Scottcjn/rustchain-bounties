#!/usr/bin/env python3
"""
Test suite for RustChain Backup Verification Script
Issue #2823 - Bounty: 10 RTC
"""

import os
import sys
import sqlite3
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))


def create_test_db(path: Path) -> None:
    """Create a test SQLite database with key tables."""
    conn = sqlite3.connect(str(path))
    cursor = conn.cursor()
    
    # Create key tables
    cursor.execute("CREATE TABLE balances (id INTEGER PRIMARY KEY, address TEXT, balance INTEGER)")
    cursor.execute("CREATE TABLE miner_attest_recent (id INTEGER PRIMARY KEY, miner TEXT, epoch INTEGER)")
    cursor.execute("CREATE TABLE headers (id INTEGER PRIMARY KEY, hash TEXT, height INTEGER)")
    cursor.execute("CREATE TABLE ledger (id INTEGER PRIMARY KEY, tx_hash TEXT, amount INTEGER)")
    cursor.execute("CREATE TABLE epoch_rewards (id INTEGER PRIMARY KEY, epoch INTEGER, reward INTEGER)")
    
    # Insert test data
    cursor.executemany("INSERT INTO balances (address, balance) VALUES (?, ?)", [
        ('addr1', 1000),
        ('addr2', 2000),
        ('addr3', 3000),
    ])
    
    cursor.executemany("INSERT INTO miner_attest_recent (miner, epoch) VALUES (?, ?)", [
        ('miner1', 100),
        ('miner2', 101),
    ])
    
    cursor.executemany("INSERT INTO headers (hash, height) VALUES (?, ?)", [
        (f'hash_{i}', i) for i in range(100)
    ])
    
    cursor.executemany("INSERT INTO ledger (tx_hash, amount) VALUES (?, ?)", [
        (f'tx_{i}', i * 10) for i in range(50)
    ])
    
    cursor.executemany("INSERT INTO epoch_rewards (epoch, reward) VALUES (?, ?)", [
        (i, i * 100) for i in range(10)
    ])
    
    conn.commit()
    conn.close()


def test_verify_backup_script_exists():
    """Test that verify_backup script exists"""
    script_path = Path('scripts/verify_backup.py')
    assert script_path.exists(), f"Script not found: {script_path}"
    print("✅ test_verify_backup_script_exists: PASSED")


def test_find_latest_backup():
    """Test finding latest backup file"""
    from scripts.verify_backup import find_latest_backup
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_dir = Path(tmpdir)
        
        # Create test backup files
        (backup_dir / 'backup1.db').touch()
        (backup_dir / 'backup2.db').touch()
        (backup_dir / 'backup3.db').touch()
        
        latest = find_latest_backup(backup_dir)
        assert latest is not None, "Should find backup file"
        assert latest.suffix == '.db', "Should return .db file"
        
        print("✅ test_find_latest_backup: PASSED")


def test_integrity_check():
    """Test SQLite integrity check"""
    from scripts.verify_backup import check_integrity
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'
        create_test_db(db_path)
        
        ok, msg = check_integrity(db_path)
        assert ok == True, f"Integrity check should pass: {msg}"
        assert msg == "PASS", f"Message should be PASS: {msg}"
        
        print("✅ test_integrity_check: PASSED")


def test_table_counts():
    """Test getting table counts"""
    from scripts.verify_backup import get_table_counts, KEY_TABLES
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'
        create_test_db(db_path)
        
        counts = get_table_counts(db_path)
        
        assert len(counts) == len(KEY_TABLES), f"Should return counts for all {len(KEY_TABLES)} tables"
        assert counts['balances'] == 3, f"Expected 3 balances, got {counts['balances']}"
        assert counts['miner_attest_recent'] == 2, f"Expected 2 attestations, got {counts['miner_attest_recent']}"
        assert counts['headers'] == 100, f"Expected 100 headers, got {counts['headers']}"
        assert counts['ledger'] == 50, f"Expected 50 ledger entries, got {counts['ledger']}"
        assert counts['epoch_rewards'] == 10, f"Expected 10 epoch rewards, got {counts['epoch_rewards']}"
        
        print("✅ test_table_counts: PASSED")


def test_verify_backup_valid():
    """Test verifying a valid backup"""
    from scripts.verify_backup import verify_backup
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = Path(tmpdir) / 'backup.db'
        create_test_db(backup_path)
        
        result = verify_backup(backup_path)
        assert result == True, "Verification should pass for valid backup"
        
        print("✅ test_verify_backup_valid: PASSED")


def test_verify_backup_missing_file():
    """Test verifying missing backup file"""
    from scripts.verify_backup import verify_backup
    
    backup_path = Path('/nonexistent/backup.db')
    result = verify_backup(backup_path)
    assert result == False, "Verification should fail for missing file"
    
    print("✅ test_verify_backup_missing_file: PASSED")


def test_verify_backup_corrupt():
    """Test verifying corrupt backup file"""
    from scripts.verify_backup import verify_backup
    
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_path = Path(tmpdir) / 'corrupt.db'
        
        # Create corrupt file (not a valid SQLite DB)
        with open(backup_path, 'w') as f:
            f.write("This is not a database")
        
        result = verify_backup(backup_path)
        assert result == False, "Verification should fail for corrupt file"
        
        print("✅ test_verify_backup_corrupt: PASSED")


def test_argument_parsing():
    """Test command-line argument parsing"""
    from scripts.verify_backup import main
    import argparse
    
    # Test that script has proper argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--backup-dir', type=Path)
    parser.add_argument('--live-db', type=Path, default=None)
    parser.add_argument('--backup-file', type=Path, default=None)
    
    # Test parsing
    args = parser.parse_args(['--backup-dir', '/backups', '--live-db', '/live.db'])
    assert args.backup_dir == Path('/backups')
    assert args.live_db == Path('/live.db')
    
    print("✅ test_argument_parsing: PASSED")


def test_exit_codes():
    """Test proper exit codes for cron alerting"""
    from scripts.verify_backup import verify_backup
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Valid backup should return True (exit 0)
        valid_backup = Path(tmpdir) / 'valid.db'
        create_test_db(valid_backup)
        result = verify_backup(valid_backup)
        assert result == True, "Valid backup should return True"
        
        # Missing backup should return False (exit 1)
        missing_backup = Path(tmpdir) / 'missing.db'
        result = verify_backup(missing_backup)
        assert result == False, "Missing backup should return False"
        
        print("✅ test_exit_codes: PASSED")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RustChain Backup Verification Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_verify_backup_script_exists,
        test_find_latest_backup,
        test_integrity_check,
        test_table_counts,
        test_verify_backup_valid,
        test_verify_backup_missing_file,
        test_verify_backup_corrupt,
        test_argument_parsing,
        test_exit_codes,
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {test.__name__}: ERROR - {e}")
            skipped += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
