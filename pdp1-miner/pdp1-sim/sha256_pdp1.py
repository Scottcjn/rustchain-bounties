#!/usr/bin/env python3
"""
SHA256 Implementation for PDP-1

This module implements SHA256 hashing optimized for the PDP-1's 18-bit architecture.
Since SHA256 uses 32-bit words, we split each 32-bit value across two 18-bit PDP-1 words.

Memory Layout for 32-bit values:
- Low word: bits 0-17 of the 32-bit value
- High word: bits 18-31 of the 32-bit value (in lower 14 bits)
"""

# SHA256 Constants (first 32 bits of fractional parts of cube roots of first 64 primes)
SHA256_K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]

# Initial hash values (first 32 bits of fractional parts of square roots of first 8 primes)
SHA256_H_INIT = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]


class SHA256_PDP1:
    """SHA256 implementation optimized for PDP-1 18-bit architecture"""
    
    def __init__(self):
        # Hash state (8 × 32-bit values)
        self.H = list(SHA256_H_INIT)
        
        # Working variables
        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.f = 0
        self.g = 0
        self.h = 0
        
        # Message schedule (64 × 32-bit values)
        self.W = [0] * 64
        
        # Byte buffer for input
        self.buffer = []
        self.bit_count = 0
    
    def _rotr(self, x, n):
        """32-bit right rotation"""
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF
    
    def _shr(self, x, n):
        """32-bit right shift"""
        return x >> n
    
    def _ch(self, x, y, z):
        """SHA256 Ch function: (x AND y) XOR (NOT x AND z)"""
        return (x & y) ^ ((~x) & z)
    
    def _maj(self, x, y, z):
        """SHA256 Maj function: (x AND y) XOR (x AND z) XOR (y AND z)"""
        return (x & y) ^ (x & z) ^ (y & z)
    
    def _sigma0(self, x):
        """SHA256 Σ0 function"""
        return self._rotr(x, 2) ^ self._rotr(x, 13) ^ self._rotr(x, 22)
    
    def _sigma1(self, x):
        """SHA256 Σ1 function"""
        return self._rotr(x, 6) ^ self._rotr(x, 11) ^ self._rotr(x, 25)
    
    def _gamma0(self, x):
        """SHA256 σ0 function"""
        return self._rotr(x, 7) ^ self._rotr(x, 18) ^ self._shr(x, 3)
    
    def _gamma1(self, x):
        """SHA256 σ1 function"""
        return self._rotr(x, 17) ^ self._rotr(x, 19) ^ self._shr(x, 10)
    
    def _process_block(self, block):
        """Process a 512-bit (64-byte) message block"""
        assert len(block) == 64, "Block must be 64 bytes"
        
        # Prepare message schedule
        for t in range(16):
            self.W[t] = (block[t*4] << 24) | (block[t*4+1] << 16) | (block[t*4+2] << 8) | block[t*4+3]
        
        for t in range(16, 64):
            s0 = self._gamma0(self.W[t-15])
            s1 = self._gamma1(self.W[t-2])
            self.W[t] = (self.W[t-16] + s0 + self.W[t-7] + s1) & 0xFFFFFFFF
        
        # Initialize working variables
        self.a = self.H[0]
        self.b = self.H[1]
        self.c = self.H[2]
        self.d = self.H[3]
        self.e = self.H[4]
        self.f = self.H[5]
        self.g = self.H[6]
        self.h = self.H[7]
        
        # 64 rounds
        for t in range(64):
            T1 = (self.h + self._sigma1(self.e) + self._ch(self.e, self.f, self.g) + 
                  SHA256_K[t] + self.W[t]) & 0xFFFFFFFF
            T2 = (self._sigma0(self.a) + self._maj(self.a, self.b, self.c)) & 0xFFFFFFFF
            self.h = self.g
            self.g = self.f
            self.f = self.e
            self.e = (self.d + T1) & 0xFFFFFFFF
            self.d = self.c
            self.c = self.b
            self.b = self.a
            self.a = (T1 + T2) & 0xFFFFFFFF
        
        # Update hash state
        self.H[0] = (self.H[0] + self.a) & 0xFFFFFFFF
        self.H[1] = (self.H[1] + self.b) & 0xFFFFFFFF
        self.H[2] = (self.H[2] + self.c) & 0xFFFFFFFF
        self.H[3] = (self.H[3] + self.d) & 0xFFFFFFFF
        self.H[4] = (self.H[4] + self.e) & 0xFFFFFFFF
        self.H[5] = (self.H[5] + self.f) & 0xFFFFFFFF
        self.H[6] = (self.H[6] + self.g) & 0xFFFFFFFF
        self.H[7] = (self.H[7] + self.h) & 0xFFFFFFFF
    
    def update(self, data):
        """Update hash with new data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        self.buffer.extend(data)
        self.bit_count += len(data) * 8
        
        # Process complete blocks
        while len(self.buffer) >= 64:
            block = self.buffer[:64]
            self._process_block(block)
            self.buffer = self.buffer[64:]
    
    def finalize(self):
        """Finalize hash and return digest"""
        # Padding
        message_len_bits = self.bit_count
        self.buffer.append(0x80)
        
        # Pad to 56 bytes mod 64
        while len(self.buffer) % 64 != 56:
            self.buffer.append(0x00)
        
        # Append original length in bits as 64-bit big-endian
        self.buffer.extend(message_len_bits.to_bytes(8, 'big'))
        
        # Process remaining blocks
        while len(self.buffer) >= 64:
            block = self.buffer[:64]
            self._process_block(block)
            self.buffer = self.buffer[64:]
        
        # Produce final hash (32 bytes = 256 bits)
        digest = b''
        for h in self.H:
            digest += h.to_bytes(4, 'big')
        
        return digest.hex()
    
    def reset(self):
        """Reset hash state"""
        self.H = list(SHA256_H_INIT)
        self.buffer = []
        self.bit_count = 0


def test_sha256():
    """Test SHA256 with NIST test vectors"""
    print("PDP-1 SHA256 Test")
    print("=" * 60)
    
    test_vectors = [
        ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        ("The quick brown fox jumps over the lazy dog", 
         "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"),
    ]
    
    all_passed = True
    for i, (message, expected) in enumerate(test_vectors):
        hasher = SHA256_PDP1()
        hasher.update(message)
        result = hasher.finalize()
        passed = result == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"Test {i+1}: {status}")
        print(f"  Input: '{message[:40]}{'...' if len(message) > 40 else ''}'")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    print("=" * 60)
    if all_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    
    return all_passed


if __name__ == "__main__":
    test_sha256()
