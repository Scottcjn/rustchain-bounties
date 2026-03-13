"""Simple test to debug the simulator."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ibm705_simulator import IBM705CPU

cpu = IBM705CPU()

# Write test data
cpu.memory.write_string(100, "0000000005")
print(f"Memory at 100: '{cpu.memory.read_string(100, 10)}'")

# Load it
cpu.instruction_set._load(100)
print(f"Accumulator (first 20 chars): {''.join(cpu.state.accumulator[:20])}")

# Get value
val = cpu.instruction_set._get_accumulator_value(10)
print(f"Accumulator value: {val}")

# Expected: 5
print(f"Expected: 5")
print(f"Match: {val == 5}")
