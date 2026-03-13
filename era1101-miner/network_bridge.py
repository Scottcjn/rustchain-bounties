#!/usr/bin/env python3
"""
Network Bridge for ERA 1101 Miner
==================================

Simulates the paper tape network interface that would connect
the ERA 1101 to the modern internet.

In a real implementation, this would be:
- Microcontroller (Arduino Due / Raspberry Pi) handling TCP/IP
- Paper tape reader/punch interface
- HTTPS communication with RustChain network

This module simulates the interface for testing.

Author: RustChain Bounty #1824 Submission
License: MIT
"""

import time
import json
import hashlib
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# Constants
# ============================================================================

RUSTCHAIN_API_BASE = "https://rustchain.org/api"
MINER_ENDPOINT = f"{RUSTCHAIN_API_BASE}/miners"
WORK_ENDPOINT = f"{RUSTCHAIN_API_BASE}/work"
SUBMIT_ENDPOINT = f"{RUSTCHAIN_API_BASE}/submit"

# Paper tape format constants
TAPE_CHAR_WIDTH = 7  # 7-bit ASCII
TAPE_SPEED_CHARS_PER_SEC = 100  # Simulated paper tape speed


# ============================================================================
# Data Structures
# ============================================================================

class TapeOperation(Enum):
    READ = "read"
    PUNCH = "punch"


@dataclass
class WorkRequest:
    """Request for mining work from RustChain network."""
    miner_id: str
    timestamp: int
    
    def to_json(self) -> str:
        return json.dumps({
            'miner_id': self.miner_id,
            'timestamp': self.timestamp
        })
    
    @classmethod
    def from_json(cls, data: str) -> 'WorkRequest':
        obj = json.loads(data)
        return cls(miner_id=obj['miner_id'], timestamp=obj['timestamp'])


@dataclass
class WorkAssignment:
    """Mining work assignment from network."""
    block_header: str
    difficulty: int
    expires_at: int
    
    def to_tape_format(self) -> List[int]:
        """Convert to paper tape format (7-bit ASCII characters)."""
        data = json.dumps({
            'block_header': self.block_header,
            'difficulty': self.difficulty,
            'expires_at': self.expires_at
        })
        return [ord(c) & 0x7F for c in data]
    
    @classmethod
    def from_tape_format(cls, chars: List[int]) -> 'WorkAssignment':
        """Parse from paper tape format."""
        data = ''.join(chr(c & 0x7F) for c in chars)
        obj = json.loads(data)
        return cls(
            block_header=obj['block_header'],
            difficulty=obj['difficulty'],
            expires_at=obj['expires_at']
        )


@dataclass
class Solution:
    """Mining solution to submit."""
    miner_id: str
    nonce: int
    hash_result: str
    timestamp: int
    
    def to_tape_format(self) -> List[int]:
        """Convert to paper tape format."""
        data = json.dumps({
            'miner_id': self.miner_id,
            'nonce': self.nonce,
            'hash_result': self.hash_result,
            'timestamp': self.timestamp
        })
        return [ord(c) & 0x7F for c in data]


# ============================================================================
# Paper Tape Interface Simulator
# ============================================================================

class PaperTapeInterface:
    """
    Simulates paper tape reader/punch interface.
    
    In real hardware, this would be:
    - Optical or mechanical paper tape reader
    - Paper tape punch for output
    - Microcontroller for buffering
    """
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.reader_buffer: List[int] = []
        self.punch_buffer: List[int] = []
        self.reader_position = 0
        self.stats = {
            'chars_read': 0,
            'chars_punched': 0,
            'total_read_time': 0,
            'total_punch_time': 0,
        }
    
    def load_tape(self, data: List[int]):
        """Load data into paper tape reader."""
        self.reader_buffer = data
        self.reader_position = 0
        if self.verbose:
            print(f"[Tape] Loaded {len(data)} characters")
    
    def read_char(self) -> Optional[int]:
        """Read next character from tape."""
        if self.reader_position < len(self.reader_buffer):
            char = self.reader_buffer[self.reader_position]
            self.reader_position += 1
            self.stats['chars_read'] += 1
            
            # Simulate paper tape read time
            time.sleep(1.0 / TAPE_SPEED_CHARS_PER_SEC)
            self.stats['total_read_time'] += 1.0 / TAPE_SPEED_CHARS_PER_SEC
            
            if self.verbose:
                print(f"[Tape Read] {chr(char & 0x7F) if 32 <= char < 127 else hex(char)}")
            
            return char
        return None
    
    def punch_char(self, char: int):
        """Punch character to output tape."""
        self.punch_buffer.append(char & 0x7F)
        self.stats['chars_punched'] += 1
        
        # Simulate paper tape punch time (slower than read)
        time.sleep(2.0 / TAPE_SPEED_CHARS_PER_SEC)
        self.stats['total_punch_time'] += 2.0 / TAPE_SPEED_CHARS_PER_SEC
        
        if self.verbose:
            print(f"[Tape Punch] {chr(char & 0x7F) if 32 <= char < 127 else hex(char)}")
    
    def get_punched_data(self) -> bytes:
        """Get all punched data."""
        return bytes(self.punch_buffer)
    
    def clear_punch(self):
        """Clear punch buffer."""
        self.punch_buffer = []
    
    def get_stats(self) -> Dict:
        """Get interface statistics."""
        return {
            **self.stats,
            'reader_buffer_size': len(self.reader_buffer),
            'punch_buffer_size': len(self.punch_buffer),
            'avg_read_rate': self.stats['chars_read'] / self.stats['total_read_time'] if self.stats['total_read_time'] > 0 else 0,
            'avg_punch_rate': self.stats['chars_punched'] / self.stats['total_punch_time'] if self.stats['total_punch_time'] > 0 else 0,
        }


