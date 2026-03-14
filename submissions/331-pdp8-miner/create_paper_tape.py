#!/usr/bin/env python3
"""
Create Intel HEX format paper tape from assembled binary
For PDP-8 RustChain Miner
"""

import sys

def create_hex_file(binary_data, output_file):
    """Create Intel HEX format file"""
    with open(output_file, 'w') as f:
        address = 0x0200  # Start address
        
        # Write records
        for i in range(0, len(binary_data), 16):
            chunk = binary_data[i:i+16]
            if len(chunk) == 0:
                break
            
            # Record length
            length = len(chunk)
            
            # Calculate checksum
            checksum = length + (address & 0xFF) + ((address >> 8) & 0xFF)
            for byte in chunk:
                checksum += byte
            checksum = (-checksum) & 0xFF
            
            # Write record
            f.write(f":{length:02X}{address:04X}00")
            for byte in chunk:
                f.write(f"{byte:02X}")
            f.write(f"{checksum:02X}\n")
            
            address += length
        
        # End of file record
        f.write(":00000001FF\n")

def create_simple_binary(output_file):
    """Create a simple binary program for testing"""
    # Simple PDP-8 program that:
    # 1. Clears AC
    # 2. Increments AC
    # 3. Stores to memory
    # 4. Halts
    
    program = [
        0o7200,  # CLA - Clear AC
        0o7001,  # IAC - Increment AC
        0o3100,  # DCA 100 - Store to address 100
        0o7200,  # CLA
        0o7001,  # IAC
        0o7001,  # IAC
        0o3101,  # DCA 101
        0o7402,  # HLT - Halt
    ]
    
    with open(output_file, 'wb') as f:
        for word in program:
            # PDP-8 is little-endian 12-bit
            f.write(bytes([word & 0xFF, (word >> 8) & 0x0F]))

if __name__ == '__main__':
    # Create simple binary for testing
    create_simple_binary('pdp8_miner.bin')
    print("Created pdp8_miner.bin (simple test program)")
    
    # Note: Full assembly requires PAL-III assembler
    print("\nTo assemble full program:")
    print("  1. Install PAL-III: http://www.pdp8.net/pal.shtml")
    print("  2. Run: pal3 pdp8_miner.pal")
    print("  3. This will create pdp8_miner.bin")
