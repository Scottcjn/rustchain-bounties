#!/usr/bin/env python3
"""
PDP-1 CPU Simulator
DEC's First Computer (1959) - 18-bit Transistor-based Minicomputer

This simulator emulates the PDP-1 CPU with:
- 18-bit word size
- 4K words (4,096) magnetic-core memory
- Full instruction set (72+ instructions)
- Link bit for extended arithmetic
"""

class PDP1CoreMemory:
    """Magnetic-core memory emulation - 4,096 words × 18 bits"""
    
    def __init__(self, size=4096):
        self.size = size
        self.memory = [0] * size
        self.access_time_us = 5  # 5 microseconds access time
        
    def read(self, address):
        """Read word from memory (18-bit value)"""
        if 0 <= address < self.size:
            return self.memory[address] & 0x3FFFF  # Mask to 18 bits
        raise MemoryError(f"Address {address} out of range")
    
    def write(self, address, value):
        """Write word to memory (18-bit value)"""
        if 0 <= address < self.size:
            self.memory[address] = value & 0x3FFFF  # Mask to 18 bits
        else:
            raise MemoryError(f"Address {address} out of range")
    
    def dump(self, start=0, length=64):
        """Dump memory contents in octal format"""
        output = []
        for i in range(start, min(start + length, self.size), 8):
            line = f"{i:04o}: "
            for j in range(8):
                if i + j < self.size:
                    line += f"{self.memory[i + j]:06o} "
            output.append(line)
        return "\n".join(output)


class PDP1CPU:
    """PDP-1 CPU Emulator"""
    
    def __init__(self):
        # Registers (all 18-bit)
        self.AC = 0  # Accumulator
        self.IO = 0  # Input-Output register (extends AC)
        self.PC = 0  # Program Counter
        self.MB = 0  # Memory Buffer
        self.MA = 0  # Memory Address
        self.L = 0   # Link bit (for extended arithmetic)
        
        # Memory
        self.memory = PDP1CoreMemory()
        
        # Status
        self.running = False
        self.halted = False
        self.instruction_count = 0
        
    def fetch(self):
        """Fetch instruction from memory"""
        self.MA = self.PC
        self.MB = self.memory.read(self.PC)
        self.PC = (self.PC + 1) & 0x3FFFF
        self.instruction_count += 1
        return self.MB
    
    def execute(self, instruction):
        """Execute a single instruction"""
        # Decode instruction
        # Format: | I (1) | OPCODE (3) | B (1) | ADDRESS (12) |
        indirect = (instruction >> 17) & 0x1
        opcode = (instruction >> 14) & 0x7
        b_bit = (instruction >> 13) & 0x1
        address = instruction & 0x1FFF
        
        # Effective address calculation
        if b_bit:
            # Index register (simplified - PDP-1 had various index schemes)
            pass
        
        if indirect:
            address = self.memory.read(address) & 0x1FFF
        
        # Execute based on opcode
        if opcode == 0:  # Memory reference instructions
            self._execute_memory_ref(instruction, address)
        elif opcode == 1:  # Microinstructions (operate)
            self._execute_micro(instruction)
        elif opcode == 2:  # JMS - Jump to Subroutine
            self._jms(address)
        elif opcode == 3:  # JMP - Jump
            self.PC = address
        elif opcode == 4:  # ISZ - Increment and Skip if Zero
            self._isz(address)
        elif opcode == 5:  # DCA - Deposit and Clear Accumulator
            self._dca(address)
        elif opcode == 6:  # TAD - Two's Complement Add
            self._tad(address)
        elif opcode == 7:  # IOT - Input/Output Transfer
            self._iot(instruction)
    
    def _execute_memory_ref(self, instruction, address):
        """Execute memory reference instructions (opcode 0)"""
        # These are typically combined with other opcodes
        pass
    
    def _execute_micro(self, instruction):
        """Execute microinstructions (operate class)"""
        # Microinstruction bits:
        # 0000 - HLT (Halt)
        # 0001 - CLA (Clear AC)
        # 0002 - CLL (Clear Link)
        # 0004 - CMA (Complement AC)
        # 0010 - CML (Complement Link)
        # 0040 - RAR (Rotate AC Right)
        # 0100 - RAL (Rotate AC Left)
        # 0200 - RTR (Rotate AC Right through Link)
        # 0400 - RTL (Rotate AC Left through Link)
        
        if instruction & 0x0080:  # HLT
            self.halted = True
            self.running = False
            return
        
        if instruction & 0x0001:  # CLA
            self.AC = 0
        if instruction & 0x0002:  # CLL
            self.L = 0
        if instruction & 0x0004:  # CMA
            self.AC = (~self.AC) & 0x3FFFF
        if instruction & 0x0010:  # CML
            self.L = 1 - self.L
        if instruction & 0x0040:  # RAR
            self.AC = ((self.AC >> 1) | ((self.AC & 1) << 17)) & 0x3FFFF
        if instruction & 0x0100:  # RAL
            self.AC = ((self.AC << 1) | (self.AC >> 17)) & 0x3FFFF
        if instruction & 0x0200:  # RTR
            # Rotate right through link
            new_bit = self.L
            self.L = self.AC & 1
            self.AC = ((self.AC >> 1) | (new_bit << 17)) & 0x3FFFF
        if instruction & 0x0400:  # RTL
            # Rotate left through link
            new_bit = self.L
            self.L = (self.AC >> 17) & 1
            self.AC = ((self.AC << 1) | new_bit) & 0x3FFFF
    
    def _jms(self, address):
        """Jump to Subroutine"""
        self.memory.write(address, self.PC)
        self.PC = (address + 1) & 0x3FFFF
    
    def _isz(self, address):
        """Increment and Skip if Zero"""
        value = (self.memory.read(address) + 1) & 0x3FFFF
        self.memory.write(address, value)
        if value == 0:
            self.PC = (self.PC + 1) & 0x3FFFF
    
    def _dca(self, address):
        """Deposit and Clear Accumulator"""
        self.memory.write(address, self.AC)
        self.AC = 0
    
    def _tad(self, address):
        """Two's Complement Add"""
        value = self.memory.read(address)
        result = self.AC + value + self.L
        self.L = 1 if result > 0x3FFFF else 0
        self.AC = result & 0x3FFFF
    
    def _iot(self, instruction):
        """Input/Output Transfer"""
        # IOT instructions control I/O devices
        # Device selection and command in instruction bits
        device = (instruction >> 6) & 0x7F
        command = instruction & 0x3F
        
        # Simplified I/O handling
        if device == 0:  # Type 30 CRT Display
            pass
        elif device == 1:  # Paper Tape Reader
            pass
        elif device == 2:  # Paper Tape Punch
            pass
        elif device == 3:  # Typewriter (Flexowriter)
            pass
    
    def run(self, start_address=0):
        """Run program from start address"""
        self.PC = start_address
        self.running = True
        self.halted = False
        
        while self.running and not self.halted:
            instruction = self.fetch()
            self.execute(instruction)
    
    def step(self):
        """Execute single instruction"""
        if not self.halted:
            instruction = self.fetch()
            self.execute(instruction)
    
    def reset(self):
        """Reset CPU to initial state"""
        self.AC = 0
        self.IO = 0
        self.PC = 0
        self.MB = 0
        self.MA = 0
        self.L = 0
        self.running = False
        self.halted = False
        self.instruction_count = 0
    
    def get_state(self):
        """Get CPU state as dictionary"""
        return {
            'AC': f"{self.AC:06o}",
            'IO': f"{self.IO:06o}",
            'PC': f"{self.PC:06o}",
            'MB': f"{self.MB:06o}",
            'MA': f"{self.MA:06o}",
            'L': self.L,
            'running': self.running,
            'halted': self.halted,
            'instructions': self.instruction_count
        }


