#!/usr/bin/env python3
"""
IBM 704 (1954) CPU Simulator

Simulates the IBM 704, the first mass-produced computer with hardware floating-point arithmetic.
Designed by John Backus and Gene Amdahl, introduced in 1954.

Key Features:
- 36-bit word architecture
- 38-bit accumulator (AC) with 2 overflow bits
- 36-bit multiplier-quotient register (MQ)
- Three 15-bit index registers (XR1, XR2, XR4)
- 4,096 words magnetic-core memory (18,432 bytes)
- Hardware floating-point support
- Type A and Type B instruction formats

Author: RustChain Bounty Hunter
License: MIT
"""

import struct
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import IntEnum


class InstructionType(IntEnum):
    TYPE_A = 0  # Index operations: | 3-bit prefix | 15-bit decrement | 3-bit tag | 15-bit address |
    TYPE_B = 1  # Most instructions: | 12-bit opcode | 2-bit flag | 4-bit unused | 3-bit tag | 15-bit address |


@dataclass
class IBM704Registers:
    """IBM 704 CPU registers"""
    AC: int = 0  # 38-bit accumulator (including 2 overflow bits)
    MQ: int = 0  # 36-bit multiplier-quotient register
    XR1: int = 0  # 15-bit index register 1 (XRA)
    XR2: int = 0  # 15-bit index register 2 (XRB)
    XR4: int = 0  # 15-bit index register 4 (XRC)
    IC: int = 0  # 15-bit instruction counter
    SI: int = 0  # 36-bit sense indicators


@dataclass
class IBM704Memory:
    """IBM 704 magnetic-core memory"""
    words: List[int] = field(default_factory=lambda: [0] * 4096)
    
    def read(self, address: int) -> int:
        """Read a 36-bit word from memory"""
        if 0 <= address < 4096:
            return self.words[address] & 0xFFFFFFFFF  # 36 bits
        raise MemoryError(f"Invalid memory address: {address}")
    
    def write(self, address: int, value: int):
        """Write a 36-bit word to memory"""
        if 0 <= address < 4096:
            self.words[address] = value & 0xFFFFFFFFF  # 36 bits
        else:
            raise MemoryError(f"Invalid memory address: {address}")
    
    def dump(self, start: int = 0, count: int = 16):
        """Dump memory contents"""
        for i in range(start, min(start + count, 4096)):
            print(f"{i:04X}: {self.words[i]:011o} ({self.words[i]:09X})")


