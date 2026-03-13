#!/usr/bin/env python3
"""
MANIAC II Miner Simulator
RustChain Proof-of-Antiquity for the 1957 Los Alamos hybrid computer

This simulator emulates the MANIAC II's unique architecture:
- 48-bit word size
- Magnetic-core memory (4,096 words)
- Williams tube supplementary memory (12,288 words)
- Hybrid vacuum tube + transistor logic
- Paper tape I/O

Author: RustChain Community
License: MIT
"""

import time
import random
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass


class MinerState(Enum):
    """Mining state machine states"""
    IDLE = 0
    MINING = 1
    ATTESTING = 2


@dataclass
class Attestation:
    """Mining attestation record"""
    epoch: int
    state: MinerState
    wallet: str
    operation_count: int
    timestamp: float
    checksum: int


class CoreMemory:
    """
    Magnetic-core memory emulation
    4,096 words × 48 bits
    Access time: 2.4 microseconds
    """
    
    def __init__(self, size: int = 4096, word_bits: int = 48):
        self.size = size
        self.word_bits = word_bits
        self.words = [0] * size
        self.access_time_us = 2.4
        self.read_count = 0
        self.write_count = 0
        
    def read(self, address: int) -> int:
        """Read a 48-bit word from core memory"""
        if address < 0 or address >= self.size:
            raise ValueError(f"Address {address} out of range (0-{self.size-1})")
        
        # Simulate access time (commented out for practical simulation)
        # time.sleep(self.access_time_us / 1_000_000)
        
        self.read_count += 1
        return self.words[address]
    
    def write(self, address: int, value: int):
        """Write a 48-bit word to core memory"""
        if address < 0 or address >= self.size:
            raise ValueError(f"Address {address} out of range (0-{self.size-1})")
        
        # Mask to 48 bits
        mask = (1 << self.word_bits) - 1
        value = value & mask
        
        # Simulate access time
        # time.sleep(self.access_time_us / 1_000_000)
        
        self.write_count += 1
        self.words[address] = value
    
    def dump(self, start: int = 0, count: int = 16):
        """Dump memory contents"""
        print(f"\n=== Core Memory Dump (words {start}-{start+count-1}) ===")
        for i in range(start, min(start + count, self.size)):
            value = self.words[i]
            print(f"  {i:04X}: {value:012X} ({value:048b})")


class WilliamsTubes:
    """
    Williams tube supplementary memory emulation
    12,288 words × 48 bits
    Access time: 15 microseconds
    CRT-based, requires refresh
    """
    
    def __init__(self, size: int = 12288, word_bits: int = 48):
        self.size = size
        self.word_bits = word_bits
        self.words = [0] * size
        self.access_time_us = 15.0
        self.refresh_count = 0
        
    def read(self, address: int) -> int:
        """Read from Williams tube memory"""
        if address < 0 or address >= self.size:
            raise ValueError(f"Address {address} out of range")
        
        # time.sleep(self.access_time_us / 1_000_000)
        return self.words[address]
    
    def write(self, address: int, value: int):
        """Write to Williams tube memory"""
        if address < 0 or address >= self.size:
            raise ValueError(f"Address {address} out of range")
        
        mask = (1 << self.word_bits) - 1
        value = value & mask
        
        # time.sleep(self.access_time_us / 1_000_000)
        self.words[address] = value
    
    def refresh(self):
        """Simulate CRT refresh cycle"""
        self.refresh_count += 1