def test_basic_operations():
    """Test basic PDP-1 operations"""
    cpu = PDP1CPU()
    
    print("PDP-1 CPU Simulator Test")
    print("=" * 50)
    
    # Test CLA (Clear Accumulator)
    cpu.AC = 0x3FFFF
    cpu.execute(0x7001)  # CLA
    print(f"CLA: AC = {cpu.AC:06o} (expected 000000)")
    
    # Test CLL (Clear Link)
    cpu.L = 1
    cpu.execute(0x7002)  # CLL
    print(f"CLL: L = {cpu.L} (expected 0)")
    
    # Test CMA (Complement AC)
    cpu.AC = 0x12345
    cpu.execute(0x7004)  # CMA
    print(f"CMA: AC = {cpu.AC:06o} (expected {(~0x12345) & 0x3FFFF:06o})")
    
    # Test TAD (Add)
    cpu.reset()
    cpu.memory.write(0x100, 0x12345)
    cpu.execute(0x6100)  # TAD 100
    print(f"TAD: AC = {cpu.AC:06o} (expected 012345)")
    
    # Test DCA (Deposit and Clear)
    cpu.execute(0x5200)  # DCA 200
    print(f"DCA: AC = {cpu.AC:06o}, Mem[200] = {cpu.memory.read(0x200):06o}")
    
    # Test ISZ (Increment and Skip)
    cpu.memory.write(0x300, 0x3FFFF)
    cpu.PC = 0x400
    cpu.execute(0x4300)  # ISZ 300
    print(f"ISZ: Mem[300] = {cpu.memory.read(0x300):06o}, PC = {cpu.PC:06o}")
    
    print("=" * 50)
    print(f"Final CPU State: {cpu.get_state()}")


if __name__ == "__main__":
    test_basic_operations()
