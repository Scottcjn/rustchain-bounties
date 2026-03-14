#!/usr/bin/env python3
"""
UNIVAC I Assembler/Disassembler

Assemble human-readable UNIVAC I assembly to 12-bit words,
and disassemble 12-bit words back to assembly.

Author: RustChain Bounty #357 Submission
License: MIT
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from univac_simulator import Instruction, Opcode


# ============================================================================
# Assembler
# ============================================================================

class UNIVACAssembler:
    """UNIVAC I Assembler"""
    
    # Opcode name mapping
    OPCODES = {
        'ADD': Opcode.ADD,
        'SUB': Opcode.SUB,
        'MUL': Opcode.MUL,
        'DIV': Opcode.DIV,
        'LDA': Opcode.LDA,
        'STA': Opcode.STA,
        'JMP': Opcode.JMP,
        'JZ': Opcode.JZ,
        'JN': Opcode.JN,
        'IN': Opcode.IN,
        'OUT': Opcode.OUT,
        'HLT': Opcode.HLT,
        'NOP': Opcode.NOP,
        'AND': Opcode.AND,
        'OR': Opcode.OR,
        'XOR': Opcode.XOR,
    }
    
    def __init__(self):
        self.labels: dict = {}
        self.program: List[Instruction] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def assemble(self, source: str) -> List[int]:
        """
        Assemble source code to machine words.
        
        Args:
            source: Assembly source code
        
        Returns:
            List of 12-bit words
        """
        self.labels = {}
        self.program = []
        self.errors = []
        self.warnings = []
        
        lines = source.split('\n')
        
        # First pass: collect labels
        addr = 0
        for line_num, line in enumerate(lines, 1):
            line = self._preprocess_line(line)
            if not line:
                continue
            
            # Check for label
            if ':' in line:
                label_part, rest = line.split(':', 1)
                label = label_part.strip()
                if label:
                    self.labels[label] = addr
            
            # Count instruction
            instruction_part = line.split(':', 1)[-1].strip() if ':' in line else line
            if instruction_part and not instruction_part.startswith('#'):
                addr += 1
        
        # Second pass: assemble instructions
        addr = 0
        for line_num, line in enumerate(lines, 1):
            line = self._preprocess_line(line)
            if not line:
                continue
            
            # Skip label definition
            if ':' in line:
                line = line.split(':', 1)[-1].strip()
            
            # Skip comments
            if not line or line.startswith('#'):
                continue
            
            # Parse instruction
            try:
                instr = self._parse_instruction(line, addr)
                if instr:
                    self.program.append(instr)
                    addr += 1
            except Exception as e:
                self.errors.append(f"Line {line_num}: {str(e)}")
        
        if self.errors:
            raise AssemblyError("Assembly failed", self.errors)
        
        return [instr.encode() for instr in self.program]
    
    def _preprocess_line(self, line: str) -> str:
        """Remove comments and whitespace"""
        # Remove inline comments
        if '#' in line:
            line = line.split('#')[0]
        return line.strip()
    
    def _parse_instruction(self, line: str, addr: int) -> Optional[Instruction]:
        """Parse single instruction"""
        parts = line.split()
        if not parts:
            return None
        
        opcode_name = parts[0].upper()
        
        if opcode_name not in self.OPCODES:
            raise ValueError(f"Unknown opcode: {opcode_name}")
        
        opcode = self.OPCODES[opcode_name]
        
        # Get operand
        if len(parts) > 1:
            operand = parts[1]
            
            # Check if it's a label
            if operand in self.labels:
                address = self.labels[operand]
            else:
                # Try to parse as number
                try:
                    if operand.startswith('0x'):
                        address = int(operand, 16)
                    else:
                        address = int(operand)
                except ValueError:
                    raise ValueError(f"Invalid operand: {operand}")
        else:
            address = 0
        
        # Validate address range
        if address < 0 or address > 1023:
            raise ValueError(f"Address out of range: {address}")
        
        return Instruction(opcode=opcode, address=address)
    
    def disassemble(self, words: List[int], start_addr: int = 0) -> str:
        """
        Disassemble machine words to assembly source.
        
        Args:
            words: List of 12-bit words
            start_addr: Starting address
        
        Returns:
            Assembly source code
        """
        lines = []
        addr = start_addr
        
        for word in words:
            instr = Instruction.decode(word)
            line = f"{addr:04d}: {instr}"
            lines.append(line)
            addr += 1
        
        return '\n'.join(lines)


class AssemblyError(Exception):
    """Assembly error with error messages"""
    def __init__(self, message: str, errors: List[str]):
        super().__init__(message)
        self.errors = errors
    
    def __str__(self):
        return f"{super().__str__()}: {'; '.join(self.errors)}"


# ============================================================================
# Sample Programs
# ============================================================================

SAMPLE_PROGRAMS = {
    'hello': """
# UNIVAC I Hello World (outputs accumulator values)
# This is a simple demonstration program

        LDA FIRST      # Load first value
        OUT            # Output it
        LDA SECOND     # Load second value
        OUT            # Output it
        HLT            # Halt

FIRST   0x048          # Value 72 ('H' in ASCII-ish)
SECOND  0x069          # Value 105 ('i')
""",
    
    'loop': """
# UNIVAC I Loop Example
# Counts from 1 to 10

        LDA ONE        # Initialize counter
        STA COUNT      # Store in COUNT
        
