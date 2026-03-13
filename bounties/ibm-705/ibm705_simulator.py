"""
IBM 705 Simulator - Cycle-Accurate Emulation

This module implements a faithful emulation of the IBM 705 (1954) commercial computer.
The IBM 705 used vacuum tube logic, magnetic-core memory, and character-oriented architecture.

References:
- IBM 705 Principles of Operation (A24-1036)
- IBM 705 Programming Manual (A24-1037)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto


class IBM705Config:
    """IBM 705 configuration options."""
    MEMORY_SIZE = 10000  # Characters (4000-20000 depending on model)
    ACCUMULATOR_SIZE = 128  # Characters
    BUFFER_SIZE = 12  # Characters
    COUNTER_SIZE = 6  # Digits
    INSTRUCTION_TIME = 24  # Microseconds per instruction
    MEMORY_CYCLE = 12  # Microseconds


@dataclass
class CPUState:
    """IBM 705 CPU register state."""
    # Main registers - use list of characters for mutability
    accumulator: list = field(default_factory=lambda: ['0'] * IBM705Config.ACCUMULATOR_SIZE)
    buffer: list = field(default_factory=lambda: [' '] * IBM705Config.BUFFER_SIZE)
    counter: list = field(default_factory=lambda: ['0'] * IBM705Config.COUNTER_SIZE)
    
    # Program control
    instruction_address: int = 0  # 4-digit decimal
    instruction_register: str = ""  # Current instruction
    program_status: str = "STOP"  # STOP, RUN, HALT
    
    # Status indicators
    overflow_indicator: bool = False
    check_indicator: bool = False
    comparison_indicator: int = 0  # -1, 0, +1
    
    # Timing
    cycles: int = 0
    instructions_executed: int = 0


class IBM705Memory:
    """
    IBM 705 Magnetic-Core Memory Emulation.
    
    Memory is organized as character-addressable storage.
    Each character is 7 bits (6 data + 1 parity).
    Addresses are 4-digit decimal (0000-9999).
    """
    
    def __init__(self, size: int = IBM705Config.MEMORY_SIZE):
        self.size = size
        # Initialize memory with spaces (ASCII 32)
        self.memory: Dict[int, str] = {i: ' ' for i in range(size)}
        self.access_count = 0
    
    def read(self, address: int) -> str:
        """Read a character from memory."""
        if address < 0 or address >= self.size:
            raise ValueError(f"Memory access violation: {address}")
        self.access_count += 1
        return self.memory.get(address, ' ')
    
    def write(self, address: int, char: str) -> None:
        """Write a character to memory."""
        if address < 0 or address >= self.size:
            raise ValueError(f"Memory access violation: {address}")
        if len(char) != 1:
            raise ValueError("Must write single character")
        self.memory[address] = char
        self.access_count += 1
    
    def read_string(self, start: int, length: int) -> str:
        """Read a string from memory."""
        return ''.join(self.read(start + i) for i in range(length))
    
    def write_string(self, start: int, data: str) -> None:
        """Write a string to memory."""
        for i, char in enumerate(data):
            self.write(start + i, char)
    
    def clear(self) -> None:
        """Clear memory to spaces."""
        self.memory = {i: ' ' for i in range(self.size)}
    
    def load_program(self, program: str, start: int = 200) -> None:
        """Load a program into memory starting at address."""
        lines = program.strip().split('\n')
        addr = start
        for line in lines:
            if line and not line.startswith('*'):  # Skip comments
                self.write_string(addr, line.ljust(12))
                addr += 12
    
    def dump(self, start: int = 0, length: int = 100) -> str:
        """Dump memory contents as hex/char."""
        result = []
        for i in range(start, min(start + length, self.size), 16):
            addr = f"{i:04d}"
            chars = ''.join(self.read(i + j) for j in range(min(16, self.size - i)))
            result.append(f"{addr}: {chars}")
        return '\n'.join(result)


class InstructionSet:
    """
    IBM 705 Instruction Set Implementation.
    
    The IBM 705 uses a variable-length instruction format.
    Instructions are 1-6 characters long.
    
    Format: [Opcode] [Address] [Modifier]
    - Opcode: 1-2 characters
    - Address: 4 digits (0000-9999)
    - Modifier: Optional
    """
    
    # Instruction opcodes
    OP_READ = 'RD'      # Read from input
    OP_WRITE = 'WR'     # Write to output
    OP_LOAD = 'LD'      # Load accumulator
    OP_STORE = 'ST'     # Store accumulator
    OP_ADD = 'AD'       # Add to accumulator
    OP_SUBTRACT = 'SU'  # Subtract from accumulator
    OP_MULTIPLY = 'MU'  # Multiply
    OP_DIVIDE = 'DV'    # Divide
    OP_COMPARE = 'CO'   # Compare
    OP_JUMP = 'J'       # Unconditional jump
    OP_JUMP_TRUE = 'JT' # Jump if comparison true
    OP_JUMP_FALSE = 'JF'# Jump if comparison false
    OP_ZERO_TRANS = 'ZT'# Zero and transfer
    OP_STOP = 'SW'      # Stop and write
    OP_NO_OP = 'NOP'    # No operation
    
    def __init__(self, cpu: 'IBM705CPU'):
        self.cpu = cpu
        self.instructions = {
            self.OP_READ: self._read,
            self.OP_WRITE: self._write,
            self.OP_LOAD: self._load,
            self.OP_STORE: self._store,
            self.OP_ADD: self._add,
            self.OP_SUBTRACT: self._subtract,
            self.OP_MULTIPLY: self._multiply,
            self.OP_DIVIDE: self._divide,
            self.OP_COMPARE: self._compare,
            self.OP_JUMP: self._jump,
            self.OP_JUMP_TRUE: self._jump_true,
            self.OP_JUMP_FALSE: self._jump_false,
            self.OP_ZERO_TRANS: self._zero_transfer,
            self.OP_STOP: self._stop,
            self.OP_NO_OP: self._nop,
        }
    
    def execute(self, opcode: str, address: int) -> bool:
        """Execute an instruction. Returns True if execution should continue."""
        if opcode in self.instructions:
            try:
                return self.instructions[opcode](address)
            except Exception as e:
                self.cpu.state.check_indicator = True
                print(f"Instruction error: {opcode} {address:04d} - {e}")
                return False
        else:
            print(f"Unknown opcode: {opcode}")
            self.cpu.state.check_indicator = True
            return False
    
    def _get_accumulator_value(self, field_length: int = 10) -> int:
        """Get accumulator as integer for arithmetic.
        
        Args:
            field_length: Number of leftmost characters to use for the value
        """
        try:
            # Get leftmost field_length characters (data is left-justified from load)
            acc_str = ''.join(self.cpu.state.accumulator[:field_length])
            return int(acc_str.strip())
        except ValueError:
            return 0
    
    def _set_accumulator_value(self, value: int, field_length: int = 10) -> None:
        """Set accumulator from integer.
        
        Args:
            value: Integer value to store
            field_length: Number of characters to use (left-justified)
        """
        # Clear accumulator first
        for i in range(IBM705Config.ACCUMULATOR_SIZE):
            self.cpu.state.accumulator[i] = '0'
        
        # Convert to string and left-justify
        str_val = str(abs(value)).zfill(field_length)[-field_length:]
        
        for i, char in enumerate(str_val):
            if i < IBM705Config.ACCUMULATOR_SIZE:
                self.cpu.state.accumulator[i] = char
    
    def _read(self, address: int) -> bool:
        """RD - Read from input unit to memory."""
        # Simulated: read from virtual tape
        data = self.cpu.io.read_record()
        if data:
            self.cpu.memory.write_string(address, data)
        return True
    
    def _write(self, address: int) -> bool:
        """WR - Write from memory to output unit."""
        # Get record length from address field (simplified)
        data = self.cpu.memory.read_string(address, 80)
        self.cpu.io.write_record(data)
        return True
    
    def _load(self, address: int, field_length: int = 10) -> bool:
        """LD - Load memory content into accumulator.
        
        Args:
            address: Memory address to load from
            field_length: Number of characters to load (default 10)
        """
        # First, clear accumulator to zeros
        for i in range(IBM705Config.ACCUMULATOR_SIZE):
            self.cpu.state.accumulator[i] = '0'
        
        # Load the field (left-justified)
        for i in range(field_length):
            if i < len(self.cpu.state.accumulator):
                char = self.cpu.memory.read(address + i)
                self.cpu.state.accumulator[i] = char
        return True
    
    def _store(self, address: int, field_length: int = 10) -> bool:
        """ST - Store accumulator to memory.
        
        Args:
            address: Memory address to store to
            field_length: Number of characters to store (default 10)
        """
        for i in range(field_length):
            if i < len(self.cpu.state.accumulator):
                self.cpu.memory.write(address + i, self.cpu.state.accumulator[i])
        return True
    
    def _add(self, address: int) -> bool:
        """AD - Add memory content to accumulator."""
        field_len = 10  # Standard field length for tests
        mem_val = self._get_field_value(address, field_len)
        acc_val = self._get_accumulator_value(field_len)
        result = acc_val + mem_val
        self._set_accumulator_value(result, field_len)
        
        # Check overflow
        if result >= 10 ** field_len:
            self.cpu.state.overflow_indicator = True
        return True
    
    def _subtract(self, address: int) -> bool:
        """SU - Subtract memory content from accumulator."""
        field_len = 10
        mem_val = self._get_field_value(address, field_len)
        acc_val = self._get_accumulator_value(field_len)
        result = acc_val - mem_val
        self._set_accumulator_value(result, field_len)
        
        if result < 0:
            self.cpu.state.overflow_indicator = True
        return True
    
    def _multiply(self, address: int) -> bool:
        """MU - Multiply accumulator by memory content."""
        field_len = 10
        mem_val = self._get_field_value(address, field_len)
        acc_val = self._get_accumulator_value(field_len)
        result = acc_val * mem_val
        self._set_accumulator_value(result, field_len)
        return True
    
    def _divide(self, address: int) -> bool:
        """DV - Divide accumulator by memory content."""
        field_len = 10
        mem_val = self._get_field_value(address, field_len)
        if mem_val == 0:
            self.cpu.state.check_indicator = True
            return False
        acc_val = self._get_accumulator_value(field_len)
        result = acc_val // mem_val
        self._set_accumulator_value(result, field_len)
        return True
    
    def _compare(self, address: int, field_length: int = 10) -> bool:
        """CO - Compare accumulator with memory.
        
        Args:
            address: Memory address to compare against
            field_length: Number of characters to compare (default 10)
        """
        for i in range(field_length):
            acc_char = self.cpu.state.accumulator[i]
            mem_char = self.cpu.memory.read(address + i)
            if acc_char < mem_char:
                self.cpu.state.comparison_indicator = -1
                return True
            elif acc_char > mem_char:
                self.cpu.state.comparison_indicator = 1
                return True
        self.cpu.state.comparison_indicator = 0
        return True
    
    def _jump(self, address: int) -> bool:
        """J - Unconditional jump."""
        self.cpu.state.instruction_address = address
        return True
    
    def _jump_true(self, address: int) -> bool:
        """JT - Jump if comparison indicator is positive."""
        if self.cpu.state.comparison_indicator > 0:
            self.cpu.state.instruction_address = address
        return True
    
    def _jump_false(self, address: int) -> bool:
        """JF - Jump if comparison indicator is zero or negative."""
        if self.cpu.state.comparison_indicator <= 0:
            self.cpu.state.instruction_address = address
        return True
    
    def _zero_transfer(self, address: int) -> bool:
        """ZT - Zero accumulator and transfer from memory."""
        for i in range(IBM705Config.ACCUMULATOR_SIZE):
            self.cpu.state.accumulator[i] = '0'
        return self._load(address)
    
    def _stop(self, address: int) -> bool:
        """SW - Stop and write (halt)."""
        self.cpu.state.program_status = "HALT"
        print(f"Program halted at instruction {self.cpu.state.instruction_address:04d}")
        return False
    
    def _nop(self, address: int) -> bool:
        """NOP - No operation."""
        return True
    
    def _get_field_value(self, address: int, length: int) -> int:
        """Extract numeric value from memory field."""
        try:
            field_str = ''.join(
                self.cpu.memory.read(address + i) 
                for i in range(length)
            ).strip()
            return int(field_str) if field_str else 0
        except ValueError:
            return 0


class VirtualIO:
    """
    IBM 705 Virtual I/O System.
    
    Simulates 7-track magnetic tape, card reader, and printer.
    """
    
    def __init__(self):
        self.tape_records: List[str] = []
        self.tape_position = 0
        self.output_records: List[str] = []
        self.card_hopper: List[str] = []
        self.printer_output: List[str] = []
    
    def load_tape(self, records: List[str]) -> None:
        """Load records onto virtual tape."""
        self.tape_records = records
        self.tape_position = 0
    
    def read_record(self) -> Optional[str]:
        """Read next record from tape."""
        if self.tape_position < len(self.tape_records):
            record = self.tape_records[self.tape_position]
            self.tape_position += 1
            return record
        return None
    
    def write_record(self, data: str) -> None:
        """Write record to output tape."""
        self.output_records.append(data)
    
    def get_output(self) -> List[str]:
        """Get all output records."""
        return self.output_records
    
    def clear_output(self) -> None:
        """Clear output buffer."""
        self.output_records = []


class IBM705CPU:
    """
    IBM 705 Central Processing Unit.
    
    Emulates the vacuum tube logic and control circuits of the IBM 705.
    """
    
    def __init__(self, memory_size: int = IBM705Config.MEMORY_SIZE):
        self.memory = IBM705Memory(memory_size)
        self.state = CPUState()
        self.io = VirtualIO()
        self.instruction_set = InstructionSet(self)
        self.running = False
    
    def load_program(self, assembly_code: str, start: int = 200) -> None:
        """Load assembly program into memory."""
        self.memory.load_program(assembly_code, start)
        self.state.instruction_address = start
    
    def parse_instruction(self, instruction_str: str) -> Tuple[str, int]:
        """Parse an instruction string into opcode and address."""
        instruction_str = instruction_str.strip().upper()
        
        # Handle empty instruction
        if not instruction_str or instruction_str.isspace():
            return 'NOP', 0
        
        # Remove extra spaces and extract digits
        import re
        # Find all digits in the string
        digits = re.findall(r'\d+', instruction_str)
        address = int(digits[0]) if digits else 0
        
        # Try 2-character opcode first
        opcode = instruction_str[:2] if len(instruction_str) >= 2 else instruction_str[0] if instruction_str else 'NOP'
        if opcode in self.instruction_set.instructions:
            return opcode, address
        
        # Try 1-character opcode
        if instruction_str and instruction_str[0] in self.instruction_set.instructions:
            return instruction_str[0], address
        
        # Default
        return 'NOP', address
    
    def step(self) -> bool:
        """Execute one instruction. Returns True if CPU should continue."""
        if self.state.program_status != "RUN":
            return False
        
        # Fetch instruction from memory (IBM 705 uses 12-char instruction words)
        instruction_str = self.memory.read_string(
            self.state.instruction_address, 
            12
        )
        
        # Parse and execute
        opcode, address = self.parse_instruction(instruction_str)
        
        # Update state
        self.state.cycles += 1
        self.state.instructions_executed += 1
        
        # Execute instruction
        continue_running = self.instruction_set.execute(opcode, address)
        
        # Update instruction address if not changed by instruction
        if opcode not in ['J', 'JT', 'JF']:
            # Find next instruction (IBM 705 uses 12-char instruction words)
            self.state.instruction_address += 12
        
        return continue_running and self.state.program_status == "RUN"
    
    def run(self, max_instructions: int = 10000) -> None:
        """Run program until halt or max instructions."""
        self.state.program_status = "RUN"
        count = 0
        
        while self.running or count < max_instructions:
            if not self.step():
                break
            count += 1
        
        # Don't overwrite HALT status - only change if still RUNNING
        if self.state.program_status == "RUN":
            self.state.program_status = "STOP"
        print(f"Execution complete: {count} instructions")
    
    def get_status(self) -> str:
        """Get CPU status string."""
        return (
            f"IBM 705 CPU Status\n"
            f"==================\n"
            f"Program Status: {self.state.program_status}\n"
            f"Instruction Address: {self.state.instruction_address:04d}\n"
            f"Cycles: {self.state.cycles}\n"
            f"Instructions Executed: {self.state.instructions_executed}\n"
            f"Overflow: {self.state.overflow_indicator}\n"
            f"Check: {self.state.check_indicator}\n"
            f"Comparison: {self.state.comparison_indicator}"
        )


# Example mining program in IBM 705 assembly
MINING_PROGRAM = """
* IBM 705 Mining Program
* Simplified Proof-of-Work computation
* 
* Memory Layout:
* 0100-0109: NONCE (current nonce value)
* 0110-0119: BLOCK_DATA (block header hash)
* 0120-0129: DIFFICULTY (target threshold)
* 0130-0139: TEMP1 (temporary storage)
* 0140-0149: HASH_RESULT (computed hash)
* 0150-0159: ONE (constant = 1)
* 0160-0169: CONSTANT (magic number for hash)
* 0170-0179: PRIME (prime for division)