# ============================================================================
# Network Bridge
# ============================================================================

class NetworkBridge:
    """
    Network bridge between ERA 1101 and RustChain network.
    
    Simulates the microcontroller that would handle:
    - TCP/IP communication
    - HTTPS requests
    - Paper tape I/O
    """
    
    def __init__(self, miner_id: str, verbose: bool = False):
        self.miner_id = miner_id
        self.verbose = verbose
        self.tape_interface = PaperTapeInterface(verbose=verbose)
        self.connected = False
        self.current_work: Optional[WorkAssignment] = None
        
        # Simulated network state
        self.simulated_blocks = self._generate_simulated_blocks()
    
    def _generate_simulated_blocks(self) -> List[Dict]:
        """Generate simulated block headers for testing."""
        blocks = []
        for i in range(10):
            block_hash = hashlib.sha256(f"block_{i}".encode()).hexdigest()
            blocks.append({
                'header': block_hash[:48],  # 24 bytes as hex
                'difficulty': 0x00FFFF,
                'created_at': int(time.time()) - i * 600
            })
        return blocks
    
    def connect(self) -> bool:
        """Connect to RustChain network."""
        if self.verbose:
            print(f"[Network] Connecting to {RUSTCHAIN_API_BASE}...")
        
        # Simulate connection
        time.sleep(0.1)
        self.connected = True
        
        if self.verbose:
            print(f"[Network] Connected as miner {self.miner_id}")
        
        return True
    
    def disconnect(self):
        """Disconnect from network."""
        self.connected = False
        if self.verbose:
            print("[Network] Disconnected")
    
    def request_work(self) -> Optional[WorkAssignment]:
        """Request mining work from network."""
        if not self.connected:
            if self.verbose:
                print("[Network] Not connected")
            return None
        
        if self.verbose:
            print("[Network] Requesting work...")
        
        # Simulate API call
        time.sleep(0.5)
        
        # Get next available block
        if self.simulated_blocks:
            block = self.simulated_blocks.pop()
            self.current_work = WorkAssignment(
                block_header=block['header'],
                difficulty=block['difficulty'],
                expires_at=int(time.time()) + 600
            )
            
            if self.verbose:
                print(f"[Network] Received work: {self.current_work.block_header[:16]}...")
            
            return self.current_work
        
        return None
    
    def submit_solution(self, solution: Solution) -> bool:
        """Submit mining solution to network."""
        if not self.connected:
            if self.verbose:
                print("[Network] Not connected")
            return False
        
        if self.verbose:
            print(f"[Network] Submitting solution: nonce={solution.nonce}")
        
        # Simulate API call
        time.sleep(0.5)
        
        # Simulate acceptance (50% chance for demo)
        accepted = True
        
        if self.verbose:
            status = "ACCEPTED" if accepted else "REJECTED"
            print(f"[Network] Solution {status}")
        
        return accepted
    
    def register_miner(self) -> bool:
        """Register miner with RustChain network."""
        if self.verbose:
            print(f"[Network] Registering miner {self.miner_id}...")
        
        # Simulate registration
        time.sleep(0.3)
        
        if self.verbose:
            print(f"[Network] Miner registered successfully")
        
        return True
    
    def get_miner_status(self) -> Dict:
        """Get miner status from network."""
        return {
            'miner_id': self.miner_id,
            'connected': self.connected,
            'has_work': self.current_work is not None,
            'status': 'mining' if self.connected and self.current_work else 'idle'
        }


