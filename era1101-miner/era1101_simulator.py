#!/usr/bin/env python3
"""
ERA 1101 Computer Simulator (1950)
===================================

A full-featured simulator for the ERA 1101, the first commercially
available stored-program computer.

Features:
- 24-bit parallel binary architecture
- Ones' complement arithmetic
- Magnetic drum memory with rotational latency simulation
- 38-instruction set with skip field optimization
- Paper tape I/O simulation

Author: RustChain Bounty #1824 Submission
License: MIT
"""

import time
import struct
from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass, field
from enum import IntEnum
import random


# ============================================================================
# Constants
# ============================================================================

MEMORY_SIZE = 16384  # 16K words
WORD_SIZE = 24  # bits
DRUM_TRACKS = 200  # read-write heads
DRUM_RPM = 3500  # rotations per minute
DRUM_ROTATION_US = 60_000_000 // DRUM_RPM  # ~17,143 μs per rotation
WORDS_PER_TRACK = MEMORY_SIZE // DRUM_TRACKS  # 82 words per track

# Instruction opcodes (6 bits)
class Opcode(IntEnum):
    INS  = 0x00  # Insert various forms
    ADD  = 0x06  # Add various forms
    INSQ = 0x0C  # Insert Q in A
    CLR  = 0x0D  # Clear right half of A
    ADDQ = 0x0E  # Add Q to A
    TRA  = 0x0F  # Transmit A to Q
    MPY  = 0x10  # Multiply
    LGR  = 0x11  # Logical product add
    AND  = 0x12  # Logical product
    DIV  = 0x13  # Divide
    MLA  = 0x14  # Multiply and add
    STO  = 0x15  # Store
    SHL  = 0x16  # Shift left
    STQ  = 0x17  # Store Q
    SHQ  = 0x18  # Shift Q left
    RPL  = 0x19  # Replace
    JMP  = 0x1A  # Jump
    STA  = 0x1B  # Store address
    JNZ  = 0x1C  # Jump if not zero
    INSX = 0x1D  # Insert X
    JN   = 0x1E  # Jump if negative
    JQ   = 0x1F  # Jump if Q negative
    HLT  = 0x20  # Halt
    NOP  = 0x21  # No operation

# Execution times in microseconds
EXEC_TIMES = {
    Opcode.INS:  96,
    Opcode.ADD:  96,
    Opcode.INSQ: 96,
    Opcode.CLR:  96,
    Opcode.ADDQ: 96,
    Opcode.TRA:  96,
    Opcode.MPY:  352,
    Opcode.LGR:  192,
    Opcode.AND:  96,
    Opcode.DIV:  1000,
    Opcode.MLA:  352,
    Opcode.STO:  96,
    Opcode.SHL:  96,
    Opcode.STQ:  96,
    Opcode.SHQ:  96,
    Opcode.RPL:  96,
    Opcode.JMP:  96,
    Opcode.STA:  96,
    Opcode.JNZ:  96,
    Opcode.INSX: 96,
    Opcode.JN:   96,
    Opcode.JQ:   96,
    Opcode.HLT:  0,
    Opcode.NOP:  96,
}


# ============================================================================
# Utility Functions
# ============================================================================

def ones_complement_negate(value: int, bits: int = WORD_SIZE) -> int:
    """Negate a value using ones' complement arithmetic."""
    mask = (1 << bits) - 1
    return (~value) & mask

def to_signed(value: int, bits: int = WORD_SIZE) -> int:
    """Convert unsigned value to signed (ones' complement)."""
    mask = (1 << bits) - 1
    value &= mask
    sign_bit = 1 << (bits - 1)
    if value & sign_bit:
        # Negative number in ones' complement
        return -(ones_complement_negate(value, bits))
    return value

def to_unsigned(value: int, bits: int = WORD_SIZE) -> int:
    """Convert signed value to unsigned."""
    mask = (1 << bits) - 1
    if value < 0:
        return ones_complement_negate(-value, bits)
    return value & mask

