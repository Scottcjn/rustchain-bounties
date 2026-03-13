#!/usr/bin/env python3
"""
Tests for SHA256 Implementation (24-bit adapted)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sha256_era1101 import (
    SHA256_ERA1101,
    mask24, add24, sub24, xor24, and24, or24, not24,
    rotl24, rotr24, shr24,
    ch24, maj24, sigma0_24, sigma1_24, gamma0_24, gamma1_24,
    Word64,
    WORD_SIZE, WORD_MASK
)


def test_24bit_arithmetic():
    """Test 24-bit arithmetic operations."""
    print("Testing 24-bit arithmetic...")
    
    # Test mask
    assert mask24(0xFFFFFF) == 0xFFFFFF
    assert mask24(0x1000000) == 0
    assert mask24(0x1234567) == 0x234567
    
    # Test addition
    assert add24(1, 2) == 3
    assert add24(0xFFFFFF, 1) == 0  # Wrap with carry
    assert add24(0x100000, 0x100000) == 0x200000
    
    # Test XOR
    assert xor24(0xFF0000, 0x00FF00) == 0xFFFF00
    assert xor24(0x123456, 0x123456) == 0
    
    # Test AND
    assert and24(0xFF00FF, 0x00FFFF) == 0x0000FF
    assert and24(0xFFFFFF, 0x123456) == 0x123456
    
    # Test OR
    assert or24(0xFF0000, 0x00FF00) == 0xFFFF00
    
    # Test NOT
    assert not24(0) == 0xFFFFFF
    assert not24(0xFFFFFF) == 0
    
    print("  ✓ 24-bit arithmetic tests passed")


def test_shifts_rotates():
    """Test shift and rotate operations."""
    print("Testing shifts and rotates...")
    
    # Test rotate left
    assert rotl24(0x000001, 1) == 0x000002
    assert rotl24(0x800000, 1) == 0x000001  # Wrap around
    assert rotl24(0x123456, 0) == 0x123456
    
    # Test rotate right
    assert rotr24(0x000002, 1) == 0x000001
    assert rotr24(0x000001, 1) == 0x800000  # Wrap around
    assert rotr24(0x123456, 0) == 0x123456
    
    # Test shift right
    assert shr24(0x000004, 2) == 0x000001
    assert shr24(0xFFFFFF, 4) == 0x0FFFFF
    
    print("  ✓ Shift and rotate tests passed")


def test_sha256_functions():
    """Test SHA256 helper functions."""
    print("Testing SHA256 functions...")
    
    # Test Ch function: (x AND y) XOR (NOT x AND z)
    result = ch24(0xFF0000, 0xF0F0F0, 0x0F0F0F)
    expected = xor24(and24(0xFF0000, 0xF0F0F0), and24(not24(0xFF0000), 0x0F0F0F))
    assert result == expected
    
    # Test Maj function: (x AND y) XOR (x AND z) XOR (y AND z)
    result = maj24(0xFF0000, 0xF0F0F0, 0x0F0F0F)
    expected = xor24(xor24(and24(0xFF0000, 0xF0F0F0), and24(0xFF0000, 0x0F0F0F)),
                     and24(0xF0F0F0, 0x0F0F0F))
    assert result == expected
    
    # Test Σ0 function
    x = 0x123456
    result = sigma0_24(x)
    expected = xor24(xor24(rotr24(x, 2), rotr24(x, 13)), rotr24(x, 22))
    assert result == expected
    
    # Test Σ1 function
    result = sigma1_24(x)
    expected = xor24(xor24(rotr24(x, 6), rotr24(x, 11)), rotr24(x, 23))
    assert result == expected
    
    # Test σ0 function
    result = gamma0_24(x)
    expected = xor24(xor24(rotr24(x, 7), rotr24(x, 18)), shr24(x, 3))
    assert result == expected
    
    # Test σ1 function
    result = gamma1_24(x)
    expected = xor24(xor24(rotr24(x, 17), rotr24(x, 19)), shr24(x, 10))
    assert result == expected
    
    print("  ✓ SHA256 function tests passed")


def test_word64():
    """Test 64-bit word operations."""
    print("Testing 64-bit word operations...")
    
    # Test from_int
    w = Word64.from_int(0x1234567890ABCDEF)
    assert w.high == 0x12
    assert w.mid == 0x345678
    assert w.low == 0x90ABCDEF
    
    # Test to_int
    w = Word64(high=0x12, mid=0x345678, low=0x90ABCDEF)
    assert w.to_int() == 0x1234567890ABCDEF
    
    # Test add
    w1 = Word64.from_int(0x1000000000000000)
    w2 = Word64.from_int(0x2000000000000000)
    w3 = w1.add(w2)
    assert w3.to_int() == 0x3000000000000000
    
    # Test with carry
    w1 = Word64.from_int(0x000000FFFFFF0000)
    w2 = Word64.from_int(0x0000000000010000)
    w3 = w1.add(w2)
    assert w3.to_int() == 0x0000010000000000
    
    # Test rotate right
    w = Word64.from_int(0x8000000000000000)
    w_rot = w.rotr(1)
    assert w_rot.to_int() == 0x4000000000000000
    
    # Test shift right
    w = Word64.from_int(0x8000000000000000)
    w_shr = w.shr(1)
    assert w_shr.to_int() == 0x4000000000000000
    
    print("  ✓ 64-bit word tests passed")


def test_sha256_basic():
    """Test basic SHA256 hashing."""
    print("Testing basic SHA256 hashing...")
    
    sha = SHA256_ERA1101()
    
    # Test empty string
    result = sha.hash(b"")
    assert len(result) == 24  # 24 bytes for 24-bit adaptation
    
    # Test simple string
    result = sha.hash(b"abc")
    assert len(result) == 24
    
    # Test that same input produces same output
    result1 = sha.hash(b"test")
    result2 = sha.hash(b"test")
    assert result1 == result2
    
    # Test that different inputs produce different outputs
    result1 = sha.hash(b"test1")
    result2 = sha.hash(b"test2")
    assert result1 != result2
    
    print("  ✓ Basic SHA256 tests passed")


def test_sha256_incremental():
    """Test incremental hashing."""
    print("Testing incremental SHA256 hashing...")
    
    sha1 = SHA256_ERA1101()
    sha1.update(b"Hello, ")
    sha1.update(b"ERA 1101!")
    result1 = sha1.digest()
    
    sha2 = SHA256_ERA1101()
    result2 = sha2.hash(b"Hello, ERA 1101!")
    
    assert result1 == result2
    
    print("  ✓ Incremental hashing tests passed")


def test_sha256_reset():
    """Test hash state reset."""
    print("Testing SHA256 reset...")
    
    sha = SHA256_ERA1101()
    
    # Hash something
    sha.update(b"test data")
    
    # Reset
    sha.reset()
    
    # Hash something else - should not include previous data
    result = sha.hash(b"new data")
    
    # Verify it matches fresh hash
    sha2 = SHA256_ERA1101()
    result2 = sha2.hash(b"new data")
    
    assert result == result2
    
    print("  ✓ Reset tests passed")


def run_all_tests():
    """Run all SHA256 tests."""
    print("=" * 60)
    print("SHA256 (24-bit) Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_24bit_arithmetic,
        test_shifts_rotates,
        test_sha256_functions,
        test_word64,
        test_sha256_basic,
        test_sha256_incremental,
        test_sha256_reset,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
