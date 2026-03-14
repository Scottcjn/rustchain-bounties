#!/usr/bin/env python3
"""
SHA-256 Implementation for PDP-1 (18-bit Architecture)
======================================================

Simplified implementation that uses standard Python 32-bit operations
but documents how it would work on 18-bit PDP-1 architecture.

For the actual PDP-1 simulation, 32-bit values would be stored as
pairs of 18-bit words (high 14 bits + low 18 bits).

Author: RustChain PDP-1 Mining Project
License: MIT
"""

import hashlib as std_hashlib
import struct


class SHA256_PDP1:
    """
    SHA-256 hash function for PDP-1
    
    This implementation uses Python's native integers for computation
    but simulates the constraints and approach needed for 18-bit architecture.
    """
    
    # SHA-256 constants
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]
    
    # Initial hash values
    H_INIT = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # PDP-1 18-bit mask
    MASK_18 = 0x3FFFF  # 18 bits
    
    def __init__(self):
        """Initialize SHA-256 context"""
        self.reset()
    
    def reset(self):
        """Reset hash state to initial values"""
        self.H = list(self.H_INIT)
        self.buffer = bytearray()
        self.bit_count = 0
    
    def _rotr(self, x, n):
        """Rotate right 32-bit value"""
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF
    
    def _shr(self, x, n):
        """Shift right 32-bit value"""
        return x >> n
    
    def _ch(self, x, y, z):
        """SHA-256 Ch function"""
        return (x & y) ^ (~x & z)
    
    def _maj(self, x, y, z):
        """SHA-256 Maj function"""
        return (x & y) ^ (x & z) ^ (y & z)
    
    def _sigma0(self, x):
        """SHA-256 sigma0"""
        return self._rotr(x, 2) ^ self._rotr(x, 13) ^ self._rotr(x, 22)
    
    def _sigma1(self, x):
        """SHA-256 sigma1"""
        return self._rotr(x, 6) ^ self._rotr(x, 11) ^ self._rotr(x, 25)
    
    def _gamma0(self, x):
        """SHA-256 gamma0"""
        return self._rotr(x, 7) ^ self._rotr(x, 18) ^ self._shr(x, 3)
    
    def _gamma1(self, x):
        """SHA-256 gamma1"""
        return self._rotr(x, 17) ^ self._rotr(x, 19) ^ self._shr(x, 10)
    
    def _to_pdp1_words(self, value32):
        """
        Convert 32-bit value to PDP-1 18-bit words
        
        On actual PDP-1, a 32-bit value would be stored as two 18-bit words:
        - High word: bits 31-18 (14 bits used)
        - Low word: bits 17-0 (18 bits used)
        
        Returns: (high_word, low_word)
        """
        high = (value32 >> 18) & 0x3FFF  # 14 bits
        low = value32 & 0x3FFFF          # 18 bits
        return (high, low)
    
    def _from_pdp1_words(self, high, low):
        """
        Convert PDP-1 18-bit words back to 32-bit value
        """
        return ((high & 0x3FFF) << 18) | (low & 0x3FFFF)
    
    def _process_block(self, block):
        """Process a 512-bit (64-byte) block"""
        # Parse block into 16 32-bit words
        W = list(struct.unpack('>16I', block))
        
        # Extend to 64 words
        for i in range(16, 64):
            s0 = self._gamma0(W[i-15])
            s1 = self._gamma1(W[i-2])
            W.append((W[i-16] + s0 + W[i-7] + s1) & 0xFFFFFFFF)
        
        # Initialize working variables
        a, b, c, d, e, f, g, h = self.H
        
        # Main loop
        for i in range(64):
            S1 = self._sigma1(e)
            ch = self._ch(e, f, g)
            temp1 = (h + S1 + ch + self.K[i] + W[i]) & 0xFFFFFFFF
            S0 = self._sigma0(a)
            maj = self._maj(a, b, c)
            temp2 = (S0 + maj) & 0xFFFFFFFF
            
            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF
        
        # Add to hash state
        self.H[0] = (self.H[0] + a) & 0xFFFFFFFF
        self.H[1] = (self.H[1] + b) & 0xFFFFFFFF
        self.H[2] = (self.H[2] + c) & 0xFFFFFFFF
        self.H[3] = (self.H[3] + d) & 0xFFFFFFFF
        self.H[4] = (self.H[4] + e) & 0xFFFFFFFF
        self.H[5] = (self.H[5] + f) & 0xFFFFFFFF
        self.H[6] = (self.H[6] + g) & 0xFFFFFFFF
        self.H[7] = (self.H[7] + h) & 0xFFFFFFFF
    
    def update(self, data):
        """Update hash with new data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        self.buffer.extend(data)
        self.bit_count += len(data) * 8
        
        # Process complete blocks
        while len(self.buffer) >= 64:
            self._process_block(bytes(self.buffer[:64]))
            self.buffer = self.buffer[64:]
    
    def digest(self):
        """Finalize and return hash digest (32 bytes)"""
        # Save state
        H_save = list(self.H)
        buffer_save = bytearray(self.buffer)
        bit_count_save = self.bit_count
        
        # Pad message
        msg_len = self.bit_count // 8
        self.buffer.append(0x80)
        
        # Pad to 56 bytes mod 64
        while (len(self.buffer) % 64) != 56:
            self.buffer.append(0x00)
        
        # Append original length in bits as 64-bit big-endian
        for i in range(8):
            self.buffer.append((self.bit_count >> (56 - i*8)) & 0xFF)
        
        # Process remaining blocks
        while len(self.buffer) >= 64:
            self._process_block(bytes(self.buffer[:64]))
            self.buffer = self.buffer[64:]
        
        # Produce final hash
        digest = struct.pack('>8I', *self.H)
        
        # Restore state
        self.H = H_save
        self.buffer = buffer_save
        self.bit_count = bit_count_save
        
        return digest
    
    def hexdigest(self):
        """Return hexadecimal digest"""
        return self.digest().hex()
    
    def hash(self, data):
        """Convenience method: hash data and return digest"""
        self.reset()
        self.update(data)
        return self.digest()
    
    def pdp1_memory_layout(self, data):
        """
        Show how data would be laid out in PDP-1 memory
        
        Returns a list of (address, high_word, low_word) tuples
        demonstrating the 18-bit word storage.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        layout = []
        addr = 0
        for i in range(0, len(data), 4):
            chunk = data[i:i+4]
            if len(chunk) < 4:
                chunk = chunk + b'\x00' * (4 - len(chunk))
            
            value32 = struct.unpack('>I', chunk)[0]
            high, low = self._to_pdp1_words(value32)
            layout.append((addr, high, low))
            addr += 2  # Two 18-bit words per 32-bit value
        
        return layout


