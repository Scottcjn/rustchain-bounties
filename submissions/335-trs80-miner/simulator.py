#!/usr/bin/env python3
"""
TRS-80 Miner Simulator
Emulates RustChain mining on TRS-80 Model I (1977) hardware

Z80 CPU @ 1.77 MHz, 4 KB RAM, 64x16 text display
"""

import time
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum

# ============================================================================
# Z80 CPU Emulation (Minimal - Mining-focused)
# ============================================================================

class Z80CPU:
    """Minimal Z80 CPU emulator for mining operations"""
    
    def __init__(self):
        # Main registers
        self.a = 0  # Accumulator
        self.f = 0  # Flags
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.h = 0
        self.l = 0
        
        # Index registers
        self.ix = 0x4000  # Points to video RAM
        self.iy = 0x4500  # Points to block data
        
        # Program counter and stack pointer
        self.pc = 0x4400
        self.sp = 0x47FF
        
        # Cycle counter
        self.cycles = 0
        
    def inc_de(self) -> int:
        """INC DE - 4 cycles"""
        e = (self.e + 1) & 0xFF
        d = self.d
        if e == 0:
            d = (d + 1) & 0xFF
        self.e = e
        self.d = d
        self.cycles += 4
        return 4
    
    def get_de(self) -> int:
        """Get DE as 16-bit value"""
        return (self.d << 8) | self.e
    
    def set_de(self, value: int):
        """Set DE from 16-bit value"""
        self.d = (value >> 8) & 0xFF
        self.e = value & 0xFF
    
    def get_hl(self) -> int:
        """Get HL as 16-bit value"""
        return (self.h << 8) | self.l
    
    def set_hl(self, value: int):
        """Set HL from 16-bit value"""
        self.h = (value >> 8) & 0xFF
        self.l = value & 0xFF
    
    def xor_a(self) -> int:
        """XOR A - 4 cycles"""
        self.a = 0
        self.f = 0x40  # Z flag set
        self.cycles += 4
        return 4
    
    def add_a_b(self) -> int:
        """ADD A, B - 4 cycles"""
        result = (self.a + self.b) & 0xFF
        self.f = 0
        if result == 0:
            self.f |= 0x40  # Z flag
        if result > 0xFF:
            self.f |= 0x01  # C flag
        self.a = result
        self.cycles += 4
        return 4


# ============================================================================
# TRS-80 Memory System
# ============================================================================

class TRS80Memory:
    """TRS-80 Model I memory system (64 KB address space)"""
    
    VIDEO_RAM_START = 0x4000
    VIDEO_RAM_SIZE = 1024  # 64×16 = 1024 bytes
    CODE_START = 0x4400
    BLOCK_DATA_START = 0x4500
    HASH_STATE_START = 0x4600
    STACK_START = 0x4700
    
    def __init__(self):
        self.ram = bytearray(65536)
        self.rom_loaded = False
        
    def write_byte(self, addr: int, value: int):
        """Write byte to memory"""
        if addr < 65536:
            self.ram[addr] = value & 0xFF
    
    def read_byte(self, addr: int) -> int:
        """Read byte from memory"""
        if addr < 65536:
            return self.ram[addr]
        return 0
    
    def write_word(self, addr: int, value: int):
        """Write 16-bit word (little-endian)"""
        self.write_byte(addr, value & 0xFF)
        self.write_byte(addr + 1, (value >> 8) & 0xFF)
    
    def read_word(self, addr: int) -> int:
        """Read 16-bit word (little-endian)"""
        lo = self.read_byte(addr)
        hi = self.read_byte(addr + 1)
        return (hi << 8) | lo
    
    def clear_screen(self):
        """Clear video RAM"""
        for i in range(self.VIDEO_RAM_SIZE):
            self.ram[self.VIDEO_RAM_START + i] = 0x20  # Space
    
    def write_string(self, row: int, col: int, text: str):
        """Write string to video RAM at specified position"""
        addr = self.VIDEO_RAM_START + (row * 64) + col
        for char in text[:64 - col]:
            if addr < self.VIDEO_RAM_START + self.VIDEO_RAM_SIZE:
                self.ram[addr] = ord(char)
                addr += 1
    
    def get_display(self) -> List[str]:
        """Get current display as list of strings"""
        lines = []
        for row in range(16):
            start = self.VIDEO_RAM_START + (row * 64)
            line = ''.join(chr(self.ram[start + col]) for col in range(64))
            lines.append(line.rstrip())
        return lines


# ============================================================================
# MiniHash-8 Algorithm (Simplified for Z80)
# ============================================================================