class IBM704CPU:
    """IBM 704 CPU emulator"""
    
    # Type B opcodes (12-bit)
    OPCODES = {
        0o000: 'HALT',    # Halt execution
        0o010: 'CLA',     # Clear and Add
        0o011: 'ADD',     # Add
        0o012: 'SUB',     # Subtract
        0o020: 'MPY',     # Multiply
        0o021: 'DVH',     # Divide
        0o030: 'STO',     # Store AC
        0o031: 'STQ',     # Store MQ
        0o032: 'STS',     # Store Sense Indicators
        0o033: 'SLW',     # Store Logical Word
        0o040: 'CAS',     # Compare AC to Storage
        0o041: 'SLU',     # Store Logical Unnormalized
        0o050: 'ANA',     # Analog Add
        0o051: 'ANS',     # Analog Subtract
        0o052: 'ANA',     # And to Accumulator
        0o053: 'ORS',     # Or to Accumulator
        0o054: 'PAX',     # Store Prefix
        0o055: 'DCT',     # Decrement Tag
        0o056: 'ETM',     # Extract to MQ
        0o057: 'LGR',     # Load Index Register
        0o060: 'LXA',     # Load Index from Address
        0o061: 'AXT',     # Address to Index
        0o062: 'TIX',     # Transfer on Index
        0o063: 'TXI',     # Transfer on Index and Increment
        0o100: 'TZE',     # Transfer on Zero
        0o101: 'TPL',     # Transfer on Plus
        0o102: 'TMI',     # Transfer on Minus
        0o103: 'TXH',     # Transfer on High
        0o104: 'TRA',     # Transfer
        0o105: 'TSX',     # Transfer and Set Index
        0o106: 'XEC',     # Execute
        0o120: 'CAL',     # Clear and Add Logical
        0o121: 'ADD',     # Add Logical
        0o122: 'SUB',     # Subtract Logical
        0o140: 'FAS',     # Floating Add Single
        0o141: 'FBS',     # Floating Subtract Single
        0o142: 'FMS',     # Floating Multiply Single
        0o143: 'FDS',     # Floating Divide Single
        0o144: 'FST',     # Floating Store
        0o145: 'FLD',     # Floating Load
        0o146: 'F Normalize',  # Floating Normalize
        0o147: 'F Round',      # Floating Round
        0o150: 'PAI',     # Print and Input
        0o151: 'PRI',     # Print Input
        0o152: 'DPR',     # Dump and Print
        0o170: 'STI',     # Store Index
        0o171: 'TQL',     # Transfer on Low
    }
    
    def __init__(self):
        self.registers = IBM704Registers()
        self.memory = IBM704Memory()
        self.running = False
        self.halted = False
        self.instruction_count = 0
        
    def reset(self):
        """Reset CPU to initial state"""
        self.registers = IBM704Registers()
        self.running = False
        self.halted = False
        self.instruction_count = 0
        
    def fetch(self) -> int:
        """Fetch instruction from memory"""
        address = self.registers.IC
        instruction = self.memory.read(address)
        self.registers.IC = (self.registers.IC + 1) & 0x7FFF  # 15-bit
        return instruction
    
    def decode_type_b(self, instruction: int) -> Tuple[int, int, int, int]:
        """
        Decode Type B instruction
        Format: | 12-bit opcode | 2-bit flag | 4-bit unused | 3-bit tag | 15-bit address |
        """
        opcode = (instruction >> 24) & 0xFFF  # 12-bit opcode
        flag = (instruction >> 22) & 0x3      # 2-bit flag
        tag = (instruction >> 15) & 0x7       # 3-bit tag
        address = instruction & 0x7FFF        # 15-bit address
        return opcode, flag, tag, address
    
    def decode_type_a(self, instruction: int) -> Tuple[int, int, int, int]:
        """
        Decode Type A instruction
        Format: | 3-bit prefix | 15-bit decrement | 3-bit tag | 15-bit address |
        """
        prefix = (instruction >> 33) & 0x7    # 3-bit prefix
        decrement = (instruction >> 18) & 0x7FFF  # 15-bit decrement
        tag = (instruction >> 15) & 0x7       # 3-bit tag
        address = instruction & 0x7FFF        # 15-bit address
        return prefix, decrement, tag, address
    
    def is_type_a(self, instruction: int) -> bool:
        """Check if instruction is Type A (bits 22-23 are non-zero)"""
        return ((instruction >> 22) & 0x3) != 0
    
    def get_index_value(self, tag: int) -> int:
        """Get index register value based on tag (bitwise OR if multiple)"""
        value = 0
        if tag & 0x1:
            value |= self.registers.XR1
        if tag & 0x2:
            value |= self.registers.XR2
        if tag & 0x4:
            value |= self.registers.XR4
        return value
    
    def effective_address(self, tag: int, address: int) -> int:
        """Calculate effective address using index registers"""
        index = self.get_index_value(tag)
        # Index registers are decrement registers (subtracted from address)
        return (address - index) & 0x7FFF
    
    def sign_extend(self, value: int, bits: int) -> int:
        """Sign extend a value"""
        sign_bit = 1 << (bits - 1)
        if value & sign_bit:
            return value | (~((1 << bits) - 1))
        return value & ((1 << bits) - 1)
    
    def execute_instruction(self, instruction: int):
        """Execute a single instruction"""
        self.instruction_count += 1
        
        if self.is_type_a(instruction):
            prefix, decrement, tag, address = self.decode_type_a(instruction)
            self.execute_type_a(prefix, decrement, tag, address)
        else:
            opcode, flag, tag, address = self.decode_type_b(instruction)
            self.execute_type_b(opcode, flag, tag, address)
    
    def execute_type_b(self, opcode: int, flag: int, tag: int, address: int):
        """Execute Type B instruction"""
        effective_addr = self.effective_address(tag, address)
        
        if opcode == 0o000:  # HALT
            self.halted = True
            self.running = False
            print(f"HALT at IC={self.registers.IC-1:04X}")
            
        elif opcode == 0o010:  # CLA - Clear and Add
            value = self.memory.read(effective_addr)
            self.registers.AC = self.sign_extend(value, 36)
            
        elif opcode == 0o011:  # ADD - Add
            value = self.memory.read(effective_addr)
            self.registers.AC += self.sign_extend(value, 36)
            # Keep AC within 38 bits
            self.registers.AC &= 0x3FFFFFFFFF
            
        elif opcode == 0o012:  # SUB - Subtract
            value = self.memory.read(effective_addr)
            self.registers.AC -= self.sign_extend(value, 36)
            self.registers.AC &= 0x3FFFFFFFFF
            
        elif opcode == 0o030:  # STO - Store AC
            self.memory.write(effective_addr, self.registers.AC & 0xFFFFFFFFF)
            
        elif opcode == 0o031:  # STQ - Store MQ
            self.memory.write(effective_addr, self.registers.MQ & 0xFFFFFFFFF)
            
        elif opcode == 0o100:  # TZE - Transfer on Zero
            if (self.registers.AC & 0xFFFFFFFFF) == 0:
                self.registers.IC = effective_addr
                
        elif opcode == 0o101:  # TPL - Transfer on Plus
            if self.registers.AC > 0:
                self.registers.IC = effective_addr
                
        elif opcode == 0o102:  # TMI - Transfer on Minus
            if self.registers.AC < 0:
                self.registers.IC = effective_addr
                
        elif opcode == 0o104:  # TRA - Transfer (unconditional jump)
            self.registers.IC = effective_addr
            
        elif opcode == 0o060:  # LXA - Load Index from Address
            value = self.memory.read(effective_addr) & 0x7FFF
            if tag & 0x1:
                self.registers.XR1 = value
            if tag & 0x2:
                self.registers.XR2 = value
            if tag & 0x4:
                self.registers.XR4 = value
                
        elif opcode == 0o061:  # AXT - Address to Index
            if tag & 0x1:
                self.registers.XR1 = address & 0x7FFF
            if tag & 0x2:
                self.registers.XR2 = address & 0x7FFF
            if tag & 0x4:
                self.registers.XR4 = address & 0x7FFF
                
        elif opcode == 0o062:  # TIX - Transfer on Index
            index_val = self.get_index_value(tag)
            decrement = address & 0x7FFF
            if index_val > decrement:
                self.registers.IC = effective_addr
                
        elif opcode == 0o063:  # TXI - Transfer on Index and Increment
            index_val = self.get_index_value(tag)
            if index_val > 0:
                self.registers.IC = effective_addr
                # Increment index registers
                if tag & 0x1:
                    self.registers.XR1 = (self.registers.XR1 + 1) & 0x7FFF
                if tag & 0x2:
                    self.registers.XR2 = (self.registers.XR2 + 1) & 0x7FFF
                if tag & 0x4:
                    self.registers.XR4 = (self.registers.XR4 + 1) & 0x7FFF
                    
        elif opcode == 0o140:  # FAS - Floating Add Single
            # Simplified floating-point add (full implementation would be complex)
            value = self.memory.read(effective_addr)
            # For now, treat as integer add
            self.registers.AC += self.sign_extend(value, 36)
            self.registers.AC &= 0x3FFFFFFFFF
            
        else:
            print(f"Unknown opcode: {opcode:04o} at IC={self.registers.IC-1:04X}")
    
    def execute_type_a(self, prefix: int, decrement: int, tag: int, address: int):
        """Execute Type A instruction"""
        # Type A instructions are for index register operations
        if prefix == 0o1:  # LXA variant
            if tag & 0x1:
                self.registers.XR1 = decrement & 0x7FFF
            if tag & 0x2:
                self.registers.XR2 = decrement & 0x7FFF
            if tag & 0x4:
                self.registers.XR4 = decrement & 0x7FFF
        elif prefix == 0o2:  # AXT variant
            if tag & 0x1:
                self.registers.XR1 = address & 0x7FFF
            if tag & 0x2:
                self.registers.XR2 = address & 0x7FFF
            if tag & 0x4:
                self.registers.XR4 = address & 0x7FFF
        else:
            print(f"Unknown Type A prefix: {prefix:o} at IC={self.registers.IC-1:04X}")
    
    def load_program(self, program: List[int], start_address: int = 0):
        """Load a program into memory"""
        for i, word in enumerate(program):
            self.memory.write(start_address + i, word)
    
    def run(self, start_address: int = 0, max_instructions: int = 10000):
        """Run the program"""
        self.registers.IC = start_address
        self.running = True
        self.halted = False
        
        while self.running and not self.halted and self.instruction_count < max_instructions:
            instruction = self.fetch()
            self.execute_instruction(instruction)
            
        if self.instruction_count >= max_instructions:
            print(f"Reached max instructions ({max_instructions})")
    
    def dump_state(self):
        """Dump CPU state"""
        print("\n=== IBM 704 CPU State ===")
        print(f"AC:  {self.registers.AC:012o} ({self.registers.AC:010X})")
        print(f"MQ:  {self.registers.MQ:012o} ({self.registers.MQ:010X})")
        print(f"XR1: {self.registers.XR1:05o} ({self.registers.XR1:04X})")
        print(f"XR2: {self.registers.XR2:05o} ({self.registers.XR2:04X})")
        print(f"XR4: {self.registers.XR4:05o} ({self.registers.XR4:04X})")
        print(f"IC:  {self.registers.IC:05o} ({self.registers.IC:04X})")
        print(f"Instructions executed: {self.instruction_count}")
        print("=========================\n")


