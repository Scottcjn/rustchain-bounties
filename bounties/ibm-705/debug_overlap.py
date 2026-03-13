"""Debug memory corruption."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ibm705_simulator import IBM705CPU

cpu = IBM705CPU()

# Setup
cpu.memory.write_string(100, "0000000000")  # NONCE
cpu.memory.write_string(150, "0000000001")  # ONE

print("Initial:")
print(f"  Memory[100]: '{cpu.memory.read_string(100, 10)}'")
print(f"  Memory[150]: '{cpu.memory.read_string(150, 10)}'")
print(f"  Memory[100-130]: '{cpu.memory.read_string(100, 31)}'")
print()

# Iteration 1
print("Iteration 1:")
cpu.instruction_set._load(100)
cpu.instruction_set._add(150)
print(f"  After AD: acc = {''.join(cpu.state.accumulator[:10])}")
cpu.instruction_set._store(100)
print(f"  After ST 100:")
print(f"    Memory[100]: '{cpu.memory.read_string(100, 10)}'")
print(f"    Memory[150]: '{cpu.memory.read_string(150, 10)}'")
print(f"    Memory[100-130]: '{cpu.memory.read_string(100, 31)}'")
print()

# Check if store overwrote address 150
print("Checking for memory overlap:")
print(f"  ACCUMULATOR_SIZE = 128")
print(f"  Store starts at 100, ends at {100 + 128 - 1}")
print(f"  ONE is at 150")
print(f"  Overlap: {100 <= 150 < 100 + 128}")
print()

# That's the bug! Store writes 128 chars starting at 100, which overwrites 150!
