"""
AVIDAC CPU Simulator

Simulates the AVIDAC (Argonne Version of the Institute's Digital Automatic Computer)
CPU based on the IAS (von Neumann) architecture.

Key features:
- 40-bit parallel binary words
- Two 20-bit instructions per 40-bit word
- Asynchronous execution (no central clock)
- Accumulator (AC) and Multiplier/Quotient (MQ) registers
"""

import time
from typing import Optional, Dict, Any, List, Callable
from enum import IntEnum

try:
    from .arithmetic import (
        MASK_40, MASK_20, MASK_39, SIGN_BIT,
        mask_40bit, to_signed_40bit, to_unsigned_40bit,
        add_40bit, sub_40bit, multiply_40bit, divide_40bit,
        rotate_left_40bit, rotate_right_40bit,
        shift_left_40bit, shift_right_40bit, arithmetic_shift_right_40bit,
        bitwise_and_40bit, bitwise_or_40bit, bitwise_xor_40bit, bitwise_not_40bit,
        is_zero_40bit, is_negative_40bit
    )
    from .williams_tube import WilliamsTubeMemory
    from .paper_tape import PaperTapeIO
except ImportError:
    from arithmetic import (
        MASK_40, MASK_20, MASK_39, SIGN_BIT,
        mask_40bit, to_signed_40bit, to_unsigned_40bit,
        add_40bit, sub_40bit, multiply_40bit, divide_40bit,
        rotate_left_40bit, rotate_right_40bit,
        shift_left_40bit, shift_right_40bit, arithmetic_shift_right_40bit,
        bitwise_and_40bit, bitwise_or_40bit, bitwise_xor_40bit, bitwise_not_40bit,
        is_zero_40bit, is_negative_40bit
    )
    from williams_tube import WilliamsTubeMemory
    from paper_tape import PaperTapeIO


class Opcode(IntEnum):
    """IAS/AVIDAC instruction opcodes."""
    STOP = 0x0  # Halt execution
    ADD = 0x1   # Add memory to AC
    SUB = 0x2   # Subtract memory from AC
    MUL = 0x3   # Multiply AC × memory → MQ:AC
    DIV = 0x4   # Divide MQ:AC by memory
    AND = 0x5   # Bitwise AND
    OR = 0x6    # Bitwise OR
    JMP = 0x7   # Unconditional jump
    JZ = 0x8    # Jump if AC = 0
    JN = 0x9    # Jump if AC < 0
    LD = 0xA    # Load memory to AC
    ST = 0xB    # Store AC to memory
    IN = 0xC    # Input from paper tape
    OUT = 0xD   # Output to paper tape
    RSH = 0xE   # Right shift AC
    LSH = 0xF   # Left shift AC


# Instruction timing in microseconds (based on historical data)
INSTRUCTION_CYCLES = {
    Opcode.STOP: 1,
    Opcode.ADD: 5,    # 62 μs
    Opcode.SUB: 5,    # 62 μs
    Opcode.MUL: 50,   # 713 μs
    Opcode.DIV: 60,   # ~800 μs
    Opcode.AND: 3,    # ~40 μs
    Opcode.OR: 3,     # ~40 μs
    Opcode.JMP: 2,    # ~25 μs
    Opcode.JZ: 2,     # ~25 μs
    Opcode.JN: 2,     # ~25 μs
    Opcode.LD: 3,     # ~40 μs
    Opcode.ST: 3,     # ~40 μs
    Opcode.IN: 100,   # ~1500 μs
    Opcode.OUT: 100,  # ~1500 μs
    Opcode.RSH: 4,    # ~50 μs
    Opcode.LSH: 4,    # ~50 μs
}

# Base cycle time in microseconds
CYCLE_TIME_US = 12.0  # ~12 μs per cycle