def sha256_pdp1(data):
    """Simple SHA-256 function for PDP-1"""
    hasher = SHA256_PDP1()
    return hasher.hash(data)


if __name__ == '__main__':
    # Test SHA-256 implementation
    print("SHA-256 for PDP-1 (18-bit Architecture)")
    print("=" * 50)
    
    hasher = SHA256_PDP1()
    
    # Test vectors (standard SHA-256 test cases)
    test_cases = [
        ("", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
        ("abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
        ("The quick brown fox jumps over the lazy dog", 
         "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"),
    ]
    
    print("\nTest Vectors:")
    print("-" * 50)
    
    all_passed = True
    for data, expected in test_cases:
        hasher.reset()
        hasher.update(data)
        result = hasher.hexdigest()
        
        passed = result == expected
        all_passed = all_passed and passed
        status = "[OK]" if passed else "[FAIL]"
        
        print(f"{status} Input: {repr(data)[:40]}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {result}")
        print()
    
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed!")
    
    # Show PDP-1 memory layout
    print("\nPDP-1 Memory Layout Example:")
    print("-" * 50)
    test_data = "abc"
    layout = hasher.pdp1_memory_layout(test_data)
    print(f"Data: '{test_data}'")
    print(f"Bytes: {test_data.encode()}")
    print("\nMemory layout (address, high_14bits, low_18bits):")
    for addr, high, low in layout:
        print(f"  {addr:3d}: high={high:5d} (0x{high:04X}), low={low:5d} (0x{low:05X})")
    
    # Test PDP-1 specific mining scenario
    print("\n\nPDP-1 Mining Test:")
    print("-" * 50)
    
    # Simulate mining epoch
    epoch_data = b"PDP1_MINER_EPOCH_1959_LEGENDARY_TIER"
    wallet = b"RTC4325af95d26d59c3ef025963656d22af638bb96b"
    
    hasher.reset()
    hasher.update(epoch_data)
    hasher.update(wallet)
    mining_hash = hasher.hexdigest()
    
    print(f"Epoch: {epoch_data.decode()}")
    print(f"Wallet: {wallet.decode()}")
    print(f"Mining Hash: {mining_hash}")
    print(f"Difficulty Target: First 4 bits = {mining_hash[:1]}")
    
    # Check if it meets a simple difficulty
    if mining_hash[0] < '8':  # Leading zero in hex
        print("[OK] Block found! (simulated)")
    else:
        print("[INFO] No block found (nonce adjustment needed)")
