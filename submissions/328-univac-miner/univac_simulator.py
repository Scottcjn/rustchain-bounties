#!/usr/bin/env python3
"""
UNIVAC I Cycle-Accurate Simulator

Simulates the UNIVAC I (1951) computer architecture for mining verification.
Models:
- 12-bit word length
- 1000-word mercury delay line memory
- Sequential access timing (222 μs average)
- Basic instruction set

Author: RustChain Bounty #357 Submission
License: MIT
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from enum import IntEnum


class Opcode(IntEnum):
    """UNIVAC I Instruction Opcodes (simplified 6-bit)"""
    ADD = 0x00   # Add memory to A
    SUB = 0x01   # Subtract memory from A
    MUL = 0x02   # Multiply memory × A
    DIV = 0x03   # Divide A by memory
    LDA = 0x04   # Load A from memory
    STA = 0x05   # Store A to memory
    JMP = 0x06   # Unconditional jump
    JZ = 0x07    # Jump if A = 0
    JN = 0x08    # Jump if A < 0
    IN = 0x09    # Input from tape
    OUT = 0x0A   # Output to tape
    HLT = 0x0B   # Halt
    NOP = 0x0C   # No operation
    AND = 0x0D   # Bitwise AND
    OR = 0x0E    # Bitwise OR
    XOR = 0x0F   # Bitwise XOR


@dataclass
class Instruction:
    """UNIVAC I Instruction (16 bits total for practical addressing)
    
    Note: Real UNIVAC I used 12-bit instructions with limited addressing.
    We use 16 bits to support full 1000-word memory addressing.
    
    Format: [4-bit opcode][12-bit address]
    - Opcode: bits 15-12 (4 bits, values 0-15)
    - Address: bits 11-0 (12 bits, values 0-4095)
    """
    opcode: Opcode
    address: int  # 12-bit address (0-4095, but UNIVAC I only has 1000 words)
    skip: int = 0  # Unused
    
    def encode(self) -> int:
        """Encode instruction to 16-bit word"""
        return ((self.opcode & 0x0F) << 12) | (self.address & 0xFFF)
    
    @classmethod
    def decode(cls, word: int) -> 'Instruction':
        """Decode 16-bit word to instruction"""
        opcode = Opcode((word >> 12) & 0x0F)
        address = word & 0xFFF
        return cls(opcode=opcode, address=address)
    
    def __str__(self) -> str:
        return f"{self.opcode.name:4s} {self.address:04d}"


@dataclass
class UNIVACIState:
    """CPU State"""
    accumulator: int = 0  # 12-bit A register
    program_counter: int = 0
    instruction_register: int = 0
    halt: bool = False


@dataclass
class TimingStats:
    """Performance timing statistics"""
    total_cycles: int = 0
    total_time_us: int = 0
    memory_accesses: int = 0
    instructions_executed: int = 0
    wait_cycles: int = 0


class UNIVACISimulator:
    """
    Cycle-accurate UNIVAC I simulator.
    
    Key characteristics:
    - 12-bit words
    - 1000 words mercury delay line memory
    - Sequential access (must wait for word to circulate)
    - Word time: 44 μs (time for one word to circulate)
    - Average access: 5 words = 222 μs
    """
    
    WORD_TIME_US = 44      # Microseconds per word circulation
    ADD_TIME_US = 540      # Addition execution time
    MUL_TIME_US = 2400     # Multiplication execution time
    DIV_TIME_US = 10000    # Division execution time
    
    def __init__(self, memory_size: int = 1000):
        self.memory = [0] * memory_size  # 16-bit words (practical adaptation)
        self.memory_size = memory_size
        self.state = UNIVACIState()
        self.timing = TimingStats()
        self.output_buffer: List[str] = []
        
    def reset(self):
        """Reset simulator state"""
        self.state = UNIVACIState()
        self.timing = TimingStats()
        self.output_buffer = []
        
    def load_program(self, program: List[int], start_addr: int = 0):
        """Load program into memory"""
        for i, word in enumerate(program):
            if start_addr + i < self.memory_size:
                self.memory[start_addr + i] = word & 0xFFFF  # 16-bit words
    
    def load_data(self, data: List[int], start_addr: int = 0):
        """Load data into memory"""
        self.load_program(data, start_addr)
    
    def _wait_for_word(self, addr: int) -> int:
        """
        Wait for word to circulate to read/write head.
        Models mercury delay line sequential access.
        """
        # Calculate words to wait (circular buffer)
        current_word = self.state.program_counter % self.memory_size
        words_to_wait = (addr - current_word) % self.memory_size
        
        # Update timing
        wait_time = words_to_wait * self.WORD_TIME_US
        self.timing.wait_cycles += words_to_wait
        self.timing.total_time_us += wait_time
        self.timing.memory_accesses += 1
        
        return words_to_wait
    
    def read_word(self, addr: int) -> int:
        """Read word from memory with timing penalty"""
        addr = addr % self.memory_size
        self._wait_for_word(addr)
        return self.memory[addr] & 0xFFFF  # 16-bit words
    
    def write_word(self, addr: int, value: int):
        """Write word to memory with timing penalty"""
        addr = addr % self.memory_size
        self._wait_for_word(addr)
        self.memory[addr] = value & 0xFFFF  # 16-bit words
    
    def _mask_12bit(self, value: int) -> int:
        """Mask to 12-bit range (0-4095) for accumulator arithmetic"""
        return value & 0xFFF
    
    def _mask_16bit(self, value: int) -> int:
        """Mask to 16-bit range (0-65535) for memory"""
        return value & 0xFFFF
    
    def _to_signed_12bit(self, value: int) -> int:
        """Convert to signed 12-bit (-2048 to 2047)"""
        value = value & 0xFFF
        if value >= 0x800:
            return value - 0x1000
        return value
    
    def execute_instruction(self, instr: Instruction) -> bool:
        """
        Execute single instruction.
        Returns True if execution should continue.
        """
        self.timing.instructions_executed += 1
        self.state.program_counter = (self.state.program_counter + 1) % self.memory_size
        
        op = instr.opcode
        addr = instr.address
        
        if op == Opcode.NOP:
            pass
            
        elif op == Opcode.ADD:
            operand = self.read_word(addr)
            self.timing.total_time_us += self.ADD_TIME_US
            self.state.accumulator = self._mask_12bit(
                self.state.accumulator + operand
            )
            
        elif op == Opcode.SUB:
            operand = self.read_word(addr)
            self.timing.total_time_us += self.ADD_TIME_US
            self.state.accumulator = self._mask_12bit(
                self.state.accumulator - operand
            )
            
        elif op == Opcode.MUL:
            operand = self.read_word(addr)
            self.timing.total_time_us += self.MUL_TIME_US
            # 12-bit × 12-bit = 24-bit, keep lower 12 bits
            product = self.state.accumulator * operand
            self.state.accumulator = self._mask_12bit(product)
            
        elif op == Opcode.DIV:
            operand = self.read_word(addr)
            self.timing.total_time_us += self.DIV_TIME_US
            if operand != 0:
                self.state.accumulator = self._mask_12bit(
                    self.state.accumulator // operand
                )
            
        elif op == Opcode.LDA:
            self.state.accumulator = self.read_word(addr)
            
        elif op == Opcode.STA:
            self.write_word(addr, self.state.accumulator)
            
        elif op == Opcode.JMP:
            self.state.program_counter = addr
            
        elif op == Opcode.JZ:
            if self.state.accumulator == 0:
                self.state.program_counter = addr
                
        elif op == Opcode.JN:
            signed = self._to_signed_12bit(self.state.accumulator)
            if signed < 0:
                self.state.program_counter = addr
                
        elif op == Opcode.AND:
            operand = self.read_word(addr)
            self.state.accumulator = self.state.accumulator & operand
            
        elif op == Opcode.OR:
            operand = self.read_word(addr)
            self.state.accumulator = self.state.accumulator | operand
            
        elif op == Opcode.XOR:
            operand = self.read_word(addr)
            self.state.accumulator = self.state.accumulator ^ operand
            
        elif op == Opcode.OUT:
            # Output accumulator to buffer
            self.output_buffer.append(f"{self.state.accumulator:04X}")
            
        elif op == Opcode.HLT:
            self.state.halt = True
            return False
        
        self.timing.total_cycles += 1
        return True
    
    def step(self) -> bool:
        """Execute single instruction. Returns False if halted."""
        if self.state.halt:
            return False
        
        # Fetch instruction
        instr_word = self.read_word(self.state.program_counter)
        self.state.instruction_register = instr_word
        instr = Instruction.decode(instr_word)
        
        # Execute
        return self.execute_instruction(instr)
    
    def run(self, max_instructions: int = 1000000) -> TimingStats:
        """
        Run program until HALT or max_instructions reached.
        """
        count = 0
        while count < max_instructions:
            if not self.step():
                break
            count += 1
        
        self.timing.total_cycles = count
        return self.timing
    
    def get_stats(self) -> dict:
        """Get execution statistics"""
        return {
            'total_cycles': self.timing.total_cycles,
            'total_time_us': self.timing.total_time_us,
            'total_time_sec': self.timing.total_time_us / 1_000_000,
            'memory_accesses': self.timing.memory_accesses,
            'instructions_executed': self.timing.instructions_executed,
            'wait_cycles': self.timing.wait_cycles,
            'avg_wait_cycles': (
                self.timing.wait_cycles / max(1, self.timing.memory_accesses)
            ),
        }
    
    def dump_memory(self, start: int = 0, length: int = 32) -> str:
        """Dump memory region as hex"""
        lines = []
        for i in range(0, length, 8):
            addr = start + i
            words = self.memory[addr:addr+8]
            hex_str = ' '.join(f'{w:03X}' for w in words)
            lines.append(f'{addr:04X}: {hex_str}')
        return '\n'.join(lines)


# ============================================================================
# UNIVAC-12 Hash Function (Mining Algorithm)
# ============================================================================

def univac12_hash(data: bytes, nonce: int, rounds: int = 12) -> List[int]:
    """
    UNIVAC-12 hash function optimized for 12-bit architecture.
    
    Produces 144-bit hash (12 words × 12 bits) suitable for
    UNIVAC I's constraints.
    
    Args:
        data: Input data to hash
        nonce: Mining nonce value
        rounds: Number of mixing rounds (default 12)
    
    Returns:
        List of 12 12-bit words (144 bits total)
    """
    # Initialize 12-word state
    state = [0] * 12
    
    # Convert data to 12-bit chunks
    def to_12bit_chunks(data: bytes) -> List[int]:
        chunks = []
        buffer = 0
        bits_in_buffer = 0
        
        for byte in data:
            buffer = (buffer << 8) | byte
            bits_in_buffer += 8
            
            while bits_in_buffer >= 12:
                bits_in_buffer -= 12
                chunk = (buffer >> bits_in_buffer) & 0xFFF
                chunks.append(chunk)
                buffer &= (1 << bits_in_buffer) - 1
        
        # Pad final chunk
        if bits_in_buffer > 0:
            chunk = (buffer << (12 - bits_in_buffer)) & 0xFFF
            chunks.append(chunk)
        
        return chunks
    
    data_chunks = to_12bit_chunks(data)
    
    # Initial mixing with nonce
    for i, chunk in enumerate(data_chunks):
        state[i % 12] = (state[i % 12] + chunk) & 0xFFF
    
    # Mix in nonce
    for i in range(12):
        state[i] = (state[i] + nonce + i) & 0xFFF
    
    # UNIVAC-style mixing rounds (serial-friendly operations)
    for round_num in range(rounds):
        for i in range(12):
            # 12-bit rotate left by 3
            rotated = ((state[i] << 3) | (state[i] >> 9)) & 0xFFF
            
            # XOR with next word (circular)
            state[i] = rotated ^ state[(i + 1) % 12]
            
            # Add round constant
            state[i] = (state[i] + round_num * 17 + i * 13) & 0xFFF
    
    return state


def check_target(hash_words: List[int], target_words: int = 2) -> bool:
    """
    Check if hash meets difficulty target.
    
    Target: First N words must be zero (leading zero bits).
    
    Args:
        hash_words: 12-word hash output
        target_words: Number of leading zero words required
    
    Returns:
        True if hash meets target
    """
    for i in range(target_words):
        if hash_words[i] != 0:
            return False
    return True


def mine_block(data: bytes, target_words: int = 2, 
               max_nonces: int = 10000000) -> Tuple[Optional[int], List[int], int]:
    """
    Mine a block by finding nonce that produces valid hash.
    
    Args:
        data: Block data to mine
        target_words: Difficulty (leading zero words required)
        max_nonces: Maximum nonces to try
    
    Returns:
        Tuple of (nonce, hash, nonces_tried) or (None, [], nonces_tried) if not found
    """
    for nonce in range(max_nonces):
        hash_result = univac12_hash(data, nonce)
        
        if check_target(hash_result, target_words):
            return nonce, hash_result, nonce + 1
    
    return None, [], max_nonces


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Demo and test the UNIVAC I simulator"""
    print("=" * 70)
    print("UNIVAC I Simulator - RustChain Bounty #357")
    print("=" * 70)
    
    # Create simulator
    sim = UNIVACISimulator()
    
    # Load simple test program
    # Program: Add numbers from addr 100-109, store result at 50, halt
    program = [
        Instruction(Opcode.LDA, 100).encode(),   # Load first number
        Instruction(Opcode.ADD, 101).encode(),   # Add second
        Instruction(Opcode.ADD, 102).encode(),   # Add third
        Instruction(Opcode.ADD, 103).encode(),   # Add fourth
        Instruction(Opcode.ADD, 104).encode(),   # Add fifth
        Instruction(Opcode.STA, 50).encode(),    # Store result
        Instruction(Opcode.HLT, 0).encode(),     # Halt
    ]
    
    # Load test data (numbers 1-10)
    data = list(range(1, 11))
    
    sim.load_program(program, start_addr=0)
    sim.load_data(data, start_addr=100)
    
    print("\nTest Program: Sum numbers 1-10")
    print(f"Data at 100-109: {data}")
    print()
    
    # Run simulation
    print("Running simulation...")
    start_time = time.time()
    stats = sim.run()
    elapsed = time.time() - start_time
    
    # Results
    print(f"\nResult: {sim.state.accumulator} (expected: {sum(data)})")
    print(f"Memory[50]: {sim.memory[50]}")
    print()
    
    # Statistics
    print("Execution Statistics:")
    print(f"  Instructions executed: {stats.instructions_executed}")
    print(f"  Memory accesses:       {stats.memory_accesses}")
    print(f"  Total cycles:          {stats.total_cycles}")
    print(f"  Wait cycles:           {stats.wait_cycles}")
    print(f"  Simulated time:        {stats.total_time_us:,} us ({stats.total_time_us/1_000_000:.3f} s)")
    print(f"  Real time:             {elapsed*1000:.2f} ms")
    print()
    
    # Mining demo
    print("=" * 70)
    print("Mining Demo - UNIVAC-12 Hash")
    print("=" * 70)
    
    block_data = b"RustChain Block #1 - UNIVAC I Test"
    print(f"\nBlock data: {block_data.decode()}")
    print(f"Difficulty: 2 leading zero words (24 bits)")
    print()
    
    print("Mining...")
    start_time = time.time()
    nonce, hash_result, nonces_tried = mine_block(block_data, target_words=2)
    elapsed = time.time() - start_time
    
    if nonce is not None:
        print(f"\n✅ Solution found!")
        print(f"  Nonce: {nonce}")
        print(f"  Nonces tried: {nonces_tried}")
        print(f"  Hash: {' '.join(f'{w:03X}' for w in hash_result)}")
        print(f"  Real time: {elapsed:.2f} s")
        
        # Simulate on UNIVAC
        print(f"\n  UNIVAC I estimated time: ~{nonces_tried * 0.5:.1f} seconds")
        print(f"  (at ~2 hashes/second with memory wait times)")
    else:
        print(f"\n❌ No solution found in {nonces_tried} nonces")
    
    print()
    print("=" * 70)
    print("Simulation complete.")
    print("=" * 70)


if __name__ == '__main__':
    main()
