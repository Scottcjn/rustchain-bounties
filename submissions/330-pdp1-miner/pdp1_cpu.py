#!/usr/bin/env python3
"""
PDP-1 CPU Simulator (1959)
==========================
Emulates DEC's first computer with 18-bit architecture.

Key Features:
- 18-bit word size
- 4K words magnetic-core memory (expandable to 64K)
- One's complement arithmetic
- Original PDP-1 instruction set
- Type 30 CRT display simulation

Author: RustChain PDP-1 Mining Project
License: MIT
"""

class PDP1CPU:
    """
    PDP-1 Central Processing Unit Simulator
    
    The PDP-1 uses an 18-bit word size with the following registers:
    - AC (Accumulator): 18 bits, main arithmetic register
    - MQ (Multiplier Quotient): 18 bits, for multiply/divide
    - PC (Program Counter): 18 bits, memory address register
    - IR (Instruction Register): 18 bits, current instruction
    """
    
    # PDP-1 Instruction Opcodes
    OP_JMP = 0o002  # Jump
    OP_JSP = 0o004  # Jump to subroutine
    OP_JRN = 0o006  # Jump if rightmost 1
    OP_JLT = 0o010  # Jump if less than zero
    OP_JLE = 0o012  # Jump if less than or equal
    OP_JEQ = 0o014  # Jump if equal to zero
    OP_JNE = 0o016  # Jump if not equal
    OP_IOA = 0o020  # I/O A
    OP_IOB = 0o022  # I/O B
    OP_ADD = 0o040  # Add
    OP_SUB = 0o042  # Subtract
    OP_MUL = 0o044  # Multiply
    OP_DIV = 0o046  # Divide
    OP_AND = 0o050  # AND
    OP_OR  = 0o052  # OR
    OP_XOR = 0o054  # Exclusive OR
    OP_LDA = 0o060  # Load AC
    OP_STA = 0o062  # Store AC
    OP_LDI = 0o064  # Load immediate
    OP_LMQ = 0o070  # Load MQ
    OP_STM = 0o072  # Store MQ
    OP_SHL = 0o074  # Shift left
    OP_SHR = 0o076  # Shift right
    OP_CSW = 0o100  # Complement switch
    OP_HALT = 0o102  # Halt
    
    # Memory size (4K words standard)
    MEMORY_SIZE = 4096
    
    def __init__(self, memory_size=MEMORY_SIZE):
        """Initialize PDP-1 CPU with memory"""
        self.memory = [0] * memory_size
        self.memory_size = memory_size
        
        # Registers (all 18-bit)
        self.ac = 0  # Accumulator
        self.mq = 0  # Multiplier Quotient
        self.pc = 0  # Program Counter
        self.ir = 0  # Instruction Register
        
        # Status flags
        self.running = False
        self.halted = False
        
        # Cycle counter for timing
        self.cycles = 0
        
        # I/O devices
        self.io_devices = {}
        
        # Mask for 18-bit values
        self.WORD_MASK = 0o777777  # 18 bits = 0x3FFFF
        
    def reset(self):
        """Reset CPU to initial state"""
        self.ac = 0
        self.mq = 0
        self.pc = 0
        self.ir = 0
        self.running = False
        self.halted = False
        self.cycles = 0
        
    def to_18bit(self, value):
        """Convert value to 18-bit one's complement representation"""
        value = value & self.WORD_MASK
        
        # Handle one's complement negative numbers
        if value & 0o400000:  # Sign bit set (bit 17)
            # Convert to negative in one's complement
            value = -(value ^ self.WORD_MASK)
        
        return value
    
    def from_18bit(self, value):
        """Convert from one's complement to Python integer"""
        if value < 0:
            # Convert negative to one's complement representation
            value = (~(-value)) & self.WORD_MASK
        return value & self.WORD_MASK
    
    def read_memory(self, address):
        """Read word from memory"""
        address = address & 0o7777  # 12-bit address (4K)
        if address < self.memory_size:
            return self.memory[address]
        return 0
    
    def write_memory(self, address, value):
        """Write word to memory"""
        address = address & 0o7777
        if address < self.memory_size:
            self.memory[address] = value & self.WORD_MASK
    
    def fetch(self):
        """Fetch instruction from memory"""
        self.ir = self.read_memory(self.pc)
        self.cycles += 1
    
    def decode(self):
        """Decode instruction"""
        opcode = (self.ir >> 12) & 0o77  # 6-bit opcode
        address = self.ir & 0o7777        # 12-bit address
        indirect = (self.ir >> 10) & 1    # Indirect bit
        return opcode, address, indirect
    
    def execute(self, opcode, address, indirect):
        """Execute decoded instruction"""
        self.cycles += 1
        
        # Handle indirect addressing
        if indirect:
            address = self.read_memory(address) & 0o7777
        
        if opcode == 0:  # NOP / Special operations
            if address == 0:
                pass  # NOP
            elif address == 0o7777:
                self.halted = True
                self.running = False
        
        elif opcode == self.OP_JMP:
            self.pc = address
        
        elif opcode == self.OP_JSP:
            # Jump to subroutine - store return in target
            self.write_memory(address, self.pc)
            self.pc = address
        
        elif opcode == self.OP_JRN:
            if self.ac & 1:
                self.pc = address
        
        elif opcode == self.OP_JLT:
            if self.to_18bit(self.ac) < 0:
                self.pc = address
        
        elif opcode == self.OP_JLE:
            if self.to_18bit(self.ac) <= 0:
                self.pc = address
        
        elif opcode == self.OP_JEQ:
            if self.ac == 0:
                self.pc = address
        
        elif opcode == self.OP_JNE:
            if self.ac != 0:
                self.pc = address
        
        elif opcode == self.OP_ADD:
            operand = self.read_memory(address)
            self.ac = (self.ac + operand) & self.WORD_MASK
        
        elif opcode == self.OP_SUB:
            operand = self.read_memory(address)
            # One's complement subtraction
            self.ac = (self.ac + (operand ^ self.WORD_MASK)) & self.WORD_MASK
        
        elif opcode == self.OP_MUL:
            # Multiply AC by memory, result in AC (high) and MQ (low)
            operand = self.read_memory(address)
            product = self.to_18bit(self.ac) * self.to_18bit(operand)
            # Store high 18 bits in AC, low 18 bits in MQ
            self.mq = product & self.WORD_MASK
            self.ac = (product >> 18) & self.WORD_MASK
        
        elif opcode == self.OP_DIV:
            # Divide AC by memory, quotient in AC, remainder in MQ
            operand = self.to_18bit(self.read_memory(address))
            if operand != 0:
                dividend = self.to_18bit(self.ac)
                self.ac = self.from_18bit(dividend // operand)
                self.mq = self.from_18bit(dividend % operand)
        
        elif opcode == self.OP_AND:
            operand = self.read_memory(address)
            self.ac = self.ac & operand
        
        elif opcode == self.OP_OR:
            operand = self.read_memory(address)
            self.ac = self.ac | operand
        
        elif opcode == self.OP_XOR:
            operand = self.read_memory(address)
            self.ac = self.ac ^ operand
        
        elif opcode == self.OP_LDA:
            self.ac = self.read_memory(address)
        
        elif opcode == self.OP_STA:
            self.write_memory(address, self.ac)
        
        elif opcode == self.OP_LDI:
            # Load immediate - address is the value
            self.ac = address & self.WORD_MASK
        
        elif opcode == self.OP_LMQ:
            self.mq = self.read_memory(address)
        
        elif opcode == self.OP_STM:
            self.write_memory(address, self.mq)
        
        elif opcode == self.OP_SHL:
            # Shift left AC
            shift_amount = address & 0o37  # 5-bit shift count
            self.ac = (self.ac << shift_amount) & self.WORD_MASK
        
        elif opcode == self.OP_SHR:
            # Shift right AC
            shift_amount = address & 0o37
            self.ac = self.ac >> shift_amount
        
        elif opcode == self.OP_CSW:
            # Complement AC
            self.ac = (~self.ac) & self.WORD_MASK
        
        elif opcode == self.OP_IOA:
            # I/O operation A
            device = address & 0o17
            if device in self.io_devices:
                self.io_devices[device]['in'] = self.ac
        
        elif opcode == self.OP_IOB:
            # I/O operation B
            device = address & 0o17
            if device in self.io_devices:
                self.io_devices[device]['out'] = self.ac
        
        elif opcode == self.OP_HALT:
            self.halted = True
            self.running = False
        
        # Increment PC if not modified by instruction
        if opcode not in [self.OP_JMP, self.OP_JSP, self.OP_JRN, 
                          self.OP_JLT, self.OP_JLE, self.OP_JEQ, self.OP_JNE]:
            self.pc = (self.pc + 1) & 0o7777
    
    def step(self):
        """Execute one instruction cycle"""
        if not self.running or self.halted:
            return False
        
        self.fetch()
        opcode, address, indirect = self.decode()
        self.execute(opcode, address, indirect)
        
        return True
    
    def run(self, start_address=0):
        """Run program from start address"""
        self.pc = start_address
        self.running = True
        self.halted = False
        
        while self.running and not self.halted:
            self.step()
    
    def load_program(self, program, start_address=0):
        """Load program into memory"""
        for i, word in enumerate(program):
            self.write_memory(start_address + i, word)
    
    def get_register_state(self):
        """Get current register state"""
        return {
            'AC': self.ac,
            'MQ': self.mq,
            'PC': self.pc,
            'IR': self.ir,
            'cycles': self.cycles,
            'running': self.running,
            'halted': self.halted
        }
    
    def dump_memory(self, start=0, length=64):
        """Dump memory contents"""
        dump = []
        for i in range(length):
            addr = (start + i) & 0o7777
            dump.append((addr, self.memory[addr]))
        return dump


class PDP1Display:
    """
    Type 30 CRT Display Simulator
    
    The original PDP-1 had a Type 30 CRT display with 1024x1024 resolution.
    Points were drawn by specifying X,Y coordinates.
    """
    
    def __init__(self, width=1024, height=1024):
        self.width = width
        self.height = height
        self.points = []
        self.intensity = 1.0
        
    def plot(self, x, y, intensity=None):
        """Plot a point on the display"""
        if intensity is None:
            intensity = self.intensity
        self.points.append((x, y, intensity))
    
    def clear(self):
        """Clear the display"""
        self.points = []
    
    def get_points(self):
        """Get all plotted points"""
        return self.points
    
    def render_ascii(self, width=80, height=40):
        """Render display as ASCII art"""
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        for x, y, intensity in self.points:
            # Scale coordinates to ASCII grid
            sx = int((x / self.width) * width)
            sy = int((y / self.height) * height)
            
            if 0 <= sx < width and 0 <= sy < height:
                # Use different characters for intensity
                if intensity > 0.7:
                    grid[sy][sx] = '█'
                elif intensity > 0.4:
                    grid[sy][sx] = '▓'
                elif intensity > 0.2:
                    grid[sy][sx] = '▒'
                else:
                    grid[sy][sx] = '░'
        
        return '\n'.join(''.join(row) for row in grid)


class PDP1Tape:
    """
    Punched Tape Reader/Punch Simulator
    
    The PDP-1 used punched paper tape for I/O.
    """
    
    def __init__(self):
        self.tape = []
        self.position = 0
        
    def load_tape(self, data):
        """Load data onto tape"""
        self.tape = list(data)
        self.position = 0
    
    def read_char(self):
        """Read character from tape"""
        if self.position < len(self.tape):
            char = self.tape[self.position]
            self.position += 1
            return char
        return None
    
    def write_char(self, char):
        """Write character to tape"""
        self.tape.append(char)
    
    def rewind(self):
        """Rewind tape to beginning"""
        self.position = 0
    
    def get_tape(self):
        """Get tape contents"""
        return bytes(self.tape)


if __name__ == '__main__':
    # Test PDP-1 CPU
    print("PDP-1 CPU Simulator (1959)")
    print("=" * 40)
    
    cpu = PDP1CPU()
    
    # Simple test program: Add two numbers
    test_program = [
        0o0600001,  # LDA 1 - Load from address 1
        0o0400002,  # ADD 2 - Add from address 2
        0o0620003,  # STA 3 - Store to address 3
        0o1020000,  # HALT
        0,          # (padding)
        25,         # Address 1: First number
        17,         # Address 2: Second number
        0           # Address 3: Result storage
    ]
    
    cpu.load_program(test_program)
    cpu.run()
    
    state = cpu.get_register_state()
    print(f"AC (Accumulator): {state['AC']} (octal: {oct(state['AC'])})")
    print(f"Result at address 3: {cpu.read_memory(3)}")
    print(f"Cycles executed: {state['cycles']}")
    print(f"25 + 17 = {cpu.read_memory(3)} ✓" if cpu.read_memory(3) == 42 else "Error!")
    
    # Test display
    print("\nType 30 CRT Display Test")
    print("=" * 40)
    display = PDP1Display()
    
    # Draw a simple pattern
    for i in range(100):
        x = (i * 37) % 1024
        y = (i * 53) % 1024
        display.plot(x, y)
    
    print(display.render_ascii(60, 20))
    
    print("\nPDP-1 Simulator ready for RustChain mining!")
