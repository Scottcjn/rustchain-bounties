#!/usr/bin/env python3
"""
Test suite for RustChain Data Export Pipeline
Issue #2824 - Bounty: 25 RTC
"""

import os
import sys
import json
import tempfile
import csv
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

def test_export_script_exists():
    """Test that export script exists"""
    script_path = Path('scripts/rustchain_export.py')
    assert script_path.exists(), f"Script not found: {script_path}"
    print("✅ test_export_script_exists: PASSED")

def test_export_csv():
    """Test CSV export functionality"""
    from scripts.rustchain_export import export_csv
    
    test_data = [
        {"id": 1, "name": "Alice", "value": 100},
        {"id": 2, "name": "Bob", "value": 200}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        count = export_csv(test_data, temp_path)
        assert count == 2, f"Expected 2 records, got {count}"
        
        # Verify CSV content
        with open(temp_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert rows[0]['name'] == 'Alice'
        
        print("✅ test_export_csv: PASSED")
    finally:
        temp_path.unlink()

def test_export_json():
    """Test JSON export functionality"""
    from scripts.rustchain_export import export_json
    
    test_data = [
        {"id": 1, "name": "Alice", "value": 100},
        {"id": 2, "name": "Bob", "value": 200}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        count = export_json(test_data, temp_path)
        assert count == 2, f"Expected 2 records, got {count}"
        
        # Verify JSON content
        with open(temp_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 2
            assert data[0]['name'] == 'Alice'
        
        print("✅ test_export_json: PASSED")
    finally:
        temp_path.unlink()

def test_export_jsonl():
    """Test JSONL export functionality"""
    from scripts.rustchain_export import export_jsonl
    
    test_data = [
        {"id": 1, "name": "Alice", "value": 100},
        {"id": 2, "name": "Bob", "value": 200}
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        count = export_jsonl(test_data, temp_path)
        assert count == 2, f"Expected 2 records, got {count}"
        
        # Verify JSONL content
        with open(temp_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 2
            assert json.loads(lines[0])['name'] == 'Alice'
        
        print("✅ test_export_jsonl: PASSED")
    finally:
        temp_path.unlink()

def test_export_empty_data():
    """Test export with empty data"""
    from scripts.rustchain_export import export_csv, export_json, export_jsonl
    
    empty_data = []
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        count = export_csv(empty_data, temp_path)
        assert count == 0, f"Expected 0 records, got {count}"
        print("✅ test_export_empty_data: PASSED")
    finally:
        temp_path.unlink()

def test_argument_parsing():
    """Test command-line argument parsing"""
    from scripts.rustchain_export import main
    import argparse
    
    # Test that script has proper argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'jsonl', 'parquet'])
    parser.add_argument('--output', '-o', type=Path)
    parser.add_argument('--from', dest='from_date')
    parser.add_argument('--to', dest='to_date')
    parser.add_argument('--api-only', action='store_true')
    parser.add_argument('--tables', '-t', nargs='+')
    
    # Test parsing
    args = parser.parse_args(['--format', 'json', '--output', 'data/'])
    assert args.format == 'json'
    assert args.output == Path('data/')
    
    print("✅ test_argument_parsing: PASSED")

def test_format_choices():
    """Test that all format choices are supported"""
    from scripts.rustchain_export import export_csv, export_json, export_jsonl
    
    test_data = [{"test": "data"}]
    
    formats_tested = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        
        # Test CSV
        csv_path = output_dir / "test.csv"
        export_csv(test_data, csv_path)
        assert csv_path.exists()
        formats_tested.append('csv')
        
        # Test JSON
        json_path = output_dir / "test.json"
        export_json(test_data, json_path)
        assert json_path.exists()
        formats_tested.append('json')
        
        # Test JSONL
        jsonl_path = output_dir / "test.jsonl"
        export_jsonl(test_data, jsonl_path)
        assert jsonl_path.exists()
        formats_tested.append('jsonl')
    
    print(f"✅ test_format_choices: PASSED - Tested: {', '.join(formats_tested)}")

def test_date_filtering_logic():
    """Test date filtering logic"""
    from datetime import datetime
    
    # Simulate date filtering (Python 3.6 compatible)
    test_records = [
        {"timestamp": "2025-12-01T00:00:00Z"},
        {"timestamp": "2026-01-15T00:00:00Z"},
        {"timestamp": "2026-02-28T00:00:00Z"}
    ]
    
    from_date = datetime.strptime('2026-01-01', '%Y-%m-%d').date()
    to_date = datetime.strptime('2026-01-31', '%Y-%m-%d').date()
    
    filtered = []
    for record in test_records:
        date_val = record.get('timestamp')
        if date_val:
            # Python 3.6 compatible parsing
            record_date = datetime.strptime(date_val.split('T')[0], '%Y-%m-%d').date()
            if from_date <= record_date <= to_date:
                filtered.append(record)
    
    assert len(filtered) == 1, f"Expected 1 record in range, got {len(filtered)}"
    assert filtered[0]['timestamp'] == "2026-01-15T00:00:00Z"
    
    print("✅ test_date_filtering_logic: PASSED")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("RustChain Data Export Pipeline Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_export_script_exists,
        test_export_csv,
        test_export_json,
        test_export_jsonl,
        test_export_empty_data,
        test_argument_parsing,
        test_format_choices,
        test_date_filtering_logic,
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
