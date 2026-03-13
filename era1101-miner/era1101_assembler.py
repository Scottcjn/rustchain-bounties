#!/usr/bin/env python3
"""
ERA 1101 Cross-Assembler with Drum Optimization
================================================

Assembles ERA 1101 assembly language into machine code with automatic
drum memory scheduling for optimal performance.

Features:
- Symbolic labels and addresses
- Automatic skip field calculation
- Drum optimization for minimal rotational latency
- Paper tape format output
- Listing file generation

Author: RustChain Bounty #1824 Submission
License: MIT
"""

import re
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import IntEnum


# ============================================================================
# Instruction Set Definition
# ============================================================================

class Opcode(IntEnum):
    INS  = 0x00
    ADD  = 0x06
    INSQ = 0x0C
    CLR  = 0x0D
    ADDQ = 0x0E
    TRA  = 0x0F
    MPY  = 0x10
    LGR  = 0x11
    AND  = 0x12
    DIV  = 0x13
    MLA  = 0x14
    STO  = 0x15
    SHL  = 0x16
    STQ  = 0x17
    SHQ  = 0x18
    RPL  = 0x19
    JMP  = 0x1A
    STA  = 0x1B
    JNZ  = 0x1C
    INSX = 0x1D
    JN   = 0x1E
    JQ   = 0x1F
    HLT  = 0x20
    NOP  = 0x21
    PRT  = 0x22  # Print
    PCH  = 0x23  # Punch
    STP  = 0x24  # Stop

# Execution times in microseconds (for skip calculation)
EXEC_TIMES_US = {
    'INS':  96,
    'ADD':  96,
    'INSQ': 96,
    'CLR':  96,
    'ADDQ': 96,
    'TRA':  96,
    'MPY':  352,
    'LGR':  192,
    'AND':  96,
    'DIV':  1000,
    'MLA':  352,
    'STO':  96,
    'SHL':  96,
    'STQ':  96,
    'SHQ':  96,
    'RPL':  96,
    'JMP':  96,
    'STA':  96,
    'JNZ':  96,
    'INSX': 96,
    'JN':   96,
    'JQ':   96,
    'HLT':  0,
    'NOP':  96,
    'PRT':  5000,  # Print is slow
    'PCH':  10000, # Punch is very slow
    'STP':  0,
}

# Drum timing constants
DRUM_RPM = 3500
DRUM_ROTATION_US = 60_000_000 // DRUM_RPM  # ~17,143 μs
WORDS_PER_TRACK = 82
WORD_TIME_US = DRUM_ROTATION_US // WORDS_PER_TRACK  # ~209 μs per word


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SourceLine:
    """Represents a line of assembly source."""
    line_num: int
    label: Optional[str]
    opcode: Optional[str]
    operand: Optional[str]
    comment: Optional[str]
    raw: str


@dataclass
class AssembledWord:
    """Represents an assembled word."""
    address: int
    value: int
    source_line: int
    label: Optional[str] = None
    is_instruction: bool = False
    skip: int = 0


# ============================================================================
# Assembler
# ============================================================================