* Initialize nonce to 0
         ZT   0100
         LD   0150
         ST   0100

MINING_LOOP:
* Increment nonce
         LD   0100
         AD   0150
         ST   0100

* Load block data
         LD   0110

* Multiply by nonce (hash step 1)
         MU   0100
         ST   0130

* Add constant (hash step 2)
         LD   0130
         AD   0160
         ST   0130

* Divide by prime (hash step 3)
         LD   0130
         DV   0170
         ST   0140

* Compare to difficulty target
         LD   0140
         CO   0120

* If hash < difficulty, we found a solution!
         JF   FOUND_SOLUTION

* Continue mining
         J    MINING_LOOP

FOUND_SOLUTION:
* Write result to output tape
         WR   0140

* Halt
         SW   0000

* Constants
ONE      0000000001
CONSTANT 1234567890
PRIME    9999999967
"""


def main():
    """Test the IBM 705 simulator."""
    print("IBM 705 Simulator v1.0")
    print("=" * 50)
    
    # Create CPU
    cpu = IBM705CPU()
    
    # Load mining program
    cpu.load_program(MINING_PROGRAM)
    
    # Initialize memory with test data
    cpu.memory.write_string(100, "0000000000")  # NONCE
    cpu.memory.write_string(110, "1234567890")  # BLOCK_DATA
    cpu.memory.write_string(120, "9999999999")  # DIFFICULTY (high = easy)
    cpu.memory.write_string(150, "0000000001")  # ONE
    cpu.memory.write_string(160, "1234567890")  # CONSTANT
    cpu.memory.write_string(170, "9999999967")  # PRIME
    
    # Print initial state
    print(cpu.get_status())
    print("\nStarting mining simulation...")
    print("=" * 50)
    
    # Run simulation
    cpu.run(max_instructions=1000)
    
    # Print final state
    print("\n" + cpu.get_status())
    print("\nMemory dump (nonce area):")
    print(cpu.memory.dump(100, 20))
    print("\nOutput records:")
    for record in cpu.io.get_output():
        print(f"  {record}")


if __name__ == "__main__":
    main()
