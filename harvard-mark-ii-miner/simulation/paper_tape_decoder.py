#!/usr/bin/env python3
"""
Paper Tape Decoder for Harvard Mark II

Decodes 8-channel paper tape format back to readable text.

Usage:
    python paper_tape_decoder.py input.pt
    python paper_tape_decoder.py input.pt --verbose

Author: RustChain Bounty Hunter
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import sys
import os
from typing import List

# Paper tape constants
SPROCKET_CHANNEL = 0x80  # Channel 8 (always punched)
DATA_CHANNELS_MASK = 0x7F  # Channels 1-7

class PaperTapeDecoder:
    """Decode 8-channel paper tape format"""
    
    def __init__(self):
        self.codes: List[int] = []
    
    def load(self, filename: str):
        """Load paper tape from binary file"""
        with open(filename, 'rb') as f:
            self.codes = list(f.read())
        print(f"Loaded {len(self.codes)} characters from {filename}")
    
    def decode_char(self, code: int) -> str:
        """Decode a single paper tape code to character"""
        # Mask off sprocket channel
        ascii_val = code & DATA_CHANNELS_MASK
        
        # Check for valid ASCII
        if 32 <= ascii_val <= 126:
            return chr(ascii_val)
        elif ascii_val == 10:  # Newline
            return '\n'
        elif ascii_val == 13:  # Carriage return
            return '\r'
        elif ascii_val == 9:  # Tab
            return '\t'
        else:
            return '.'  # Non-printable
    
    def decode_all(self) -> str:
        """Decode entire tape to string"""
        return ''.join([self.decode_char(code) for code in self.codes])
    
    def decode_to_lines(self) -> List[str]:
        """Decode tape to lines of text"""
        text = self.decode_all()
        return text.split('\n')
    
    def analyze(self):
        """Analyze tape contents"""
        print("\n" + "=" * 60)
        print("PAPER TAPE ANALYSIS")
        print("=" * 60)
        print(f"Total characters: {len(self.codes)}")
        
        # Count character types
        printable = 0
        non_printable = 0
        sprocket_errors = 0
        
        for code in self.codes:
            if code & SPROCKET_CHANNEL:
                ascii_val = code & DATA_CHANNELS_MASK
                if 32 <= ascii_val <= 126 or ascii_val in [9, 10, 13]:
                    printable += 1
                else:
                    non_printable += 1
            else:
                sprocket_errors += 1
        
        print(f"Printable characters: {printable}")
        print(f"Non-printable: {non_printable}")
        print(f"Sprocket errors: {sprocket_errors}")
        
        # Check for wallet address
        text = self.decode_all()
        if "RTC" in text:
            print("\n✓ Found wallet address pattern (RTC...)")
        
        if "EPOCH" in text:
            print("✓ Found epoch counter")
        
        if "ATTEST" in text:
            print("✓ Found attestation data")
        
        if "HARVARD" in text or "MARK" in text:
            print("✓ Found Harvard Mark II header")
        
        print("=" * 60)
    
    def print_hex_dump(self, rows: int = 16):
        """Print hex dump of tape contents"""
        print("\nHEX DUMP:")
        print("-" * 60)
        
        for i in range(0, min(len(self.codes), rows * 16), 16):
            row = self.codes[i:i+16]
            hex_str = ' '.join([f"{b:02X}" for b in row])
            ascii_str = ''.join([self.decode_char(b) for b in row])
            print(f"{i:04X}  {hex_str:<48}  |{ascii_str}|")
        
        if len(self.codes) > rows * 16:
            print(f"... ({len(self.codes) - rows * 16} more bytes)")
        
        print("-" * 60)
    
    def extract_wallet(self) -> str:
        """Extract wallet address from tape"""
        text = self.decode_all()
        
        # Look for WALLET: pattern
        if "WALLET:" in text:
            start = text.find("WALLET:") + 7
            end = text.find('\n', start)
            if end == -1:
                end = len(text)
            return text[start:end].strip()
        
        # Look for RTC pattern
        import re
        match = re.search(r'RTC[a-zA-Z0-9]{40}', text)
        if match:
            return match.group(0)
        
        return "Not found"


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Harvard Mark II Paper Tape Decoder")
        print("=" * 50)
        print()
        print("Usage:")
        print("  python paper_tape_decoder.py <input_file> [options]")
        print()
        print("Options:")
        print("  --verbose   Show detailed analysis")
        print("  --hex       Show hex dump")
        print("  --wallet    Extract wallet address only")
        print("  --help      Show this help message")
        print()
        print("Examples:")
        print("  python paper_tape_decoder.py miner.pt")
        print("  python paper_tape_decoder.py miner.pt --verbose")
        print("  python paper_tape_decoder.py miner.pt --wallet")
        print()
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    decoder = PaperTapeDecoder()
    decoder.load(input_file)
    
    # Parse options
    show_verbose = "--verbose" in sys.argv
    show_hex = "--hex" in sys.argv
    show_wallet_only = "--wallet" in sys.argv
    
    if show_wallet_only:
        wallet = decoder.extract_wallet()
        print(f"\nWallet Address: {wallet}")
        sys.exit(0)
    
    # Print decoded content
    print("\n" + "=" * 60)
    print("DECODED PAPER TAPE CONTENTS")
    print("=" * 60)
    
    lines = decoder.decode_to_lines()
    for line in lines:
        if line.strip():  # Skip empty lines
            print(line)
    
    # Analysis
    if show_verbose:
        decoder.analyze()
    
    # Hex dump
    if show_hex:
        decoder.print_hex_dump()
    
    print("\n" + "=" * 60)
    print("DECODING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