class MiniHash8:
    """8-bit optimized hash function for Z80"""
    
    # Initial values (like SHA-256 IV)
    IV = [0x67, 0xEF, 0xAB, 0x45]
    
    def __init__(self):
        self.state = self.IV.copy()
    
    def reset(self):
        """Reset hash state"""
        self.state = self.IV.copy()
    
    def rotl8(self, value: int, shift: int) -> int:
        """Rotate left 8-bit value"""
        return ((value << shift) | (value >> (8 - shift))) & 0xFF
    
    def update(self, data: bytes) -> bytes:
        """Process data and return 4-byte hash"""
        self.reset()
        
        for byte in data:
            # Update state
            self.state[0] = (self.state[0] + byte) & 0xFF
            self.state[1] ^= self.state[0]
            self.state[2] = self.rotl8(self.state[2], 3) ^ byte
            self.state[3] = (self.state[3] * 7) & 0xFF
            
            # Mix states
            temp = self.state[0]
            self.state[0] = self.state[1]
            self.state[1] = self.state[2]
            self.state[2] = self.state[3]
            self.state[3] = temp
        
        return bytes(self.state)
    
    def hash_to_int(self, hash_bytes: bytes) -> int:
        """Convert 4-byte hash to integer"""
        return int.from_bytes(hash_bytes, 'little')


# ============================================================================
# TRS-80 Miner
# ============================================================================

@dataclass
class BlockHeader:
    """Simplified block header (32 bytes)"""
    version: int = 1
    prev_hash: bytes = field(default_factory=lambda: b'\x00' * 8)
    timestamp: int = 0
    difficulty: int = 0x0FFFFFFF  # Easier difficulty for testing (top 4 bits must be 0)
    nonce: int = 0
    
    def to_bytes(self) -> bytes:
        """Serialize to bytes"""
        data = bytearray(32)
        data[0] = self.version & 0xFF
        data[1:9] = self.prev_hash
        data[9:13] = self.timestamp.to_bytes(4, 'little')
        data[13:17] = self.difficulty.to_bytes(4, 'little')
        data[28:30] = self.nonce.to_bytes(2, 'little')
        return bytes(data)


