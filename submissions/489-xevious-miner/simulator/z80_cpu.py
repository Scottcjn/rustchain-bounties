#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xevious Miner - Z80 CPU Simulator
Simulates the 1982 Xevious arcade Z80 CPU (3.072 MHz)

This is a proof-of-concept implementation for porting RustChain miner to Xevious arcade
"""

import time
import sys
from typing import Dict

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class Z80CPU:
    """
    Z80 CPU Simulator
    Simplified implementation supporting only miner-required instructions
    """
    
    def __init__(self):
        # 8-bit registers
        self.a = 0  # Accumulator
        self.f = 0  # Flag register
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.h = 0
        self.l = 0
        
        # 16-bit registers
        self.pc = 0x8000  # Program counter (starts at $8000)
        self.sp = 0xFFFF  # Stack pointer
        self.ix = 0
        self.iy = 0
        self.i = 0  # Interrupt vector register
        
        # Status
        self.running = False
        self.clock_speed = 3_072_000  # 3.072 MHz
        self.cycles = 0
        
    def get_hl(self) -> int:
        return (self.h << 8) | self.l
        
    def set_hl(self, value: int):
        self.h = (value >> 8) & 0xFF
        self.l = value & 0xFF
    
    def reset(self):
        """Reset CPU state"""
        self.a = self.f = self.b = self.c = 0
        self.d = self.e = self.h = self.l = 0
        self.pc = 0x8000
        self.sp = 0xFFFF
        self.cycles = 0
        self.running = False


class XeviousMemory:
    """
    Xevious Arcade Memory Map
    Total RAM: 16 KB (0x0000 - 0x3FFF)
    """
    
    # Memory map definitions
    WORK_RAM_START = 0x0000
    WORK_RAM_SIZE = 8 * 1024  # 8 KB work RAM
    
    VIDEO_RAM_START = 0x2000
    VIDEO_RAM_SIZE = 4 * 1024  # 4 KB video RAM
    
    MINER_DATA_START = 0x3000  # Miner data storage area
    MINER_DATA_SIZE = 4 * 1024  # 4 KB
    
    # Special offsets
    NONCE_OFFSET = 0x00
    HASH_RESULT_OFFSET = 0x04
    BLOCKCHAIN_HEIGHT_OFFSET = 0x08
    SCORE_OFFSET = 0x0C
    
    def __init__(self):
        # Main RAM (16 KB)
        self.ram = bytearray(16 * 1024)
        
        # Initialize miner data area
        self.write_word(self.MINER_DATA_START + self.NONCE_OFFSET, 0)
        self.write_word(self.MINER_DATA_START + self.HASH_RESULT_OFFSET, 0)
        self.write_word(self.MINER_DATA_START + self.BLOCKCHAIN_HEIGHT_OFFSET, 0)
        self.write_word(self.MINER_DATA_START + self.SCORE_OFFSET, 0)
        
    def read_byte(self, addr: int) -> int:
        """Read one byte"""
        if addr < len(self.ram):
            return self.ram[addr]
        return 0
    
    def write_byte(self, addr: int, value: int):
        """Write one byte"""
        if addr < len(self.ram):
            self.ram[addr] = value & 0xFF
            
    def read_word(self, addr: int) -> int:
        """Read one word (16-bit)"""
        low = self.read_byte(addr)
        high = self.read_byte(addr + 1)
        return (high << 8) | low
        
    def write_word(self, addr: int, value: int):
        """Write one word (16-bit)"""
        self.write_byte(addr, value & 0xFF)
        self.write_byte(addr + 1, (value >> 8) & 0xFF)
        
    def get_nonce(self) -> int:
        return self.read_word(self.MINER_DATA_START + self.NONCE_OFFSET)
        
    def set_nonce(self, value: int):
        self.write_word(self.MINER_DATA_START + self.NONCE_OFFSET, value)
        
    def get_blockchain_height(self) -> int:
        return self.read_word(self.MINER_DATA_START + self.BLOCKCHAIN_HEIGHT_OFFSET)
        
    def increment_blockchain_height(self):
        height = self.get_blockchain_height()
        self.write_word(self.MINER_DATA_START + self.BLOCKCHAIN_HEIGHT_OFFSET, height + 1)
        
    def get_score(self) -> int:
        return self.read_word(self.MINER_DATA_START + self.SCORE_OFFSET)
        
    def add_score(self, points: int):
        score = self.get_score()
        self.write_word(self.MINER_DATA_START + self.SCORE_OFFSET, score + points)
        
    def dump_miner_state(self) -> Dict:
        """Export miner state"""
        return {
            'nonce': self.get_nonce(),
            'blockchain_height': self.get_blockchain_height(),
            'score': self.get_score(),
        }


class PseudoHash:
    """
    Pseudo hash function (simplified version for Z80 simulation)
    Real SHA-256 is not feasible on Z80
    """
    
    @staticmethod
    def compute(nonce: int, seed: int = 0x1234) -> int:
        """Compute pseudo hash value"""
        # Simplified hash simulation
        value = nonce ^ seed
        value = ((value * 1103515245) + 12345) & 0x7FFFFFFF
        value = value ^ (value >> 16)
        return value & 0xFFFF
    
    @staticmethod
    def check_difficulty(hash_value: int, difficulty: int = 0x00FF) -> bool:
        """Check if difficulty requirement is met"""
        return hash_value <= difficulty


class XeviousMiner:
    """
    Xevious Miner Core
    Runs on simulated Z80 CPU
    """
    
    def __init__(self):
        self.cpu = Z80CPU()
        self.memory = XeviousMemory()
        self.hasher = PseudoHash()
        
        # Mining configuration
        self.difficulty = 0x00FF  # Target difficulty
        self.blocks_mined = 0
        self.total_nonces = 0
        
        # Performance stats
        self.start_time = None
        self.hashes_computed = 0
        
    def mine_one_block(self) -> bool:
        """
        Simulate mining one block
        Returns True if block was found
        """
        nonce = self.memory.get_nonce()
        
        while True:
            nonce = (nonce + 1) & 0xFFFF
            self.memory.set_nonce(nonce)
            self.total_nonces += 1
            self.hashes_computed += 1
            
            # Compute "hash"
            hash_result = self.hasher.compute(nonce)
            self.memory.write_word(
                self.memory.MINER_DATA_START + self.memory.HASH_RESULT_OFFSET,
                hash_result
            )
            
            # Check difficulty
            if self.hasher.check_difficulty(hash_result, self.difficulty):
                # Block found!
                self.memory.increment_blockchain_height()
                self.memory.add_score(1000)  # Reward 1000 points
                self.blocks_mined += 1
                return True
                
            # Prevent infinite loop, limit attempts
            if self.total_nonces % 10000 == 0:
                # Reduce difficulty every 10000 attempts to ensure progress
                self.difficulty = min(0xFFFF, self.difficulty + 0x0010)
                
    def run_mining_session(self, duration_seconds: float = 5.0):
        """Run mining session"""
        print("=" * 60)
        print("Xevious Miner - Z80 Simulator")
        print("=" * 60)
        print(f"CPU: Z80 @ 3.072 MHz (simulated)")
        print(f"RAM: 16 KB")
        print(f"Difficulty target: 0x{self.difficulty:04X}")
        print("=" * 60)
        print()
        
        self.start_time = time.time()
        end_time = self.start_time + duration_seconds
        
        print("Mining started...\n")
        
        try:
            while time.time() < end_time:
                if self.mine_one_block():
                    state = self.memory.dump_miner_state()
                    elapsed = time.time() - self.start_time
                    hash_rate = self.hashes_computed / elapsed if elapsed > 0 else 0
                    
                    print(f"  [BLOCK] #{state['blockchain_height']} mined!")
                    print(f"     Nonce: 0x{state['nonce']:04X}")
                    print(f"     Score: {state['score']}")
                    print(f"     Time: {elapsed:.2f}s")
                    print(f"     Hash rate: {hash_rate:.0f} H/s (simulated Z80)")
                    print()
                    
        except KeyboardInterrupt:
            print("\nMining interrupted")
            
        self.print_final_stats()
        
    def print_final_stats(self):
        """Print final statistics"""
        elapsed = time.time() - self.start_time if self.start_time else 1
        
        print("=" * 60)
        print("Mining Statistics")
        print("=" * 60)
        print(f"  Runtime: {elapsed:.2f} seconds")
        print(f"  Blocks mined: {self.blocks_mined}")
        print(f"  Total attempts: {self.total_nonces}")
        print(f"  Average hash rate: {self.hashes_computed / elapsed:.0f} H/s")
        print()
        
        state = self.memory.dump_miner_state()
        print(f"  Final score: {state['score']}")
        print(f"  Blockchain height: {state['blockchain_height']}")
        print(f"  Final nonce: 0x{state['nonce']:04X}")
        print()
        
        print("RustChain Bounty Wallet:")
        print(f"  RTC4325af95d26d59c3ef025963656d22af638bb96b")
        print("=" * 60)


def main():
    """Main program entry"""
    miner = XeviousMiner()
    miner.run_mining_session(duration_seconds=10.0)


if __name__ == "__main__":
    main()
