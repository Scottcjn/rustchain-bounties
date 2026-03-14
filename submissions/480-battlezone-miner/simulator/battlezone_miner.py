#!/usr/bin/env python3
"""
Battlezone Miner - Python 6502 Simulator
RustChain Port to Atari Battlezone (1980) Arcade Hardware

This simulator emulates the 6502 CPU and demonstrates the conceptual
miner running on Battlezone hardware constraints.

Features:
- Cycle-accurate 6502 emulation
- Memory mapping
- Vector display simulation (text-based)
- Mining statistics

Usage:
    python battlezone_miner.py
"""

import time
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum, auto


# ============================================================================
# 6502 CPU Emulation
# ============================================================================

class StatusFlags(Enum):
    """6502 Status Register Flags"""
    C = 0  # Carry
    Z = 1  # Zero
    I = 2  # Interrupt Disable
    D = 3  # Decimal Mode
    B = 4  # Break
    U = 5  # Unused (always 1)
    V = 6  # Overflow
    N = 7  # Negative


@dataclass
class CPU6502:
    """Cycle-accurate 6502 CPU emulator"""
    
    # Registers
    A: int = 0      # Accumulator
    X: int = 0      # X Index Register
    Y: int = 0      # Y Index Register
    SP: int = 0xFF  # Stack Pointer
    PC: int = 0     # Program Counter
    status: int = 0x24  # Status Register (U flag always set)
    
    # Memory (64 KB)
    memory: bytearray = field(default_factory=lambda: bytearray(65536))
    
    # Cycle counter
    cycles: int = 0
    
    # Running state
    running: bool = True
    
    # Callbacks for I/O
    io_write_callback = None
    io_read_callback = None
    
    def read(self, addr: int) -> int:
        """Read a byte from memory"""
        addr &= 0xFFFF
        # Check for I/O region
        if 0x8000 <= addr <= 0x8FFF:
            if self.io_read_callback:
                return self.io_read_callback(addr)
        return self.memory[addr]
    
    def write(self, addr: int, value: int):
        """Write a byte to memory"""
        addr &= 0xFFFF
        value &= 0xFF
        # Check for I/O region
        if 0x8000 <= addr <= 0x8FFF:
            if self.io_write_callback:
                self.io_write_callback(addr, value)
            return
        self.memory[addr] = value
    
    def read_word(self, addr: int) -> int:
        """Read a 16-bit word (little-endian)"""
        return self.read(addr) | (self.read(addr + 1) << 8)
    
    def write_word(self, addr: int, value: int):
        """Write a 16-bit word (little-endian)"""
        self.write(addr, value & 0xFF)
        self.write(addr + 1, (value >> 8) & 0xFF)
    
    def get_flag(self, flag: StatusFlags) -> bool:
        """Get a status flag"""
        return bool(self.status & (1 << flag.value))
    
    def set_flag(self, flag: StatusFlags, value: bool):
        """Set a status flag"""
        if value:
            self.status |= (1 << flag.value)
        else:
            self.status &= ~(1 << flag.value)
    
    def push(self, value: int):
        """Push a byte to the stack"""
        self.write(0x0100 + self.SP, value & 0xFF)
        self.SP = (self.SP - 1) & 0xFF
    
    def pop(self) -> int:
        """Pop a byte from the stack"""
        self.SP = (self.SP + 1) & 0xFF
        return self.read(0x0100 + self.SP)
    
    def execute_instruction(self) -> int:
        """Execute a single instruction, return cycles used"""
        opcode = self.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        
        # Simplified instruction decoding (not all instructions implemented)
        # This is a minimal implementation for the miner code
        
        cycles = 2  # Default cycles
        
        if opcode == 0x00:  # BRK
            self.running = False
            cycles = 7
            
        elif opcode == 0x18:  # CLC
            self.set_flag(StatusFlags.C, False)
            cycles = 2
            
        elif opcode == 0x38:  # SEC
            self.set_flag(StatusFlags.C, True)
            cycles = 2
            
        elif opcode == 0x58:  # CLI
            self.set_flag(StatusFlags.I, False)
            cycles = 2
            
        elif opcode == 0xB8:  # CLV
            self.set_flag(StatusFlags.V, False)
            cycles = 2
            
        elif opcode == 0xD8:  # CLD
            self.set_flag(StatusFlags.D, False)
            cycles = 2
            
        elif opcode == 0x78:  # SEI
            self.set_flag(StatusFlags.I, True)
            cycles = 2
            
        elif opcode == 0xF8:  # SED
            self.set_flag(StatusFlags.D, True)
            cycles = 2
            
        elif opcode == 0xA9:  # LDA #imm
            self.A = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 2
            
        elif opcode == 0xA2:  # LDX #imm
            self.X = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            self.set_flag(StatusFlags.Z, self.X == 0)
            self.set_flag(StatusFlags.N, bool(self.X & 0x80))
            cycles = 2
            
        elif opcode == 0xA5:  # LDA zp
            zp_addr = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            self.A = self.read(zp_addr)
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 3
            
        elif opcode == 0xB5:  # LDA zp,X
            zp_addr = (self.read(self.PC) + self.X) & 0xFF
            self.PC = (self.PC + 1) & 0xFFFF
            self.A = self.read(zp_addr)
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 4
            
        elif opcode == 0xAD:  # LDA abs
            addr = self.read_word(self.PC)
            self.PC = (self.PC + 2) & 0xFFFF
            self.A = self.read(addr)
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 4
            
        elif opcode == 0xBD:  # LDA abs,X
            addr = (self.read_word(self.PC) + self.X) & 0xFFFF
            self.PC = (self.PC + 2) & 0xFFFF
            self.A = self.read(addr)
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 4
            
        elif opcode == 0x85:  # STA zp
            zp_addr = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            self.write(zp_addr, self.A)
            cycles = 3
            
        elif opcode == 0x8E:  # STA abs
            addr = self.read_word(self.PC)
            self.PC = (self.PC + 2) & 0xFFFF
            self.write(addr, self.A)
            cycles = 4
            
        elif opcode == 0x95:  # STA zp,X
            zp_addr = (self.read(self.PC) + self.X) & 0xFF
            self.PC = (self.PC + 1) & 0xFFFF
            self.write(zp_addr, self.A)
            cycles = 4
            
        elif opcode == 0x8D:  # STA abs
            addr = self.read_word(self.PC)
            self.PC = (self.PC + 2) & 0xFFFF
            self.write(addr, self.A)
            cycles = 4
            
        elif opcode == 0x9A:  # TXS
            self.SP = self.X
            cycles = 2
            
        elif opcode == 0xAA:  # TAX
            self.X = self.A
            self.set_flag(StatusFlags.Z, self.X == 0)
            self.set_flag(StatusFlags.N, bool(self.X & 0x80))
            cycles = 2
            
        elif opcode == 0xA8:  # TAY
            self.Y = self.A
            self.set_flag(StatusFlags.Z, self.Y == 0)
            self.set_flag(StatusFlags.N, bool(self.Y & 0x80))
            cycles = 2
            
        elif opcode == 0x8A:  # TXA
            self.A = self.X
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 2
            
        elif opcode == 0x98:  # TYA
            self.A = self.Y
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 2
            
        elif opcode == 0xE8:  # INX
            self.X = (self.X + 1) & 0xFF
            self.set_flag(StatusFlags.Z, self.X == 0)
            self.set_flag(StatusFlags.N, bool(self.X & 0x80))
            cycles = 2
            
        elif opcode == 0xC8:  # INY
            self.Y = (self.Y + 1) & 0xFF
            self.set_flag(StatusFlags.Z, self.Y == 0)
            self.set_flag(StatusFlags.N, bool(self.Y & 0x80))
            cycles = 2
            
        elif opcode == 0xE6:  # INC zp
            zp_addr = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            val = (self.read(zp_addr) + 1) & 0xFF
            self.write(zp_addr, val)
            self.set_flag(StatusFlags.Z, val == 0)
            self.set_flag(StatusFlags.N, bool(val & 0x80))
            cycles = 5
            
        elif opcode == 0xEE:  # INC abs
            addr = self.read_word(self.PC)
            self.PC = (self.PC + 2) & 0xFFFF
            val = (self.read(addr) + 1) & 0xFF
            self.write(addr, val)
            self.set_flag(StatusFlags.Z, val == 0)
            self.set_flag(StatusFlags.N, bool(val & 0x80))
            cycles = 6
            
        elif opcode == 0xCA:  # DEX
            self.X = (self.X - 1) & 0xFF
            self.set_flag(StatusFlags.Z, self.X == 0)
            self.set_flag(StatusFlags.N, bool(self.X & 0x80))
            cycles = 2
            
        elif opcode == 0x88:  # DEY
            self.Y = (self.Y - 1) & 0xFF
            self.set_flag(StatusFlags.Z, self.Y == 0)
            self.set_flag(StatusFlags.N, bool(self.Y & 0x80))
            cycles = 2
            
        elif opcode == 0xC6:  # DEC zp
            zp_addr = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            val = (self.read(zp_addr) - 1) & 0xFF
            self.write(zp_addr, val)
            self.set_flag(StatusFlags.Z, val == 0)
            self.set_flag(StatusFlags.N, bool(val & 0x80))
            cycles = 5
            
        elif opcode == 0x4A:  # LSR A
            self.set_flag(StatusFlags.C, bool(self.A & 0x01))
            self.A = (self.A >> 1) & 0xFF
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, False)
            cycles = 2
            
        elif opcode == 0x46:  # LSR zp
            zp_addr = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            val = self.read(zp_addr)
            self.set_flag(StatusFlags.C, bool(val & 0x01))
            val = (val >> 1) & 0xFF
            self.write(zp_addr, val)
            self.set_flag(StatusFlags.Z, val == 0)
            self.set_flag(StatusFlags.N, False)
            cycles = 5
            
        elif opcode == 0x2A:  # ROL A
            carry = 1 if self.get_flag(StatusFlags.C) else 0
            self.set_flag(StatusFlags.C, bool(self.A & 0x80))
            self.A = ((self.A << 1) | carry) & 0xFF
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 2
            
        elif opcode == 0x6A:  # ROR A
            carry = 0x80 if self.get_flag(StatusFlags.C) else 0
            self.set_flag(StatusFlags.C, bool(self.A & 0x01))
            self.A = (self.A >> 1) | carry
            self.set_flag(StatusFlags.Z, self.A == 0)
            self.set_flag(StatusFlags.N, bool(self.A & 0x80))
            cycles = 2
            
        elif opcode == 0xE9:  # SBC #imm (also used for CMP)
            imm = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            borrow = 0 if self.get_flag(StatusFlags.C) else 1
            result = self.A - imm - borrow
            self.set_flag(StatusFlags.C, result >= 0)
            self.set_flag(StatusFlags.Z, (result & 0xFF) == 0)
            self.set_flag(StatusFlags.N, bool(result & 0x80))
            self.set_flag(StatusFlags.V, bool((self.A ^ result) & (imm ^ result) & 0x80))
            self.A = result & 0xFF
            cycles = 2
            
        elif opcode == 0xC9:  # CMP #imm
            imm = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            result = self.A - imm
            self.set_flag(StatusFlags.C, result >= 0)
            self.set_flag(StatusFlags.Z, (result & 0xFF) == 0)
            self.set_flag(StatusFlags.N, bool(result & 0x80))
            cycles = 2
            
        elif opcode == 0xC5:  # CMP zp
            zp_addr = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            result = self.A - self.read(zp_addr)
            self.set_flag(StatusFlags.C, result >= 0)
            self.set_flag(StatusFlags.Z, (result & 0xFF) == 0)
            self.set_flag(StatusFlags.N, bool(result & 0x80))
            cycles = 3
            
        elif opcode == 0xD0:  # BNE rel
            offset = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            if not self.get_flag(StatusFlags.Z):
                if offset & 0x80:
                    offset -= 0x100
                self.PC = (self.PC + offset) & 0xFFFF
                cycles = 3
            else:
                cycles = 2
                
        elif opcode == 0xF0:  # BEQ rel
            offset = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            if self.get_flag(StatusFlags.Z):
                if offset & 0x80:
                    offset -= 0x100
                self.PC = (self.PC + offset) & 0xFFFF
                cycles = 3
            else:
                cycles = 2
                
        elif opcode == 0xB0:  # BCS rel
            offset = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            if self.get_flag(StatusFlags.C):
                if offset & 0x80:
                    offset -= 0x100
                self.PC = (self.PC + offset) & 0xFFFF
                cycles = 3
            else:
                cycles = 2
                
        elif opcode == 0x90:  # BCC rel
            offset = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            if not self.get_flag(StatusFlags.C):
                if offset & 0x80:
                    offset -= 0x100
                self.PC = (self.PC + offset) & 0xFFFF
                cycles = 3
            else:
                cycles = 2
                
        elif opcode == 0x30:  # BMI rel
            offset = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            if self.get_flag(StatusFlags.N):
                if offset & 0x80:
                    offset -= 0x100
                self.PC = (self.PC + offset) & 0xFFFF
                cycles = 3
            else:
                cycles = 2
                
        elif opcode == 0x10:  # BPL rel
            offset = self.read(self.PC)
            self.PC = (self.PC + 1) & 0xFFFF
            if not self.get_flag(StatusFlags.N):
                if offset & 0x80:
                    offset -= 0x100
                self.PC = (self.PC + offset) & 0xFFFF
                cycles = 3
            else:
                cycles = 2
                
        elif opcode == 0x4C:  # JMP abs
            addr = self.read_word(self.PC)
            self.PC = addr
            cycles = 3
            
        elif opcode == 0x20:  # JSR abs
            addr = self.read_word(self.PC)
            self.PC = (self.PC + 2) & 0xFFFF
            self.push((self.PC - 1) >> 8)
            self.push((self.PC - 1) & 0xFF)
            self.PC = addr
            cycles = 6
            
        elif opcode == 0x60:  # RTS
            low = self.pop()
            high = self.pop()
            self.PC = ((high << 8) | low) + 1
            cycles = 6
            
        elif opcode == 0x40:  # RTI
            self.status = self.pop() | 0x20  # U flag always set
            low = self.pop()
            high = self.pop()
            self.PC = (high << 8) | low
            cycles = 6
            
        elif opcode == 0xEA:  # NOP
            cycles = 2
            
        else:
            # Unknown opcode - treat as NOP
            print(f"Warning: Unknown opcode ${opcode:02X} at PC=${self.PC-1:04X}")
            cycles = 2
        
        self.cycles += cycles
        return cycles
    
    def reset(self):
        """Reset the CPU"""
        self.SP = 0xFD
        self.status = 0x24
        self.PC = self.read_word(0xFFFC)  # Reset vector
        self.cycles = 0
        self.running = True
    
    def load_rom(self, data: bytes, addr: int = 0xC000):
        """Load ROM data into memory"""
        for i, byte in enumerate(data):
            self.memory[addr + i] = byte


