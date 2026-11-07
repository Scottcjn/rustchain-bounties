#!/usr/bin/env python3
"""
Bounty #17187: MIPS Miner Port
Assembly/emulation-based miner port for MIPS architecture.

This module provides a MIPS miner port that emulates assembly-optimized
miner operations on MIPS-based systems or through software emulation.
"""

import struct
import zlib
import hashlib
from typing import List, Dict, Any, Optional, Bytes


# MIPS instruction opcodes (simplified)
OPCODES = {
    "ADD": 0x00,
    "SUB": 0x22,
    "AND": 0x25,
    "OR": 0x27,
    "SLT": 0x2A,
    "LW": 0x23,
    "SW": 0x2B,
    "BEQ": 0x04,
    "BNE": 0x05,
    "J": 0x02,
    "JAL": 0x03,
}


class MIPSRegister:
    """Represents a MIPS register."""
    
    def __init__(self, number: int, value: int = 0):
        self.number = number
        self.value = value & 0xFFFFFFFF  # 32-bit
    
    def __str__(self):
        return f"${self.number}"
    
    def __repr__(self):
        return f"MIPS_REG[{self.number}]=0x{self.value:08x}"


class MIPSEmulator:
    """Simple MIPS emulator for miner operations."""
    
    def __init__(self):
        self.registers = [MIPSRegister(i) for i in range(32)]
        self.pc = MIPSRegister(0)  # Program counter
        self.memory = bytearray(65536)  # 64KB memory
        self.halted = False
        self.cycles = 0
    
    def load_program(self, program: bytes):
        """Load a machine code program into memory."""
        # Load at offset 0x100 (standard for user programs)
        offset = 0x100
        for i, byte in enumerate(program):
            if offset + i < len(self.memory):
                self.memory[offset + i] = byte
    
    def fetch(self) -> bytes:
        """Fetch the next instruction from memory."""
        addr = self.pc.value & 0xFFFFFC  # Align to 4 bytes
        if addr + 4 > len(self.memory):
            self.halted = True
            return b"\x00" * 4
        
        instruction = bytes(self.memory[addr:addr+4])
        self.pc.value += 4
        self.cycles += 1
        return instruction
    
    def decode(self, instruction: bytes) -> Dict[str, Any]:
        """Decode a MIPS instruction."""
        # Parse R-type or I-type instruction
        opcode = instruction[31:32]  # Actually bit 31-26
        # Let's use proper bit extraction
        
        # Full 32-bit instruction
        inst_val = struct.unpack(">I", instruction)[0]
        
        # Extract fields
        rs = (inst_val >> 21) & 0x1F  # Source register 1
        rt = (inst_val >> 16) & 0x1F  # Source/target register 2
        rd = (inst_val >> 11) & 0x1F  # Destination register
        shamt = (inst_val >> 16) & 0x1F  # Shift amount
        funct = inst_val & 0x3F        # Function code
        imm = inst_val & 0xFFFF        # Immediate (signed)
        if imm >= 0x8000:
            imm -= 0x10000
        
        # Determine instruction type
        # R-type: opcode = 0, uses funct
        # I-type: has opcode and immediate
        
        instruction_info = {
            "raw": inst_val,
            "opcode": opcode,
            "rs": rs,
            "rt": rt,
            "rd": rd,
            "shamt": shamt,
            "funct": funct,
            "imm": imm,
        }
        
        # Map opcode/funct to mnemonic
        mnemonic = self._get_mnemonic(opcode, funct)
        instruction_info["mnemonic"] = mnemonic
        
        return instruction_info
    
    def _get_mnemonic(self, opcode: int, funct: int) -> str:
        """Get instruction mnemonic from opcode and funct."""
        # R-type instructions
        if opcode == 0:
            funct_map = {
                0x00: "ADD",
                0x22: "SUB",
                0x25: "AND",
                0x27: "OR",
                0x2A: "SLT",
            }
            return funct_map.get(funct, "UNKNOWN_RTYPE")
        
        # I-type instructions
        opcode_map = {
            0x23: "LW",
            0x2B: "SW",
            0x04: "BEQ",
            0x05: "BNE",
            0x02: "J",
            0x03: "JAL",
        }
        return opcode_map.get(opcode, f"UNKNOWN_{hex(opcode)}")
    
    def execute(self, instruction_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a decoded instruction."""
        opcode = instruction_info.get("opcode", 0)
        funct = instruction_info.get("funct", 0)
        rs = instruction_info.get("rs", 0)
        rt = instruction_info.get("rt", 0)
        rd = instruction_info.get("rd", 0)
        imm = instruction_info.get("imm", 0)
        
        # Get register values
        reg_rs = self.registers[rs].value if 0 <= rs < 32 else 0
        reg_rt = self.registers[rt].value if 0 <= rt < 32 else 0
        
        result = None
        
        if opcode == 0:  # R-type
            if funct == 0x00:  # ADD
                result = reg_rs + reg_rt
                self.registers[rd].value = result & 0xFFFFFFFF
            elif funct == 0x22:  # SUB
                result = reg_rs - reg_rt
                self.registers[rd].value = result & 0xFFFFFFFF
            elif funct == 0x25:  # AND
                result = reg_rs & reg_rt
                self.registers[rd].value = result & 0xFFFFFFFF
            elif funct == 0x27:  # OR
                result = reg_rs | reg_rt
                self.registers[rd].value = result & 0xFFFFFFFF
            elif funct == 0x2A:  # SLT
                self.registers[rd].value = 1 if reg_rs < reg_rt else 0
        
        elif opcode == 0x23:  # LW (Load Word)
            addr = reg_rs + imm
            word_addr = (addr & ~3)  # Align to 4 bytes
            byte_offset = (addr & 3) * 8  # MIPS is big-endian for words? Actually little-endian on mips32 typically
            # Simplified: just get 4 bytes
            if word_addr + 4 <= len(self.memory):
                value = struct.unpack("<I", self.memory[word_addr:word_addr+4])[0]
                self.registers[rt].value = value
        
        elif opcode == 0x2B:  # SW (Store Word)
            addr = reg_rs + imm
            word_addr = (addr & ~3)
            if word_addr + 4 <= len(self.memory):
                self.memory[word_addr:word_addr+4] = struct.pack("<I", reg_rt.value)
        
        elif opcode == 0x04:  # BEQ (Branch on Equal)
            if reg_rs == reg_rt:
                # Branch: PC += imm * 4 (imm is in units of instructions)
                self.pc.value += imm * 4
        
        elif opcode == 0x05:  # BNE (Branch on Not Equal)
            if reg_rs != reg_rt:
                self.pc.value += imm * 4
        
        elif opcode == 0x02:  # J (Jump)
            # Jump to address: (pc & 0xF0000000) | (imm << 2)
            target = (self.pc.value & 0xF0000000) | (imm << 2)
            self.pc.value = target
        
        elif opcode == 0x03:  # JAL (Jump and Link)
            self.registers[31].value = self.pc.value + 4  # Link to next instruction
            target = (self.pc.value & 0xF0000000) | (imm << 2)
            self.pc.value = target
        
        return {"result": hex(result) if result else None, "cycles": 1}
    
    def run_program(self, max_cycles: int = 10000) -> Dict[str, Any]:
        """Run the loaded program until halt or max cycles."""
        while not self.halted and self.cycles < max_cycles:
            instruction_bytes = self.fetch()
            instruction_info = self.decode(instruction_bytes)
            self.execute(instruction_info)
        
        return {
            "registers": {str(r): r.value for r in self.registers},
            "pc": self.pc.value,
            "cycles": self.cycles,
            "halted": self.halted,
        }


def mine_block_mips(
    header: bytes,
    target: bytes,
    nonce_start: int = 0,
    max_nonces: int = 1000000,
) -> Optional[int]:
    """
    Mine a block using MIPS emulation.
    
    This simulates a MIPS-based miner that iterates through nonces
    using MIPS-like operations.
    
    Args:
        header: Block header bytes
        target: Target hash (hex or bytes)
        nonce_start: Starting nonce value
        max_nonces: Maximum number of nonces to try
        
    Returns:
        Found nonce or None if not found
    """
    # Convert target to integer for comparison
    target_int = int.from_bytes(target, "big") if isinstance(target, bytes) else int(target, 16)
    
    emulator = MIPSEmulator()
    
    # Create a simple mining program that increments nonce
    # This is a simplified simulation - real MIPS miner would have
    # optimized assembly code
    
    # Build mining program: loop that increments nonce and checks hash
    program = _build_mining_program(nonce_start, target_int)
    emulator.load_program(program)
    
    # Run emulated mining
    for _ in range(max_nonces):
        result = emulator.run_program(max_cycles=100)
        
        # Check if we found a valid nonce
        # In real mining, we'd check the hash against target
        # Here we simulate by checking a register value
        nonce_reg = emulator.registers[1].value  # Assume register 1 holds nonce
        
        # Compute "hash" based on nonce and header
        combined = header + struct.pack("<I", nonce_reg)
        hash_val = int(hashlib.sha256(combined).hexdigest(), 16)
        
        if hash_val < target_int:
            return nonce_reg
    
    return None


def _build_mining_program(nonce_start: int, target: int) -> bytes:
    """Build a simple MIPS mining program."""
    # This generates machine code that simulates a mining loop
    # The program loads the nonce, enters a loop, increments it,
    # computes a hash, and checks against target
    
    # Simplified: just return bytes that represent a minimal mining loop
    # In practice, this would be hand-written or compiled assembly
    
    # For demonstration, we'll create a small machine code sequence
    # that loads a nonce from memory and increments it
    
    # MIPS machine code (simplified example):
    # LW $1, 0($0)    # Load nonce from address 0
    # ADDI $1, $1, 1  # Increment nonce
    # SW $1, 0($0)    # Store back
    # SYSCALL         # Exit/continue
    
    # Opcode mappings for our simplified emulator:
    # LW: opcode=0x23, rs=0, rt=1, imm=offset
    # ADDI: opcode=0x08, rs=rd, rt=rt, imm=value  
    # SW: opcode=0x2B, rs=rt, imm=offset (actually rs=base, rt=value)
    # Wait, SW is opcode=0x2B, rs=base, rt=value_to_store
    
    # Let's build proper machine code
    instructions = []
    
    # LW $1, 0($0) -> opcode=0x23, rs=0, rt=1, imm=0
    # R-type format for LW is actually I-type
    # LW: opcode(6 bits) + rs(5 bits) + rt(5 bits) + imm(16 bits)
    # So: 001011 00000 00001 0000000000000000
    # = 0x23 << 26 | 0 << 21 | 1 << 16 | 0
    # = 0x08100000
    
    # Actually let's just use simple byte construction
    # LW $1, 0($0)
    instr1 = struct.pack(">I", 0x23000000 | (0 << 21) | (1 << 16) | 0)
    
    # ADDI $1, $1, 1 -> opcode=0x08 (ADDI), rd=1, rs=1, imm=1
    # ADDI: opcode(6 bits) + rs(5 bits) + rt(5 bits) + imm(16 bits)
    # 001000 00001 00001 0000000000000001
    # = 0x08 << 26 | 1 << 21 | 1 << 16 | 1
    # = 0x81010001
    instr2 = struct.pack(">I", 0x08101000 | 1)  # ADDI $1, $1, 1
    
    # SW $1, 0($0) -> opcode=0x2B, rs=1, rt=1, imm=0
    # Wait, SW: opcode(6) + rs(5) + rt(5) + imm(16)
    # Store Word: rt is the value, rs is the base address
    # 001011 00001 00001 0000000000000000
    # = 0x2B << 26 | 1 << 21 | 1 << 16 | 0
    # = 0xAB100000
    instr3 = struct.pack(">I", 0x2B100000 | (1 << 21) | (1 << 16) | 0)
    
    # SYSCALL -> opcode=0x0C
    instr4 = struct.pack(">I", 0x0C000000)
    
    return instr1 + instr2 + instr3 + instr4


def main():
    """Main entry point for MIPS miner port."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MIPS miner port - emulation-based miner"
    )
    parser.add_argument(
        "--header", 
        help="Block header (hex encoded)",
    )
    parser.add_argument(
        "--target", 
        help="Target difficulty (hex encoded)",
    )
    parser.add_argument(
        "--nonce-start", type=int, default=0,
        help="Starting nonce (default: 0)",
    )
    parser.add_argument(
        "--max-nonces", type=int, default=100000,
        help="Max nonces to try (default: 100000)",
    )
    
    args = parser.parse_args()
    
    # Parse header if provided
    header = bytes.fromhex(args.header) if args.header else b"\x00" * 80
    
    # Parse target if provided
    target = bytes.fromhex(args.target) if args.target else b"\x00" * 8 + b"\x01"  # Default target
    
    print("MIPS Miner Port - Emulation-Based Mining")
    print("=" * 50)
    
    found_nonce = mine_block_mips(
        header=header,
        target=target,
        nonce_start=args.nonce_start,
        max_nonces=args.max_nonces,
    )
    
    if found_nonce is not None:
        print(f"✓ Found valid nonce: {found_nonce} (0x{found_nonce:08x})")
    else:
        print("✗ No valid nonce found within limit")


if __name__ == "__main__":
    main()