class HybridCPU:
    """
    MANIAC II CPU emulation
    Hybrid vacuum tube + transistor design
    48-bit ALU
    """
    
    # Instruction opcodes
    OP_LOAD = 0
    OP_ADD = 1
    OP_STORE = 2
    OP_SUB = 3
    OP_MUL = 4
    OP_DIV = 5
    OP_PRINT = 6
    OP_JUMP = 7
    OP_JZ = 8
    OP_JN = 9
    
    def __init__(self, core_mem: CoreMemory, williams: WilliamsTubes):
        self.core_mem = core_mem
        self.williams = williams
        
        # 48-bit accumulator
        self.accumulator = 0
        
        # Program counter (12-bit address)
        self.pc = 0
        
        # Instruction register
        self.ir = 0
        
        # Operation counter for timing simulation
        self.op_count = 0
        
        # Timing parameters (microseconds)
        self.timing_early = {
            self.OP_LOAD: 40,
            self.OP_ADD: 40,
            self.OP_STORE: 40,
            self.OP_SUB: 40,
            self.OP_MUL: 180,
            self.OP_DIV: 300,
            self.OP_PRINT: 10000,
            self.OP_JUMP: 40,
            self.OP_JZ: 40,
            self.OP_JN: 40,
        }
        
        self.timing_solid_state = {
            self.OP_LOAD: 2.5,
            self.OP_ADD: 2.5,
            self.OP_STORE: 2.5,
            self.OP_SUB: 2.5,
            self.OP_MUL: 8,
            self.OP_DIV: 25,
            self.OP_PRINT: 2000,
            self.OP_JUMP: 2.5,
            self.OP_JZ: 2.5,
            self.OP_JN: 2.5,
        }
        
        # Use solid-state timing by default (upgraded system)
        self.timing = self.timing_solid_state
        
    def fetch(self) -> int:
        """Fetch instruction from memory"""
        instruction = self.core_mem.read(self.pc)
        self.pc = (self.pc + 1) % self.core_mem.size
        self.op_count += 1
        return instruction
    
    def execute(self, instruction: int):
        """Execute a single instruction"""
        # Decode instruction (48-bit word)
        # Format: [Opcode: 4 bits][Address: 12 bits][Unused: 32 bits]
        opcode = (instruction >> 44) & 0xF
        address = (instruction >> 32) & 0xFFF
        operand = instruction & 0xFFFFFFFF
        
        # Get timing for this instruction
        op_time = self.timing.get(opcode, 2.5)
        # time.sleep(op_time / 1_000_000)  # Simulate execution time
        
        # Execute based on opcode
        if opcode == self.OP_LOAD:
            self.accumulator = self.core_mem.read(address)
            
        elif opcode == self.OP_ADD:
            value = self.core_mem.read(address)
            self.accumulator = (self.accumulator + value) & ((1 << 48) - 1)
            
        elif opcode == self.OP_STORE:
            self.core_mem.write(address, self.accumulator)
            
        elif opcode == self.OP_SUB:
            value = self.core_mem.read(address)
            self.accumulator = (self.accumulator - value) & ((1 << 48) - 1)
            
        elif opcode == self.OP_MUL:
            value = self.core_mem.read(address)
            # 48-bit multiplication (simplified)
            self.accumulator = (self.accumulator * value) & ((1 << 48) - 1)
            
        elif opcode == self.OP_DIV:
            value = self.core_mem.read(address)
            if value != 0:
                self.accumulator = self.accumulator // value
                
        elif opcode == self.OP_PRINT:
            # Output to paper tape (simulated)
            print(f"  [PRINT] {self.accumulator:012X}")
            
        elif opcode == self.OP_JUMP:
            self.pc = address
            
        elif opcode == self.OP_JZ:
            if self.accumulator == 0:
                self.pc = address
                
        elif opcode == self.OP_JN:
            # Check sign bit (bit 47)
            if self.accumulator & (1 << 47):
                self.pc = address
    
    def run_program(self, start_address: int, max_instructions: int = 1000):
        """Run a program from memory"""
        self.pc = start_address
        count = 0
        
        while count < max_instructions:
            instruction = self.fetch()
            if instruction == 0:  # NOP or end
                break
            self.execute(instruction)
            count += 1
            
        return count


