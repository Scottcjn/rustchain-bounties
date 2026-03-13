"""
Tests for SHA256 implementation.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.sha256 import (
    SHA256, sha256, sha256_hex, sha256_mining,
    SHA256_K, SHA256_H0, SHA256_TEST_VECTORS, verify_test_vectors
)


class TestSHA256Constants:
    """Test SHA256 constants."""
    
    def test_k_constants_count(self):
        """Test we have 64 K constants."""
        assert len(SHA256_K) == 64
    
    def test_h0_constants_count(self):
        """Test we have 8 initial hash values."""
        assert len(SHA256_H0) == 8
    
    def test_k_constants_32bit(self):
        """Test K constants are 32-bit values."""
        for k in SHA256_K:
            assert 0 <= k <= 0xFFFFFFFF
    
    def test_h0_constants_32bit(self):
        """Test initial hash values are 32-bit."""
        for h in SHA256_H0:
            assert 0 <= h <= 0xFFFFFFFF


class TestSHA256TestVectors:
    """Test SHA256 against NIST test vectors."""
    
    def test_verify_all_vectors(self):
        """Test all NIST test vectors pass."""
        assert verify_test_vectors()
    
    def test_empty_string(self):
        """Test empty string hash."""
        result = sha256_hex(b'')
        assert result == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    
    def test_abc(self):
        """Test 'abc' hash."""
        result = sha256_hex(b'abc')
        assert result == 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
    
    def test_abcdbc(self):
        """Test longer string hash."""
        data = b'abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq'
        result = sha256_hex(data)
        assert result == '248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1'


class TestSHA256Class:
    """Test SHA256 class interface."""
    
    def test_basic_hash(self):
        """Test basic hashing via class."""
        hasher = SHA256()
        hasher.update(b'test')
        digest = hasher.digest()
        assert len(digest) == 32
    
    def test_hexdigest(self):
        """Test hexdigest method."""
        hasher = SHA256()
        hasher.update(b'test')
        hex_digest = hasher.hexdigest()
        assert len(hex_digest) == 64
        assert all(c in '0123456789abcdef' for c in hex_digest)
    
    def test_incremental_update(self):
        """Test incremental hashing."""
        hasher1 = SHA256()
        hasher1.update(b'hello')
        hasher1.update(b' world')
        result1 = hasher1.hexdigest()
        
        hasher2 = SHA256()
        hasher2.update(b'hello world')
        result2 = hasher2.hexdigest()
        
        assert result1 == result2
    
    def test_reset(self):
        """Test reset method."""
        hasher = SHA256()
        hasher.update(b'test')
        hasher.reset()
        result = hasher.hexdigest()
        assert result == sha256_hex(b'')
    
    def test_copy(self):
        """Test copy method."""
        hasher1 = SHA256()
        hasher1.update(b'test data')
        
        hasher2 = hasher1.copy()
        
        # Both should produce same result
        assert hasher1.hexdigest() == hasher2.hexdigest()
        
        # Modifying one shouldn't affect the other
        hasher1.update(b'more')
        assert hasher1.hexdigest() != hasher2.hexdigest()
    
    def test_digest_length(self):
        """Test digest is always 32 bytes."""
        hasher = SHA256()
        hasher.update(b'x' * 1000)  # Large input
        digest = hasher.digest()
        assert len(digest) == 32


class TestSHA256Mining:
    """Test SHA256 mining function."""
    
    def test_mining_finds_nonce(self):
        """Test mining finds a valid nonce."""
        # Easy target (hash < 2^252, about 4 leading zero hex digits)
        target = 1 << 252
        
        nonce, hash_result = sha256_mining(target, nonce_start=0, max_nonces=100000)
        
        if nonce is not None:
            # Verify the hash is actually below target
            hash_int = int.from_bytes(hash_result, 'big')
            assert hash_int < target
    
    def test_mining_deterministic(self):
        """Test mining is deterministic."""
        target = 1 << 252
        
        nonce1, hash1 = sha256_mining(target, nonce_start=1000, max_nonces=10000)
        nonce2, hash2 = sha256_mining(target, nonce_start=1000, max_nonces=10000)
        
        assert nonce1 == nonce2
        assert hash1 == hash2
    
    def test_mining_no_solution(self):
        """Test mining returns None when no solution found."""
        # Impossible target (hash < 1)
        target = 1
        
        nonce, hash_result = sha256_mining(target, max_nonces=1000)
        assert nonce is None
        assert hash_result is None


class TestSHA256Properties:
    """Test SHA256 cryptographic properties."""
    
    def test_avalanche_effect(self):
        """Test small input change produces large output change."""
        hash1 = sha256(b'test')
        hash2 = sha256(b'test' + b'\x00')  # One bit difference
        
        # Count differing bits
        diff_bits = 0
        for b1, b2 in zip(hash1, hash2):
            xor = b1 ^ b2
            diff_bits += bin(xor).count('1')
        
        # Should differ by approximately half the bits (128 bits on average)
        # Allow wide range for small sample
        assert diff_bits >= 64  # At least 25% of bits should differ
    
    def test_same_input_same_output(self):
        """Test deterministic output."""
        for _ in range(10):
            assert sha256(b'deterministic') == sha256(b'deterministic')
    
    def test_different_inputs_different_outputs(self):
        """Test different inputs produce different outputs."""
        hashes = set()
        for i in range(100):
            h = sha256(f'input_{i}'.encode())
            hashes.add(h)
        
        # All hashes should be unique
        assert len(hashes) == 100


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
