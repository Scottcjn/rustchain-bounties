#!/usr/bin/env python3
"""
ORACLE (1952) CPU Simulator
Oak Ridge Automatic Computer - IAS Architecture Emulator
"""

import struct
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import IntEnum


class Opcode(IntEnum):
    """ORACLE (IAS) Instruction Set"""
    STOP = 0x00
    ADD = 0x01
    SUB = 0x02
    MUL = 0x03
    DIV = 0x04
    AND = 0x05
    OR = 0x06
    JMP = 0x07
    JZ = 0x08
    JN = 0x09
    LD = 0x0A
    ST = 0x0B
    IN = 0x0C
    OUT = 0x0D
    RSH = 0x0E
    LSH = 0x0F


@dataclass
class WilliamsTubeMemory:
    """Williams-Kilburn Tube Memory Model"""
    WORDS: int = 1024
    BITS_PER_WORD: int = 40
    memory: List[int] = field(default_factory=lambda: [0] * 1024)
    drift_factor: float = 0.0
    temperature: float = 25.0
    refresh_counter: int = 0
    REFRESH_INTERVAL: int = 10000
    
    def read(self, address: int) -> int:
        if address < 0 or address >= self.WORDS:
            raise ValueError(f"Memory address out of range: {address}")
        drift = int(self.drift_factor * self.temperature * (self.refresh_counter / self.REFRESH_INTERVAL))
        value = self.memory[address] ^ drift
        return value & ((1 << self.BITS_PER_WORD) - 1)
    
    def write(self, address: int, value: int):
        if address < 0 or address >= self.WORDS:
            raise ValueError(f"Memory address out of range: {address}")
        value = value & ((1 << self.BITS_PER_WORD) - 1)
        self.memory[address] = value
        self.refresh_counter = 0
    
    def refresh(self):
        self.refresh_counter = 0
        self.drift_factor += 0.0001


@dataclass
class ORACLECPU:
    """ORACLE CPU Emulator"""
    WORDS: int = 1024
    BITS_PER_WORD: int = 40
    AC: int = 0
    MBR: int = 0
    PC: int = 0
    IR: int = 0
    zero_flag: bool = False
    negative_flag: bool = False
    memory: WilliamsTubeMemory = field(default_factory=WilliamsTubeMemory)
    running: bool = False
    halted: bool = False
    cycles: int = 0
    paper_tape_input: List[int] = field(default_factory=list)
    paper_tape_output: List[int] = field(default_factory=list)
    
    def reset(self):
        self.AC = 0
        self.MBR = 0
        self.PC = 0
        self.IR = 0
        self.zero_flag = False
        self.negative_flag = False
        self.running = False
        self.halted = False
        self.cycles = 0
        self.paper_tape_input = []
        self.paper_tape_output = []
    
    def load_program(self, program: List[int], start_addr: int = 0):
        for i, word in enumerate(program):
            self.memory.write(start_addr + i, word)
    
    def fetch(self) -> int:
        instruction = self.memory.read(self.PC)
        self.PC = (self.PC + 1) % self.WORDS
        return instruction
    
    def decode(self, instruction: int) -> Tuple[Opcode, int]:
        opcode = Opcode((instruction >> 32) & 0xFF)
        address = instruction & 0xFFFFFFFF
        return opcode, address
    
    def update_flags(self, value: int):
        self.zero_flag = (value & ((1 << self.BITS_PER_WORD) - 1)) == 0
        self.negative_flag = bool(value & (1 << 39))
    
    def execute(self, opcode: Opcode, address: int):
        if opcode == Opcode.STOP:
            self.halted = True
            self.running = False
        elif opcode == Opcode.ADD:
            operand = self.memory.read(address)
            self.AC = (self.AC + operand) & ((1 << self.BITS_PER_WORD) - 1)
            self.update_flags(self.AC)
        elif opcode == Opcode.SUB:
            operand = self.memory.read(address)
            self.AC = (self.AC - operand) & ((1 << self.BITS_PER_WORD) - 1)
            self.update_flags(self.AC)
        elif opcode == Opcode.LD:
            self.AC = self.memory.read(address)
            self.update_flags(self.AC)
        elif opcode == Opcode.ST:
            self.memory.write(address, self.AC)
        elif opcode == Opcode.JMP:
            self.PC = address
        elif opcode == Opcode.JZ:
            if self.zero_flag:
                self.PC = address
        elif opcode == Opcode.JN:
            if self.negative_flag:
                self.PC = address
        self.cycles += 1
    
    def step(self) -> bool:
        if self.halted:
            return False
        self.IR = self.fetch()
        opcode, address = self.decode(self.IR)
        self.execute(opcode, address)
        self.memory.refresh_counter += 1
        if self.memory.refresh_counter >= self.memory.REFRESH_INTERVAL:
            self.memory.refresh()
        return not self.halted
    
    def run(self, max_cycles: int = 1000000):
        self.running = True
        while self.running and self.cycles < max_cycles:
            self.step()
    
    def get_state(self) -> Dict:
        return {
            'PC': self.PC, 'AC': self.AC, 'MBR': self.MBR, 'IR': self.IR,
            'zero': self.zero_flag, 'negative': self.negative_flag,
            'cycles': self.cycles, 'halted': self.halted,
        }


if __name__ == '__main__':
    print("=" * 60)
    print("ORACLE (1952) CPU Simulator")
    print("Oak Ridge Automatic Computer - IAS Architecture")
    print("=" * 60)
    
    cpu = ORACLECPU()
    test_program = [
        0x0A00000100,  # LD 0x100
        0x0100000101,  # ADD 0x101
        0x0B00000102,  # ST 0x102
        0x0000000000,  # STOP
    ]
    
    cpu.memory.write(0x100, 42)
    cpu.memory.write(0x101, 58)
    cpu.load_program(test_program)
    cpu.run()
    
    print(f"\nProgram executed in {cpu.cycles} cycles")
    print(f"Result: {cpu.memory.read(0x102)} (expected: 100)")
    print(f"\nCPU State: {cpu.get_state()}")
    print("\nSimulator test complete!")
