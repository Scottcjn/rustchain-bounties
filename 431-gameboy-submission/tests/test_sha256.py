#!/usr/bin/env python3
"""
SHA-256 Test Vectors for Game Boy Miner

Tests SHA-256 implementation against NIST test vectors.
"""

import hashlib
import sys

# Test vectors from NIST FIPS 180-4
TEST_VECTORS = [
    {
        "input": b"",
        "expected": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    {
        "input": b"abc",
        "expected": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    },
    {
        "input": b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
        "expected": "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"
    },
]

def test_sha256():
    """Test SHA-256 against known vectors."""
    print("SHA-256 Test Vectors")
    print("=" * 60)
    
    all_passed = True
    
    for i, vector in enumerate(TEST_VECTORS, 1):
        input_data = vector["input"]
        expected = vector["expected"]
        
        # Compute SHA-256 using Python's hashlib
        computed = hashlib.sha256(input_data).hexdigest()
        
        # Compare
        passed = computed == expected
        all_passed = all_passed and passed
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"\nTest {i}: {status}")
        print(f"  Input:    {input_data!r}")
        print(f"  Expected: {expected}")
        print(f"  Computed: {computed}")
        
        if not passed:
            print(f"  ERROR: Hash mismatch!")
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests PASSED ✓")
        return 0
    else:
        print("Some tests FAILED ✗")
        return 1

def generate_gb_test_data():
    """Generate test data for Game Boy unit tests."""
    print("\n\nGame Boy Test Data")
    print("=" * 60)
    
    for i, vector in enumerate(TEST_VECTORS, 1):
        input_data = vector["input"]
        expected = vector["expected"]
        
        print(f"\n; Test Vector {i}")
        print(f"; Input length: {len(input_data)} bytes")
        
        # Input bytes
        print("TestInput{}:".format(i))
        if len(input_data) == 0:
            print("    DB $00  ; Empty input")
        else:
            for j in range(0, len(input_data), 16):
                chunk = input_data[j:j+16]
                hex_str = ", ".join(f"${b:02X}" for b in chunk)
                print(f"    DB {hex_str}")
        
        # Expected hash
        print(f"TestExpected{}:".format(i))
        hash_bytes = bytes.fromhex(expected)
        for j in range(0, 32, 16):
            chunk = hash_bytes[j:j+16]
            hex_str = ", ".join(f"${b:02X}" for b in chunk)
            print(f"    DB {hex_str}")
    
    print("\n; Use these in Game Boy assembly tests")

if __name__ == "__main__":
    # Run tests
    exit_code = test_sha256()
    
    # Generate GB test data
    if len(sys.argv) > 1 and sys.argv[1] == "--generate":
        generate_gb_test_data()
    
    sys.exit(exit_code)
