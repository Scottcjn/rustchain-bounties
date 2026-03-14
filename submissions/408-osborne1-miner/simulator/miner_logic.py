"""
OsborneHash - Retro-Friendly Proof-of-Work Algorithm
Designed for Z80 8-bit architecture (Osborne 1, 1981)

This algorithm uses only 16-bit arithmetic and simple operations
that are native to the Z80 CPU.
"""

def rotate_left_16(value: int, bits: int = 1) -> int:
    """Rotate left a 16-bit value by specified bits."""
    value &= 0xFFFF
    for _ in range(bits):
        high_bit = (value >> 15) & 1
        value = ((value << 1) | high_bit) & 0xFFFF
    return value


def rotate_right_16(value: int, bits: int = 1) -> int:
    """Rotate right a 16-bit value by specified bits."""
    value &= 0xFFFF
    for _ in range(bits):
        low_bit = value & 1
        value = ((value >> 1) | (low_bit << 15)) & 0xFFFF
    return value


def osborne_hash(data: bytes, seed: int = 0x1234) -> int:
    """
    Compute OsborneHash of data.
    
    Algorithm:
    1. Initialize hash with seed
    2. For each byte:
       - XOR byte into hash
       - Add to hash (16-bit)
       - Rotate left by 1
    3. Final mixing
    
    Returns: 16-bit hash value
    """
    hash_value = seed & 0xFFFF
    
    for byte in data:
        # XOR byte into low byte of hash
        hash_value = hash_value ^ byte
        
        # Add byte to hash (16-bit addition)
        hash_value = (hash_value + byte) & 0xFFFF
        
        # Rotate left by 1
        hash_value = rotate_left_16(hash_value, 1)
    
    # Final mixing - XOR with rotated versions
    hash_value = hash_value ^ rotate_right_16(hash_value, 3)
    hash_value = hash_value ^ rotate_left_16(hash_value, 5)
    hash_value &= 0xFFFF
    
    return hash_value


def osborne_hash_with_nonce(data: bytes, nonce: int, seed: int = 0x1234) -> int:
    """
    Compute OsborneHash with nonce for mining.
    
    Combines data + nonce before hashing.
    """
    # Combine data with nonce (nonce as 2 bytes, little-endian)
    nonce_bytes = bytes([nonce & 0xFF, (nonce >> 8) & 0xFF])
    combined = data + nonce_bytes
    
    return osborne_hash(combined, seed)


def count_leading_zeros(value: int, bits: int = 16) -> int:
    """Count leading zero bits in a 16-bit value."""
    count = 0
    for i in range(bits - 1, -1, -1):
        if (value >> i) & 1:
            break
        count += 1
    return count


def mine_block(data: bytes, difficulty: int = 3, seed: int = 0x1234, max_nonce: int = 65535):
    """
    Mine a block by finding a nonce that produces enough leading zeros.
    
    Args:
        data: Block data to mine
        difficulty: Number of leading zero bits required
        seed: Hash seed
        max_nonce: Maximum nonce to try (default: 65535 for 16-bit)
    
    Returns:
        Tuple of (nonce, hash) if found, None if not found
    """
    threshold = 0xFFFF >> difficulty
    
    print(f"  Difficulty: {difficulty} leading zeros (threshold: 0x{threshold:04X})")
    print(f"  Searching nonces 0-{max_nonce}...")
    
    for nonce in range(max_nonce + 1):
        hash_value = osborne_hash_with_nonce(data, nonce, seed)
        
        if hash_value <= threshold:
            leading_zeros = count_leading_zeros(hash_value)
            return (nonce, hash_value, leading_zeros)
    
    return None


def verify_block(data: bytes, nonce: int, expected_hash: int, seed: int = 0x1234) -> bool:
    """Verify a mined block."""
    computed = osborne_hash_with_nonce(data, nonce, seed)
    return computed == expected_hash


# Test vectors
TEST_DATA = b"RustChain-Osborne1-Bounty-408"
TEST_SEED = 0x1234

if __name__ == "__main__":
    print("=== OsborneHash Test Vectors ===\n")
    
    # Test basic hash
    test_hash = osborne_hash(TEST_DATA, TEST_SEED)
    print(f"Data: {TEST_DATA.decode()}")
    print(f"Seed: 0x{TEST_SEED:04X}")
    print(f"Hash: 0x{test_hash:04X}")
    print(f"Binary: {test_hash:016b}")
    print(f"Leading zeros: {count_leading_zeros(test_hash)}\n")
    
    # Test mining
    print("=== Mining Test ===\n")
    result = mine_block(TEST_DATA, difficulty=3, seed=TEST_SEED)
    
    if result:
        nonce, hash_val, zeros = result
        print(f"\n[OK] FOUND!")
        print(f"  Nonce: {nonce} (0x{nonce:04X})")
        print(f"  Hash: 0x{hash_val:04X}")
        print(f"  Leading zeros: {zeros}")
        
        # Verify
        assert verify_block(TEST_DATA, nonce, hash_val, TEST_SEED)
        print(f"  Verification: PASSED [OK]")
    else:
        print("\n[FAIL] No valid nonce found in range")