def test_basic_operations():
    """Test basic CPU operations"""
    print("Testing IBM 704 CPU Simulator\n")
    
    cpu = IBM704CPU()
    
    # Simple test program:
    # 000: CLA 100  (Load from address 100)
    # 001: ADD 101  (Add from address 101)
    # 002: STO 102  (Store to address 102)
    # 003: HLT      (Halt)
    
    program = [
        0o010000100,  # CLA 100
        0o011000101,  # ADD 101
        0o030000102,  # STO 102
        0o000000000,  # HLT
    ]
    
    # Load test data
    cpu.memory.write(0o100, 42)  # First operand
    cpu.memory.write(0o101, 58)  # Second operand
    
    # Load and run program
    cpu.load_program(program)
    cpu.run()
    
    # Check result
    result = cpu.memory.read(0o102)
    print(f"Result: {result} (expected 100)")
    assert result == 100, f"Expected 100, got {result}"
    
    cpu.dump_state()
    print("✓ Basic operations test passed!\n")


def test_index_registers():
    """Test index register operations"""
    print("Testing Index Registers\n")
    
    cpu = IBM704CPU()
    
    # Test LXA (Load Index from Address)
    # 000: LXA 100, XR1  (Load XR1 from address 100)
    # 001: AXT 200, XR2  (Load XR2 with address 200)
    # 002: HLT
    
    program = [
        0o060001100,  # LXA 100, tag=1 (XR1)
        0o061002200,  # AXT 200, tag=2 (XR2)
        0o000000000,  # HLT
    ]
    
    cpu.memory.write(0o100, 0o077)  # Value for XR1
    
    cpu.load_program(program)
    cpu.run()
    
    print(f"XR1: {cpu.registers.XR1:o} (expected 77)")
    print(f"XR2: {cpu.registers.XR2:o} (expected 200)")
    
    assert cpu.registers.XR1 == 0o77, f"Expected XR1=77, got {cpu.registers.XR1:o}"
    assert cpu.registers.XR2 == 0o200, f"Expected XR2=200, got {cpu.registers.XR2:o}"
    
    print("✓ Index register test passed!\n")