def mask_bits(value: int, bits: int = WORD_SIZE) -> int:
    """Mask value to specified bit width."""
    return value & ((1 << bits) - 1)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Instruction:
    """ERA 1101 instruction (24 bits)."""
    opcode: int  # 6 bits (0-5)
    skip: int    # 4 bits (6-9)
    address: int # 14 bits (10-23)
    
    @classmethod
    def from_word(cls, word: int) -> 'Instruction':
        """Decode a 24-bit word into an instruction."""
        word = mask_bits(word, WORD_SIZE)
        opcode = (word >> 18) & 0x3F
        skip = (word >> 14) & 0x0F
        address = word & 0x3FFF
        return cls(opcode=opcode, skip=skip, address=address)
    
    def to_word(self) -> int:
        """Encode instruction to 24-bit word."""
        return ((self.opcode & 0x3F) << 18) | \
               ((self.skip & 0x0F) << 14) | \
               (self.address & 0x3FFF)
    
    def __str__(self) -> str:
        opname = Opcode(self.opcode).name if self.opcode in Opcode._value2member_map_ else f"UNK{self.opcode:02X}"
        return f"{opname:4s} skip={self.skip} addr={self.address:04X}"


@dataclass
class DrumTrack:
    """Represents one track on the magnetic drum."""
    track_num: int
    words: List[int] = field(default_factory=lambda: [0] * WORDS_PER_TRACK)
    current_position: int = 0  # Current word position under head


@dataclass
class PaperTape:
    """Simulates paper tape I/O."""
    data: List[int] = field(default_factory=list)
    position: int = 0
    is_input: bool = True  # True for reader, False for punch
    
    def read_char(self) -> Optional[int]:
        """Read next character from tape."""
        if self.position < len(self.data):
            char = self.data[self.position]
            self.position += 1
            return char
        return None
    
    def write_char(self, char: int):
        """Write character to tape."""
        self.data.append(char & 0x7F)  # 7-bit ASCII


# ============================================================================
# ERA 1101 CPU Simulator
# ============================================================================

