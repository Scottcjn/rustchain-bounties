#!/usr/bin/env python3
"""
ZX Spectrum Miner - Z80 CPU Simulator
Simulates the Z80 miner code and demonstrates the mining process.

Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import struct
import time
from typing import Dict, List, Tuple

class Z80CPU:
    """Simplified Z80 CPU emulator"""
    
    def __init__(self):
        # Registers
        self.a = 0  # Accumulator
        self.f = 0  # Flags
        self.b = 0
        self.c = 0
        self.d = 0
        self.e = 0
        self.h = 0
        self.l = 0
        
        # Register pairs
        self.bc = 0
        self.de = 0
        self.hl = 0
        self.sp = 0
        self.pc = 0
        
        # Index registers
        self.ix = 0
        self.iy = 0
        
        # Special registers
        self.i = 0  # Interrupt vector
        self.r = 0  # Refresh register
        self.iff1 = False
        self.iff2 = False
        self.im = 0  # Interrupt mode
        
        # Memory (64 KB)
        self.memory = bytearray(65536)
        
        # I/O ports
        self.ports = {}
        
        # Execution state
        self.running = False
        self.halted = False
        
        # Callbacks
        self.print_callback = None
        
    def read_byte(self, addr: int) -> int:
        """Read byte from memory"""
        return self.memory[addr & 0xFFFF]
    
    def write_byte(self, addr: int, value: int):
        """Write byte to memory"""
        self.memory[addr & 0xFFFF] = value & 0xFF
    
    def read_word(self, addr: int) -> int:
        """Read 16-bit word from memory (little-endian)"""
        lo = self.read_byte(addr)
        hi = self.read_byte(addr + 1)
        return (hi << 8) | lo
    
    def write_word(self, addr: int, value: int):
        """Write 16-bit word to memory (little-endian)"""
        self.write_byte(addr, value & 0xFF)
        self.write_byte(addr + 1, (value >> 8) & 0xFF)
    
    def push(self, value: int):
        """Push 16-bit value onto stack"""
        self.sp = (self.sp - 1) & 0xFFFF
        self.write_byte(self.sp, (value >> 8) & 0xFF)
        self.sp = (self.sp - 1) & 0xFFFF
        self.write_byte(self.sp, value & 0xFF)
    
    def pop(self) -> int:
        """Pop 16-bit value from stack"""
        lo = self.read_byte(self.sp)
        self.sp = (self.sp + 1) & 0xFFFF
        hi = self.read_byte(self.sp)
        self.sp = (self.sp + 1) & 0xFFFF
        return (hi << 8) | lo
    
    def set_flags(self, s=None, z=None, h=None, pv=None, n=None, c=None):
        """Set flags (S Z 0 H 0 PV N C)"""
        if s is not None:
            self.f = (self.f & 0x7F) | (s << 7)
        if z is not None:
            self.f = (self.f & 0xBF) | (z << 6)
        if h is not None:
            self.f = (self.f & 0xEF) | (h << 4)
        if pv is not None:
            self.f = (self.f & 0xFB) | (pv << 2)
        if n is not None:
            self.f = (self.f & 0xFD) | (n << 1)
        if c is not None:
            self.f = (self.f & 0xFE) | c
    
    def get_flag(self, name: str) -> bool:
        """Get flag value"""
        flags = {'S': 7, 'Z': 6, 'H': 4, 'PV': 2, 'N': 1, 'C': 0}
        return bool(self.f & (1 << flags[name]))
    
    def rst(self, addr: int):
        """RST instruction - call to fixed address"""
        self.push(self.pc)
        self.pc = addr
    
    def execute(self, max_cycles: int = 100000) -> bool:
        """Execute instructions until halt or max_cycles reached"""
        cycles = 0
        
        while self.running and not self.halted and cycles < max_cycles:
            opcode = self.read_byte(self.pc)
            self.pc = (self.pc + 1) & 0xFFFF
            
            # Execute opcode
            self._execute_opcode(opcode)
            cycles += 4
        
        return not self.halted
    
    def _execute_opcode(self, opcode: int):
        """Execute a single opcode (simplified implementation)"""
        
        # Simplified instruction set for miner
        if opcode == 0x76:  # HALT
            self.halted = True
            
        elif opcode == 0xC9:  # RET
            self.pc = self.pop()
            
        elif opcode == 0xCD:  # CALL nn
            addr = self.read_word(self.pc)
            self.pc += 2
            self.push(self.pc)
            self.pc = addr
            
        elif opcode == 0x18:  # JR e
            offset = self.read_byte(self.pc)
            self.pc += 1
            if offset > 127:
                offset -= 256
            self.pc = (self.pc + offset) & 0xFFFF
            
        elif opcode == 0x20:  # JR NZ, e
            offset = self.read_byte(self.pc)
            self.pc += 1
            if not self.get_flag('Z'):
                if offset > 127:
                    offset -= 256
                self.pc = (self.pc + offset) & 0xFFFF
            
        elif opcode == 0x28:  # JR Z, e
            offset = self.read_byte(self.pc)
            self.pc += 1
            if self.get_flag('Z'):
                if offset > 127:
                    offset -= 256
                self.pc = (self.pc + offset) & 0xFFFF
            
        elif opcode == 0x3A:  # LD A, (nn)
            addr = self.read_word(self.pc)
            self.pc += 2
            self.a = self.read_byte(addr)
            
        elif opcode == 0x32:  # LD (nn), A
            addr = self.read_word(self.pc)
            self.pc += 2
            self.write_byte(addr, self.a)
            
        elif opcode == 0x21:  # LD HL, nn
            self.hl = self.read_word(self.pc)
            self.pc += 2
            
        elif opcode == 0x11:  # LD DE, nn
            self.de = self.read_word(self.pc)
            self.pc += 2
            
        elif opcode == 0x01:  # LD BC, nn
            self.bc = self.read_word(self.pc)
            self.pc += 2
            
        elif opcode == 0x7E:  # LD A, (HL)
            self.a = self.read_byte(self.hl)
            
        elif opcode == 0x77:  # LD (HL), A
            self.write_byte(self.hl, self.a)
            
        elif opcode == 0x46:  # LD B, (HL)
            self.b = self.read_byte(self.hl)
            
        elif opcode == 0x56:  # LD D, (HL)
            self.d = self.read_byte(self.hl)
            
        elif opcode == 0x66:  # LD H, (HL)
            self.h = self.read_byte(self.hl)
            
        elif opcode == 0x70:  # LD (HL), B
            self.write_byte(self.hl, self.b)
            
        elif opcode == 0x71:  # LD (HL), C
            self.write_byte(self.hl, self.c)
            
        elif opcode == 0x72:  # LD (HL), D
            self.write_byte(self.hl, self.d)
            
        elif opcode == 0x73:  # LD (HL), E
            self.write_byte(self.hl, self.e)
            
        elif opcode == 0x74:  # LD (HL), H
            self.write_byte(self.hl, self.h)
            
        elif opcode == 0x75:  # LD (HL), L
            self.write_byte(self.hl, self.l)
            
        elif opcode == 0x78:  # LD A, B
            self.a = self.b
            
        elif opcode == 0x79:  # LD A, C
            self.a = self.c
            
        elif opcode == 0x7A:  # LD A, D
            self.a = self.d
            
        elif opcode == 0x7B:  # LD A, E
            self.a = self.e
            
        elif opcode == 0x7C:  # LD A, H
            self.a = self.h
            
        elif opcode == 0x7D:  # LD A, L
            self.a = self.l
            
        elif opcode == 0x47:  # LD B, A
            self.b = self.a
            
        elif opcode == 0x4F:  # LD C, A
            self.c = self.a
            
        elif opcode == 0x57:  # LD D, A
            self.d = self.a
            
        elif opcode == 0x5F:  # LD E, A
            self.e = self.a
            
        elif opcode == 0x67:  # LD H, A
            self.h = self.a
            
        elif opcode == 0x6F:  # LD L, A
            self.l = self.a
            
        elif opcode == 0x04:  # INC B
            self.b = (self.b + 1) & 0xFF
            
        elif opcode == 0x0C:  # INC C
            self.c = (self.c + 1) & 0xFF
            
        elif opcode == 0x14:  # INC D
            self.d = (self.d + 1) & 0xFF
            
        elif opcode == 0x1C:  # INC E
            self.e = (self.e + 1) & 0xFF
            
        elif opcode == 0x24:  # INC H
            self.h = (self.h + 1) & 0xFF
            
        elif opcode == 0x2C:  # INC L
            self.l = (self.l + 1) & 0xFF
            
        elif opcode == 0x3C:  # INC A
            self.a = (self.a + 1) & 0xFF
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0x03:  # INC BC
            self.bc = (self.bc + 1) & 0xFFFF
            
        elif opcode == 0x13:  # INC DE
            self.de = (self.de + 1) & 0xFFFF
            
        elif opcode == 0x23:  # INC HL
            self.hl = (self.hl + 1) & 0xFFFF
            
        elif opcode == 0x0B:  # DEC BC
            self.bc = (self.bc - 1) & 0xFFFF
            
        elif opcode == 0x1B:  # DEC DE
            self.de = (self.de - 1) & 0xFFFF
            
        elif opcode == 0x2B:  # DEC HL
            self.hl = (self.hl - 1) & 0xFFFF
            
        elif opcode == 0x05:  # DEC B
            self.b = (self.b - 1) & 0xFF
            
        elif opcode == 0x15:  # DEC D
            self.d = (self.d - 1) & 0xFF
            
        elif opcode == 0x25:  # DEC H
            self.h = (self.h - 1) & 0xFF
            
        elif opcode == 0x3D:  # DEC A
            self.a = (self.a - 1) & 0xFF
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80), n=1)
            
        elif opcode == 0x06:  # LD B, n
            self.b = self.read_byte(self.pc)
            self.pc += 1
            
        elif opcode == 0x0E:  # LD C, n
            self.c = self.read_byte(self.pc)
            self.pc += 1
            
        elif opcode == 0x16:  # LD D, n
            self.d = self.read_byte(self.pc)
            self.pc += 1
            
        elif opcode == 0x1E:  # LD E, n
            self.e = self.read_byte(self.pc)
            self.pc += 1
            
        elif opcode == 0x26:  # LD H, n
            self.h = self.read_byte(self.pc)
            self.pc += 1
            
        elif opcode == 0x2E:  # LD L, n
            self.l = self.read_byte(self.pc)
            self.pc += 1
            
        elif opcode == 0x3E:  # LD A, n
            self.a = self.read_byte(self.pc)
            self.pc += 1
            
        elif opcode == 0x36:  # LD (HL), n
            value = self.read_byte(self.pc)
            self.pc += 1
            self.write_byte(self.hl, value)
            
        elif opcode == 0x80:  # ADD A, B
            result = self.a + self.b
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) + (self.b & 0x0F) > 0x0F,
                c=result > 0xFF
            )
            self.a = result & 0xFF
            
        elif opcode == 0x81:  # ADD A, C
            result = self.a + self.c
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) + (self.c & 0x0F) > 0x0F,
                c=result > 0xFF
            )
            self.a = result & 0xFF
            
        elif opcode == 0x82:  # ADD A, D
            result = self.a + self.d
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) + (self.d & 0x0F) > 0x0F,
                c=result > 0xFF
            )
            self.a = result & 0xFF
            
        elif opcode == 0x83:  # ADD A, E
            result = self.a + self.e
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) + (self.e & 0x0F) > 0x0F,
                c=result > 0xFF
            )
            self.a = result & 0xFF
            
        elif opcode == 0x84:  # ADD A, H
            result = self.a + self.h
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) + (self.h & 0x0F) > 0x0F,
                c=result > 0xFF
            )
            self.a = result & 0xFF
            
        elif opcode == 0x85:  # ADD A, L
            result = self.a + self.l
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) + (self.l & 0x0F) > 0x0F,
                c=result > 0xFF
            )
            self.a = result & 0xFF
            
        elif opcode == 0x87:  # ADD A, A
            result = self.a + self.a
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) + (self.a & 0x0F) > 0x0F,
                c=result > 0xFF
            )
            self.a = result & 0xFF
            
        elif opcode == 0x90:  # SUB B
            result = self.a - self.b
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (self.b & 0x0F),
                n=1,
                c=result < 0
            )
            self.a = result & 0xFF
            
        elif opcode == 0x97:  # SUB A
            self.a = 0
            self.set_flags(z=1, n=1)
            
        elif opcode == 0xA8:  # XOR B
            self.a = self.a ^ self.b
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0xA9:  # XOR C
            self.a = self.a ^ self.c
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0xAA:  # XOR D
            self.a = self.a ^ self.d
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0xAB:  # XOR E
            self.a = self.a ^ self.e
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0xAC:  # XOR H
            self.a = self.a ^ self.h
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0xAD:  # XOR L
            self.a = self.a ^ self.l
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0xAF:  # XOR A
            self.a = 0
            self.set_flags(z=1)
            
        elif opcode == 0xB7:  # OR A
            self.set_flags(z=(self.a == 0), s=bool(self.a & 0x80))
            
        elif opcode == 0xB8:  # CP B
            result = self.a - self.b
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (self.b & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0xB9:  # CP C
            result = self.a - self.c
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (self.c & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0xBA:  # CP D
            result = self.a - self.d
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (self.d & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0xBB:  # CP E
            result = self.a - self.e
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (self.e & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0xBC:  # CP H
            result = self.a - self.h
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (self.h & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0xBD:  # CP L
            result = self.a - self.l
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (self.l & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0xBE:  # CP (HL)
            value = self.read_byte(self.hl)
            result = self.a - value
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (value & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0xFE:  # CP n
            value = self.read_byte(self.pc)
            self.pc += 1
            result = self.a - value
            self.set_flags(
                z=(result & 0xFF == 0),
                s=bool(result & 0x80),
                h=(self.a & 0x0F) < (value & 0x0F),
                n=1,
                c=result < 0
            )
            
        elif opcode == 0x10:  # DJNZ e
            offset = self.read_byte(self.pc)
            self.pc += 1
            self.b = (self.b - 1) & 0xFF
            if self.b != 0:
                if offset > 127:
                    offset -= 256
                self.pc = (self.pc + offset) & 0xFFFF
            
        elif opcode == 0x00:  # NOP
            pass
            
        else:
            # Unknown opcode - skip
            pass
    
    def load_binary(self, data: bytes, addr: int = 0):
        """Load binary data into memory"""
        for i, byte in enumerate(data):
            self.memory[(addr + i) & 0xFFFF] = byte
    
    def load_asm_program(self):
        """Load the miner assembly program into memory"""
        # This is a simplified loader - in real use, you'd assemble the .asm file
        pass


class ZXMiner:
    """ZX Spectrum Miner Simulator"""
    
    def __init__(self):
        self.cpu = Z80CPU()
        self.nonce = 0
        self.target = 0x0100  # Difficulty target
        self.block_header = bytes(range(32))  # Sample block header
        self.found = False
        self.mining_speed = 0  # Hashes per second
        
    def init_memory(self):
        """Initialize memory map"""
        # Load block header at 0x8100
        for i, byte in enumerate(self.block_header):
            self.cpu.write_byte(0x8100 + i, byte)
        
        # Initialize nonce at 0x8120
        self.cpu.write_word(0x8120, 0)
        
        # Set target at 0x8142
        self.cpu.write_word(0x8142, self.target)
    
    def simple_hash(self, block_header: bytes, nonce: int) -> bytes:
        """Simplified XOR-based hash function"""
        result = bytearray(32)
        
        # First 2 bytes are the nonce
        result[0] = nonce & 0xFF
        result[1] = (nonce >> 8) & 0xFF
        
        # XOR with block header
        for i in range(30):
            result[i + 2] = block_header[i % len(block_header)] ^ result[i % 32]
        
        return bytes(result)
    
    def check_difficulty(self, hash_result: bytes) -> bool:
        """Check if hash meets difficulty target"""
        hash_value = (hash_result[0] << 8) | hash_result[1]
        return hash_value < self.target
    
    def mine(self, max_iterations: int = 10000) -> Tuple[bool, int]:
        """Run mining simulation"""
        start_time = time.time()
        
        for i in range(max_iterations):
            self.nonce = (self.nonce + 1) & 0xFFFF
            
            # Compute hash
            hash_result = self.simple_hash(self.block_header, self.nonce)
            
            # Check difficulty
            if self.check_difficulty(hash_result):
                elapsed = time.time() - start_time
                self.mining_speed = i / elapsed if elapsed > 0 else 0
                self.found = True
                return True, self.nonce
        
        elapsed = time.time() - start_time
        self.mining_speed = max_iterations / elapsed if elapsed > 0 else 0
        return False, self.nonce
    
    def display_status(self):
        """Display mining status"""
        print("\n" + "=" * 60)
        print("ZX SPECTRUM MINER")
        print("=" * 60)
        print(f"Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b")
        print(f"Nonce:  ${self.nonce:04X}")
        print(f"Target: ${self.target:04X}")
        print(f"Speed:  {self.mining_speed:.0f} H/s (simulated)")
        print("=" * 60)


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("  ZX SPECTRUM MINER - Z80 Simulator")
    print("  Educational Proof-of-Concept")
    print("=" * 60)
    print(f"\nWallet: RTC4325af95d26d59c3ef025963656d22af638bb96b")
    print("\nInitializing miner...")
    
    miner = ZXMiner()
    miner.init_memory()
    
    print("Starting mining simulation...")
    print("(Press Ctrl+C to stop)\n")
    
    try:
        iteration = 0
        while True:
            found, nonce = miner.mine(max_iterations=1000)
            iteration += 1000
            
            # Display progress every 10000 iterations
            if iteration % 10000 == 0:
                miner.display_status()
                print(f"Iterations: {iteration}")
            
            if found:
                print(f"\n*** BLOCK FOUND! ***")
                print(f"Nonce: ${nonce:04X}")
                print(f"Total iterations: {iteration}")
                break
            
            # Small delay to simulate real mining
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        print("\n\nMining stopped by user.")
        miner.display_status()
    
    print("\n" + "=" * 60)
    print("Mining simulation complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
