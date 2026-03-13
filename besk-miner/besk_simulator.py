"""
BESK (Binär Elektronisk SekvensKalkylator) Simulator
Sweden's First Electronic Computer (1953)

RustChain Miner Implementation
Issue: #1815
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import time
import random
import hashlib
from typing import Tuple, Optional, Dict, List
from dataclasses import dataclass
from enum import IntEnum


class BESKOpCodes(IntEnum):
    """BESK Instruction Set (based on IAS architecture)"""
    STOP = 0x00
    ADD = 0x01
    SUB = 0x02
    MUL = 0x03
    DIV = 0x04
    AND = 0x05
    OR = 0x06
    XOR = 0x07
    JMP = 0x08
    JZ = 0x09
    JN = 0x0A
    JP = 0x0B
    LD = 0x0C
    ST = 0x0D
    RSH = 0x0E
    LSH = 0x0F
    IN = 0x10
    OUT = 0x11


@dataclass
class BESKInstruction:
    """Represents a BESK instruction"""
    opcode: int
    address: int
    raw: int  # Raw 20-bit instruction
    
    def __str__(self):
        opcode_name = BESKOpCodes(self.opcode).name
        return f"{opcode_name} {self.address}"


class BESKWilliamsMemory:
    """
    Simulates BESK's original Williams tube memory (1953-1956)
    512 words × 40 bits using 40 cathode ray tubes + 8 spares
    """
    
    MASK_40 = 0xFFFFFFFFFF  # 40 bits all ones
    
    def __init__(self, words: int = 512, refresh_rate_hz: int = 100):
        self.words = words
        self.refresh_rate = refresh_rate_hz
        self.data = [0] * words
        self.drift_pattern = self._generate_drift_pattern()
        self.temperature = 25.0
        self.last_refresh_time = time.time()
        self.refresh_interval = 1.0 / refresh_rate_hz
        self.base_error_rate = 0.0002  # BESK had ~5 min MTBF initially
        self.access_count = 0
        
    def _generate_drift_pattern(self) -> List[int]:
        """Generate unique drift pattern for BESK's Swedish-manufactured tubes"""
        return [random.randint(0, 0xFF) for _ in range(self.words)]
        
    def read(self, address: int) -> int:
        """Read word with Williams tube drift and error simulation"""
        if address < 0 or address >= self.words:
            raise ValueError(f"Invalid memory address: {address}")
            
        self.access_count += 1
        base_value = self.data[address]
        
        # Calculate drift based on time since refresh
        time_since_refresh = time.time() - self.last_refresh_time
        drift_factor = min(1.0, time_since_refresh / self.refresh_interval)
        drift = int(self.drift_pattern[address] * drift_factor) & 0xFF
        drifted_value = base_value ^ (drift << 32)
        
        # Random bit errors (BESK characteristic)
        if random.random() < self._calculate_error_rate():
            error_bit = random.randint(0, 39)
            drifted_value ^= (1 << error_bit)
            
        return drifted_value & self.MASK_40
        
    def write(self, address: int, value: int) -> bool:
        """Write word with temperature-dependent reliability"""
        if address < 0 or address >= self.words:
            raise ValueError(f"Invalid memory address: {address}")
            
        self.access_count += 1
        reliability = self._calculate_reliability()
        
        if random.random() < reliability:
            self.data[address] = value & self.MASK_40
            return True
        return False
        
    def refresh(self):
        """Refresh all memory cells (required ~100 Hz for Williams tubes)"""
        self.last_refresh_time = time.time()
        # Re-write all values to maintain charge
        for i in range(self.words):
            self.data[i] = self.data[i]
            
    def _calculate_error_rate(self) -> float:
        """Calculate bit error rate based on temperature and drift"""
        temp_factor = 1.0 + (self.temperature - 25.0) * 0.05
        return self.base_error_rate * temp_factor
        
    def _calculate_reliability(self) -> float:
        """Calculate write reliability (0.0 to 1.0)"""
        return max(0.9, 1.0 - (self.temperature - 25.0) * 0.01)


