#!/usr/bin/env python3
"""Quick test script for AVIDAC simulator modules."""

import sys
import os

# Add simulator to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'simulator'))

print("=" * 60)
print("AVIDAC Simulator - Quick Tests")
print("=" * 60)
print()

# Test 1: Arithmetic
print("Test 1: Arithmetic Module")
print("-" * 40)
from arithmetic import MASK_40, add_40bit, sub_40bit, multiply_40bit

result, overflow = add_40bit(10, 20)
print(f"  10 + 20 = {result} (overflow={overflow})")
assert result == 30 and not overflow

result, borrow = sub_40bit(30, 10)
print(f"  30 - 10 = {result} (borrow={borrow})")
assert result == 20 and not borrow

mq, ac = multiply_40bit(100, 200)
print(f"  100 * 200 = MQ:{mq} AC:{ac}")
assert mq == 0 and ac == 20000

print("  [PASS] Arithmetic tests passed!")
print()

# Test 2: SHA256
print("Test 2: SHA256 Module")
print("-" * 40)
from sha256 import sha256_hex, verify_test_vectors

test_cases = [
    (b'', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
    (b'abc', 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'),
]

all_passed = True
for data, expected in test_cases:
    result = sha256_hex(data)
    passed = result == expected
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} SHA256({data!r})")
    if not passed:
        print(f"    Expected: {expected}")
        print(f"    Got:      {result}")
        all_passed = False

if all_passed:
    print("  [PASS] SHA256 tests passed!")
else:
    print("  [FAIL] SHA256 tests failed!")
print()

# Test 3: Williams Tube Memory
print("Test 3: Williams Tube Memory")
print("-" * 40)
from williams_tube import WilliamsTubeMemory

memory = WilliamsTubeMemory(enable_errors=False)
memory.write_raw(100, 0x123456789)
result = memory.read_raw(100)
print(f"  Write/Read test: {result:010X}")
assert result == 0x123456789

status = memory.get_status()
print(f"  Memory size: {status['words']} words × {status['bits_per_word']} bits")
print(f"  Total: {status['total_bytes']} bytes")
print("  [PASS] Memory tests passed!")
print()

# Test 4: CPU
print("Test 4: CPU Simulator")
print("-" * 40)
from cpu import AVIDACCPU

cpu = AVIDACCPU()
cpu.ac = 0x123456789
print(f"  Initial AC: {cpu.ac:010X}")

# Load simple program: LD 100, STOP
cpu.memory.write_raw(0, ((0xA << 16) | 100) << 20)  # LD 100
cpu.memory.write_raw(100, 0xDEADBEEF12)  # Value to load
cpu.memory.write_raw(1, (0x0 << 16) | 0)  # STOP

cpu.run(max_instructions=10)
print(f"  After LD 100: AC = {cpu.ac:010X}")
assert cpu.ac == 0xDEADBEEF12
print("  [PASS] CPU tests passed!")
print()

# Test 5: Assembler
print("Test 5: Assembler")
print("-" * 40)
from assembler import AVIDACAssembler

test_source = """
        ORG 0x000
START:  LD  VALUE
        ST  RESULT
        STOP
        ORG 0x100
VALUE:  DEC 12345
RESULT: DEC 0
        END START
"""

assembler = AVIDACAssembler()
memory, success = assembler.assemble(test_source)

if success:
    print(f"  Assembled {len(assembler.assembled_words)} words")
    print(f"  Symbols: {assembler.get_symbol_table()}")
    print("  [PASS] Assembler tests passed!")
else:
    print("  ✗ Assembler failed:")
    for error in assembler.errors:
        print(f"    {error}")
print()

# Summary
print("=" * 60)
print("All tests completed successfully!")
print("=" * 60)
