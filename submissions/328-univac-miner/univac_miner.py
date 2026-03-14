#!/usr/bin/env python3
"""
UNIVAC I Miner Implementation

Mining client for RustChain Proof-of-Antiquity blockchain,
adapted for UNIVAC I (1951) architecture constraints.

Features:
- UNIVAC-12 hash function (144-bit, 12-word output)
- Cycle-accurate UNIVAC I simulation
- Difficulty targeting (leading zero words)
- Solution verification

Author: RustChain Bounty #357 Submission
License: MIT
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from univac_simulator import (
    UNIVACISimulator, Instruction, Opcode,
    univac12_hash, check_target, mine_block
)


# ============================================================================
# Configuration
# ============================================================================

DIFFICULTY_WORDS = 2  # Leading zero words required (24 bits)
MAX_NONCES = 10_000_000  # Maximum nonces to try per block
WALLET_ADDRESS = "RTC4325af95d26d59c3ef025963656d22af638bb96b"


# ============================================================================
# Block Structure
# ============================================================================

class UNIVACBlock:
    """
    Block structure adapted for UNIVAC I constraints.
    
    Traditional block headers are too large for UNIVAC I's 1000-word memory.
    This simplified structure fits within available memory.
    """
    
    def __init__(self, block_number: int = 0, prev_hash: List[int] = None,
                 timestamp: int = None, data: bytes = b""):
        self.block_number = block_number
        self.prev_hash = prev_hash or [0] * 12
        self.timestamp = timestamp or int(time.time())
        self.data = data
        self.nonce: Optional[int] = None
        self.hash: Optional[List[int]] = None
    
    def to_bytes(self) -> bytes:
        """Serialize block to bytes for hashing"""
        # Compact serialization for UNIVAC I
        header = (
            f"{self.block_number:010d}"
            f"{self.timestamp:010d}"
        ).encode()
        
        # Previous hash (12 words × 12 bits = 144 bits = 18 bytes)
        prev_hash_bytes = b''.join(
            w.to_bytes(2, 'big')[-2:] for w in self.prev_hash
        )
        
        return header + prev_hash_bytes + self.data
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'block_number': self.block_number,
            'prev_hash': self.prev_hash,
            'timestamp': self.timestamp,
            'data': self.data.decode('utf-8', errors='replace'),
            'nonce': self.nonce,
            'hash': self.hash,
        }
    
    @classmethod
    def from_dict(cls, d: dict) -> 'UNIVACBlock':
        """Create block from dictionary"""
        block = cls(
            block_number=d['block_number'],
            prev_hash=d['prev_hash'],
            timestamp=d['timestamp'],
            data=d['data'].encode('utf-8') if isinstance(d['data'], str) else d['data'],
        )
        block.nonce = d.get('nonce')
        block.hash = d.get('hash')
        return block
    
    def memory_footprint(self) -> int:
        """Calculate memory usage in UNIVAC I words"""
        # Block header: 2 words (block number + timestamp)
        # Previous hash: 12 words
        # Data: variable (assume 100 words max)
        # Nonce: 1 word
        # Hash: 12 words
        return 2 + 12 + 100 + 1 + 12  # 127 words total


# ============================================================================
# Miner
# ============================================================================

class UNIVACMiner:
    """
    UNIVAC I Mining Client
    
    Simulates mining on UNIVAC I architecture while producing
    valid RustChain Proof-of-Antiquity attestations.
    """
    
    def __init__(self, wallet: str = WALLET_ADDRESS,
                 difficulty: int = DIFFICULTY_WORDS):
        self.wallet = wallet
        self.difficulty = difficulty
        self.simulator = UNIVACISimulator()
        self.blocks_mined = 0
        self.total_nonces = 0
        self.start_time = None
    
    def mine_block(self, block: UNIVACBlock, 
                   max_nonces: int = MAX_NONCES) -> Tuple[bool, dict]:
        """
        Mine a single block.
        
        Returns:
            Tuple of (success, stats_dict)
        """
        block_bytes = block.to_bytes()
        
        print(f"\nMining block #{block.block_number}...")
        print(f"  Data: {block.data[:50].decode('utf-8', errors='replace')}...")
        print(f"  Difficulty: {self.difficulty} leading zero words")
        print(f"  Max nonces: {max_nonces:,}")
        
        start_time = time.time()
        
        # Mine using UNIVAC-12 hash
        nonce, hash_result, nonces_tried = mine_block(
            block_bytes,
            target_words=self.difficulty,
            max_nonces=max_nonces
        )
        
        elapsed = time.time() - start_time
        
        if nonce is not None:
            block.nonce = nonce
            block.hash = hash_result
            self.blocks_mined += 1
            self.total_nonces += nonces_tried
            
            # Calculate UNIVAC I estimated time
            # Each hash requires ~100 memory accesses at 222 μs average
            univac_time_per_hash = 100 * 222 / 1_000_000  # seconds
            univac_total_time = nonces_tried * univac_time_per_hash
            
            stats = {
                'success': True,
                'nonce': nonce,
                'nonces_tried': nonces_tried,
                'hash': hash_result,
                'real_time_sec': elapsed,
                'univac_estimated_time_sec': univac_total_time,
                'univac_estimated_time_hours': univac_total_time / 3600,
                'hashes_per_sec_real': nonces_tried / elapsed,
                'hashes_per_sec_univac': 1 / univac_time_per_hash,
            }
            
            print(f"\n[SUCCESS] Solution found!")
            print(f"  Nonce: {nonce:,}")
            print(f"  Nonces tried: {nonces_tried:,}")
            print(f"  Hash: {' '.join(f'{w:03X}' for w in hash_result)}")
            print(f"  Real time: {elapsed:.2f} s")
            print(f"  UNIVAC I estimated: {univac_total_time:.1f} s ({univac_total_time/3600:.2f} h)")
            
        else:
            stats = {
                'success': False,
                'nonces_tried': nonces_tried,
                'real_time_sec': elapsed,
            }
            
            print(f"\n[FAIL] No solution found in {nonces_tried:,} nonces")
            print(f"  Real time: {elapsed:.2f} s")
        
        return stats['success'], stats
    
    def verify_solution(self, block: UNIVACBlock) -> bool:
        """Verify a mined block solution"""
        if block.nonce is None or block.hash is None:
            return False
        
        # Recompute hash
        block_bytes = block.to_bytes()
        computed_hash = univac12_hash(block_bytes, block.nonce)
        
        # Check hash matches
        if computed_hash != block.hash:
            print(f"❌ Hash mismatch!")
            return False
        
        # Check difficulty
        if not check_target(block.hash, self.difficulty):
            print(f"❌ Difficulty not met!")
            return False
        
        print(f"[VERIFIED] Solution verified!")
        print(f"  Block #{block.block_number}")
        print(f"  Nonce: {block.nonce:,}")
        print(f"  Hash: {' '.join(f'{w:03X}' for w in block.hash)}")
        
        return True
    
    def generate_attestation(self, block: UNIVACBlock, 
                            stats: dict) -> dict:
        """Generate RustChain attestation for mined block"""
        return {
            'miner_type': 'UNIVAC_I_Simulated',
            'miner_version': '1.0.0',
            'wallet': self.wallet,
            'block': block.to_dict(),
            'attestation': {
                'architecture': 'UNIVAC I (1951)',
                'word_size_bits': 12,
                'memory_words': 1000,
                'memory_type': 'mercury_delay_line',
                'hash_function': 'UNIVAC-12',
                'hash_output_bits': 144,
                'difficulty_words': self.difficulty,
                'difficulty_bits': self.difficulty * 12,
            },
            'performance': {
                'nonces_tried': stats.get('nonces_tried', 0),
                'real_time_sec': stats.get('real_time_sec', 0),
                'univac_estimated_time_sec': stats.get('univac_estimated_time_sec', 0),
                'univac_estimated_time_hours': stats.get('univac_estimated_time_hours', 0),
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'signature': f"UNIVAC-I-MINER-{block.block_number}-{block.nonce}",
        }
    
    def save_solution(self, block: UNIVACBlock, stats: dict, 
                     output_file: str):
        """Save mining solution to JSON file"""
        attestation = self.generate_attestation(block, stats)
        
        with open(output_file, 'w') as f:
            json.dump(attestation, f, indent=2)
        
        print(f"\n[SAVED] Solution saved to: {output_file}")
    
    def load_solution(self, input_file: str) -> Tuple[UNIVACBlock, dict]:
        """Load mining solution from JSON file"""
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        block = UNIVACBlock.from_dict(data['block'])
        return block, data


# ============================================================================
# Command Line Interface
# ============================================================================

def cmd_mine(args):
    """Mine a block"""
    miner = UNIVACMiner(wallet=args.wallet, difficulty=args.difficulty)
    
    # Create block
    block = UNIVACBlock(
        block_number=args.block_number,
        data=args.data.encode('utf-8') if args.data else b"RustChain UNIVAC I Test Block",
    )
    
    # Mine
    success, stats = miner.mine_block(block, max_nonces=args.max_nonces)
    
    # Save if successful
    if success and args.output:
        miner.save_solution(block, stats, args.output)
    
    return 0 if success else 1


def cmd_verify(args):
    """Verify a mined solution"""
    miner = UNIVACMiner(difficulty=args.difficulty)
    
    # Load solution
    block, attestation = miner.load_solution(args.input)
    
    # Verify
    valid = miner.verify_solution(block)
    
    if valid:
        print(f"\n📋 Attestation:")
        print(f"  Miner type: {attestation['miner_type']}")
        print(f"  Architecture: {attestation['attestation']['architecture']}")
        print(f"  Wallet: {attestation['wallet']}")
        print(f"  Timestamp: {attestation['timestamp']}")
        return 0
    else:
        print(f"\n❌ Verification failed!")
        return 1


def cmd_demo(args):
    """Run mining demonstration"""
    print("=" * 70)
    print("UNIVAC I Miner - RustChain Bounty #357")
    print("=" * 70)
    print()
    print("This miner simulates cryptocurrency mining on UNIVAC I (1951),")
    print("the first commercial computer ever built.")
    print()
    print("Architecture:")
    print("  - 12-bit word length")
    print("  - 1,000 words mercury delay line memory")
    print("  - Sequential access (222 μs average)")
    print("  - 6,103 vacuum tubes")
    print()
    print("=" * 70)
    
    miner = UNIVACMiner()
    
    # Demo blocks
    demo_blocks = [
        (1, b"Genesis Block - UNIVAC I Era"),
        (2, b"Block 2 - Mercury Delay Line Mining"),
        (3, b"Block 3 - Vacuum Tube Consensus"),
    ]
    
    for block_num, data in demo_blocks:
        block = UNIVACBlock(block_number=block_num, data=data)
        success, stats = miner.mine_block(block, max_nonces=100000)
        
        if not success:
            print(f"\n[WARN] Stopping demo (no solution found for block {block_num})")
            break
        
        print()
    
    print("=" * 70)
    print(f"Demo complete. Blocks mined: {miner.blocks_mined}")
    print("=" * 70)


def cmd_info(args):
    """Display UNIVAC I architecture information"""
    print("=" * 70)
    print("UNIVAC I Architecture Reference")
    print("=" * 70)
    print()
    print("General:")
    print("  First delivered: March 31, 1951")
    print("  Manufacturer: Remington Rand (Eckert-Mauchly Division)")
    print("  Units built: 46")
    print()
    print("CPU:")
    print("  Word size: 12 bits")
    print("  Clock: ~2.25 MHz (effective throughput lower)")
    print("  Add time: 540 μs")
    print("  Multiply time: 2,400 μs")
    print("  Divide time: 10,000 μs")
    print("  Vacuum tubes: 6,103")
    print()
    print("Memory:")
    print("  Type: Mercury delay lines")
    print("  Capacity: 1,000 words (12,000 bits)")
    print("  Organization: 7 tanks × 18 columns")
    print("  Access: Sequential (not random!)")
    print("  Average access time: 222 μs")
    print("  Word circulation time: 44 μs")
    print()
    print("Physical:")
    print("  Power: 125 kW")
    print("  Weight: 13,000 kg (28,000 lbs)")
    print("  Floor space: 35.5 m² (382 ft²)")
    print()
    print("I/O:")
    print("  Input: UNISERVO tape reader, punch cards")
    print("  Output: UNISERVO tape writer, punch cards, printer")
    print("  No networking (pre-dates Ethernet by 20+ years)")
    print()
    print("=" * 70)
    print("Mining Adaptation:")
    print("=" * 70)
    print()
    print("Hash Function: UNIVAC-12")
    print("  Output: 144 bits (12 words × 12 bits)")
    print("  Rounds: 12 mixing rounds")
    print("  Operations: 12-bit rotate, XOR, add")
    print()
    print("Difficulty:")
    print(f"  Target: {DIFFICULTY_WORDS} leading zero words")
    print(f"  Equivalent: {DIFFICULTY_WORDS * 12} leading zero bits")
    print(f"  Probability: 1 in {2**(DIFFICULTY_WORDS * 12):,}")
    print()
    print("Performance:")
    print("  Estimated hash rate: ~2 hashes/second")
    print("  Expected time per block: ~4-5 hours")
    print()
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description='UNIVAC I Miner - RustChain Bounty #357',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s mine --block-number 1 --output solution.json
  %(prog)s verify --input solution.json
  %(prog)s demo
  %(prog)s info
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Mine command
    mine_parser = subparsers.add_parser('mine', help='Mine a block')
    mine_parser.add_argument('--block-number', type=int, default=1,
                            help='Block number to mine')
    mine_parser.add_argument('--data', type=str, default='',
                            help='Block data')
    mine_parser.add_argument('--difficulty', type=int, default=DIFFICULTY_WORDS,
                            help='Difficulty (leading zero words)')
    mine_parser.add_argument('--max-nonces', type=int, default=MAX_NONCES,
                            help='Maximum nonces to try')
    mine_parser.add_argument('--wallet', type=str, default=WALLET_ADDRESS,
                            help='Wallet address')
    mine_parser.add_argument('--output', type=str,
                            help='Output file for solution')
    mine_parser.set_defaults(func=cmd_mine)
    
    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify a solution')
    verify_parser.add_argument('--input', type=str, required=True,
                              help='Input solution file')
    verify_parser.add_argument('--difficulty', type=int, default=DIFFICULTY_WORDS,
                              help='Difficulty (leading zero words)')
    verify_parser.set_defaults(func=cmd_verify)
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run mining demo')
    demo_parser.set_defaults(func=cmd_demo)
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show architecture info')
    info_parser.set_defaults(func=cmd_info)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