class BESKCoreMemory:
    """
    Simulates BESK's 1956 ferrite core memory upgrade
    Built by housewives with knitting experience!
    More reliable and faster than Williams tubes
    """
    
    MASK_40 = 0xFFFFFFFFFF
    
    def __init__(self, words: int = 512):
        self.words = words
        self.data = [0] * words
        self.error_rate = 0.00001  # 0.001% (much better than Williams)
        self.access_time = 40e-6  # 40 μs
        self.access_count = 0
        
    def read(self, address: int) -> int:
        """Core memory read (destructive, requires immediate rewrite)"""
        if address < 0 or address >= self.words:
            raise ValueError(f"Invalid memory address: {address}")
            
        self.access_count += 1
        value = self.data[address]
        # Simulate destructive read + rewrite
        self.data[address] = 0
        self.data[address] = value
        return value
        
    def write(self, address: int, value: int) -> bool:
        """Core memory write (very reliable)"""
        if address < 0 or address >= self.words:
            raise ValueError(f"Invalid memory address: {address}")
            
        self.access_count += 1
        if random.random() < (1.0 - self.error_rate):
            self.data[address] = value & self.MASK_40
            return True
        return False


class BESKCPU:
    """
    BESK CPU Simulator
    Implements IAS architecture with BESK-specific timing
    """
    
    MASK_40 = 0xFFFFFFFFFF
    MASK_20 = 0xFFFFF
    SIGN_BIT_40 = 1 << 39
    
    def __init__(self, use_core_memory: bool = False):
        # Registers
        self.ac = 0  # Accumulator (40 bits)
        self.mq = 0  # Multiplier/Quotient (40 bits)
        self.mbr = 0  # Memory Buffer Register
        self.ir = 0  # Instruction Register (20 bits)
        self.pc = 0  # Program Counter (9 bits for 512 words)
        
        # Memory
        if use_core_memory:
            self.memory = BESKCoreMemory()
        else:
            self.memory = BESKWilliamsMemory()
            
        # Status
        self.zero_flag = False
        self.negative_flag = False
        self.running = False
        
        # Timing
        self.cycle_count = 0
        self.instruction_count = 0
        self.use_left_instruction = True
        
        # Statistics
        self.stats = {
            'adds': 0,
            'multiplies': 0,
            'memory_reads': 0,
            'memory_writes': 0,
            'jumps': 0
        }
        
    def reset(self):
        """Reset CPU to initial state"""
        self.ac = 0
        self.mq = 0
        self.mbr = 0
        self.pc = 0
        self.zero_flag = False
        self.negative_flag = False
        self.running = False
        self.cycle_count = 0
        self.instruction_count = 0
        self.stats = {k: 0 for k in self.stats}
        
    def decode_instruction(self, raw: int) -> BESKInstruction:
        """Decode 20-bit raw instruction"""
        opcode = (raw >> 15) & 0x1F  # 5-bit opcode
        address = raw & 0x7FFF  # 13-bit address
        return BESKInstruction(opcode=opcode, address=address, raw=raw)
        
    def fetch(self) -> BESKInstruction:
        """Fetch instruction from memory"""
        word = self.memory.read(self.pc)
        self.stats['memory_reads'] += 1
        
        # BESK: two 20-bit instructions per 40-bit word
        if self.use_left_instruction:
            raw = (word >> 20) & self.MASK_20
            self.use_left_instruction = False
        else:
            raw = word & self.MASK_20
            self.use_left_instruction = True
            self.pc = (self.pc + 1) % 512  # Wrap around at 512
            
        return self.decode_instruction(raw)
        
    def execute(self, instr: BESKInstruction) -> int:
        """Execute instruction, return cycle count"""
        cycles = 0
        
        try:
            if instr.opcode == BESKOpCodes.STOP:
                self.running = False
                cycles = 1
                
            elif instr.opcode == BESKOpCodes.ADD:
                value = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self.ac = self._add_40bit(self.ac, value)
                self._update_flags(self.ac)
                self.stats['adds'] += 1
                cycles = 5  # 56 μs
                
            elif instr.opcode == BESKOpCodes.SUB:
                value = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self.ac = self._sub_40bit(self.ac, value)
                self._update_flags(self.ac)
                self.stats['adds'] += 1
                cycles = 5  # 56 μs
                
            elif instr.opcode == BESKOpCodes.MUL:
                value = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self._multiply_40bit(value)
                self.stats['multiplies'] += 1
                cycles = 30  # 350 μs
                
            elif instr.opcode == BESKOpCodes.DIV:
                value = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self._divide_40bit(value)
                cycles = 35  # ~400 μs
                
            elif instr.opcode == BESKOpCodes.AND:
                value = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self.ac = self.ac & value
                self._update_flags(self.ac)
                cycles = 3
                
            elif instr.opcode == BESKOpCodes.OR:
                value = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self.ac = self.ac | value
                self._update_flags(self.ac)
                cycles = 3
                
            elif instr.opcode == BESKOpCodes.XOR:
                value = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self.ac = self.ac ^ value
                self._update_flags(self.ac)
                cycles = 3
                
            elif instr.opcode == BESKOpCodes.JMP:
                self.pc = instr.address
                self.stats['jumps'] += 1
                cycles = 2
                
            elif instr.opcode == BESKOpCodes.JZ:
                if self.zero_flag:
                    self.pc = instr.address
                    self.stats['jumps'] += 1
                cycles = 2
                
            elif instr.opcode == BESKOpCodes.JN:
                if self.negative_flag:
                    self.pc = instr.address
                    self.stats['jumps'] += 1
                cycles = 2
                
            elif instr.opcode == BESKOpCodes.JP:
                if not self.zero_flag and not self.negative_flag:
                    self.pc = instr.address
                    self.stats['jumps'] += 1
                cycles = 2
                
            elif instr.opcode == BESKOpCodes.LD:
                self.ac = self.memory.read(instr.address)
                self.stats['memory_reads'] += 1
                self._update_flags(self.ac)
                cycles = 3
                
            elif instr.opcode == BESKOpCodes.ST:
                self.memory.write(instr.address, self.ac)
                self.stats['memory_writes'] += 1
                cycles = 3
                
            elif instr.opcode == BESKOpCodes.RSH:
                shift_amount = instr.address & 0x3F  # 6-bit shift count
                self.ac = self._rsh_40bit(self.ac, shift_amount)
                self._update_flags(self.ac)
                cycles = 4
                
            elif instr.opcode == BESKOpCodes.LSH:
                shift_amount = instr.address & 0x3F
                self.ac = self._lsh_40bit(self.ac, shift_amount)
                self._update_flags(self.ac)
                cycles = 4
                
            elif instr.opcode == BESKOpCodes.IN:
                # Simulated input
                cycles = 100
                
            elif instr.opcode == BESKOpCodes.OUT:
                # Simulated output
                cycles = 100
                
            else:
                # Unknown opcode - treat as NOP
                cycles = 1
                
        except Exception as e:
            print(f"CPU Error: {e}")
            self.running = False
            cycles = 0
            
        self.cycle_count += cycles
        self.instruction_count += 1
        return cycles
        
    def step(self) -> int:
        """Execute one instruction cycle"""
        if not self.running:
            return 0
        instr = self.fetch()
        return self.execute(instr)
        
    def run(self, max_instructions: int = 0):
        """Run CPU until STOP or max_instructions reached"""
        self.running = True
        count = 0
        
        while self.running and (max_instructions == 0 or count < max_instructions):
            self.step()
            count += 1
            
            # Refresh Williams memory periodically
            if isinstance(self.memory, BESKWilliamsMemory):
                if time.time() - self.memory.last_refresh_time > self.memory.refresh_interval:
                    self.memory.refresh()
                    
    def _add_40bit(self, a: int, b: int) -> int:
        """40-bit addition with overflow"""
        result = a + b
        return result & self.MASK_40
        
    def _sub_40bit(self, a: int, b: int) -> int:
        """40-bit subtraction"""
        result = a - b
        if result < 0:
            result += (1 << 40)
        return result & self.MASK_40
        
    def _multiply_40bit(self, b: int):
        """Multiply AC × b, result in MQ:AC (80 bits)"""
        product = self.ac * b
        self.mq = (product >> 40) & self.MASK_40
        self.ac = product & self.MASK_40
        
    def _divide_40bit(self, b: int):
        """Divide MQ:AC by b, quotient in AC, remainder in MQ"""
        dividend = (self.mq << 40) | self.ac
        if b != 0:
            self.ac = dividend // b
            self.mq = dividend % b
        else:
            self.ac = 0
            self.mq = 0
            
    def _rsh_40bit(self, value: int, shift: int) -> int:
        """40-bit right shift"""
        shift = shift % 40
        return (value >> shift) & self.MASK_40
        
    def _lsh_40bit(self, value: int, shift: int) -> int:
        """40-bit left shift"""
        shift = shift % 40
        return (value << shift) & self.MASK_40
        
    def _update_flags(self, value: int):
        """Update zero and negative flags"""
        self.zero_flag = (value == 0)
        self.negative_flag = bool(value & self.SIGN_BIT_40)
        
    def get_status(self) -> Dict:
        """Get CPU status"""
        return {
            'pc': self.pc,
            'ac': f"0x{self.ac:010X}",
            'mq': f"0x{self.mq:010X}",
            'running': self.running,
            'zero': self.zero_flag,
            'negative': self.negative_flag,
            'cycles': self.cycle_count,
            'instructions': self.instruction_count,
            'memory_accesses': self.memory.access_count,
            'stats': self.stats
        }