# ============================================================================
# Complete Mining Cycle
# ============================================================================

class MiningCycle:
    """
    Complete mining cycle using paper tape interface.
    
    Simulates the full workflow:
    1. Request work via paper tape
    2. Mine on ERA 1101
    3. Submit solution via paper tape
    """
    
    def __init__(self, miner_id: str, verbose: bool = False):
        self.miner_id = miner_id
        self.verbose = verbose
        self.bridge = NetworkBridge(miner_id, verbose=verbose)
        self.hashes_computed = 0
        self.solutions_found = 0
    
    def run_cycle(self):
        """Run one complete mining cycle."""
        print(f"\n{'='*60}")
        print(f"ERA 1101 Mining Cycle")
        print(f"{'='*60}")
        
        # Step 1: Connect to network
        print("\n[Step 1] Connecting to RustChain network...")
        self.bridge.connect()
        
        # Step 2: Register miner
        print("\n[Step 2] Registering miner...")
        self.bridge.register_miner()
        
        # Step 3: Request work
        print("\n[Step 3] Requesting mining work...")
        work = self.bridge.request_work()
        
        if not work:
            print("[Error] No work available")
            return False
        
        # Step 4: Simulate mining on ERA 1101
        print("\n[Step 4] Mining on ERA 1101...")
        print(f"  Block header: {work.block_header[:16]}...")
        print(f"  Difficulty: 0x{work.difficulty:06X}")
        
        # Simulate mining (in real hardware, this would run on ERA 1101)
        import random
        nonce = random.randint(0, 0xFFFFFF)
        hash_result = hashlib.sha256(f"{work.block_header}{nonce}".encode()).hexdigest()
        
        self.hashes_computed += 1
        
        print(f"  Found nonce: {nonce}")
        print(f"  Hash: {hash_result[:32]}...")
        
        # Step 5: Create solution
        solution = Solution(
            miner_id=self.miner_id,
            nonce=nonce,
            hash_result=hash_result,
            timestamp=int(time.time())
        )
        
        # Step 6: Submit solution
        print("\n[Step 6] Submitting solution...")
        success = self.bridge.submit_solution(solution)
        
        if success:
            self.solutions_found += 1
            print("\n✓ Solution ACCEPTED!")
        else:
            print("\n✗ Solution REJECTED")
        
        # Step 7: Disconnect
        print("\n[Step 7] Disconnecting...")
        self.bridge.disconnect()
        
        # Summary
        print(f"\n{'='*60}")
        print(f"Cycle Complete")
        print(f"{'='*60}")
        print(f"  Hashes computed: {self.hashes_computed}")
        print(f"  Solutions found: {self.solutions_found}")
        print(f"  Success rate: {self.solutions_found/self.hashes_computed*100:.1f}%")
        
        return success
    
    def get_stats(self) -> Dict:
        """Get mining statistics."""
        return {
            'miner_id': self.miner_id,
            'hashes_computed': self.hashes_computed,
            'solutions_found': self.solutions_found,
            'bridge_stats': self.bridge.tape_interface.get_stats()
        }


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ERA 1101 Network Bridge')
    parser.add_argument('--demo', action='store_true', help='Run demo mining cycle')
    parser.add_argument('--miner-id', type=str, default='era1101_demo', help='Miner ID')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--test-tape', action='store_true', help='Test paper tape interface')
    
    args = parser.parse_args()
    
    if args.demo:
        cycle = MiningCycle(args.miner_id, verbose=args.verbose)
        cycle.run_cycle()
        print(f"\nFinal Stats:")
        stats = cycle.get_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
    
    if args.test_tape:
        print("Testing Paper Tape Interface...")
        tape = PaperTapeInterface(verbose=args.verbose)
        
        # Load test data
        test_data = [ord(c) for c in "Hello, ERA 1101!"]
        tape.load_tape(test_data)
        
        # Read all characters
        print("\nReading tape:")
        chars = []
        while True:
            char = tape.read_char()
            if char is None:
                break
            chars.append(char)
        
        print(f"\nRead {len(chars)} characters")
        print(f"Stats: {tape.get_stats()}")
    
    if not any([args.demo, args.test_tape]):
        parser.print_help()
        print("\nExample usage:")
        print("  python network_bridge.py --demo")
        print("  python network_bridge.py --demo --verbose")
        print("  python network_bridge.py --test-tape")


if __name__ == '__main__':
    main()
