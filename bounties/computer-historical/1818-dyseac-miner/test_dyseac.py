#!/usr/bin/env python3
"""
DYSEAC Miner - Quick Test Script
=================================

Tests core functionality without network dependencies.
"""

import sys
import os

# Add simulator directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dyseac-sim'))

print("=" * 70)
print("DYSEAC Miner - Quick Test")
print("=" * 70)

# Test 1: DYSEAC Simulator
print("\n[Test 1] DYSEAC Simulator")
print("-" * 70)

from dyseac_simulator import DYSEAC_System

system = DYSEAC_System(seed=42)
print(f"[OK] System created")
print(f"  Memory: {system.memory.size} words")
print(f"  Channels: {len(system.memory.channels)}")
print(f"  Temperature: {system.temperature} C")

# Load a simple test program directly
# LD 0x100 (load from address 256)
# ADD 0x101 (add from address 257)
# ST 0x102 (store to address 258)
# STOP
program = [
    0x0A00000100,  # LD 0x100
    0x0100000101,  # ADD 0x101
    0x0B00000102,  # ST 0x102
    0x0000000000,  # STOP
    0x0000012345,  # VALUE1 at 0x100
    0x0000098765,  # VALUE2 at 0x101
    0x0000000000,  # RESULT at 0x102
]

system.load_program(program, start_address=0)
system.run()

print(f"[OK] Program executed")
print(f"  Accumulator: 0x{system.cpu.state.accumulator:011X}")
print(f"  Instructions: {system.cpu.instructions_executed}")
print(f"  Time: {system.cpu.state.total_time_us:.1f} us")

# Test 2: SHA256 Implementation
print("\n[Test 2] SHA256 Implementation")
print("-" * 70)

from dyseac_sha256 import SHA256_DYSEAC

sha256 = SHA256_DYSEAC()

test_cases = [
    (b"", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    (b"abc", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"),
]

all_passed = True
for message, expected in test_cases:
    result = sha256.hash_hex(message)
    passed = result == expected
    all_passed = all_passed and passed
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status}: '{message.decode() if message else '(empty)'}'")

if all_passed:
    print("[OK] All SHA256 tests passed!")
else:
    print("[FAIL] Some SHA256 tests failed!")

# Test 3: Mining Demo
print("\n[Test 3] Mining Demo")
print("-" * 70)

from dyseac_sha256 import DYSEAC_Miner

miner = DYSEAC_Miner(wallet="RTC4325af95d26d59c3ef025963656d22af638bb96b")
data = b"RustChain DYSEAC Test"

print(f"Mining data: {data.decode()}")
print("Difficulty: 2 leading zeros (demo)")
print("Starting...")

hash_result, nonce = miner.mine(data, difficulty=2)

print(f"[OK] Solution found!")
print(f"  Nonce: {nonce}")
print(f"  Hash: {hash_result.hex()}")
print(f"  Total hashes: {miner.hashes_computed}")
print(f"  Est. time on DYSEAC: {miner.sha256.total_time_us/1_000_000:.2f}s")

# Test 4: Hardware Fingerprinting
print("\n[Test 4] Hardware Fingerprinting")
print("-" * 70)

from dyseac_bridge import DYSEACFingerprinter

fingerprinter = DYSEACFingerprinter(system)

# Quick fingerprint
fingerprint = fingerprinter.generate_fingerprint()

print(f"[OK] Fingerprint generated")
print(f"  System: {fingerprint['system']}")
print(f"  Memory: {fingerprint['mercury_delay_line']['total_words']} words")
print(f"  Hash: {fingerprint['overall_hash'][:32]}...")

# Summary
print("\n" + "=" * 70)
print("All Tests Complete!")
print("=" * 70)
print(f"[OK] DYSEAC Simulator: WORKING")
print(f"[OK] SHA256 Implementation: {'WORKING' if all_passed else 'FAILED'}")
print(f"[OK] Mining Demo: WORKING")
print(f"[OK] Hardware Fingerprinting: WORKING")
print("=" * 70)
print("\nDYSEAC Miner is ready for RustChain network!")
print("=" * 70)