class MANIAC2Miner:
    """
    MANIAC II RustChain Miner
    Proof-of-Antiquity implementation
    """
    
    WALLET_ADDRESS = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    
    # Memory addresses
    ADDR_PROGRAM = 0x0100
    ADDR_STATE = 0x0200
    ADDR_EPOCH_LOW = 0x0201
    ADDR_EPOCH_HIGH = 0x0202
    ADDR_WALLET = 0x0300
    ADDR_WORK_REG = 0x0400
    
    def __init__(self):
        self.core_mem = CoreMemory()
        self.williams = WilliamsTubes()
        self.cpu = HybridCPU(self.core_mem, self.williams)
        
        self.state = MinerState.IDLE
        self.epoch = 0
        self.attestations: List[Attestation] = []
        
        # Load miner program into memory
        self._load_program()
        
    def _load_program(self):
        """Load the miner program into core memory"""
        # Simple mining loop program
        program = [
            # Load epoch counter
            (self.cpu.OP_LOAD << 44) | (self.ADDR_EPOCH_LOW << 32),
            # Add 1
            (self.cpu.OP_ADD << 44) | self._encode_constant(1),
            # Store back
            (self.cpu.OP_STORE << 44) | (self.ADDR_EPOCH_LOW << 32),
            # Load state
            (self.cpu.OP_LOAD << 44) | (self.ADDR_STATE << 32),
            # Check if MINING state
            (self.cpu.OP_SUB << 44) | self._encode_constant(MinerState.MINING.value),
            # Jump if zero (is mining)
            (self.cpu.OP_JZ << 44) | (self.ADDR_PROGRAM + 10),
            # Print IDLE status
            (self.cpu.OP_LOAD << 44) | self._encode_constant(0x49444C450000),  # "IDLE"
            (self.cpu.OP_PRINT << 44),
            # Jump to start
            (self.cpu.OP_JUMP << 44) | self.ADDR_PROGRAM,
            
            # MINING state (address 10)
            (self.cpu.OP_LOAD << 44) | self._encode_constant(0x4D494E450000),  # "MINE"
            (self.cpu.OP_PRINT << 44),
            # Transition to ATTESTING
            (self.cpu.OP_LOAD << 44) | self._encode_constant(MinerState.ATTESTING.value),
            (self.cpu.OP_STORE << 44) | (self.ADDR_STATE << 32),
            
            # ATTESTING state
            (self.cpu.OP_LOAD << 44) | self._encode_constant(0x415454455354),  # "ATTEST"
            (self.cpu.OP_PRINT << 44),
            # Print wallet
            (self.cpu.OP_LOAD << 44) | (self.ADDR_WALLET << 32),
            (self.cpu.OP_PRINT << 44),
            # Reset state to IDLE
            (self.cpu.OP_LOAD << 44) | self._encode_constant(MinerState.IDLE.value),
            (self.cpu.OP_STORE << 44) | (self.ADDR_STATE << 32),
            # Jump to start
            (self.cpu.OP_JUMP << 44) | self.ADDR_PROGRAM,
        ]
        
        # Load program into core memory
        for i, instruction in enumerate(program):
            self.core_mem.write(self.ADDR_PROGRAM + i, instruction)
        
        # Initialize state
        self.core_mem.write(self.ADDR_STATE, MinerState.IDLE.value)
        self.core_mem.write(self.ADDR_EPOCH_LOW, 0)
        self.core_mem.write(self.ADDR_EPOCH_HIGH, 0)
        
    def _encode_constant(self, value: int) -> int:
        """Encode a constant value for instruction"""
        return value & 0xFFFFFFFF
    
    def run_epoch(self) -> Attestation:
        """Run one mining epoch"""
        print(f"\n{'='*60}")
        print(f"MANIAC II Miner - Epoch {self.epoch}")
        print(f"{'='*60}")
        
        # Transition to MINING state
        self.state = MinerState.MINING
        self.core_mem.write(self.ADDR_STATE, MinerState.MINING.value)
        
        print(f"State: MINING")
        print(f"Running mining simulation...")
        
        # Simulate mining operations
        ops = self.cpu.run_program(self.ADDR_PROGRAM, max_instructions=50)
        
        # Transition to ATTESTING
        self.state = MinerState.ATTESTING
        self.core_mem.write(self.ADDR_STATE, MinerState.ATTESTING.value)
        
        print(f"State: ATTESTING")
        print(f"Generating attestation...")
        
        # Generate attestation
        attestation = Attestation(
            epoch=self.epoch,
            state=self.state,
            wallet=self.WALLET_ADDRESS,
            operation_count=ops,
            timestamp=time.time(),
            checksum=self._compute_checksum()
        )
        
        self.attestations.append(attestation)
        
        # Reset to IDLE
        self.state = MinerState.IDLE
        self.core_mem.write(self.ADDR_STATE, MinerState.IDLE.value)
        self.epoch += 1
        
        print(f"Attestation generated: {attestation.checksum:08X}")
        print(f"Total operations: {ops}")
        print(f"Wallet: {self.WALLET_ADDRESS}")
        
        return attestation
    
    def _compute_checksum(self) -> int:
        """Compute simple checksum for attestation"""
        data = f"{self.epoch}:{self.state.value}:{self.WALLET_ADDRESS}"
        checksum = 0
        for char in data:
            checksum = (checksum + ord(char)) & 0xFFFFFFFF
        return checksum
    
    def run(self, epochs: int = 3):
        """Run the miner for specified epochs"""
        print("\n" + "="*60)
        print("MANIAC II RUSTCHAIN MINER")
        print("Proof-of-Antiquity Simulator")
        print("="*60)
        print(f"\nWallet: {self.WALLET_ADDRESS}")
        print(f"Memory: 4,096 words core + 12,288 words Williams tubes")
        print(f"Word size: 48 bits")
        print(f"Technology: Hybrid (vacuum tubes + transistors)")
        print(f"\nStarting mining simulation for {epochs} epochs...")
        
        for i in range(epochs):
            self.run_epoch()
            time.sleep(0.5)  # Pause between epochs
        
        # Print summary
        print(f"\n{'='*60}")
        print("MINING SUMMARY")
        print(f"{'='*60}")
        print(f"Total epochs: {len(self.attestations)}")
        print(f"Core memory reads: {self.core_mem.read_count}")
        print(f"Core memory writes: {self.core_mem.write_count}")
        print(f"Williams tube refreshes: {self.williams.refresh_count}")
        print(f"CPU operations: {self.cpu.op_count}")
        print(f"\nAntiquity Multiplier: 2.5× (Museum tier - 1957)")
        print(f"Bounty Tier: LEGENDARY (200 RTC / $20)")
        print(f"\nAll attestations recorded successfully!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MANIAC II Miner Simulator')
    parser.add_argument('--epochs', type=int, default=3, help='Number of epochs to mine')
    parser.add_argument('--dump-memory', action='store_true', help='Dump memory after mining')
    args = parser.parse_args()
    
    miner = MANIAC2Miner()
    miner.run(epochs=args.epochs)
    
    if args.dump_memory:
        miner.core_mem.dump(start=0x0100, count=32)


if __name__ == '__main__':
    main()
