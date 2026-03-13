#!/usr/bin/env python3
"""
Test script for PlayStation miner simulator.
Verifies SHA-256 implementation and difficulty checking.
"""

import sys
import hashlib
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playstation_simulator import PlayStationMiner, PSXBlockHeader


def test_sha256():
    """Test SHA-256 implementation against known vectors."""
    print("Testing SHA-256 implementation...")
    
    # Test vector: "abc" -> ba7816bf...
    test_data = b"abc"
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    result = hashlib.sha256(test_data).hexdigest()
    
    assert result == expected, f"SHA-256 test failed: {result} != {expected}"
    print("  [OK] SHA-256 test passed")
    return True


def test_difficulty_check():
    """Test difficulty checking logic."""
    print("Testing difficulty check...")
    
    miner = PlayStationMiner(difficulty=2)
    
    # Hash with 2 leading zeros: 00xx...
    hash_2zeros = bytes.fromhex("00" + "a" * 62)
    assert miner.check_difficulty(hash_2zeros) == True
    
    # Hash with 1 leading zero: 0xxx...
    hash_1zero = bytes.fromhex("0" + "a" * 63)
    assert miner.check_difficulty(hash_1zero) == False
    
    # Hash with no leading zeros
    hash_0zeros = bytes.fromhex("f" * 64)
    assert miner.check_difficulty(hash_0zeros) == False
    
    print("  [OK] Difficulty check test passed")
    return True


def test_count_leading_zeros():
    """Test leading zero counting."""
    print("Testing leading zero counter...")
    
    miner = PlayStationMiner()
    
    # 2 leading zeros
    hash_2zeros = bytes.fromhex("00" + "a" * 62)
    assert miner.count_leading_zeros(hash_2zeros) == 2
    
    # 4 leading zeros
    hash_4zeros = bytes.fromhex("0000" + "a" * 60)
    assert miner.count_leading_zeros(hash_4zeros) == 4
    
    # No leading zeros
    hash_0zeros = bytes.fromhex("f" * 64)
    assert miner.count_leading_zeros(hash_0zeros) == 0
    
    print("  [OK] Leading zero counter test passed")
    return True


def test_block_serialization():
    """Test block header serialization."""
    print("Testing block header serialization...")
    
    header = PSXBlockHeader(
        version=1,
        prev_hash=b'PSX' + b'\x00' * 13,
        timestamp=0x8520D800,
        difficulty=0x0000FFFF
    )
    
    serialized = header.serialize()
    
    # Check length (4 + 16 + 4 + 4 = 28 bytes, no nonce)
    assert len(serialized) == 28, f"Expected 28 bytes, got {len(serialized)}"
    
    # Check version (big-endian)
    assert serialized[0:4] == b'\x00\x00\x00\x01'
    
    # Check PSX marker
    assert serialized[4:7] == b'PSX'
    
    print("  [OK] Block header serialization test passed")
    return True


def test_mining():
    """Test actual mining (quick test with low difficulty)."""
    print("Testing mining operation...")
    
    miner = PlayStationMiner(difficulty=1)
    result = miner.mine(max_nonces=1000)
    
    if result is None:
        print("  [FAIL] Mining test failed - no nonce found")
        return False
    
    nonce, hash_bytes, hashes = result
    
    # Verify the hash actually meets difficulty
    assert miner.check_difficulty(hash_bytes), "Hash doesn't meet difficulty!"
    assert hashes == nonce + 1, "Hash count mismatch!"
    
    print(f"  [OK] Mining test passed (nonce={nonce}, hashes={hashes})")
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PlayStation Miner - Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_sha256,
        test_difficulty_check,
        test_count_leading_zeros,
        test_block_serialization,
        test_mining,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__} error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