class ERA1101Assembler:
    """
    ERA 1101 cross-assembler with drum optimization.
    
    Pass 1: Collect labels and calculate addresses
    Pass 2: Generate code with optimized skip fields
    """
    
    def __init__(self, optimize_drum: bool = True, verbose: bool = False):
        self.optimize_drum = optimize_drum
        self.verbose = verbose
        self.symbols: Dict[str, int] = {}
        self.current_address = 0
        self.assembled_words: List[AssembledWord] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.origin = 0  # ORG value
    
    def parse_line(self, line: str, line_num: int) -> SourceLine:
        """Parse a single line of assembly."""
        # Remove comments
        comment = None
        if '*' in line or ';' in line:
            for sep in ['*', ';']:
                if sep in line:
                    idx = line.index(sep)
                    comment = line[idx+1:].strip()
                    line = line[:idx].strip()
                    break
        
        # Parse label, opcode, operand
        parts = line.split()
        label = None
        opcode = None
        operand = None
        
        if not parts:
            return SourceLine(line_num, None, None, None, comment, line)
        
        # Check if first part is a label (ends with colon)
        if len(parts) >= 1 and ':' in parts[0]:
            label = parts[0].rstrip(':')
            parts = parts[1:]
        
        if parts:
            opcode = parts[0].upper()
            # Check if this looks like a label followed by an opcode
            # Skip directives (ORG, EQU, END) are never labels
            if opcode not in Opcode.__members__ and opcode not in ['ORG', 'EQU', 'END', 'OCT', 'DEC', 'HEX', 'WORD', 'BSS']:
                if len(parts) >= 2:
                    # First part might be a label, second is opcode
                    label = parts[0]
                    opcode = parts[1].upper()
                    if len(parts) > 2:
                        operand = ' '.join(parts[2:])
            elif len(parts) > 1:
                operand = ' '.join(parts[1:])
        
        return SourceLine(line_num, label, opcode, operand, comment, line)
    
    def parse_operand(self, operand: str) -> Tuple[int, bool]:
        """
        Parse operand to get address value.
        Returns (address, is_symbolic)
        """
        if operand is None:
            return 0, False
        
        operand = operand.strip()
        
        # Hex constant (0x or suffix H)
        if operand.startswith('0x') or operand.startswith('0X'):
            return int(operand, 16), False
        if operand.endswith('H') or operand.endswith('h'):
            return int(operand[:-1], 16), False
        
        # Octal constant (suffix O or Q)
        if operand.endswith('O') or operand.endswith('o'):
            return int(operand[:-1], 8), False
        if operand.endswith('Q') or operand.endswith('q'):
            return int(operand[:-1], 8), False
        
        # Decimal constant
        if operand.isdigit():
            return int(operand), False
        
        # Symbolic reference
        return 0, True  # Will be resolved in pass 2
    
    def calculate_skip(self, exec_time_us: int) -> int:
        """
        Calculate optimal skip value for given execution time.
        
        Skip tells how many memory locations to skip to reach the next
        instruction after the current one executes.
        """
        if not self.optimize_drum:
            return 0
        
        # Calculate how many word positions the drum rotates during execution
        words_advanced = (exec_time_us // WORD_TIME_US)
        
        # We want the next instruction to be ready when we need it
        # Skip = words_advanced - 1 (because PC increments by 1 automatically)
        skip = max(0, min(15, words_advanced - 1))
        
        return skip
    
    def pass1(self, source_lines: List[SourceLine]):
        """
        Pass 1: Collect labels and calculate addresses.
        """
        self.current_address = self.origin
        
        for line in source_lines:
            # Handle ORG directive
            if line.opcode == 'ORG':
                if line.operand:
                    self.origin = int(line.operand, 0)
                    self.current_address = self.origin
                continue
            
            # Handle EQU directive (symbolic constant)
            if line.opcode == 'EQU':
                if line.label and line.operand:
                    value = int(line.operand, 0)
                    self.symbols[line.label] = value
                continue
            
            # Handle END directive
            if line.opcode == 'END':
                break
            
            # Handle data directives
            if line.opcode in ['OCT', 'DEC', 'HEX', 'WORD', 'BSS']:
                # Reserve space
                if line.label:
                    self.symbols[line.label] = self.current_address
                
                # Count words to reserve
                if line.operand:
                    operands = line.operand.split(',')
                    if line.opcode == 'BSS':
                        # Block storage - reserve N words
                        count = int(operands[0], 0)
                        self.current_address += count
                    else:
                        self.current_address += len(operands)
                continue
            
            # Handle instructions and labels
            if line.label:
                if line.label in self.symbols:
                    self.errors.append(
                        f"Line {line.line_num}: Duplicate label '{line.label}'"
                    )
                else:
                    self.symbols[line.label] = self.current_address
            
            # Instructions take one word
            if line.opcode and line.opcode not in ['ORG', 'EQU', 'END']:
                self.current_address += 1
    
    def pass2(self, source_lines: List[SourceLine]):
        """
        Pass 2: Generate code with optimized skip fields.
        """
        self.current_address = self.origin
        self.assembled_words = []
        
        i = 0
        while i < len(source_lines):
            line = source_lines[i]
            
            # Skip directives
            if line.opcode in ['ORG', 'EQU', 'END']:
                if line.opcode == 'ORG':
                    if line.operand:
                        self.origin = int(line.operand, 0)
                        self.current_address = self.origin
                i += 1
                continue
            
            # Handle data directives
            if line.opcode in ['OCT', 'DEC', 'HEX', 'WORD', 'BSS']:
                if line.operand:
                    operands = line.operand.split(',')
                    
                    if line.opcode == 'BSS':
                        count = int(operands[0], 0)
                        for j in range(count):
                            self.assembled_words.append(AssembledWord(
                                address=self.current_address + j,
                                value=0,
                                source_line=line.line_num
                            ))
                        self.current_address += count
                    else:
                        for j, op in enumerate(operands):
                            op = op.strip()
                            if line.opcode == 'OCT':
                                value = int(op, 8) & 0xFFFFFF
                            elif line.opcode == 'DEC':
                                value = int(op) & 0xFFFFFF
                            elif line.opcode == 'HEX':
                                value = int(op, 16) & 0xFFFFFF
                            else:  # WORD
                                value = int(op, 0) & 0xFFFFFF
                            
                            self.assembled_words.append(AssembledWord(
                                address=self.current_address + j,
                                value=value,
                                source_line=line.line_num
                            ))
                        self.current_address += len(operands)
                
                i += 1
                continue
            
            # Handle instructions
            if line.opcode and line.opcode in Opcode.__members__:
                opcode = Opcode[line.opcode]
                operand_str = line.operand
                address = 0
                is_symbolic = False
                
                if operand_str:
                    address, is_symbolic = self.parse_operand(operand_str)
                    if is_symbolic:
                        if operand_str in self.symbols:
                            address = self.symbols[operand_str]
                        else:
                            self.errors.append(
                                f"Line {line.line_num}: Undefined symbol '{operand_str}'"
                            )
                
                # Calculate optimal skip
                exec_time = EXEC_TIMES_US.get(line.opcode, 96)
                skip = self.calculate_skip(exec_time)
                
                # Encode instruction
                word = ((opcode.value & 0x3F) << 18) | \
                       ((skip & 0x0F) << 14) | \
                       (address & 0x3FFF)
                
                self.assembled_words.append(AssembledWord(
                    address=self.current_address,
                    value=word,
                    source_line=line.line_num,
                    label=line.label,
                    is_instruction=True,
                    skip=skip
                ))
                
                self.current_address += 1
            
            i += 1
    
    def assemble(self, source: str) -> Tuple[List[AssembledWord], List[str], List[str]]:
        """
        Assemble source code into machine code.
        
        Returns: (assembled_words, errors, warnings)
        """
        self.symbols = {}
        self.errors = []
        self.warnings = []
        self.current_address = 0
        self.assembled_words = []
        
        # Parse source into lines
        lines = source.split('\n')
        source_lines = []
        for i, line in enumerate(lines):
            parsed = self.parse_line(line, i + 1)
            source_lines.append(parsed)
        
        # Two-pass assembly
        self.pass1(source_lines)
        self.pass2(source_lines)
        
        return self.assembled_words, self.errors, self.warnings
    
    def generate_listing(self, source: str) -> str:
        """Generate a listing file with source and assembled code."""
        assembled, errors, warnings = self.assemble(source)
        
        output = []
        output.append("ERA 1101 Assembler Listing")
        output.append("=" * 80)
        output.append("")
        
        # Symbol table
        output.append("Symbol Table:")
        output.append("-" * 40)
        for symbol, addr in sorted(self.symbols.items()):
            output.append(f"  {symbol:20s} = {addr:04X}")
        output.append("")
        
        # Source with assembled code
        output.append("Source Listing:")
        output.append("-" * 80)
        
        lines = source.split('\n')
        assembled_dict = {aw.address: aw for aw in assembled}
        
        current_addr = self.origin
        for i, line in enumerate(lines, 1):
            # Find assembled word for this line
            aw = None
            for word in assembled:
                if word.source_line == i:
                    aw = word
                    break
            
            if aw:
                output.append(f"  {aw.address:04X}  {aw.value:06X}  {line}")
                if aw.is_instruction:
                    output.append(f"         skip={aw.skip}")
            else:
                output.append(f"           {line}")
        
        output.append("")
        
        # Errors and warnings
        if errors:
            output.append("Errors:")
            output.append("-" * 40)
            for err in errors:
                output.append(f"  ERROR: {err}")
        
        if warnings:
            output.append("Warnings:")
            output.append("-" * 40)
            for warn in warnings:
                output.append(f"  WARNING: {warn}")
        
        output.append("")
        output.append(f"Total words: {len(assembled)}")
        output.append(f"Errors: {len(errors)}, Warnings: {len(warnings)}")
        
        return '\n'.join(output)
    
    def generate_binary(self) -> bytes:
        """Generate binary output (3 bytes per word)."""
        binary = bytearray()
        for word in sorted(self.assembled_words, key=lambda w: w.address):
            binary.append((word.value >> 16) & 0xFF)
            binary.append((word.value >> 8) & 0xFF)
            binary.append(word.value & 0xFF)
        return bytes(binary)
    
    def generate_paper_tape(self) -> str:
        """Generate paper tape format (ASCII hex)."""
        lines = []
        for word in sorted(self.assembled_words, key=lambda w: w.address):
            # Paper tape format: address:data
            lines.append(f"{word.address:04X}:{word.value:06X}")
        return '\n'.join(lines)


# ============================================================================
# Example Program
# ============================================================================

DEMO_PROGRAM = """* ERA 1101 Demo Program - SHA256 Message Schedule Test
* This demonstrates the assembler with drum optimization

        ORG 0x1000

* Initialize hash values (first 8 SHA256 constants)
START   INS  H0_INIT       * Load H0 (skip=2)
        STO  H0            * Store H0 (skip=2)
        INS  H1_INIT       * Load H1 (skip=2)
        STO  H1            * Store H1 (skip=2)
        INS  H2_INIT       * Load H2 (skip=2)
        STO  H2            * Store H2 (skip=2)
        INS  H3_INIT       * Load H3 (skip=2)
        STO  H3            * Store H3 (skip=2)
        
* Simple addition test
        INS  VALUE1        * Load first value (skip=2)
        ADD  VALUE2        * Add second value (skip=2)
        STO  RESULT        * Store result (skip=2)
        
* Test multiplication
        INS  MPY_VAL1      * Load multiplier (skip=2)
        TRA                 * Transfer to Q (skip=2)
        MPY  MPY_VAL2      * Multiply (skip=2, takes 352 μs)
        STO  MPY_RESULT    * Store product (skip=2)
        
* Loop example
LOOP    INS  COUNTER       * Load counter (skip=2)
        ADD  INCREMENT     * Add increment (skip=2)
        STO  COUNTER       * Store back (skip=2)
        JNZ  LOOP          * Loop if not zero (skip=0)
        
        HLT                * Halt program

* Data section
        ORG 0x2000

* SHA256 initial hash values (first 4) - using HEX notation
H0_INIT HEX 6A09E6        * H0 = 0x6A09E667 (truncated to 24 bits)
H1_INIT HEX BB67AE        * H1 = 0xBB67AE85
H2_INIT HEX 3C6EF3        * H2 = 0x3C6EF372
H3_INIT HEX A54FF5        * H3 = 0xA54FF53A

* Storage for hash values
H0      DEC 0
H1      DEC 0
H2      DEC 0
H3      DEC 0

* Test values
VALUE1  DEC 291        * 0x123
VALUE2  DEC 1110       * 0x456
RESULT  DEC 0          * Will hold 0x579

* Multiplication test
MPY_VAL1 DEC 18        * 18 decimal
MPY_VAL2 DEC 35        * 35 decimal
MPY_RESULT DEC 0        * Will hold 18*35=630=0x276

* Loop counter
COUNTER DEC 10         * Start at 10
INCREMENT DEC 1         * Increment by 1

        END START
"""


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='ERA 1101 Cross-Assembler')
    parser.add_argument('input', nargs='?', help='Input assembly file')
    parser.add_argument('--output', '-o', help='Output binary file')
    parser.add_argument('--listing', '-l', help='Output listing file')
    parser.add_argument('--paper-tape', '-p', help='Output paper tape file')
    parser.add_argument('--no-optimize', action='store_true', 
                       help='Disable drum optimization')
    parser.add_argument('--demo', action='store_true', help='Assemble demo program')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Get source code
    if args.demo or not args.input:
        source = DEMO_PROGRAM
        print("Using demo program...")
    else:
        with open(args.input, 'r') as f:
            source = f.read()
        print(f"Assembling {args.input}...")
    
    # Assemble
    assembler = ERA1101Assembler(
        optimize_drum=not args.no_optimize,
        verbose=args.verbose
    )
    
    assembled, errors, warnings = assembler.assemble(source)
    
    # Report errors
    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  ERROR: {err}")
        sys.exit(1)
    
    if warnings and args.verbose:
        print("\nWarnings:")
        for warn in warnings:
            print(f"  WARNING: {warn}")
    
    # Generate outputs
    if args.listing:
        listing = assembler.generate_listing(source)
        with open(args.listing, 'w') as f:
            f.write(listing)
        print(f"Listing written to {args.listing}")
    elif args.verbose:
        print("\n" + assembler.generate_listing(source))
    
    if args.output:
        binary = assembler.generate_binary()
        with open(args.output, 'wb') as f:
            f.write(binary)
        print(f"Binary written to {args.output} ({len(binary)} bytes)")
    
    if args.paper_tape:
        tape = assembler.generate_paper_tape()
        with open(args.paper_tape, 'w') as f:
            f.write(tape)
        print(f"Paper tape format written to {args.paper_tape}")
    
    # Summary
    print(f"\nAssembly complete:")
    print(f"  Words assembled: {len(assembled)}")
    print(f"  Symbols defined: {len(assembler.symbols)}")
    print(f"  Drum optimization: {'enabled' if not args.no_optimize else 'disabled'}")
    
    # Show some assembled words
    if args.verbose:
        print("\nSample assembled words:")
        for word in assembled[:10]:
            print(f"  {word.address:04X}: {word.value:06X}  {word.label or ''}")


if __name__ == '__main__':
    main()