class TRS80Miner:
    """Main miner class"""
    
    def __init__(self):
        self.cpu = Z80CPU()
        self.memory = TRS80Memory()
        self.hasher = MiniHash8()
        
        self.current_block = BlockHeader()
        self.hash_count = 0
        self.blocks_found = 0
        self.start_time = time.time()
        self.running = False
        
        # Initialize display
        self.memory.clear_screen()
        self._draw_ui()
    
    def _draw_ui(self):
        """Draw initial UI"""
        self.memory.write_string(0, 0, "=" * 64)
        self.memory.write_string(1, 18, "RUSTCHAIN TRS-80 MINER v1.0")
        self.memory.write_string(2, 0, "=" * 64)
        self.memory.write_string(4, 0, "BLOCK: 000000  NONCE: 00000")
        self.memory.write_string(5, 0, "HASH: 0x00000000  TARGET: 0x0FFFFFFF")
        self.memory.write_string(6, 0, "STATUS: INITIALIZING...")
        self.memory.write_string(7, 0, "RATE: 0 H/s")
        self.memory.write_string(8, 0, "FOUND: 0")
        self.memory.write_string(9, 0, "-" * 64)
        self.memory.write_string(10, 0, "Z80 @ 1.77 MHz | 4 KB RAM | 1977")
    
    def _update_display(self):
        """Update mining display"""
        # Block number
        block_text = f"BLOCK: {self.blocks_found:06d}"
        self.memory.write_string(4, 0, block_text + "  ")
        
        # Nonce (just the number, position 21 is after "NONCE: ")
        nonce_num = f"{self.cpu.get_de():05d}"
        self.memory.write_string(4, 29, nonce_num)
        
        # Hash rate
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            rate = int(self.hash_count / elapsed)
            rate_text = f"RATE: {rate} H/s"
            self.memory.write_string(7, 0, rate_text)
        
        # Blocks found
        found_text = f"FOUND: {self.blocks_found}"
        self.memory.write_string(8, 0, found_text)
    
    def init_block(self):
        """Initialize new block"""
        self.current_block = BlockHeader()
        self.current_block.timestamp = int(time.time())
        self.current_block.prev_hash = bytes([random.randint(0, 255) for _ in range(8)])
        self.cpu.set_de(0)  # Reset nonce
        
        # Write to memory
        block_bytes = self.current_block.to_bytes()
        for i, b in enumerate(block_bytes):
            self.memory.write_byte(0x4500 + i, b)
    
    def mine_step(self) -> bool:
        """Execute one mining iteration. Returns True if block found."""
        # Increment nonce (Z80: INC DE)
        self.cpu.inc_de()
        nonce = self.cpu.get_de()
        
        # Update block with nonce
        self.current_block.nonce = nonce
        block_bytes = self.current_block.to_bytes()
        
        # Calculate hash
        hash_result = self.hasher.update(block_bytes)
        hash_int = self.hasher.hash_to_int(hash_result)
        
        self.hash_count += 1
        
        # Check against target
        if hash_int < self.current_block.difficulty:
            # Found valid block!
            self.blocks_found += 1
            
            # Update display with result
            hash_hex = f"HASH: 0x{hash_int:08X}"
            self.memory.write_string(5, 0, hash_hex + "  ")
            self.memory.write_string(6, 0, "STATUS: BLOCK FOUND! ***")
            
            return True
        
        # Update hash display periodically
        if self.hash_count % 16 == 0:
            hash_hex = f"HASH: 0x{hash_int:08X}"
            self.memory.write_string(5, 0, hash_hex + "  ")
            self._update_display()
        
        return False
    
    def run(self, max_blocks: int = 1):
        """Run miner"""
        print("TRS-80 Miner Starting...")
        print("Z80 @ 1.77 MHz | 4 KB RAM | MiniHash-8")
        print("=" * 50)
        
        self.running = True
        self.start_time = time.time()
        
        blocks_mined = 0
        while self.running and blocks_mined < max_blocks:
            self.init_block()
            self.memory.write_string(6, 0, "STATUS: MINING...")
            
            # Mine until block found
            while self.running:
                found = self.mine_step()
                if found:
                    blocks_mined += 1
                    print(f"\n*** BLOCK {blocks_mined} FOUND! ***")
                    print(f"Nonce: {self.cpu.get_de()}")
                    
                    if blocks_mined >= max_blocks:
                        break
                    
                    # Small delay before next block
                    time.sleep(0.5)
                    self.init_block()
        
        self.running = False
        
        # Final statistics
        elapsed = time.time() - self.start_time
        print("\n" + "=" * 50)
        print("MINING COMPLETE")
        print(f"Blocks found: {blocks_mined}")
        print(f"Total hashes: {self.hash_count}")
        print(f"Time elapsed: {elapsed:.2f}s")
        if elapsed > 0:
            print(f"Average hash rate: {int(self.hash_count / elapsed)} H/s")
        print("=" * 50)
    
    def get_display(self) -> str:
        """Get current display as string"""
        lines = self.memory.get_display()
        return '\n'.join(lines)


# ============================================================================
# Test Suite
# ============================================================================

def test_minihash():
    """Test MiniHash-8 algorithm"""
    print("Testing MiniHash-8...")
    hasher = MiniHash8()
    
    # Test 1: Empty input
    result = hasher.update(b'')
    print(f"Empty hash: {result.hex()}")
    
    # Test 2: Simple input
    result = hasher.update(b'TEST')
    print(f"'TEST' hash: {result.hex()}")
    
    # Test 3: Consistency
    result1 = hasher.update(b'RUSTCHAIN')
    result2 = hasher.update(b'RUSTCHAIN')
    assert result1 == result2, "Hash not consistent!"
    print(f"'RUSTCHAIN' hash: {result1.hex()} ✓")
    
    print("MiniHash-8 tests passed!\n")


def test_miner():
    """Test miner functionality"""
    print("Testing TRS-80 Miner...")
    miner = TRS80Miner()
    
    # Test display initialization
    display = miner.get_display()
    assert "RUSTCHAIN" in display
    print("Display initialization ✓")
    
    # Test hash calculation
    miner.init_block()
    print(f"Block initialized, nonce=0")
    
    # Test mining (find 1 block)
    print("Starting mining test...")
    miner.run(max_blocks=1)
    
    assert miner.blocks_found >= 1
    print("Mining test passed!\n")


def run_demo():
    """Run interactive demo"""
    print("\n" + "=" * 64)
    print("  TRS-80 MINER - RUSTCHAIN PORT TO 1977 HARDWARE")
    print("=" * 64)
    print()
    
    miner = TRS80Miner()
    
    # Show initial display
    print("Initial Display:")
    print(miner.get_display())
    print()
    
    # Run mining (auto-start, no input needed)
    print("Starting mining (3 blocks)...")
    print()
    miner.run(max_blocks=3)
    
    # Show final display
    print("\nFinal Display:")
    print(miner.get_display())


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            test_minihash()
            test_miner()
        elif sys.argv[1] == "--hash":
            test_minihash()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: python simulator.py [--test|--hash]")
    else:
        run_demo()