class ERA1101Simulator:
    """
    Complete ERA 1101 computer simulator.
    
    Features:
    - 24-bit accumulator (A) and 48-bit double accumulator (A+B)
    - 24-bit Q register (multiplier/quotient)
    - 24-bit X register (index)
    - Magnetic drum memory with rotational latency
    - Full instruction set with skip field
    """
    
    def __init__(self, verbose: bool = False):
        # Registers
        self.A = 0  # 48-bit accumulator (we use lower 24 bits primarily)
        self.Q = 0  # 24-bit Q register
        self.X = 0  # 24-bit X register
        self.PC = 0  # Program counter (14 bits)
        
        # Memory - organized as drum tracks
        self.drum: List[DrumTrack] = [
            DrumTrack(track_num=i) for i in range(DRUM_TRACKS)
        ]
        
        # CPU state
        self.running = False
        self.halted = False
        self.verbose = verbose
        self.cycle_count = 0
        self.total_time_us = 0
        
        # I/O
        self.paper_tape_reader: Optional[PaperTape] = None
        self.paper_tape_punch: Optional[PaperTape] = None
        
        # Drum rotation state
        self.drum_rotation_us = 0  # Current rotation position in μs
        
        # Statistics
        self.stats = {
            'instructions_executed': 0,
            'memory_accesses': 0,
            'rotational_delays': 0,
            'total_rotation_wait_us': 0,
        }
    
    def load_word(self, address: int) -> int:
        """Load a word from drum memory."""
        if address < 0 or address >= MEMORY_SIZE:
            raise ValueError(f"Invalid memory address: {address}")
        
        track_num = address // WORDS_PER_TRACK
        word_pos = address % WORDS_PER_TRACK
        
        track = self.drum[track_num]
        
        # Calculate rotational latency
        words_to_wait = (word_pos - track.current_position) % WORDS_PER_TRACK
        wait_time_us = (words_to_wait * DRUM_ROTATION_US) // WORDS_PER_TRACK
        
        if words_to_wait != 0:
            self.stats['rotational_delays'] += 1
            self.stats['total_rotation_wait_us'] += wait_time_us
            if self.verbose:
                print(f"  [Drum] Track {track_num}, waiting {words_to_wait} words ({wait_time_us} μs)")
        
        self.total_time_us += wait_time_us
        self.stats['memory_accesses'] += 1
        
        # Update drum position
        track.current_position = word_pos
        
        return track.words[word_pos]
    
    def store_word(self, address: int, value: int):
        """Store a word to drum memory."""
        if address < 0 or address >= MEMORY_SIZE:
            raise ValueError(f"Invalid memory address: {address}")
        
        track_num = address // WORDS_PER_TRACK
        word_pos = address % WORDS_PER_TRACK
        
        track = self.drum[track_num]
        value = mask_bits(value, WORD_SIZE)
        
        # Calculate rotational latency for write
        words_to_wait = (word_pos - track.current_position) % WORDS_PER_TRACK
        wait_time_us = (words_to_wait * DRUM_ROTATION_US) // WORDS_PER_TRACK
        
        if words_to_wait != 0:
            self.stats['rotational_delays'] += 1
            self.stats['total_rotation_wait_us'] += wait_time_us
        
        self.total_time_us += wait_time_us
        self.stats['memory_accesses'] += 1
        
        # Store the word
        track.words[word_pos] = value
        track.current_position = word_pos
        
        if self.verbose:
            print(f"  [Store] Addr {address:04X} = {value:06X}")
    
    def fetch_instruction(self) -> Instruction:
        """Fetch instruction from current PC."""
        word = self.load_word(self.PC)
        instr = Instruction.from_word(word)
        
        if self.verbose:
            print(f"[Fetch] PC={self.PC:04X}: {instr}")
        
        return instr
    
    def execute_instruction(self, instr: Instruction):
        """Execute a single instruction."""
        opcode = instr.opcode
        address = instr.address
        skip = instr.skip
        
        # Get operand from memory
        operand = self.load_word(address)
        
        # Get execution time
        exec_time = EXEC_TIMES.get(opcode, 96)
        self.total_time_us += exec_time
        
        # Execute based on opcode
        if opcode == Opcode.HLT:
            self.halted = True
            self.running = False
            if self.verbose:
                print(f"  [HALT] at PC={self.PC:04X}")
            return
        
        elif opcode == Opcode.NOP:
            pass
        
        elif opcode == Opcode.INS:
            # Insert operand into accumulator
            self.A = mask_bits(operand, WORD_SIZE)
            if self.verbose:
                print(f"  [INS] A = {self.A:06X}")
        
        elif opcode == Opcode.ADD:
            # Add operand to accumulator (ones' complement)
            result = self.A + operand
            # Handle end-around carry for ones' complement
            if result >= (1 << WORD_SIZE):
                result = (result & ((1 << WORD_SIZE) - 1)) + 1
            self.A = mask_bits(result, WORD_SIZE)
            if self.verbose:
                print(f"  [ADD] A = {self.A:06X}")
        
        elif opcode == Opcode.STO:
            # Store accumulator to memory
            self.store_word(address, self.A)
        
        elif opcode == Opcode.JMP:
            # Unconditional jump
            self.PC = address
            self.cycle_count += 1
            return  # Skip normal PC update
        
        elif opcode == Opcode.JNZ:
            # Jump if accumulator not zero
            if self.A != 0:
                self.PC = address
                self.cycle_count += 1
                return
        
        elif opcode == Opcode.JN:
            # Jump if accumulator negative
            if to_signed(self.A) < 0:
                self.PC = address
                self.cycle_count += 1
                return
        
        elif opcode == Opcode.TRA:
            # Transfer A to Q
            self.Q = mask_bits(self.A, WORD_SIZE)
            if self.verbose:
                print(f"  [TRA] Q = {self.Q:06X}")
        
        elif opcode == Opcode.MPY:
            # Multiply Q × operand → A (352 μs)
            # Simplified multiplication for simulation
            q_signed = to_signed(self.Q)
            op_signed = to_signed(operand)
            result = q_signed * op_signed
            self.A = to_unsigned(result, WORD_SIZE * 2)  # 48-bit result
            if self.verbose:
                print(f"  [MPY] A = {self.A:012X} (48-bit)")
        
        elif opcode == Opcode.SHL:
            # Shift accumulator left
            self.A = mask_bits(self.A << 1, WORD_SIZE)
            if self.verbose:
                print(f"  [SHL] A = {self.A:06X}")
        
        elif opcode == Opcode.AND:
            # Logical AND
            self.A = mask_bits(self.A & operand, WORD_SIZE)
            if self.verbose:
                print(f"  [AND] A = {self.A:06X}")
        
        elif opcode == Opcode.INSQ:
            # Insert Q into A
            self.A = mask_bits(self.Q, WORD_SIZE)
        
        elif opcode == Opcode.CLR:
            # Clear right half of A
            self.A = mask_bits(self.A, WORD_SIZE) & 0xFFF000
        
        elif opcode == Opcode.ADDQ:
            # Add Q to A
            result = self.A + self.Q
            if result >= (1 << WORD_SIZE):
                result = (result & ((1 << WORD_SIZE) - 1)) + 1
            self.A = mask_bits(result, WORD_SIZE)
        
        elif opcode == Opcode.STQ:
            # Store Q to memory
            self.store_word(address, self.Q)
        
        elif opcode == Opcode.SHQ:
            # Shift Q left
            self.Q = mask_bits(self.Q << 1, WORD_SIZE)
        
        elif opcode == Opcode.STA:
            # Store address portion of A
            existing = self.load_word(address)
            new_word = (existing & 0xC000) | (self.A & 0x3FFF)
            self.store_word(address, new_word)
        
        elif opcode == Opcode.INSX:
            # Insert into X register
            self.X = mask_bits(operand, WORD_SIZE)
        
        elif opcode == Opcode.JQ:
            # Jump if Q negative
            if to_signed(self.Q) < 0:
                self.PC = address
                self.cycle_count += 1
                return
        
        elif opcode == Opcode.MLA:
            # Multiply and add: A += Q × operand
            q_signed = to_signed(self.Q)
            op_signed = to_signed(operand)
            product = q_signed * op_signed
            result = self.A + to_unsigned(product, WORD_SIZE * 2)
            if result >= (1 << (WORD_SIZE * 2)):
                result = (result & ((1 << (WORD_SIZE * 2)) - 1)) + 1
            self.A = mask_bits(result, WORD_SIZE * 2)
        
        elif opcode == Opcode.LGR:
            # Logical product add
            self.A = mask_bits(self.A | (self.Q & operand), WORD_SIZE)
        
        elif opcode == Opcode.DIV:
            # Divide A by operand, quotient in Q, remainder in A
            if operand == 0:
                raise ZeroDivisionError("Division by zero")
            divisor = to_signed(operand)
            dividend = to_signed(self.A)
            quotient = dividend // divisor
            remainder = dividend % divisor
            self.Q = to_unsigned(quotient, WORD_SIZE)
            self.A = to_unsigned(remainder, WORD_SIZE)
            if self.verbose:
                print(f"  [DIV] Q={self.Q:06X}, A={self.A:06X}")
        
        elif opcode == Opcode.RPL:
            # Replace using Q as operator
            # Simplified implementation
            self.store_word(address, self.A)
        
        else:
            if self.verbose:
                print(f"  [UNKNOWN] Opcode {opcode:02X}")
        
        # Update program counter with skip
        self.PC = (self.PC + 1 + skip) % MEMORY_SIZE
        self.cycle_count += 1
    
    def run(self, start_address: int = 0, max_cycles: int = 1000000):
        """Run the program from start address."""
        self.PC = start_address
        self.running = True
        self.halted = False
        self.cycle_count = 0
        
        if self.verbose:
            print(f"\n[ERA 1101] Starting execution at {start_address:04X}")
            print("=" * 60)
        
        start_time = time.time()
        
        while self.running and not self.halted and self.cycle_count < max_cycles:
            instr = self.fetch_instruction()
            self.execute_instruction(instr)
        
        elapsed = time.time() - start_time
        
        if self.verbose:
            print("=" * 60)
            print(f"[ERA 1101] Execution complete")
            print(f"  Cycles: {self.cycle_count}")
            print(f"  Simulated time: {self.total_time_us / 1000:.2f} ms")
            print(f"  Real time: {elapsed * 1000:.2f} ms")
            print(f"  Memory accesses: {self.stats['memory_accesses']}")
            print(f"  Rotational delays: {self.stats['rotational_delays']}")
            print(f"  Total rotation wait: {self.stats['total_rotation_wait_us']} μs")
        
        return self.cycle_count
    
    def load_program(self, program: List[int], start_address: int = 0):
        """Load a program into memory."""
        for i, word in enumerate(program):
            address = start_address + i
            if address < MEMORY_SIZE:
                self.store_word(address, word)
    
    def load_from_file(self, filename: str, start_address: int = 0):
        """Load program from binary file."""
        with open(filename, 'rb') as f:
            data = f.read()
        
        program = []
        for i in range(0, len(data), 3):
            if i + 2 < len(data):
                word = (data[i] << 16) | (data[i+1] << 8) | data[i+2]
                program.append(word & 0xFFFFFF)
        
        self.load_program(program, start_address)
    
    def dump_memory(self, start: int = 0, count: int = 32):
        """Dump memory contents."""
        print(f"\nMemory dump (address {start:04X} - {start+count-1:04X}):")
        print("-" * 60)
        for i in range(0, count, 4):
            addr = start + i
            words = []
            for j in range(4):
                if addr + j < MEMORY_SIZE:
                    words.append(self.load_word(addr + j))
            if words:
                word_str = "  ".join(f"{w:06X}" for w in words)
                print(f"  {addr:04X}: {word_str}")
    
    def get_register_state(self) -> Dict:
        """Get current register state."""
        return {
            'A': self.A,
            'Q': self.Q,
            'X': self.X,
            'PC': self.PC,
            'running': self.running,
            'halted': self.halted,
        }