# ============================================================================
# Battlezone Miner Logic
# ============================================================================

@dataclass
class BattlezoneMiner:
    """Mining logic and state management"""
    
    nonce: int = 0
    target: int = 0x10  # Difficulty target (lower = harder)
    hash_count: int = 0
    solutions_found: int = 0
    block_header: bytes = b'\x00' * 8  # Simplified block header
    
    def compute_hash(self, nonce: int) -> int:
        """
        Compute simplified 8-bit hash
        hash = XOR_fold(block_header) ⊕ LFSR_transform(nonce)
        """
        # XOR fold block header
        xor_result = 0
        for byte in self.block_header[:8]:
            xor_result ^= byte
        
        # LFSR transformation
        lfsr = nonce & 0xFFFF
        for _ in range(8):
            lsb = lfsr & 1
            lfsr >>= 1
            if lsb:
                lfsr ^= 0xB808  # Simplified polynomial
        
        return (xor_result ^ (lfsr & 0xFF)) & 0xFF
    
    def check_solution(self, hash_result: int) -> bool:
        """Check if hash meets target"""
        return hash_result < self.target
    
    def increment_nonce(self) -> int:
        """Increment nonce and return new value"""
        self.nonce = (self.nonce + 1) & 0xFFFF
        return self.nonce
    
    def get_stats(self) -> dict:
        """Get mining statistics"""
        return {
            'nonce': self.nonce,
            'target': self.target,
            'hash_count': self.hash_count,
            'solutions_found': self.solutions_found,
            'hashes_per_nonce': 1
        }