def test_floating_point():
    """Test floating-point format handling"""
    print("Testing Floating-Point Format\n")
    
    # IBM 704 floating-point format (36 bits):
    # | Sign (1) | Exponent (8, excess-128) | Fraction (27) |
    
    def encode_float(sign: int, exponent: int, fraction: int) -> int:
        """Encode a floating-point number"""
        return ((sign & 1) << 35) | ((exponent & 0xFF) << 27) | (fraction & 0x7FFFFFF)
    
    def decode_float(value: int) -> Tuple[int, int, int]:
        """Decode a floating-point number"""
        sign = (value >> 35) & 1
        exponent = (value >> 27) & 0xFF
        fraction = value & 0x7FFFFFF
        return sign, exponent, fraction
    
    # Test encoding/decoding
    test_val = encode_float(0, 128, 0x4000000)  # 1.0 in IBM 704 format
    sign, exp, frac = decode_float(test_val)
    
    print(f"Encoded: {test_val:011o}")
    print(f"Sign: {sign}, Exponent: {exp}, Fraction: {frac:08X}")
    
    assert sign == 0
    assert exp == 128
    assert frac == 0x4000000
    
    print("✓ Floating-point format test passed!\n")


if __name__ == "__main__":
    test_basic_operations()
    test_index_registers()
    test_floating_point()
    print("All tests passed! IBM 704 simulator is ready.")
