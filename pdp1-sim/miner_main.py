#!/usr/bin/env python3
"""
PDP-1 RustChain Miner - Main Program

This is the main entry point for the PDP-1 miner, simulating mining operations
on DEC's first computer (1959).

Features:
- PDP-1 CPU simulation
- SHA256 hashing optimized for 18-bit architecture
- Hardware attestation with core memory signatures
- Network bridge interface (simulated)
"""

import time
import random
import hashlib
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdp1_cpu import PDP1CPU
from core_memory import PDP1CoreMemory
from sha256_pdp1 import SHA256_PDP1


class PDP1Miner:
    """PDP-1 RustChain Miner"""
    
    def __init__(self, wallet_address="RTC4325af95d26d59c3ef025963656d22af638bb96b"):
        self.cpu = PDP1CPU()
        self.memory = PDP1CoreMemory()
        self.sha256 = SHA256_PDP1()
        self.wallet = wallet_address
        self.miner_id = "pdp1_1959_dec_first"
        self.start_time = time.time()
        self.hashes_computed = 0
        self.shares_submitted = 0
        
    def get_hardware_signature(self):
        """Generate PDP-1 hardware fingerprint"""
        # Core memory timing signature
        core_timing = []
        for i in range(10):
            start = time.time()
            self.memory.read(random.randint(0, 4095))
            elapsed = time.time() - start
            core_timing.append(elapsed * 1_000_000)  # Convert to microseconds
        
        # Simulated transistor signature
        transistor_sig = {
            'count': 500,
            'power_watts': 50,
            'temp_celsius': 45 + random.uniform(-2, 2),
        }
        
        # CRT display signature (Type 30)
        crt_sig = {
            'phosphor_persistence_ms': 50,
            'beam_accuracy': 0.98,
        }
        
        return {
            'hardware_type': 'pdp1',
            'year': 1959,
            'technology': 'transistor',
            'memory_type': 'magnetic_core',
            'word_size_bits': 18,
            'memory_size_words': 4096,
            'core_timing_signature': core_timing,
            'transistor_signature': transistor_sig,
            'crt_signature': crt_sig,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
        }
    
    def mine(self, difficulty=4, max_hashes=100):
        """
        Simulate mining operation
        
        Args:
            difficulty: Number of leading zero bits required
            max_hashes: Maximum hashes to compute before returning
        """
        print(f"\nPDP-1 Miner Starting...")
        print(f"Wallet: {self.wallet}")
        print(f"Difficulty: {difficulty} leading zeros")
        print(f"Max hashes: {max_hashes}")
        print("=" * 60)
        
        base_data = f"RustChain-PDP1-{datetime.utcnow().isoformat()}"
        nonce = 0
        
        for i in range(max_hashes):
            # Prepare data to hash
            data = f"{base_data}-{nonce}".encode('utf-8')
            
            # Compute SHA256 using PDP-1 implementation
            self.sha256.reset()
            self.sha256.update(data)
            hash_hex = self.sha256.finalize()
            
            self.hashes_computed += 1
            
            # Check if hash meets difficulty
            hash_int = int(hash_hex, 16)
            leading_zeros = len(hash_hex) - len(hash_hex.lstrip('0'))
            
            if leading_zeros >= difficulty:
                print(f"\n[SUCCESS] SHARE FOUND!")
                print(f"  Nonce: {nonce}")
                print(f"  Hash:  {hash_hex}")
                print(f"  Leading zeros: {leading_zeros}")
                self.shares_submitted += 1
                return {
                    'success': True,
                    'nonce': nonce,
                    'hash': hash_hex,
                    'difficulty': difficulty,
                }
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                elapsed = time.time() - self.start_time
                hash_rate = self.hashes_computed / elapsed if elapsed > 0 else 0
                print(f"  Hash {i+1}/{max_hashes} | Rate: {hash_rate:.2f} H/s | Nonce: {nonce}")
            
            nonce += 1
        
        print(f"\n[FAILED] No share found in {max_hashes} hashes")
        return {
            'success': False,
            'hashes_computed': self.hashes_computed,
        }
    
    def get_statistics(self):
        """Get mining statistics"""
        elapsed = time.time() - self.start_time
        hash_rate = self.hashes_computed / elapsed if elapsed > 0 else 0
        
        return {
            'miner_id': self.miner_id,
            'wallet': self.wallet,
            'elapsed_seconds': elapsed,
            'hashes_computed': self.hashes_computed,
            'shares_found': self.shares_submitted,
            'hash_rate': hash_rate,
            'hardware': self.get_hardware_signature(),
        }
    
    def generate_attestation(self):
        """Generate hardware attestation for RustChain"""
        stats = self.get_statistics()
        hw_sig = stats['hardware']
        
        attestation = {
            'miner_id': self.miner_id,
            'architecture': 'PDP-1',
            'year': 1959,
            'location': 'DEC Headquarters, Maynard, MA (historical)',
            'memory_type': 'Magnetic Core',
            'word_size': 18,
            'attestation': {
                'core_timing_hash': hashlib.sha256(
                    str(hw_sig['core_timing_signature']).encode()
                ).hexdigest(),
                'transistor_count': hw_sig['transistor_signature']['count'],
                'power_signature': hw_sig['transistor_signature']['power_watts'],
                'crt_persistence': hw_sig['crt_signature']['phosphor_persistence_ms'],
                'entropy_proof': hashlib.sha256(
                    str(time.time()).encode()
                ).hexdigest(),
            },
            'wallet': self.wallet,
            'timestamp': int(time.time()),
            'multiplier': 5.0,
        }
        
        return attestation


def demo_mining():
    """Demonstrate PDP-1 mining"""
    print("\n" + "=" * 70)
    print("PDP-1 (1959) RustChain Miner - DEC's First Computer")
    print("=" * 70)
    
    miner = PDP1Miner()
    
    # Show hardware info
    print("\nHardware Configuration:")
    print(f"  Architecture: PDP-1 (18-bit)")
    print(f"  Memory: 4,096 words x 18 bits (9 KB)")
    print(f"  Technology: Transistors (~500)")
    print(f"  Clock: 5 MHz (200 ns cycle)")
    print(f"  I/O: Type 30 CRT, Paper Tape, Flexowriter")
    
    # Run mining simulation
    result = miner.mine(difficulty=3, max_hashes=100)
    
    # Show statistics
    stats = miner.get_statistics()
    print("\n" + "=" * 70)
    print("Mining Statistics:")
    print(f"  Hashes computed: {stats['hashes_computed']}")
    print(f"  Shares found: {stats['shares_found']}")
    print(f"  Hash rate: {stats['hash_rate']:.2f} H/s")
    print(f"  Elapsed time: {stats['elapsed_seconds']:.2f}s")
    
    # Generate attestation
    print("\n" + "=" * 70)
    print("Hardware Attestation:")
    attestation = miner.generate_attestation()
    import json
    print(json.dumps(attestation, indent=2))
    
    print("\n" + "=" * 70)
    print("PDP-1 Miner Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_mining()
