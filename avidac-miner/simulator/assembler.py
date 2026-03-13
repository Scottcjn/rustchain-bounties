"""
AVIDAC Cross-Assembler

Assembles AVIDAC/IAS assembly language into machine code.

Assembly syntax:
    LABEL:  OP  ADDRESS    ; Comment
    
Directives:
    ORG address     - Set origin (load address)
    EQU value       - Define constant
    DEC value       - Define decimal data
    HEX value       - Define hexadecimal data
    RES count       - Reserve words
    END [label]     - End of source

Example:
        ORG 0x000
START:  LD  ZERO        ; Clear accumulator
        ST  SUM
LOOP:   ADD ONE
        ST  TEMP
        SUB LIMIT
        JN  DONE
        JMP LOOP
DONE:   STOP
        ORG 0x100
ZERO:   DEC 0
ONE:    DEC 1
SUM:    DEC 0
TEMP:   RES 1
LIMIT:  DEC 100
        END START
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path

try:
    from .arithmetic import MASK_40, MASK_20, mask_40bit
except ImportError:
    from arithmetic import MASK_40, MASK_20, mask_40bit


@dataclass
class SourceLine:
    """Represents one line of assembly source."""
    line_num: int
    original: str
    label: Optional[str] = None
    opcode: Optional[str] = None
    operand: Optional[str] = None
    comment: Optional[str] = None
    is_directive: bool = False
    is_data: bool = False


@dataclass
class AssembledWord:
    """Represents one assembled 40-bit word."""
    address: int
    value: int
    source_line: Optional[int] = None
    label: Optional[str] = None


class AVIDACAssembler:
    """
    AVIDAC/IAS Cross-Assembler.
    
    Converts assembly language source into 40-bit machine code words.
    Two-pass assembler:
    - Pass 1: Collect labels and calculate addresses
    - Pass 2: Generate machine code
    """
    
    # Opcode mnemonic to binary encoding
    OPCODES = {
        'STOP': 0x0, 'ADD': 0x1, 'SUB': 0x2, 'MUL': 0x3,
        'DIV': 0x4, 'AND': 0x5, 'OR': 0x6, 'JMP': 0x7,
        'JZ': 0x8, 'JN': 0x9, 'LD': 0xA, 'ST': 0xB,
        'IN': 0xC, 'OUT': 0xD, 'RSH': 0xE, 'LSH': 0xF
    }
    
    # Directives
    DIRECTIVES = {'ORG', 'EQU', 'DEC', 'HEX', 'RES', 'END', 'DW', 'DC'}
    
    def __init__(self):
        """Initialize assembler."""
        self.symbols: Dict[str, int] = {}
        self.memory: List[int] = [0] * 1024
        self.location = 0
        self.source_lines: List[SourceLine] = []
        self.assembled_words: List[AssembledWord] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.entry_point: Optional[int] = None
    
    def reset(self) -> None:
        """Reset assembler state."""
        self.symbols = {}
        self.memory = [0] * 1024
        self.location = 0
        self.source_lines = []
        self.assembled_words = []
        self.errors = []
        self.warnings = []
        self.entry_point = None
    
    def parse_line(self, line_num: int, line: str) -> SourceLine:
        """
        Parse one line of assembly source.
        
        Format: [LABEL:] [OP [OPERAND]] [; COMMENT]
        """
        original = line
        source_line = SourceLine(line_num=line_num, original=line)
        
        # Remove comment
        if ';' in line:
            line, comment = line.split(';', 1)
            source_line.comment = comment.strip()
            line = line.strip()
        
        if not line:
            return source_line
        
        # Parse label
        if ':' in line:
            label_part, rest = line.split(':', 1)
            source_line.label = label_part.strip()
            line = rest.strip()
        
        if not line:
            return source_line
        
        # Parse opcode/directive and operand
        parts = line.split(None, 1)
        opcode = parts[0].upper()
        operand = parts[1].strip() if len(parts) > 1 else None
        
        source_line.opcode = opcode
        source_line.operand = operand
        source_line.is_directive = opcode in self.DIRECTIVES
        source_line.is_data = opcode in {'DEC', 'HEX', 'RES', 'DW', 'DC'}
        
        return source_line
    
    def parse_source(self, source: str) -> None:
        """
        Parse complete source file.
        
        Args:
            source: Assembly source code
        """
        lines = source.split('\n')
        
        for i, line in enumerate(lines):
            line_num = i + 1
            source_line = self.parse_line(line_num, line)
            self.source_lines.append(source_line)
    
    def first_pass(self) -> None:
        """
        First pass: collect labels and calculate addresses.
        """
        self.location = 0
        
        for source_line in self.source_lines:
            # Handle label
            if source_line.label:
                if source_line.label in self.symbols:
                    self.errors.append(
                        f"Line {source_line.line_num}: Duplicate label '{source_line.label}'"
                    )
                else:
                    self.symbols[source_line.label] = self.location
            
            # Handle directives that affect location
            if source_line.is_directive:
                if source_line.opcode == 'ORG':
                    self.location = self._parse_value(source_line.operand)
                elif source_line.opcode == 'RES':
                    count = self._parse_value(source_line.operand)
                    self.location += count
                elif source_line.opcode in {'DEC', 'HEX', 'DW', 'DC'}:
                    self.location += 1
                elif source_line.opcode == 'END':
                    if source_line.operand:
                        self.entry_point = source_line.operand
                    break
            elif source_line.opcode:
                # Regular instruction takes one word
                self.location += 1
    
    def second_pass(self) -> None:
        """
        Second pass: generate machine code.
        """
        self.location = 0
        
        for source_line in self.source_lines:
            # Skip empty lines
            if not source_line.opcode:
                continue
            
            # Handle directives
            if source_line.is_directive:
                if source_line.opcode == 'ORG':
                    self.location = self._parse_value(source_line.operand)
                elif source_line.opcode == 'EQU':
                    # Symbol already defined in first pass
                    pass
                elif source_line.opcode == 'DEC':
                    value = self._parse_value(source_line.operand)
                    self._write_word(mask_40bit(value), source_line)
                elif source_line.opcode == 'HEX':
                    value = int(source_line.operand.replace('0x', '').replace('H', ''), 16)
                    self._write_word(mask_40bit(value), source_line)
                elif source_line.opcode == 'RES':
                    count = self._parse_value(source_line.operand)
                    for _ in range(count):
                        self._write_word(0, source_line)
                elif source_line.opcode == 'END':
                    break
                elif source_line.opcode in {'DW', 'DC'}:
                    value = self._parse_value(source_line.operand)
                    self._write_word(mask_40bit(value), source_line)
                continue
            
            # Handle instructions
            if source_line.opcode in self.OPCODES:
                opcode = self.OPCODES[source_line.opcode]
                address = self._resolve_address(source_line.operand)
                instruction = self._encode_instruction(opcode, address)
                self._write_word(instruction, source_line)
            else:
                self.errors.append(
                    f"Line {source_line.line_num}: Unknown opcode '{source_line.opcode}'"
                )
    
    def _parse_value(self, operand: str) -> int:
        """Parse numeric value (decimal, hex, or symbol)."""
        if operand is None:
            return 0
        
        operand = operand.strip()
        
        # Check for hex notation
        if operand.startswith('0x') or operand.startswith('0X'):
            return int(operand, 16)
        elif operand.endswith('H') or operand.endswith('h'):
            return int(operand[:-1], 16)
        
        # Check for binary notation
        if operand.startswith('0b') or operand.startswith('0B'):
            return int(operand, 2)
        
        # Check for symbol
        if operand in self.symbols:
            return self.symbols[operand]
        
        # Try decimal
        try:
            return int(operand)
        except ValueError:
            self.errors.append(f"Invalid operand: {operand}")
            return 0
    
    def _resolve_address(self, operand: str) -> int:
        """Resolve operand to memory address."""
        if operand is None:
            return 0
        return self._parse_value(operand) & 0x3FF  # 10-bit address
    
    def _encode_instruction(self, opcode: int, address: int) -> int:
        """
        Encode IAS instruction (20 bits).
        
        Format:
        - Bits 19-16: Opcode (4 bits)
        - Bits 15-10: Unused (6 bits)
        - Bits 9-0: Address (10 bits)
        """
        instruction = ((opcode & 0xF) << 16) | (address & 0x3FF)
        return instruction & MASK_20
    
    def _write_word(self, value: int, source_line: SourceLine) -> None:
        """Write word to memory at current location."""
        if self.location >= 1024:
            self.errors.append(
                f"Line {source_line.line_num}: Memory overflow at address {self.location}"
            )
            return
        
        self.memory[self.location] = mask_40bit(value)
        
        self.assembled_words.append(AssembledWord(
            address=self.location,
            value=value,
            source_line=source_line.line_num,
            label=source_line.label
        ))
        
        self.location += 1
    
    def assemble(self, source: str) -> Tuple[List[int], bool]:
        """
        Assemble source code.
        
        Args:
            source: Assembly source code
        
        Returns:
            (memory_image, success) tuple
        """
        self.reset()
        
        # Parse source
        self.parse_source(source)
        
        # First pass: collect labels
        self.first_pass()
        
        # Second pass: generate code
        self.second_pass()
        
        success = len(self.errors) == 0
        return self.memory, success
    
    def assemble_file(self, filepath: str) -> Tuple[List[int], bool]:
        """
        Assemble source file.
        
        Args:
            filepath: Path to assembly source file
        
        Returns:
            (memory_image, success) tuple
        """
        filepath = Path(filepath)
        with open(filepath, 'r') as f:
            source = f.read()
        return self.assemble(source)
    
    def save_binary(self, filepath: str, start: int = 0, length: int = None) -> None:
        """
        Save assembled code as binary file.
        
        Args:
            filepath: Output file path
            start: Starting address
            length: Number of words to save (default: all)
        """
        filepath = Path(filepath)
        
        if length is None:
            length = self.location - start
        
        with open(filepath, 'wb') as f:
            for i in range(length):
                addr = start + i
                if addr < len(self.memory):
                    # Write as 5 bytes (40 bits), big-endian
                    word = self.memory[addr]
                    for j in range(4, -1, -1):
                        byte = (word >> (j * 8)) & 0xFF
                        f.write(bytes([byte]))
    
    def save_hex(self, filepath: str, start: int = 0, length: int = None) -> None:
        """
        Save assembled code as Intel HEX file.
        
        Args:
            filepath: Output file path
            start: Starting address
            length: Number of words to save
        """
        filepath = Path(filepath)
        
        if length is None:
            length = self.location - start
        
        with open(filepath, 'w') as f:
            address = start
            while address < start + length:
                # Write up to 16 words per line
                count = min(16, start + length - address)
                
                # Build record
                record = f":{count:02X}{address:04X}00"
                for i in range(count):
                    word = self.memory[address + i]
                    # Write 5 bytes per 40-bit word
                    for j in range(4, -1, -1):
                        byte = (word >> (j * 8)) & 0xFF
                        record += f"{byte:02X}"
                
                # Calculate checksum
                checksum = count + (address >> 8) + (address & 0xFF)
                for i in range(count * 5):
                    byte_str = record[4 + i*2:6 + i*2]
                    checksum += int(byte_str, 16)
                checksum = (-checksum) & 0xFF
                record += f"{checksum:02X}\n"
                
                f.write(record)
                address += count
    
    def get_symbol_table(self) -> Dict[str, int]:
        """Get symbol table."""
        return self.symbols.copy()
    
    def get_listing(self) -> str:
        """
        Generate assembly listing.
        
        Returns:
            Formatted listing string
        """
        lines = []
        lines.append("AVIDAC Assembly Listing")
        lines.append("=" * 80)
        lines.append("")
        
        # Create address-to-word mapping
        word_map = {w.address: w for w in self.assembled_words}
        
        for source_line in self.source_lines:
            line_num = source_line.line_num
            original = source_line.original
            
            # Find corresponding assembled word
            word = None
            for w in self.assembled_words:
                if w.source_line == line_num:
                    word = w
                    break
            
            if word:
                lines.append(f"{word.address:03X}  {word.value:010X}  {line_num:4}:  {original}")
            else:
                lines.append(f"{' ' * 14} {line_num:4}:  {original}")
        
        # Add errors and warnings
        if self.errors:
            lines.append("")
            lines.append("Errors:")
            for error in self.errors:
                lines.append(f"  ERROR: {error}")
        
        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  WARNING: {warning}")
        
        # Add symbol table
        lines.append("")
        lines.append("Symbol Table:")
        for symbol, address in sorted(self.symbols.items()):
            lines.append(f"  {symbol:20} = {address:03X} ({address})")
        
        return '\n'.join(lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get assembly statistics."""
        return {
            'source_lines': len(self.source_lines),
            'assembled_words': len(self.assembled_words),
            'symbols': len(self.symbols),
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'memory_used': self.location,
            'memory_free': 1024 - self.location,
            'entry_point': self.entry_point
        }