LOOP    LDA COUNT      # Load counter
        OUT            # Output it
        ADD ONE        # Increment
        STA COUNT      # Store back
        SUB TEN        # Check if reached 10
        JZ DONE        # If zero, we're done
        JMP LOOP       # Otherwise, continue
        
DONE    HLT            # Halt

COUNT   0              # Counter variable
ONE     1              # Constant 1
TEN     10             # Constant 10
""",
    
    'miner': """
# UNIVAC I Mining Loop (Simplified)
# Demonstrates mining algorithm structure

        LDA NONCE      # Load nonce
        STA TEMP       # Store in TEMP
        
# Hash mixing round 1
        ADD CONST1     # Add constant 1
        XOR TEMP       # XOR with temp
        ROL 3          # Rotate left 3 (pseudo-instruction)
        
# Hash mixing round 2  
        ADD CONST2     # Add constant 2
        XOR TEMP       # XOR with temp
        ROL 3          # Rotate left 3
        
# Check target (simplified)
        LDA RESULT     # Load hash result
        JZ FOUND       # If zero, found solution!
        
# Increment nonce
        LDA NONCE
        ADD ONE
        STA NONCE
        JMP START      # Try next nonce
        
FOUND   OUT            # Output solution
        HLT            # Halt
        
NONCE   0              # Current nonce
TEMP    0              # Temporary storage
RESULT  0              # Hash result
CONST1  0x123          # Mixing constant 1
CONST2  0x456          # Mixing constant 2
ONE     1              # Constant 1
START   0              # Start of loop (will be filled)
""",
}


# ============================================================================
# Command Line Interface
# ============================================================================

def cmd_assemble(args):
    """Assemble source file"""
    assembler = UNIVACAssembler()
    
    # Read source
    if args.input:
        with open(args.input, 'r') as f:
            source = f.read()
    else:
        source = sys.stdin.read()
    
    # Assemble
    try:
        words = assembler.assemble(source)
    except AssemblyError as e:
        print(f"Assembly failed:", file=sys.stderr)
        for error in e.errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    
    # Output
    if args.output:
        with open(args.output, 'wb') as f:
            for word in words:
                f.write(word.to_bytes(2, 'big'))
        print(f"Assembled {len(words)} instructions to {args.output}")
    else:
        # Print as hex
        for i, word in enumerate(words):
            print(f"{i:04d}: {word:03X} ({word:012b})")
    
    return 0


def cmd_disassemble(args):
    """Disassemble binary file"""
    assembler = UNIVACAssembler()
    
    # Read binary
    if args.input:
        with open(args.input, 'rb') as f:
            data = f.read()
    else:
        data = sys.stdin.buffer.read()
    
    # Convert to words
    words = []
    for i in range(0, len(data), 2):
        if i + 1 < len(data):
            word = (data[i] << 8) | data[i + 1]
            words.append(word & 0xFFF)
    
    # Disassemble
    source = assembler.disassemble(words, start_addr=args.start_addr)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(source)
        print(f"Disassembled {len(words)} instructions to {args.output}")
    else:
        print(source)
    
    return 0


def cmd_demo(args):
    """Demonstrate assembler with sample programs"""
    assembler = UNIVACAssembler()
    
    if args.program not in SAMPLE_PROGRAMS:
        print(f"Unknown program: {args.program}", file=sys.stderr)
        print(f"Available: {', '.join(SAMPLE_PROGRAMS.keys())}", file=sys.stderr)
        return 1
    
    source = SAMPLE_PROGRAMS[args.program]
    
    print(f"=== {args.program.upper()} ===")
    print("\nSource:")
    print(source)
    
    print("\nAssembly:")
    try:
        words = assembler.assemble(source)
        for i, word in enumerate(words):
            instr = Instruction.decode(word)
            print(f"{i:04d}: {word:03X}  {instr}")
    except AssemblyError as e:
        print(f"Assembly failed: {e}")
        return 1
    
    return 0


def cmd_list(args):
    """List available sample programs"""
    print("Available sample programs:")
    for name in SAMPLE_PROGRAMS.keys():
        print(f"  {name}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='UNIVAC I Assembler/Disassembler - RustChain Bounty #357'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Assemble command
    asm_parser = subparsers.add_parser('assemble', help='Assemble source code')
    asm_parser.add_argument('--input', '-i', type=str,
                           help='Input source file (default: stdin)')
    asm_parser.add_argument('--output', '-o', type=str,
                           help='Output binary file (default: stdout hex)')
    asm_parser.set_defaults(func=cmd_assemble)
    
    # Disassemble command
    disasm_parser = subparsers.add_parser('disassemble', help='Disassemble binary')
    disasm_parser.add_argument('--input', '-i', type=str,
                              help='Input binary file (default: stdin)')
    disasm_parser.add_argument('--output', '-o', type=str,
                              help='Output source file (default: stdout)')
    disasm_parser.add_argument('--start-addr', type=int, default=0,
                              help='Starting address')
    disasm_parser.set_defaults(func=cmd_disassemble)
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Demo with sample program')
    demo_parser.add_argument('--program', '-p', type=str, default='hello',
                            help='Sample program name')
    demo_parser.set_defaults(func=cmd_demo)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List sample programs')
    list_parser.set_defaults(func=cmd_list)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