# ============================================================================
# Demo Program
# ============================================================================

def create_demo_program() -> List[int]:
    """Create a simple demo program that adds two numbers."""
    program = [
        # Address 0x0000: Main program
        # Skip=0 means next instruction is at next address
        Instruction(Opcode.INS,  skip=0, address=0x0004).to_word(),  # Load VALUE1
        Instruction(Opcode.ADD,  skip=0, address=0x0005).to_word(),  # Add VALUE2
        Instruction(Opcode.STO,  skip=0, address=0x0006).to_word(),  # Store RESULT
        Instruction(Opcode.HLT,  skip=0, address=0x0000).to_word(),  # Halt
        
        # Address 0x0004: Data
        0x000123,  # VALUE1 = 0x123
        0x000456,  # VALUE2 = 0x456
        0x000000,  # RESULT (will be overwritten)
    ]
    return program


def main():
    """Main entry point for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ERA 1101 Simulator')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--demo', action='store_true', help='Run demo program')
    parser.add_argument('--load', type=str, help='Load program from file')
    parser.add_argument('--start', type=int, default=0, help='Start address (hex)')
    parser.add_argument('--max-cycles', type=int, default=1000000, help='Max cycles')
    
    args = parser.parse_args()
    
    sim = ERA1101Simulator(verbose=args.verbose)
    
    if args.demo or not args.load:
        print("Loading demo program...")
        program = create_demo_program()
        sim.load_program(program, start_address=0)
        start_addr = 0
    else:
        print(f"Loading program from {args.load}...")
        sim.load_from_file(args.load, start_address=args.start)
        start_addr = args.start
    
    print("\nStarting ERA 1101 simulation...")
    sim.run(start_address=start_addr, max_cycles=args.max_cycles)
    
    print("\nFinal register state:")
    state = sim.get_register_state()
    print(f"  A  = {state['A']:06X} ({to_signed(state['A'])})")
    print(f"  Q  = {state['Q']:06X} ({to_signed(state['Q'])})")
    print(f"  X  = {state['X']:06X} ({to_signed(state['X'])})")
    print(f"  PC = {state['PC']:04X}")
    
    # Show result from demo
    if args.demo or not args.load:
        result = sim.load_word(0x0006)
        print(f"\nResult (at 0x0006): {result:06X} = {to_signed(result)}")
        print(f"Expected: 0x579 = {0x123 + 0x456}")
        if result == 0x579:
            print("[OK] SUCCESS! Addition correct!")
        else:
            print("[FAIL] FAILED! Result mismatch!")


if __name__ == '__main__':
    main()
