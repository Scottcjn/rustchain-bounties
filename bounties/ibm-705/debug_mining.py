"""Debug the mining loop."""

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
print()

# Iteration 1
print("Iteration 1:")
cpu.instruction_set._load(100)
print(f"  After LD 100: acc = {''.join(cpu.state.accumulator[:10])}")
print(f"  acc value = {cpu.instruction_set._get_accumulator_value()}")

cpu.instruction_set._add(150)
print(f"  After AD 150: acc = {''.join(cpu.state.accumulator[:10])}")
print(f"  acc value = {cpu.instruction_set._get_accumulator_value()}")

cpu.instruction_set._store(100)
print(f"  After ST 100: memory = '{cpu.memory.read_string(100, 10)}'")
print()

# Iteration 2
print("Iteration 2:")
cpu.instruction_set._load(100)
print(f"  After LD 100: acc = {''.join(cpu.state.accumulator[:10])}")
print(f"  acc value = {cpu.instruction_set._get_accumulator_value()}")

cpu.instruction_set._add(150)
print(f"  After AD 150: acc = {''.join(cpu.state.accumulator[:10])}")
print(f"  acc value = {cpu.instruction_set._get_accumulator_value()}")

cpu.instruction_set._store(100)
print(f"  After ST 100: memory = '{cpu.memory.read_string(100, 10)}'")
print()

# Iteration 3
print("Iteration 3:")
cpu.instruction_set._load(100)
print(f"  After LD 100: acc = {''.join(cpu.state.accumulator[:10])}")
print(f"  acc value = {cpu.instruction_set._get_accumulator_value()}")
