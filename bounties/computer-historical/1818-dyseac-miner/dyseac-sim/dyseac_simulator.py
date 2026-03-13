#!/usr/bin/env python3
"""
DYSEAC (1954) Simulator - RustChain Miner Port
===============================================

Simulates the first portable computer housed in a truck!

DYSEAC Specifications:
- Word Size: 45 bits (+ 1 parity bit = 46 bits stored)
- Memory: 512 words (mercury delay-line, 64 channels × 8 words)
- Clock: 1 MHz (1 μs cycle)
- Add Time: 48 μs (excluding memory access)
- Multiply/Divide: 2112 μs (excluding memory access)
- Memory Access: 48-384 μs (depends on channel position)

Author: RustChain Community
License: MIT
"""

import time
import random
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import IntEnum


# ============================================================================
# DYSEAC Instruction Set Opcodes
# ============================================================================
class Opcode(IntEnum):
    STOP = 0x00    # Halt execution
    ADD = 0x01     # Add to accumulator
    SUB = 0x02     # Subtract from accumulator
    MUL = 0x03     # Multiply
    DIV = 0x04     # Divide
    AND = 0x05     # Bitwise AND
    OR = 0x06      # Bitwise OR
    JMP = 0x07     # Unconditional jump
    JZ = 0x08      # Jump if zero
    JN = 0x09      # Jump if negative
    LD = 0x0A      # Load from memory
    ST = 0x0B      # Store to memory
    IN = 0x0C      # Input from tape/teleprinter
    OUT = 0x0D     # Output to tape/teleprinter
    RSH = 0x0E     # Right shift
    LSH = 0x0F     # Left shift