if __name__ == "__main__":
    # Test BESK CPU
    print("BESK CPU Simulator Test")
    print("=" * 50)
    
    cpu = BESKCPU(use_core_memory=False)
    
    # Load simple test program - manually pack instructions
    # BESK: 2 instructions per 40-bit word (left = bits 39-20, right = bits 19-0)
    # Program: Add numbers 0+10+20+30 = 60, store at 0x180
    
    # Word 0: LD 0x100 (left), ADD 0x101 (right)
    # LD = 0x0C, ADD = 0x01
    left_instr = (0x0C << 15) | 0x100  # LD 0x100
    right_instr = (0x01 << 15) | 0x101  # ADD 0x101
    cpu.memory.data[0] = (left_instr << 20) | right_instr
    
    # Word 1: ADD 0x102 (left), ADD 0x103 (right)
    left_instr = (0x01 << 15) | 0x102  # ADD 0x102
    right_instr = (0x01 << 15) | 0x103  # ADD 0x103
    cpu.memory.data[1] = (left_instr << 20) | right_instr
    
    # Word 2: ST 0x180 (left), STOP (right)
    left_instr = (0x0D << 15) | 0x180  # ST 0x180
    right_instr = (0x00 << 15) | 0x000  # STOP
    cpu.memory.data[2] = (left_instr << 20) | right_instr
    
    # Initialize data
    cpu.memory.write(0x100, 0)    # First number
    cpu.memory.write(0x101, 10)   # Second number
    cpu.memory.write(0x102, 20)   # Third number
    cpu.memory.write(0x103, 30)   # Fourth number
    
    # Run program
    cpu.run()
    
    # Get result
    result = cpu.memory.read(0x180)
    print(f"Result: {result} (expected: 60)")
    print(f"\nCPU Status: {cpu.get_status()}")
