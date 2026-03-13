"""
SHA256 Implementation for AVIDAC

Implements SHA256 hash function optimized for AVIDAC's 40-bit architecture.
SHA256 operates on 32-bit words, which fit comfortably in AVIDAC's 40-bit words.

This module provides:
- SHA256 constants (K values and initial hash values)
- SHA256 compression function
- Message schedule expansion
- Full SHA256 hash computation

Memory requirements:
- 64 words for K constants
- 8 words for hash state (H0-H7)
- 64 words for message schedule (W0-W63)
- 8 words for working variables (a-h)
- 16 words for input block
Total: ~160 words (well within AVIDAC's 1024 words)
"""

from typing import List, Tuple
try:
    from .arithmetic import (
        MASK_32, sha256_rotr_32, sha256_shr_32,
        ch_32, maj_32, sigma0_32, sigma1_32, gamma0_32, gamma1_32, add_32bit
    )
except ImportError:
    from arithmetic import (
        MASK_32, sha256_rotr_32, sha256_shr_32,
        ch_32, maj_32, sigma0_32, sigma1_32, gamma0_32, gamma1_32, add_32bit
    )


# SHA256 Constants
# First 32 bits of fractional parts of cube roots of first 64 primes (2-311)
SHA256_K = [
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5,
    0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3,
    0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC,
    0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7,
    0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13,
    0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3,
    0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5,
    0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208,
    0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2
]

# Initial hash values
# First 32 bits of fractional parts of square roots of first 8 primes (2-19)
SHA256_H0 = [
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19
]


class SHA256:
    """
    SHA256 hash implementation for AVIDAC.
    
    Optimized for 40-bit architecture but operates on 32-bit values.
    """
    
    def __init__(self):
        """Initialize SHA256 hasher."""
        self.reset()
    
    def reset(self) -> None:
        """Reset hasher to initial state."""
        self.h = list(SHA256_H0)  # Copy initial hash values
        self.buffer = bytearray()
        self.total_length = 0
    
    def _process_block(self, block: bytes) -> None:
        """
        Process one 512-bit (64-byte) block.
        
        Args:
            block: 64-byte block to process
        """
        assert len(block) == 64, "Block must be 64 bytes"
        
        # Parse block into 16 32-bit words (big-endian)
        w = []
        for i in range(16):
            word = int.from_bytes(block[i*4:(i+1)*4], 'big')
            w.append(word)
        
        # Extend to 64 words (message schedule)
        for i in range(16, 64):
            s0 = gamma0_32(w[i-15])
            s1 = gamma1_32(w[i-2])
            w.append(add_32bit(add_32bit(add_32bit(w[i-16], s0), w[i-7]), s1))
        
        # Initialize working variables
        a, b, c, d, e, f, g, h = self.h
        
        # 64 rounds
        for i in range(64):
            S1 = sigma1_32(e)
            ch = ch_32(e, f, g)
            temp1 = add_32bit(add_32bit(add_32bit(add_32bit(h, S1), ch), SHA256_K[i]), w[i])
            S0 = sigma0_32(a)
            maj = maj_32(a, b, c)
            temp2 = add_32bit(S0, maj)
            
            h = g
            g = f
            f = e
            e = add_32bit(d, temp1)
            d = c
            c = b
            b = a
            a = add_32bit(temp1, temp2)
        
        # Add working variables to hash state
        self.h[0] = add_32bit(self.h[0], a)
        self.h[1] = add_32bit(self.h[1], b)
        self.h[2] = add_32bit(self.h[2], c)
        self.h[3] = add_32bit(self.h[3], d)
        self.h[4] = add_32bit(self.h[4], e)
        self.h[5] = add_32bit(self.h[5], f)
        self.h[6] = add_32bit(self.h[6], g)
        self.h[7] = add_32bit(self.h[7], h)
    
    def update(self, data: bytes) -> 'SHA256':
        """
        Update hash with more data.
        
        Args:
            data: Bytes to add to hash
        
        Returns:
            Self for chaining
        """
        self.total_length += len(data) * 8  # Length in bits
        self.buffer.extend(data)
        
        # Process complete blocks
        while len(self.buffer) >= 64:
            self._process_block(bytes(self.buffer[:64]))
            self.buffer = self.buffer[64:]
        
        return self
    
    def digest(self) -> bytes:
        """
        Finalize hash and return digest.
        
        Returns:
            32-byte SHA256 digest
        """
        # Save state for potential reuse
        h_save = list(self.h)
        buffer_save = bytearray(self.buffer)
        length_save = self.total_length
        
        # Padding
        message_length = len(self.buffer)
        self.buffer.append(0x80)  # Append bit 1
        
        # Pad to 56 bytes mod 64
        while len(self.buffer) % 64 != 56:
            self.buffer.append(0x00)
        
        # Append original length in bits as 64-bit big-endian
        self.buffer.extend(length_save.to_bytes(8, 'big'))
        
        # Process remaining blocks
        assert len(self.buffer) % 64 == 0
        for i in range(0, len(self.buffer), 64):
            self._process_block(bytes(self.buffer[i:i+64]))
        
        # Produce digest
        digest = b''.join(h.to_bytes(4, 'big') for h in self.h)
        
        # Restore state
        self.h = h_save
        self.buffer = buffer_save
        self.total_length = length_save
        
        return digest
    
    def hexdigest(self) -> str:
        """
        Finalize hash and return hex string.
        
        Returns:
            64-character hex string
        """
        return self.digest().hex()
    
    def copy(self) -> 'SHA256':
        """
        Create a copy of this hasher.
        
        Returns:
            New SHA256 instance with same state
        """
        new_hasher = SHA256()
        new_hasher.h = list(self.h)
        new_hasher.buffer = bytearray(self.buffer)
        new_hasher.total_length = self.total_length
        return new_hasher