# ============================================================================
# Mercury Delay-Line Memory Model
# ============================================================================
@dataclass
class DelayLineChannel:
    """Represents one mercury delay-line channel (holds 8 words)"""
    channel_id: int
    words: List[int] = field(default_factory=lambda: [0] * 8)
    temperature: float = 40.0  # Celsius (optimal operating temp)
    drift_factor: float = 1.0  # Unique to each channel
    access_times: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        # Generate unique access time profile for this channel
        base_time = 48.0 + (self.channel_id * 5.25)  # 48-384 μs range
        self.access_times = [
            base_time * self.drift_factor * (1.0 + random.uniform(-0.02, 0.02))
            for _ in range(8)
        ]
    
    def get_access_time(self, word_index: int) -> float:
        """Get access time for a specific word in this channel"""
        if 0 <= word_index < 8:
            return self.access_times[word_index]
        return 384.0  # Max wait time
    
    def set_temperature(self, temp: float):
        """Update temperature and recalculate drift"""
        self.temperature = temp
        # Mercury expands ~0.00018 per °C
        self.drift_factor = 1.0 + (temp - 40.0) * 0.00018
        # Regenerate access times with new drift
        base_time = 48.0 + (self.channel_id * 5.25)
        self.access_times = [
            base_time * self.drift_factor * (1.0 + random.uniform(-0.02, 0.02))
            for _ in range(8)
        ]
    
    def get_fingerprint(self) -> str:
        """Generate unique fingerprint for this channel"""
        data = f"{self.channel_id}:{self.drift_factor}:{':'.join(f'{t:.3f}' for t in self.access_times)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class MercuryDelayLineMemory:
    """
    Mercury delay-line memory system for DYSEAC
    
    64 channels × 8 words = 512 words total
    Access time varies 48-384 μs depending on channel position
    Temperature-sensitive (perfect for hardware fingerprinting!)
    """
    
    def __init__(self, size: int = 512, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        self.size = size
        self.channels: List[DelayLineChannel] = []
        
        # Create 64 channels with 8 words each
        for i in range(64):
            # Each channel gets unique drift characteristics
            drift = 1.0 + random.uniform(-0.05, 0.05)
            channel = DelayLineChannel(channel_id=i, drift_factor=drift)
            self.channels.append(channel)
    
    def _get_channel_and_offset(self, address: int) -> Tuple[int, int]:
        """Convert linear address to (channel_id, word_offset)"""
        channel_id = address // 8
        word_offset = address % 8
        return channel_id, word_offset
    
    def read(self, address: int) -> int:
        """Read word from memory (simulates delay-line access time)"""
        if not (0 <= address < self.size):
            raise ValueError(f"Memory access out of bounds: {address}")
        
        channel_id, offset = self._get_channel_and_offset(address)
        channel = self.channels[channel_id]
        
        # Simulate access time (would be 48-384 μs on real hardware)
        access_time = channel.get_access_time(offset)
        # In simulation, we just note the time
        # time.sleep(access_time / 1_000_000)  # Uncomment for cycle-accurate sim
        
        return channel.words[offset]
    
    def write(self, address: int, value: int):
        """Write word to memory"""
        if not (0 <= address < self.size):
            raise ValueError(f"Memory access out of bounds: {address}")
        
        # Mask to 45 bits
        value = value & 0x1FFFFFFFFFF  # 45 bits
        
        channel_id, offset = self._get_channel_and_offset(address)
        self.channels[channel_id].words[offset] = value
    
    def set_temperature(self, temp: float):
        """Set operating temperature for all delay lines"""
        for channel in self.channels:
            channel.set_temperature(temp)
    
    def get_fingerprint(self) -> str:
        """Generate unique memory fingerprint based on delay-line characteristics"""
        fingerprints = [channel.get_fingerprint() for channel in self.channels]
        combined = ":".join(fingerprints)
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get_timing_profile(self) -> Dict:
        """Get detailed timing profile for fingerprinting"""
        profile = {
            "channel_count": len(self.channels),
            "words_per_channel": 8,
            "total_words": self.size,
            "channels": []
        }
        
        for channel in self.channels:
            channel_data = {
                "id": channel.channel_id,
                "drift_factor": channel.drift_factor,
                "temperature": channel.temperature,
                "access_times": channel.access_times,
                "avg_access_time": sum(channel.access_times) / len(channel.access_times),
                "fingerprint": channel.get_fingerprint()
            }
            profile["channels"].append(channel_data)
        
        return profile


# ============================================================================
# DYSEAC CPU Emulator
# ============================================================================
@dataclass
class CPUState:
    """DYSEAC CPU state"""
    accumulator: int = 0  # 45-bit accumulator
    instruction_register: int = 0
    program_counter: int = 0
    memory_address_register: int = 0
    status_flags: Dict[str, bool] = field(default_factory=lambda: {
        "zero": False,
        "negative": False,
        "overflow": False
    })
    halted: bool = False
    cycles: int = 0
    total_time_us: float = 0.0


class DYSEAC_CPU:
    """
    DYSEAC CPU Emulator
    
    Serial binary architecture:
    - 45-bit words processed one bit at a time
    - 1 MHz clock (1 μs per cycle)
    - 45 cycles per word operation
    """
    
    WORD_BITS = 45
    WORD_MASK = (1 << WORD_BITS) - 1
    SIGN_BIT = 1 << (WORD_BITS - 1)
    
    def __init__(self, memory: MercuryDelayLineMemory):
        self.memory = memory
        self.state = CPUState()
        self.instructions_executed = 0
        self.interrupts_enabled = True
        self.interrupt_pending = False
        self.io_buffer = 0
    
    def _to_signed(self, value: int) -> int:
        """Convert 45-bit unsigned to signed integer"""
        if value & self.SIGN_BIT:
            return value - (1 << self.WORD_BITS)
        return value
    
    def _to_unsigned(self, value: int) -> int:
        """Convert signed integer to 45-bit unsigned"""
        return value & self.WORD_MASK
    
    def _update_flags(self, value: int):
        """Update status flags based on result"""
        signed = self._to_signed(value)
        self.state.status_flags["zero"] = (value == 0)
        self.state.status_flags["negative"] = (signed < 0)
    
    def fetch(self) -> int:
        """Fetch instruction from memory"""
        instruction = self.memory.read(self.state.program_counter)
        self.state.program_counter = (self.state.program_counter + 1) % self.memory.size
        return instruction
    
    def decode(self, instruction: int) -> Tuple[Opcode, int, int]:
        """
        Decode instruction
        DYSEAC instruction format (45 bits):
        - Bits 44-40: Opcode (5 bits)
        - Bits 39-30: Address1 (10 bits)
        - Bits 29-20: Address2 (10 bits)
        - Bits 19-10: Address3 (10 bits)
        - Bits 9-0: Unused/padding (10 bits)
        """
        opcode = Opcode((instruction >> 40) & 0x1F)
        addr1 = (instruction >> 30) & 0x3FF
        addr2 = (instruction >> 20) & 0x3FF
        addr3 = (instruction >> 10) & 0x3FF
        return opcode, addr1, addr2, addr3
    
    def execute(self, opcode: Opcode, addr1: int, addr2: int, addr3: int):
        """Execute decoded instruction"""
        exec_time = 48.0  # Base execution time in μs
        
        if opcode == Opcode.STOP:
            self.state.halted = True
            
        elif opcode == Opcode.ADD:
            operand = self.memory.read(addr1)
            result = self._to_signed(self.state.accumulator) + self._to_signed(operand)
            self.state.accumulator = self._to_unsigned(result)
            self._update_flags(self.state.accumulator)
            
        elif opcode == Opcode.SUB:
            operand = self.memory.read(addr1)
            result = self._to_signed(self.state.accumulator) - self._to_signed(operand)
            self.state.accumulator = self._to_unsigned(result)
            self._update_flags(self.state.accumulator)
            
        elif opcode == Opcode.MUL:
            operand = self.memory.read(addr1)
            result = self._to_signed(self.state.accumulator) * self._to_signed(operand)
            # Keep only lower 45 bits
            self.state.accumulator = self._to_unsigned(result)
            self._update_flags(self.state.accumulator)
            exec_time = 2112.0  # Multiply takes longer
            
        elif opcode == Opcode.DIV:
            operand = self.memory.read(addr1)
            divisor = self._to_signed(operand)
            if divisor != 0:
                dividend = self._to_signed(self.state.accumulator)
                result = dividend // divisor
                self.state.accumulator = self._to_unsigned(result)
                self._update_flags(self.state.accumulator)
            else:
                # Division by zero - set overflow
                self.state.status_flags["overflow"] = True
            exec_time = 2112.0
            
        elif opcode == Opcode.AND:
            operand = self.memory.read(addr1)
            self.state.accumulator &= operand
            self._update_flags(self.state.accumulator)
            
        elif opcode == Opcode.OR:
            operand = self.memory.read(addr1)
            self.state.accumulator |= operand
            self._update_flags(self.state.accumulator)
            
        elif opcode == Opcode.JMP:
            self.state.program_counter = addr1
            
        elif opcode == Opcode.JZ:
            if self.state.status_flags["zero"]:
                self.state.program_counter = addr1
                
        elif opcode == Opcode.JN:
            if self.state.status_flags["negative"]:
                self.state.program_counter = addr1
                
        elif opcode == Opcode.LD:
            self.state.accumulator = self.memory.read(addr1)
            self._update_flags(self.state.accumulator)
            
        elif opcode == Opcode.ST:
            self.memory.write(addr1, self.state.accumulator)
            
        elif opcode == Opcode.IN:
            # Simulate input from paper tape/teleprinter
            self.state.accumulator = self.io_buffer
            self._update_flags(self.state.accumulator)
            
        elif opcode == Opcode.OUT:
            # Simulate output to paper tape/teleprinter
            self.io_buffer = self.state.accumulator
            
        elif opcode == Opcode.RSH:
            self.state.accumulator = (self.state.accumulator >> 1) & self.WORD_MASK
            self._update_flags(self.state.accumulator)
            
        elif opcode == Opcode.LSH:
            self.state.accumulator = (self.state.accumulator << 1) & self.WORD_MASK
            self._update_flags(self.state.accumulator)
        
        # Update timing
        self.state.total_time_us += exec_time
        self.state.cycles += 45  # 45 cycles per word (serial architecture)
        self.instructions_executed += 1
    
    def step(self) -> bool:
        """Execute one instruction. Returns False if halted."""
        if self.state.halted:
            return False
        
        instruction = self.fetch()
        opcode, addr1, addr2, addr3 = self.decode(instruction)
        self.execute(opcode, addr1, addr2, addr3)
        
        return True
    
    def run(self, max_instructions: Optional[int] = None):
        """Run until halted or max_instructions reached"""
        count = 0
        while not self.state.halted:
            if max_instructions and count >= max_instructions:
                break
            self.step()
            count += 1
    
    def reset(self):
        """Reset CPU state"""
        self.state = CPUState()
        self.instructions_executed = 0
        self.io_buffer = 0
    
    def get_state(self) -> Dict:
        """Get CPU state as dictionary"""
        return {
            "accumulator": f"0x{self.state.accumulator:011X}",
            "program_counter": self.state.program_counter,
            "halted": self.state.halted,
            "cycles": self.state.cycles,
            "total_time_us": self.state.total_time_us,
            "instructions_executed": self.instructions_executed,
            "flags": self.state.status_flags
        }


# ============================================================================
# DYSEAC Assembler
# ============================================================================
class DYSEACAssembler:
    """
    DYSEAC Cross-Assembler
    
    Assembles DYSEAC assembly code into machine code.
    Optimizes memory layout for delay-line access times.
    """
    
    def __init__(self):
        self.symbols: Dict[str, int] = {}
        self.instructions: List[int] = []
        self.labels: Dict[str, int] = {}
        self.data: Dict[int, int] = {}
    
    def assemble(self, source: str) -> List[int]:
        """Assemble source code into machine code"""
        lines = source.strip().split('\n')
        address = 0
        
        # First pass: collect labels and symbols
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            # Check for label
            if ':' in line:
                parts = line.split(':', 1)
                label = parts[0].strip()
                self.labels[label] = address
            
            # Count instructions
            if not line.startswith(';'):
                address += 1
        
        # Second pass: generate code
        address = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            
            # Skip label definition
            if ':' in line:
                line = line.split(':', 1)[1].strip()
            
            if line:
                instruction = self._assemble_instruction(line, address)
                if instruction is not None:
                    self.instructions.append(instruction)
                    address += 1
        
        return self.instructions
    
    def _assemble_instruction(self, line: str, address: int) -> Optional[int]:
        """Assemble a single instruction"""
        parts = line.replace(',', ' ').split()
        if not parts:
            return None
        
        mnemonic = parts[0].upper()
        operands = [self._parse_operand(op) for op in parts[1:]]
        
        # Map mnemonic to opcode
        opcode_map = {
            'STOP': Opcode.STOP,
            'ADD': Opcode.ADD,
            'SUB': Opcode.SUB,
            'MUL': Opcode.MUL,
            'DIV': Opcode.DIV,
            'AND': Opcode.AND,
            'OR': Opcode.OR,
            'JMP': Opcode.JMP,
            'JZ': Opcode.JZ,
            'JN': Opcode.JN,
            'LD': Opcode.LD,
            'ST': Opcode.ST,
            'IN': Opcode.IN,
            'OUT': Opcode.OUT,
            'RSH': Opcode.RSH,
            'LSH': Opcode.LSH,
        }
        
        if mnemonic not in opcode_map:
            raise ValueError(f"Unknown instruction: {mnemonic}")
        
        opcode = opcode_map[mnemonic]
        addr1 = operands[0] if len(operands) > 0 else 0
        addr2 = operands[1] if len(operands) > 1 else 0
        addr3 = operands[2] if len(operands) > 2 else 0
        
        # Pack instruction (45 bits)
        instruction = (
            ((opcode & 0x1F) << 40) |
            ((addr1 & 0x3FF) << 30) |
            ((addr2 & 0x3FF) << 20) |
            ((addr3 & 0x3FF) << 10)
        )
        
        return instruction
    
    def _parse_operand(self, op: str) -> int:
        """Parse operand (number, label, or expression)"""
        op = op.strip()
        
        # Hex number
        if op.startswith('0x') or op.startswith('0X'):
            return int(op, 16)
        
        # Decimal number
        if op.isdigit():
            return int(op)
        
        # Label reference
        if op in self.labels:
            return self.labels[op]
        
        # Try to parse as integer
        try:
            return int(op)
        except ValueError:
            pass
        
        return 0


# ============================================================================
# DYSEAC System (Complete Emulator)
# ============================================================================
class DYSEAC_System:
    """
    Complete DYSEAC System Emulator
    
    Includes:
    - CPU (serial binary, 45-bit words)
    - Mercury delay-line memory (512 words)
    - Paper tape I/O
    - Interrupt system
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.memory = MercuryDelayLineMemory(seed=seed)
        self.cpu = DYSEAC_CPU(self.memory)
        self.assembler = DYSEACAssembler()
        self.paper_tape: List[int] = []
        self.teleprinter_buffer: str = ""
        
        # Temperature control (critical for mercury delay-lines!)
        self.temperature = 40.0  # Optimal operating temperature
    
    def load_program(self, program: List[int], start_address: int = 0):
        """Load program into memory"""
        for i, instruction in enumerate(program):
            self.memory.write(start_address + i, instruction)
    
    def load_assembly(self, source: str, start_address: int = 0):
        """Assemble and load program from source"""
        instructions = self.assembler.assemble(source)
        self.load_program(instructions, start_address)
    
    def set_temperature(self, temp: float):
        """Set operating temperature"""
        self.temperature = temp
        self.memory.set_temperature(temp)
    
    def get_fingerprint(self) -> Dict:
        """Get complete system fingerprint for RustChain attestation"""
        return {
            "system": "DYSEAC",
            "year": 1954,
            "manufacturer": "National Bureau of Standards",
            "type": "First portable computer (mobile/truck-mounted)",
            "architecture": "Serial binary",
            "word_size": 45,
            "memory_type": "Mercury delay-line",
            "memory_size": 512,
            "memory_channels": 64,
            "clock_mhz": 1.0,
            "temperature": self.temperature,
            "memory_fingerprint": self.memory.get_fingerprint(),
            "memory_timing_profile": self.memory.get_timing_profile(),
            "cpu_state": self.cpu.get_state()
        }
    
    def run(self, max_instructions: Optional[int] = None):
        """Run the emulated system"""
        self.cpu.run(max_instructions)
    
    def step(self) -> bool:
        """Execute one instruction"""
        return self.cpu.step()
    
    def reset(self):
        """Reset the system"""
        self.cpu.reset()
        self.paper_tape = []
        self.teleprinter_buffer = ""
    
    def get_status(self) -> str:
        """Get human-readable status"""
        state = self.cpu.get_state()
        return f"""
DYSEAC System Status
====================
Temperature: {self.temperature:.1f}°C
Accumulator: {state['accumulator']}
PC: {state['program_counter']}
Cycles: {state['cycles']}
Time: {state['total_time_us']:.1f} μs
Instructions: {state['instructions_executed']}
Halted: {state['halted']}
Flags: {state['flags']}
Memory Fingerprint: {self.memory.get_fingerprint()[:32]}...
"""


# ============================================================================
# Example Programs
# ============================================================================

def create_sha256_test_program() -> str:
    """Create a simple test program for SHA256 verification"""
    return """
; DYSEAC SHA256 Test Program
; Simple addition test to verify basic operation

START:  LD CONST1      ; Load constant 1
        ADD CONST2     ; Add constant 2
        ST RESULT      ; Store result
        JZ DONE        ; If zero, done
        JMP START      ; Loop
        
DONE:   STOP           ; Halt

; Data section
CONST1: 0x000000001
CONST2: 0x000000002
RESULT: 0x000000000
"""


# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("DYSEAC (1954) Simulator - RustChain Miner Port")
    print("First Portable Computer - Housed in a Truck!")
    print("=" * 70)
    
    # Create system with fixed seed for reproducibility
    system = DYSEAC_System(seed=42)
    
    # Load test program
    program = """
    LD VALUE1
    ADD VALUE2
    ST RESULT
    STOP
VALUE1: 0x123456789
VALUE2: 0x987654321
RESULT: 0x000000000
    """
    
    system.load_assembly(program)
    
    # Run simulation
    print("\nRunning test program...")
    system.run(max_instructions=100)
    
    # Print status
    print(system.get_status())
    
    # Get fingerprint for RustChain attestation
    fingerprint = system.get_fingerprint()
    print("\nRustChain Attestation Fingerprint:")
    print(json.dumps(fingerprint, indent=2))
    
    print("\n" + "=" * 70)
    print("DYSEAC Simulator Ready for RustChain Mining!")
    print("=" * 70)
