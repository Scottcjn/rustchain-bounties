#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for OsborneHash Algorithm
Validates correctness and edge cases
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from miner_logic import (
    rotate_left_16,
    rotate_right_16,
    osborne_hash,
    osborne_hash_with_nonce,
    count_leading_zeros,
    mine_block,
    verify_block
)


def test_rotate_left():
    """Test 16-bit left rotation."""
    print("Testing rotate_left_16...")
    
    # Test basic rotation
    assert rotate_left_16(0b0000000000000001, 1) == 0b0000000000000010
    assert rotate_left_16(0b0000000000000001, 2) == 0b0000000000000100
    
    # Test wrap-around
    assert rotate_left_16(0b1000000000000000, 1) == 0b0000000000000001
    
    # Test full rotation (should return to original)
    assert rotate_left_16(0xABCD, 16) == 0xABCD
    
    print("  [OK] rotate_left_16 passed")


def test_rotate_right():
    """Test 16-bit right rotation."""
    print("Testing rotate_right_16...")
    
    # Test basic rotation
    assert rotate_right_16(0b0000000000000010, 1) == 0b0000000000000001
    assert rotate_right_16(0b0000000000000100, 2) == 0b0000000000000001
    
    # Test wrap-around
    assert rotate_right_16(0b0000000000000001, 1) == 0b1000000000000000
    
    # Test full rotation
    assert rotate_right_16(0xABCD, 16) == 0xABCD
    
    print("  [OK] rotate_right_16 passed")


def test_hash_determinism():
    """Test that hash is deterministic."""
    print("Testing hash determinism...")
    
    data = b"test data"
    seed = 0x1234
    
    hash1 = osborne_hash(data, seed)
    hash2 = osborne_hash(data, seed)
    
    assert hash1 == hash2, "Hash should be deterministic"
    
    print("  [OK] Hash determinism passed")


def test_hash_sensitivity():
    """Test that hash is sensitive to input changes."""
    print("Testing hash sensitivity...")
    
    data1 = b"test"
    data2 = b"test!"  # One byte different
    seed = 0x1234
    
    hash1 = osborne_hash(data1, seed)
    hash2 = osborne_hash(data2, seed)
    
    assert hash1 != hash2, "Hash should change with input"
    
    # Test seed sensitivity
    seed2 = 0x5678
    hash3 = osborne_hash(data1, seed2)
    
    assert hash1 != hash3, "Hash should change with seed"
    
    print("  [OK] Hash sensitivity passed")


def test_leading_zeros():
    """Test leading zero counting."""
    print("Testing leading zero count...")
    
    assert count_leading_zeros(0b0001000000000000, 16) == 3
    assert count_leading_zeros(0b1000000000000000, 16) == 0
    assert count_leading_zeros(0b0000000000000000, 16) == 16
    assert count_leading_zeros(0b0111111111111111, 16) == 1
    
    print("  [OK] Leading zero count passed")


def test_mining_basic():
    """Test basic mining functionality."""
    print("Testing basic mining...")
    
    data = b"test block"
    difficulty = 2  # Easy difficulty for testing
    
    result = mine_block(data, difficulty=difficulty, seed=0x1234)
    
    assert result is not None, "Should find nonce for easy difficulty"
    
    nonce, hash_val, zeros = result
    assert zeros >= difficulty, f"Should have at least {difficulty} leading zeros"
    
    # Verify
    assert verify_block(data, nonce, hash_val, 0x1234), "Verification should pass"
    
    print(f"  [OK] Basic mining passed (nonce={nonce}, zeros={zeros})")


def test_mining_difficulty():
    """Test mining with different difficulties."""
    print("Testing mining with various difficulties...")
    
    data = b"RustChain-Osborne1-Bounty-408"
    
    for diff in range(1, 5):
        result = mine_block(data, difficulty=diff, seed=0x1234)
        
        if result:
            nonce, hash_val, zeros = result
            assert zeros >= diff, f"Difficulty {diff} not met"
            print(f"  [OK] Difficulty {diff}: nonce={nonce}, zeros={zeros}")
        else:
            print(f"  [WARN] Difficulty {diff}: no solution in 16-bit range")


def test_verification():
    """Test block verification."""
    print("Testing block verification...")
    
    data = b"test data"
    nonce = 42
    seed = 0x1234
    
    # Get valid hash
    valid_hash = osborne_hash_with_nonce(data, nonce, seed)
    
    # Verify should pass
    assert verify_block(data, nonce, valid_hash, seed), "Valid block should verify"
    
    # Wrong data should fail (different data produces different hash)
    different_data_hash = osborne_hash_with_nonce(b"different", nonce, seed)
    assert different_data_hash != valid_hash, "Different data should produce different hash"
    
    print("  [OK] Verification passed")


def test_edge_cases():
    """Test edge cases."""
    print("Testing edge cases...")
    
    # Empty data
    hash_empty = osborne_hash(b"", 0x1234)
    assert isinstance(hash_empty, int), "Empty data should produce hash"
    
    # Single byte
    hash_single = osborne_hash(b"\x00", 0x1234)
    assert hash_single != hash_empty, "Single byte should differ from empty"
    
    # Maximum values
    hash_max = osborne_hash(b"\xFF" * 100, 0xFFFF)
    assert 0 <= hash_max <= 0xFFFF, "Hash should be 16-bit"
    
    print("  [OK] Edge cases passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("  OsborneHash Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_rotate_left,
        test_rotate_right,
        test_hash_determinism,
        test_hash_sensitivity,
        test_leading_zeros,
        test_mining_basic,
        test_mining_difficulty,
        test_verification,
        test_edge_cases,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__} ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
