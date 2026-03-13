#!/usr/bin/env python3
"""
Paper Tape Encoder for Harvard Mark II

Encodes assembly-like programs and data into 8-channel paper tape format.

Usage:
    python paper_tape_encoder.py input.asm output.pt
    python paper_tape_encoder.py --text "Hello World" output.pt

Author: RustChain Bounty Hunter
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import sys
import os
from typing import List

# Paper tape constants
SPROCKET_CHANNEL = 0x80  # Channel 8 (always punched)
DATA_CHANNELS_MASK = 0x7F  # Channels 1-7

class PaperTapeEncoder:
    """Encode programs and data to 8-channel paper tape format"""
    
    def __init__(self):
        self.tape_data: List[int] = []
    
    def encode_char(self, char: str) -> int:
        """Encode a single character to paper tape code"""
        ascii_val = ord(char) & 0x7F  # 7-bit ASCII
        return ascii_val | SPROCKET_CHANNEL
    
    def encode_string(self, text: str):
        """Encode a string to paper tape"""
        for char in text:
            if char != '\n':  # Skip newlines in source
                code = self.encode_char(char)
                self.tape_data.append(code)
    
    def encode_leader(self, length: int = 100):
        """Encode leader (blank tape at start)"""
        # Leader is all channels punched except data channels
        leader_code = SPROCKET_CHANNEL
        for _ in range(length):
            self.tape_data.append(leader_code)
    
    def encode_trailer(self, length: int = 50):
        """Encode trailer (blank tape at end)"""
        self.encode_leader(length)
    
    def encode_instruction(self, opcode: str, addr1: str = "", addr2: str = "", addr3: str = ""):
        """Encode a machine instruction"""
        # Format: OPCODE ADDR1 ADDR2 ADDR3 CHECKSUM
        instruction = f"{opcode}{addr1:>4}{addr2:>4}{addr3:>4}"
        self.encode_string(instruction)
    
    def encode_data(self, label: str, value: str):
        """Encode a data definition"""
        self.encode_string(f"{label}:{value}")
        self.encode_char('\n')
    
    def encode_wallet(self, wallet: str):
        """Encode wallet address as ASCII"""
        self.encode_string(f"WALLET:{wallet}")
        self.encode_char('\n')
    
    def save(self, filename: str):
        """Save tape data to file"""
        # Save as binary
        with open(filename, 'wb') as f:
            f.write(bytes(self.tape_data))
        print(f"Saved {len(self.tape_data)} characters to {filename}")
    
    def save_as_text(self, filename: str):
        """Save tape data as human-readable text"""
        with open(filename, 'w') as f:
            f.write("# Paper Tape Data (8-channel)\n")
            f.write(f"# Total characters: {len(self.tape_data)}\n")
            f.write("# Format: Position | Code (hex) | Code (bin) | Char\n")
            f.write("#" + "-" * 60 + "\n")
            
            for i, code in enumerate(self.tape_data):
                char_repr = chr(code & 0x7F) if 32 <= (code & 0x7F) <= 126 else '.'
                f.write(f"{i:4d} | 0x{code:02X} | {code:08b} | '{char_repr}'\n")
        
        print(f"Saved text representation to {filename}")
    
    def clear(self):
        """Clear tape data"""
        self.tape_data = []


def encode_miner_program():
    """Encode the main miner program"""
    encoder = PaperTapeEncoder()
    
    # Leader
    encoder.encode_leader(100)
    
    # Program header
    encoder.encode_string("HARVARD MARK II MINER\n")
    encoder.encode_string("RUSTCHAIN PROOF-OF-ANTIQUITY\n")
    encoder.encode_string("EPOCH: 1947\n")
    encoder.encode_string("\n")
    
    # Main program
    encoder.encode_string("; MINER PROGRAM\n")
    encoder.encode_instruction('L', '0', '', '')  # LOAD 0
    encoder.encode_string("\n")
    encoder.encode_instruction('A', '1', '', '')  # ADD 1
    encoder.encode_string("\n")
    encoder.encode_instruction('S', '100', '', '')  # STORE 100 (epoch counter)
    encoder.encode_string("\n")
    encoder.encode_instruction('P', '200', '', '')  # PRINT 200 (status message)
    encoder.encode_string("\n")
    encoder.encode_instruction('P', '300', '', '')  # PRINT 300 (wallet)
    encoder.encode_string("\n")
    encoder.encode_instruction('H', '', '', '')  # HALT
    encoder.encode_string("\n")
    
    # Data section
    encoder.encode_string("; DATA SECTION\n")
    encoder.encode_data("EPOCH", "0")
    encoder.encode_data("STATE", "1")
    encoder.encode_data("ONE", "1")
    encoder.encode_data("ZERO", "0")
    
    # Messages
    encoder.encode_string("STATUS_IDLE:IDLE\n")
    encoder.encode_string("STATUS_MINING:MINING\n")
    encoder.encode_string("STATUS_ATTEST:ATTESTED\n")
    
    # Wallet address
    encoder.encode_wallet("RTC4325af95d26d59c3ef025963656d22af638bb96b")
    
    # Attestation message
    encoder.encode_string("ATTESTATION:PROOF-OF-ANTIQUITY-VERIFIED\n")
    encoder.encode_string("ANTIQUITY:MUSEUM-TIER\n")
    encoder.encode_string("MULTIPLIER:2.5X\n")
    
    # Trailer
    encoder.encode_trailer(50)
    
    return encoder


def encode_from_text(text: str) -> PaperTapeEncoder:
    """Encode arbitrary text to paper tape"""
    encoder = PaperTapeEncoder()
    encoder.encode_leader(50)
    encoder.encode_string(text)
    encoder.encode_trailer(50)
    return encoder


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Harvard Mark II Paper Tape Encoder")
        print("=" * 50)
        print()
        print("Usage:")
        print("  python paper_tape_encoder.py <input_file> <output_file>")
        print("  python paper_tape_encoder.py --text \"text\" <output_file>")
        print("  python paper_tape_encoder.py --miner <output_file>")
        print()
        print("Options:")
        print("  --text    Encode the following text string")
        print("  --miner   Encode the built-in miner program")
        print("  --help    Show this help message")
        print()
        print("Examples:")
        print("  python paper_tape_encoder.py program.asm output.pt")
        print("  python paper_tape_encoder.py --text \"Hello World\" hello.pt")
        print("  python paper_tape_encoder.py --miner miner.pt")
        print()
        sys.exit(1)
    
    encoder = PaperTapeEncoder()
    output_file = None
    
    if sys.argv[1] == "--text":
        if len(sys.argv) < 4:
            print("Error: --text requires text and output file")
            sys.exit(1)
        text = sys.argv[2]
        output_file = sys.argv[3]
        encoder = encode_from_text(text)
    
    elif sys.argv[1] == "--miner":
        if len(sys.argv) < 3:
            print("Error: --miner requires output file")
            sys.exit(1)
        output_file = sys.argv[2]
        encoder = encode_miner_program()
    
    elif sys.argv[1] == "--help":
        main()
    
    else:
        # Encode from file
        if len(sys.argv) < 3:
            print("Error: Input and output files required")
            sys.exit(1)
        
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found")
            sys.exit(1)
        
        with open(input_file, 'r') as f:
            text = f.read()
        
        encoder = encode_from_text(text)
    
    # Save output
    encoder.save(output_file)
    
    # Also save human-readable version
    base_name = os.path.splitext(output_file)[0]
    encoder.save_as_text(f"{base_name}.txt")
    
    print(f"\nEncoding complete!")
    print(f"Binary output: {output_file}")
    print(f"Text output:   {base_name}.txt")


if __name__ == "__main__":
    main()