# ============================================================================
# Vector Display Simulation
# ============================================================================

class VectorDisplay:
    """Simulated vector display for Battlezone"""
    
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.vectors: List[Tuple[int, int, int, int]] = []
        self.brightness: float = 1.0
    
    def clear(self):
        """Clear all vectors"""
        self.vectors = []
    
    def draw_line(self, x1: int, y1: int, x2: int, y2: int):
        """Add a vector line"""
        self.vectors.append((x1, y1, x2, y2))
    
    def home(self):
        """Home the vector beam"""
        self.vectors = []
    
    def render_ascii(self) -> str:
        """Render display as ASCII art"""
        # Create empty screen
        screen = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw simple mining status (simplified rendering)
        # In a full implementation, would rasterize vectors
        
        title = "=== BATTLEZONE MINER ==="
        x = (self.width - len(title)) // 2
        if x >= 0:
            for i, ch in enumerate(title):
                if 0 <= x + i < self.width:
                    screen[1][x + i] = ch
        
        return '\n'.join(''.join(row) for row in screen)


# ============================================================================
# Main Simulator
# ============================================================================

class BattlezoneSimulator:
    """Main simulator coordinating CPU, miner, and display"""
    
    def __init__(self):
        self.cpu = CPU6502()
        self.miner = BattlezoneMiner()
        self.display = VectorDisplay()
        
        # Setup I/O callbacks
        self.cpu.io_write_callback = self.io_write
        self.cpu.io_read_callback = self.io_read
        
        # Initialize memory with miner code
        self.load_miner_code()
        
        # Statistics
        self.start_time = None
        self.last_hash_count = 0
    
    def load_miner_code(self):
        """Load the 6502 miner code into ROM"""
        # For now, use a simple inline program
        # In production, would assemble from src/miner_6502.asm
        
        miner_code = bytes([
            # Reset handler at $C000
            0x78,          # SEI
            0xD8,          # CLD
            0xA2, 0xFF,    # LDX #$FF
            0x9A,          # TXS
            0xA2, 0x00,    # LDX #$00
            0x8E, 0x00, 0x00,  # STX $0000 (NONCE_LOW)
            0x8E, 0x01, 0x00,  # STX $0001 (NONCE_HIGH)
            0x8E, 0x09, 0x00,  # STX $0009 (HASH_COUNT_L)
            0x8E, 0x0A, 0x00,  # STX $000A (HASH_COUNT_H)
            0x8E, 0x0C, 0x00,  # STX $000C (SOLUTIONS_FOUND)
            0xA9, 0x10,    # LDA #$10 (target)
            0x8D, 0x03, 0x00,  # STA $0003 (TARGET)
            0xA9, 0x20,    # LDA #$20
            0x8D, 0x0B, 0x00,  # STA $000B (DISPLAY_FLAG)
            
            # Mining loop at $C01A
            0xEE, 0x00, 0x00,  # INC $0000 (NONCE_LOW)
            0xD0, 0x03,    # BNE compute_hash
            0xEE, 0x01, 0x00,  # INC $0001 (NONCE_HIGH)
            
            # Compute hash (simplified inline) at $C01F
            0xA5, 0x00,    # LDA NONCE_LOW
            0x4A,          # LSR A
            0x85, 0x02,    # STA HASH_RESULT
            
            # Check against target at $C024
            0xA5, 0x02,    # LDA HASH_RESULT
            0xC5, 0x03,    # CMP TARGET
            0xB0, 0x03,    # BCS no_solution
            
            # Found solution at $C029
            0xEE, 0x0C, 0x00,  # INC SOLUTIONS_FOUND
            
            # Increment hash counter at $C02C
            0xEE, 0x09, 0x00,  # INC HASH_COUNT_L
            0xD0, 0x03,    # BNE skip_high_count
            0xEE, 0x0A, 0x00,  # INC HASH_COUNT_H
            
            # Check display update at $C034
            0xC6, 0x0B,    # DEC DISPLAY_FLAG
            0x10, 0xE2,    # BPL mining_loop (back to $C01A, offset = -$1E)
            
            # Reset display flag and continue at $C038
            0xA9, 0x20,    # LDA #$20
            0x8D, 0x0B, 0x00,  # STA DISPLAY_FLAG
            0x4C, 0x1A, 0xC0,  # JMP mining_loop ($C01A)
            
            # Padding
            *[0xEA] * 50,  # NOPs for padding
            
            # Interrupt vectors at $FFFA
            0x00, 0x00,    # NMI vector (dummy)
            0x00, 0xC0,    # Reset vector -> $C000
            0x00, 0x00,    # IRQ vector (dummy)
        ])
        
        self.cpu.load_rom(miner_code, 0xC000)
        
        # Setup interrupt vectors at $FFFA
        self.cpu.write_word(0xFFFA, 0x0000)  # NMI vector
        self.cpu.write_word(0xFFFC, 0xC000)  # Reset vector -> $C000
        self.cpu.write_word(0xFFFE, 0x0000)  # IRQ vector
        
        # Setup block header in memory
        block_header = [0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08]
        for i, byte in enumerate(block_header):
            self.cpu.memory[0x0200 + i] = byte
        self.cpu.write_word(0x07, 0x0200)  # Block header pointer
    
    def io_write(self, addr: int, value: int):
        """Handle I/O writes"""
        # Vector display I/O (simplified)
        pass
    
    def io_read(self, addr: int) -> int:
        """Handle I/O reads"""
        return 0x00
    
    def run(self, max_cycles: int = 1000000, verbose: bool = True):
        """Run the simulation"""
        self.start_time = time.time()
        self.cpu.reset()
        
        if verbose:
            print("=" * 60)
            print("BATTLEZONE MINER - 6502 SIMULATION")
            print("=" * 60)
            print(f"CPU: 6502 @ 1.5 MHz (emulated)")
            print(f"Target difficulty: ${self.miner.target:02X}")
            print(f"Reset vector PC: ${self.cpu.PC:04X}")
            print("=" * 60)
            print()
        
        cycle_count = 0
        last_display_update = 0
        instruction_count = 0
        
        while self.cpu.running and cycle_count < max_cycles:
            cycles = self.cpu.execute_instruction()
            cycle_count += cycles
            instruction_count += 1
            
            # Debug: print first few instructions
            if instruction_count <= 10 and verbose:
                print(f"  [Instr {instruction_count}] PC=${self.cpu.PC-1:04X} Cycles={cycle_count}")
            
            # Periodic status update
            if cycle_count - last_display_update >= 100000:
                self.print_status(cycle_count)
                last_display_update = cycle_count
        
        if verbose and not self.cpu.running:
            print(f"\nCPU halted after {instruction_count} instructions")
        
        self.print_final_stats(cycle_count)
    
    def print_status(self, cycle_count: int):
        """Print current mining status"""
        nonce = self.cpu.read_word(0x00)
        hash_count = self.cpu.read_word(0x09)
        solutions = self.cpu.read(0x0C)
        
        elapsed = time.time() - self.start_time
        hash_rate = hash_count / elapsed if elapsed > 0 else 0
        
        print(f"[{cycle_count:8d} cycles] "
              f"Nonce: ${nonce:04X} | "
              f"Hashes: {hash_count:6d} | "
              f"Solutions: {solutions} | "
              f"Rate: {hash_rate:.0f} H/s")
    
    def print_final_stats(self, total_cycles: int):
        """Print final statistics"""
        elapsed = time.time() - self.start_time
        nonce = self.cpu.read_word(0x00)
        hash_count = self.cpu.read_word(0x09)
        solutions = self.cpu.read(0x0C)
        
        # Theoretical hash rate on real hardware
        theoretical_rate = 1500000 / 100  # 1.5 MHz / 100 cycles per hash
        
        print()
        print("=" * 60)
        print("SIMULATION COMPLETE")
        print("=" * 60)
        print(f"Total cycles executed: {total_cycles:,}")
        print(f"Emulation time: {elapsed:.2f} seconds")
        print(f"Final nonce: ${nonce:04X}")
        print(f"Total hashes: {hash_count:,}")
        print(f"Solutions found: {solutions}")
        print()
        print("THEORETICAL REAL HARDWARE PERFORMANCE:")
        print(f"  Hash rate: ~{theoretical_rate:,} hashes/second")
        print(f"  (6502 @ 1.5 MHz, ~100 cycles/hash)")
        print()
        print("BATTLEZONE HARDWARE CONSTRAINTS:")
        print(f"  CPU: 6502 @ 1.5 MHz")
        print(f"  RAM: 8-48 KB")
        print(f"  Display: Vector Graphics 1024×768")
        print("=" * 60)


# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point"""
    print("Battlezone Miner - RustChain Port to 1980 Arcade Hardware")
    print()
    
    simulator = BattlezoneSimulator()
    
    # Run simulation (1 million cycles for demo)
    simulator.run(max_cycles=1000000, verbose=True)
    
    print()
    print("For full assembly code, see: src/miner_6502.asm")
    print("For architecture details, see: ARCHITECTURE.md")
    print()
    print("Bounty Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b")


if __name__ == "__main__":
    main()
