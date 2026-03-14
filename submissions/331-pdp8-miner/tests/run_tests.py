#!/usr/bin/env python3
"""
Simple test runner for PDP-8 RustChain Miner
(No pytest dependency)
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdp8_simulator import PDP8CPU, RustChainMiner, MEMORY_SIZE, WORD_MASK


def test_cpu_initial_state():
    cpu = PDP8CPU()
    assert cpu.ac == 0
    assert cpu.pc == 0
    assert cpu.l == 0
    print("  [PASS] CPU initial state")


def test_cpu_memory():
    cpu = PDP8CPU()
    cpu.write_memory(100, 0x123)
    assert cpu.read_memory(100) == 0x123
    cpu.write_memory(0, 0xFFFF)
    assert cpu.read_memory(0) == WORD_MASK
    print("  [PASS] CPU memory operations")


def test_cpu_instructions():
    cpu = PDP8CPU()
    
    # Test AND - use page 0 address (0x000-0x077)
    cpu.ac = 0xFFF
    cpu.l = 0
    cpu.write_memory(0x050, 0x0F0)  # Page 0 address
    cpu.execute(0o0000 | 0x050)
    assert cpu.ac == 0x0F0, f"Expected 0x0F0, got {cpu.ac:03X}"
    
    # Test TAD - use page 0 address
    cpu = PDP8CPU()  # Fresh CPU
    cpu.ac = 0x100
    cpu.write_memory(0x050, 0x050)
    cpu.execute(0o1000 | 0x050)
    assert cpu.ac == 0x150, f"Expected 0x150, got {cpu.ac:03X}"
    
    # Test JMP - use page 0 address
    cpu = PDP8CPU()  # Fresh CPU
    cpu.execute(0o5000 | 0x050)
    assert cpu.pc == 0x050, f"Expected 0x050, got {cpu.pc:03X}"
    
    print("  [PASS] CPU instructions")


def test_miner_entropy():
    cpu = PDP8CPU()
    miner = RustChainMiner(cpu)
    miner.collect_entropy(32)
    assert len(miner.entropy_pool) == 32
    print("  [PASS] Miner entropy collection")


def test_miner_wallet():
    cpu = PDP8CPU()
    miner = RustChainMiner(cpu)
    wallet = miner.generate_wallet()
    assert wallet.startswith("RTC")
    assert len(wallet) == 43
    print("  [PASS] Miner wallet generation")


def test_miner_attestation():
    cpu = PDP8CPU()
    miner = RustChainMiner(cpu)
    miner.collect_entropy(32)
    miner.generate_wallet()
    attestation = miner.create_attestation()
    
    assert 'epoch' in attestation
    assert 'timestamp' in attestation
    assert 'antiquity_multiplier' in attestation
    assert attestation['antiquity_multiplier'] == 5.0
    print("  [PASS] Miner attestation creation")


def test_full_mining():
    cpu = PDP8CPU()
    miner = RustChainMiner(cpu)
    attestations = miner.run_miner(epochs=3)
    assert len(attestations) == 3
    print("  [PASS] Full mining cycle")


def main():
    print("\n" + "=" * 60)
    print("  PDP-8 RustChain Miner - Test Suite")
    print("=" * 60 + "\n")
    
    tests = [
        test_cpu_initial_state,
        test_cpu_memory,
        test_cpu_instructions,
        test_miner_entropy,
        test_miner_wallet,
        test_miner_attestation,
        test_full_mining,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
