"""Debug the _add method."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ibm705_simulator import IBM705CPU

cpu = IBM705CPU()

# Setup
cpu.memory.write_string(100, "0000000001")  # Current nonce = 1
cpu.memory.write_string(150, "0000000001")  # ONE

print("Setup:")
print(f"  Memory[100] (nonce): '{cpu.memory.read_string(100, 10)}'")
print(f"  Memory[150] (ONE): '{cpu.memory.read_string(150, 10)}'")
print()

# Load nonce into accumulator
cpu.instruction_set._load(100)
print("After LD 100:")
print(f"  Acc: '{''.join(cpu.state.accumulator[:10])}'")
print(f"  Acc value: {cpu.instruction_set._get_accumulator_value(10)}")
print()

# Debug _add
print("During AD 150:")
field_len = 10
mem_val = cpu.instruction_set._get_field_value(150, field_len)
acc_val = cpu.instruction_set._get_accumulator_value(field_len)
print(f"  mem_val (from 150): {mem_val}")
print(f"  acc_val: {acc_val}")
print(f"  result: {acc_val + mem_val}")
print()

# Actually do the add
cpu.instruction_set._add(150)
print("After AD 150:")
print(f"  Acc: '{''.join(cpu.state.accumulator[:10])}'")
print(f"  Acc value: {cpu.instruction_set._get_accumulator_value(10)}")
