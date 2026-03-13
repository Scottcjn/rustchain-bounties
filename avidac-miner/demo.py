#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AVIDAC Miner Demo

Quick demonstration of the AVIDAC miner capabilities.
"""

import sys
import time

sys.path.insert(0, 'simulator')

from cpu import AVIDACCPU
from williams_tube import WilliamsTubeMemory
from sha256 import sha256_hex, SHA256
from arithmetic import MASK_40


def demo_cpu():
    """Demonstrate AVIDAC CPU."""
    print("\n" + "=" * 60)
    print("  AVIDAC CPU Demo")
    print("=" * 60)
    
    cpu = AVIDACCPU(debug=False)
    
    # Simple program: LD 10, ADD 11, STOP
    # Word 0: Left=LD 10, Right=ADD 11
    # Word 1: Left=STOP
    # Word 10: value 100
    # Word 11: value 50
    cpu.memory.write_raw(0, (0xA << 16 | 10) << 20 | (0x1 << 16 | 11))
    cpu.memory.write_raw(1, 0x0 << 20)
    cpu.memory.write_raw(10, 100)
    cpu.memory.write_raw(11, 50)
    
    print("Program: LD 10, ADD 11, STOP")
    cpu.run(max_instructions=10)
    
    print(f"Result: {cpu.ac} (expected: 150)")
    print(f"Instructions: {cpu.instruction_count}")
    
    if cpu.ac == 150:
        print("[PASS] CPU test")
        return True
    else:
        print("[FAIL] CPU test")
        return False


def demo_memory():
    """Demonstrate Williams tube memory."""
    print("\n" + "=" * 60)
    print("  Williams Tube Memory Demo")
    print("=" * 60)
    
    memory = WilliamsTubeMemory(words=1024, bits_per_word=40, enable_errors=False)
    
    print(f"Memory: {memory.words} words x {memory.bits_per_word} bits")
    print(f"Total: {memory.get_status()['total_bytes']} bytes")
    
    test_values = [0x123456789, 0xDEADBEEF12, 0xFFFFFFFFFF]
    
    for i, value in enumerate(test_values):
        memory.write_raw(i, value)
        read_value = memory.read_raw(i)
        status = "PASS" if value == read_value else "FAIL"
        print(f"[{status}] Address {i:03X}: {value:010X}")
    
    return True


def demo_sha256():
    """Demonstrate SHA256."""
    print("\n" + "=" * 60)
    print("  SHA256 Demo")
    print("=" * 60)
    
    test_cases = [
        (b'', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'),
        (b'abc', 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'),
    ]
    
    all_pass = True
    for data, expected in test_cases:
        result = sha256_hex(data)
        status = "PASS" if result == expected else "FAIL"
        print(f"[{status}] sha256({data!r})")
        if result != expected:
            all_pass = False
    
    return all_pass


def demo_mining():
    """Demonstrate mining."""
    print("\n" + "=" * 60)
    print("  Mining Demo")
    print("=" * 60)
    
    target = 1 << 252
    print(f"Target: < {target:064x}")
    
    start_time = time.time()
    for nonce in range(10000):
        hash_hex = sha256_hex(nonce.to_bytes(8, 'big'))
        hash_int = int(hash_hex, 16)
        
        if hash_int < target:
            elapsed = time.time() - start_time
            print(f"[PASS] Found nonce {nonce} in {elapsed:.3f}s")
            print(f"Hash: {hash_hex}")
            return True
    
    print("[FAIL] No solution found")
    return False


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("  AVIDAC (1953) Miner Demo")
    print("  Nuclear Research Computing Meets Blockchain")
    print("=" * 60)
    
    results = []
    results.append(("CPU", demo_cpu()))
    results.append(("Memory", demo_memory()))
    results.append(("SHA256", demo_sha256()))
    results.append(("Mining", demo_mining()))
    
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
    
    all_pass = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_pass:
        print("  ALL TESTS PASSED!")
        print("  AVIDAC miner is ready!")
    else:
        print("  SOME TESTS FAILED")
    print("=" * 60 + "\n")
    
    return 0 if all_pass else 1


if __name__ == '__main__':
    sys.exit(main())