def assemble_file(input_path: str, output_path: str = None, listing_path: str = None) -> bool:
    """
    Assemble a file and optionally save output.
    
    Args:
        input_path: Input assembly file
        output_path: Output binary file (optional)
        listing_path: Listing file (optional)
    
    Returns:
        True if successful
    """
    assembler = AVIDACAssembler()
    memory, success = assembler.assemble_file(input_path)
    
    if success:
        if output_path:
            assembler.save_binary(output_path)
            print(f"Binary saved to {output_path}")
        
        if listing_path:
            with open(listing_path, 'w') as f:
                f.write(assembler.get_listing())
            print(f"Listing saved to {listing_path}")
        
        stats = assembler.get_statistics()
        print(f"Assembled {stats['assembled_words']} words, {stats['memory_used']}/1024 memory used")
    else:
        print("Assembly failed:")
        for error in assembler.errors:
            print(f"  {error}")
    
    return success


if __name__ == '__main__':
    # Test assembler with simple program
    test_source = """
; Test program - add numbers 1 to 10
        ORG 0x000
START:  LD  ZERO        ; Clear AC
        ST  SUM         ; SUM = 0
        LD  TEN         ; Load counter
        ST  COUNT       ; COUNT = 10
LOOP:   ADD ONE         ; AC = AC + 1
        ST  SUM         ; Save sum
        LD  COUNT       ; Load counter
        SUB ONE         ; Decrement
        ST  COUNT       ; Save counter
        JZ  DONE        ; If zero, done
        JMP LOOP        ; Otherwise continue
DONE:   STOP            ; Halt
        
        ORG 0x100
ZERO:   DEC 0
ONE:    DEC 1
TEN:    DEC 10
SUM:    DEC 0
COUNT:  DEC 0
        
        END START
"""
    
    assembler = AVIDACAssembler()
    memory, success = assembler.assemble(test_source)
    
    if success:
        print("Assembly successful!")
        print(assembler.get_listing())
        print("\nStatistics:")
        for key, value in assembler.get_statistics().items():
            print(f"  {key}: {value}")
    else:
        print("Assembly failed:")
        for error in assembler.errors:
            print(f"  {error}")
