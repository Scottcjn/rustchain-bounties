#!/usr/bin/env python3
"""HP 2116 (1966) Simulator - Simplified"""
import time

class HP2116Simulator:
    """HP 2116 Minicomputer Simulator"""
    def __init__(self):
        self.memory = [0] * 32768
        self.A = self.B = self.P = 0
        self.halted = False
        
    def load(self, program, addr=0):
        for i, w in enumerate(program):
            if addr + i < len(self.memory):
                self.memory[addr + i] = w & 0xFFFF
                
    def run(self, max_instr=0):
        count = 0
        while not self.halted and (max_instr == 0 or count < max_instr):
            instr = self.memory[self.P]
            if instr == 0x00FF:  # HLT
                self.halted = True
            elif instr == 0x4000:  # CLA
                self.A = 0
            elif instr == 0x4018:  # INCA
                self.A = (self.A + 1) & 0xFFFF
            self.P = (self.P + 1) & 0x7FFF
            count += 1
        return count

if __name__ == '__main__':
    sim = HP2116Simulator()
    sim.load([0x4000, 0x4018, 0x00FF])  # CLA, INCA, HLT
    n = sim.run()
    print(f"HP 2116 Simulator OK - Executed {n} instructions, A={sim.A}")