def sha256(data: bytes) -> bytes:
    """
    Compute SHA256 hash of data.
    
    Args:
        data: Input bytes
    
    Returns:
        32-byte SHA256 digest
    """
    hasher = SHA256()
    hasher.update(data)
    return hasher.digest()


def sha256_hex(data: bytes) -> str:
    """
    Compute SHA256 hash as hex string.
    
    Args:
        data: Input bytes
    
    Returns:
        64-character hex string
    """
    return sha256(data).hex()


def sha256_mining(target: int, nonce_start: int = 0, max_nonces: int = 1000000) -> tuple:
    """
    Simple SHA256 mining function.
    
    Searches for a nonce that produces a hash below the target.
    
    Args:
        target: Target threshold (hash must be < target)
        nonce_start: Starting nonce value
        max_nonces: Maximum nonces to try
    
    Returns:
        (nonce, hash_bytes) if found, (None, None) if not found
    """
    for nonce in range(nonce_start, nonce_start + max_nonces):
        # Create block header (simplified - just nonce for testing)
        header = nonce.to_bytes(8, 'big')
        hash_result = sha256(header)
        hash_int = int.from_bytes(hash_result, 'big')
        
        if hash_int < target:
            return nonce, hash_result
    
    return None, None


# NIST SHA256 Test Vectors
SHA256_TEST_VECTORS = [
    # (input, expected_hex_digest)
    (b'', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    (b'abc', 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'),
    (
        b'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq',
        '248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1'
    ),
]


def verify_test_vectors() -> bool:
    """
    Verify SHA256 implementation against NIST test vectors.
    
    Returns:
        True if all tests pass
    """
    all_passed = True
    
    for data, expected in SHA256_TEST_VECTORS:
        result = sha256_hex(data)
        if result != expected:
            print(f"FAIL: Input {data!r}")
            print(f"  Expected: {expected}")
            print(f"  Got:      {result}")
            all_passed = False
        else:
            print(f"PASS: {data!r}")
    
    return all_passed


if __name__ == '__main__':
    print("SHA256 Test Vectors")
    print("=" * 60)
    
    if verify_test_vectors():
        print("\n✓ All test vectors passed!")
    else:
        print("\n✗ Some test vectors failed!")
        exit(1)
    
    # Demo mining
    print("\nDemo Mining")
    print("=" * 60)
    
    # Easy target for demo (hash must start with 0000)
    target = 1 << 252  # Approximately 4 leading zero hex digits
    
    print(f"Target: {target:064x}")
    print("Searching for valid nonce...")
    
    nonce, hash_result = sha256_mining(target, max_nonces=100000)
    
    if nonce is not None:
        print(f"Found nonce: {nonce}")
        print(f"Hash: {hash_result.hex()}")
    else:
        print("No valid nonce found in search range")