class AVIDACCPU:
    """
    AVIDAC CPU Simulator.
    
    Implements the IAS architecture with:
    - 40-bit accumulator (AC)
    - 40-bit multiplier/quotient register (MQ)
    - 10-bit program counter (PC) for 1024 words
    - Memory buffer register (MBR)
    - Instruction register (IR)
    
    Asynchronous execution: instructions complete in variable time
    based on their operation type.
    """
    
    def __init__(
        self,
        memory: Optional[WilliamsTubeMemory] = None,
        paper_tape: Optional[PaperTapeIO] = None,
        enable_timing: bool = True,
        debug: bool = False
    ):
        """
        Initialize AVIDAC CPU.
        
        Args:
            memory: WilliamsTubeMemory instance (created if None)
            paper_tape: PaperTapeIO instance (created if None)
            enable_timing: Simulate instruction timing
            debug: Enable debug output
        """
        # Initialize memory
        self.memory = memory or WilliamsTubeMemory()
        
        # Initialize I/O
        self.paper_tape = paper_tape or PaperTapeIO()
        
        # Registers
        self.ac = 0  # Accumulator (40 bits)
        self.mq = 0  # Multiplier/Quotient (40 bits)
        self.mbr = 0  # Memory Buffer Register (40 bits)
        self.ir = 0  # Instruction Register (20 bits)
        self.pc = 0  # Program Counter (10 bits, 0-1023)
        
        # Control
        self.running = False
        self.halted = False
        self.use_left_instruction = True  # IAS: two instructions per word
        
        # Timing
        self.enable_timing = enable_timing
        self.cycle_count = 0
        self.instruction_count = 0
        self.start_time = 0.0
        self.simulated_time_us = 0.0
        
        # Flags
        self.zero_flag = False
        self.negative_flag = False
        
        # Debug
        self.debug = debug
        self.instruction_log: List[Dict[str, Any]] = []
        
        # Hooks for I/O operations
        self.on_input: Optional[Callable[[], int]] = None
        self.on_output: Optional[Callable[[int], None]] = None
    
    def reset(self) -> None:
        """Reset CPU to initial state."""
        self.ac = 0
        self.mq = 0
        self.mbr = 0
        self.ir = 0
        self.pc = 0
        self.running = False
        self.halted = False
        self.use_left_instruction = True
        self.cycle_count = 0
        self.instruction_count = 0
        self.simulated_time_us = 0.0
        self.zero_flag = False
        self.negative_flag = False
        self.instruction_log = []
        self.memory.clear()
    
    def load_program(self, program: List[int], start_address: int = 0) -> None:
        """
        Load program into memory.
        
        Args:
            program: List of 40-bit words
            start_address: Starting memory address
        """
        for i, word in enumerate(program):
            addr = start_address + i
            if addr < self.memory.words:
                self.memory.write_raw(addr, word)
    
    def fetch_instruction(self) -> bool:
        """
        Fetch next instruction from memory.
        
        IAS format: two 20-bit instructions per 40-bit word.
        Left instruction (bits 39-20), Right instruction (bits 19-0).
        
        Returns:
            True if instruction fetched, False if halted
        """
        if self.halted:
            return False
        
        # Fetch 40-bit word from memory
        word = self.memory.read(self.pc)
        self.mbr = word
        
        # Extract instruction
        if self.use_left_instruction:
            # Left instruction: bits 39-20
            self.ir = (word >> 20) & MASK_20
            self.use_left_instruction = False
        else:
            # Right instruction: bits 19-0
            self.ir = word & MASK_20
            self.use_left_instruction = True
            self.pc = (self.pc + 1) & 0x3FF  # Wrap at 1024
        
        return True
    
    def decode_instruction(self) -> tuple:
        """
        Decode current instruction.
        
        IAS instruction format (20 bits):
        - Bits 19-16: Opcode (4 bits)
        - Bits 15-10: Unused (6 bits)
        - Bits 9-0: Address (10 bits)
        
        Returns:
            (opcode, address) tuple
        """
        opcode = (self.ir >> 16) & 0xF
        address = self.ir & 0x3FF
        return opcode, address
    
    def execute_instruction(self) -> int:
        """
        Execute current instruction.
        
        Returns:
            Number of cycles taken
        """
        opcode, address = self.decode_instruction()
        
        # Log instruction for debugging
        if self.debug:
            self._log_instruction(opcode, address)
        
        # Execute based on opcode
        cycles = self._execute_opcode(opcode, address)
        
        # Update flags
        self.zero_flag = is_zero_40bit(self.ac)
        self.negative_flag = is_negative_40bit(self.ac)
        
        return cycles
    
    def _execute_opcode(self, opcode: int, address: int) -> int:
        """
        Execute specific opcode.
        
        Args:
            opcode: 4-bit opcode
            address: 10-bit memory address
        
        Returns:
            Number of cycles taken
        """
        try:
            op = Opcode(opcode)
        except ValueError:
            # Invalid opcode - treat as STOP
            self.halted = True
            return 1
        
        # Get base cycle count
        cycles = INSTRUCTION_CYCLES.get(op, 1)
        
        # Execute operation
        if op == Opcode.STOP:
            self.halted = True
        
        elif op == Opcode.ADD:
            value = self.memory.read(address)
            result, overflow = add_40bit(self.ac, value)
            self.ac = result
        
        elif op == Opcode.SUB:
            value = self.memory.read(address)
            result, borrow = sub_40bit(self.ac, value)
            self.ac = result
        
        elif op == Opcode.MUL:
            value = self.memory.read(address)
            mq, ac = multiply_40bit(self.ac, value)
            self.mq = mq
            self.ac = ac
        
        elif op == Opcode.DIV:
            value = self.memory.read(address)
            if value != 0:
                quotient, remainder = divide_40bit(self.mq, self.ac, value)
                self.mq = quotient
                self.ac = remainder
        
        elif op == Opcode.AND:
            value = self.memory.read(address)
            self.ac = bitwise_and_40bit(self.ac, value)
        
        elif op == Opcode.OR:
            value = self.memory.read(address)
            self.ac = bitwise_or_40bit(self.ac, value)
        
        elif op == Opcode.JMP:
            self.pc = address
            return cycles  # Don't increment PC
        
        elif op == Opcode.JZ:
            if self.zero_flag:
                self.pc = address
                return cycles
        
        elif op == Opcode.JN:
            if self.negative_flag:
                self.pc = address
                return cycles
        
        elif op == Opcode.LD:
            value = self.memory.read(address)
            self.ac = value
        
        elif op == Opcode.ST:
            self.memory.write(address, self.ac)
        
        elif op == Opcode.IN:
            # Input from paper tape
            if self.on_input:
                value = self.on_input()
                self.ac = mask_40bit(value)
            else:
                # Default: read from paper tape
                word = self.paper_tape.read_word()
                if word is not None:
                    self.ac = word
        
        elif op == Opcode.OUT:
            # Output to paper tape
            if self.on_output:
                self.on_output(self.ac)
            else:
                # Default: write to paper tape
                self.paper_tape.punch_word(self.ac)
        
        elif op == Opcode.RSH:
            # Right shift by address bits (or use address as shift count)
            shift = address & 0x3F  # Use lower 6 bits for shift count
            self.ac = shift_right_40bit(self.ac, shift)
        
        elif op == Opcode.LSH:
            # Left shift by address bits
            shift = address & 0x3F
            self.ac = shift_left_40bit(self.ac, shift)
        
        return cycles
    
    def step(self) -> int:
        """
        Execute one instruction.
        
        Returns:
            Number of cycles taken
        """
        if self.halted:
            return 0
        
        # Fetch
        if not self.fetch_instruction():
            return 0
        
        # Execute
        cycles = self.execute_instruction()
        
        # Update counters
        self.cycle_count += cycles
        self.instruction_count += 1
        
        if self.enable_timing:
            elapsed_us = cycles * CYCLE_TIME_US
            self.simulated_time_us += elapsed_us
            # Simulate real-time delay (optional)
            # time.sleep(elapsed_us / 1_000_000)
        
        return cycles
    
    def run(self, max_instructions: int = 0, max_time_s: float = 0.0) -> None:
        """
        Run CPU until halted or limit reached.
        
        Args:
            max_instructions: Maximum instructions to execute (0 = unlimited)
            max_time_s: Maximum real time to run (0 = unlimited)
        """
        self.running = True
        self.halted = False
        self.start_time = time.time()
        
        instructions_executed = 0
        
        while self.running and not self.halted:
            # Check instruction limit
            if max_instructions > 0 and instructions_executed >= max_instructions:
                break
            
            # Check time limit
            if max_time_s > 0:
                elapsed = time.time() - self.start_time
                if elapsed >= max_time_s:
                    break
            
            # Execute one instruction
            self.step()
            instructions_executed += 1
            
            # Refresh memory periodically (Williams tubes need ~100 Hz refresh)
            if instructions_executed % 1000 == 0:
                self.memory.refresh()
        
        self.running = False
    
    def stop(self) -> None:
        """Stop CPU execution."""
        self.running = False
    
    def _log_instruction(self, opcode: int, address: int) -> None:
        """Log instruction for debugging."""
        op_name = Opcode(opcode).name if opcode in [o.value for o in Opcode] else f"UNKNOWN({opcode})"
        
        log_entry = {
            'pc': self.pc,
            'instruction': f"{op_name} {address}",
            'ac': f"{self.ac:010X}",
            'mq': f"{self.mq:010X}",
            'ir': f"{self.ir:05X}",
            'cycles': self.cycle_count,
            'time_us': self.simulated_time_us
        }
        
        self.instruction_log.append(log_entry)
        
        # Print to console
        print(f"PC={self.pc:03X} {op_name:4} {address:03X}  AC={self.ac:010X}  MQ={self.mq:010X}")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get CPU state.
        
        Returns:
            Dictionary with CPU state
        """
        return {
            'registers': {
                'ac': self.ac,
                'ac_hex': f"{self.ac:010X}",
                'mq': self.mq,
                'mq_hex': f"{self.mq:010X}",
                'mbr': self.mbr,
                'mbr_hex': f"{self.mbr:010X}",
                'ir': self.ir,
                'ir_hex': f"{self.ir:05X}",
                'pc': self.pc,
                'pc_hex': f"{self.pc:03X}"
            },
            'flags': {
                'zero': self.zero_flag,
                'negative': self.negative_flag
            },
            'control': {
                'running': self.running,
                'halted': self.halted,
                'use_left_instruction': self.use_left_instruction
            },
            'timing': {
                'cycle_count': self.cycle_count,
                'instruction_count': self.instruction_count,
                'simulated_time_us': self.simulated_time_us,
                'simulated_time_s': self.simulated_time_us / 1_000_000
            },
            'memory': self.memory.get_status()
        }
    
    def dump_state(self) -> str:
        """
        Dump CPU state as formatted string.
        
        Returns:
            Formatted state string
        """
        state = self.get_state()
        
        lines = [
            "=== AVIDAC CPU State ===",
            f"AC = {state['registers']['ac_hex']} ({to_signed_40bit(state['registers']['ac'])})",
            f"MQ = {state['registers']['mq_hex']}",
            f"MBR = {state['registers']['mbr_hex']}",
            f"IR = {state['registers']['ir_hex']}",
            f"PC = {state['registers']['pc_hex']} ({state['registers']['pc']})",
            f"Flags: Zero={state['flags']['zero']}, Negative={state['flags']['negative']}",
            f"Running={state['control']['running']}, Halted={state['control']['halted']}",
            f"Instructions: {state['timing']['instruction_count']}",
            f"Cycles: {state['timing']['cycle_count']}",
            f"Simulated Time: {state['timing']['simulated_time_s']:.6f} s"
        ]
        
        return '\n'.join(lines)


def create_test_cpu() -> AVIDACCPU:
    """
    Create a CPU with test program for verification.
    
    Returns:
        AVIDACCPU with simple test program loaded
    """
    cpu = AVIDACCPU(debug=False)
    
    # Simple test program: add numbers 1-10
    test_program = [
        0x0000000000,  # 0x000: (unused)
        0x000000000A,  # 0x001: LD 10 (load counter)
        0x0000000000,  # 0x002: (unused)
        0x0A00000003,  # 0x003: LD SUM | ADD ONE (left: LD SUM, right: ADD ONE)
        0x0B00000003,  # 0x004: ST SUM | SUB ONE
        0x0900000003,  # 0x005: JN END | JZ END
        0x0700000003,  # 0x006: JMP LOOP
        0x0000000000,  # 0x007: END: STOP
        0x0000000000,  # SUM: (will be 0)
        0x0000000001,  # ONE: 1
        0x000000000A,  # Counter start: 10
    ]
    
    cpu.load_program(test_program)
    return cpu


if __name__ == '__main__':
    # Run simple test
    cpu = create_test_cpu()
    cpu.run(max_instructions=100)
    print(cpu.dump_state())
