#!/usr/bin/env python3
"""
Test suite for IBM 650 Miner Simulator
Verifies proof cards, simulator accuracy, and hash functions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ibm650_miner_sim import IBM650Simulator, RustChainMiner650


def test_simulator_basic():
    """Test basic simulator functionality"""
    print("Testing basic simulator operations...")
    
    sim = IBM650Simulator(drum_size=2000)
    
    # Test memory read/write
    sim.write_word(100, 1234567890)
    assert sim.read_word(100) == 1234567890, "Memory write/read failed"
    
    # Test console switches
    sim.console_switches = 9876543210
    assert sim.read_word(8000) == 9876543210, "Console switch read failed"
    
    # Test accumulator
    sim.accumulator_lo = 1111111111
    sim.accumulator_hi = 2222222222
    assert sim.read_word(8002) == 1111111111, "Accumulator LO read failed"
    assert sim.read_word(8003) == 2222222222, "Accumulator HI read failed"
    
    print("  [PASS] Basic operations")


def test_arithmetic():
    """Test arithmetic operations"""
    print("Testing arithmetic operations...")
    
    sim = IBM650Simulator()
    
    # Test addition
    sim.accumulator_lo = 100
    sim.execute_instruction(15, 0, 0)  # AL - but we need to set up data first
    sim.write_word(200, 50)
    sim.accumulator_lo = 100
    result = sim.execute_instruction(15, 200, 0)  # AL 200
    assert sim.accumulator_lo == 150, f"Addition failed: {sim.accumulator_lo}"
    
    # Test multiplication
    sim.accumulator_lo = 123
    sim.write_word(201, 456)
    sim.execute_instruction(19, 201, 0)  # MULT 201
    expected = 123 * 456
    assert sim.accumulator_lo == (expected % (10**10)), "Multiplication failed"
    assert sim.accumulator_hi == (expected // (10**10)), "Multiplication HI failed"
    
    print("  [PASS] Arithmetic operations")


def test_hash_function():
    """Test decimal hash function"""
    print("Testing hash function...")
    
    sim = IBM650Simulator()
    miner = RustChainMiner650("RTC4325af95d26d59c3ef025963656d22af638bb96b", sim)
    
    # Test determinism
    sim.console_switches = 1234567890
    hash1 = miner.compute_proof_hash(1234567890, 2603140100)
    hash2 = miner.compute_proof_hash(1234567890, 2603140100)
    assert hash1 == hash2, "Hash not deterministic"
    
    # Test avalanche (small change = big difference)
    hash3 = miner.compute_proof_hash(1234567891, 2603140100)
    assert hash1 != hash3, "Hash should change with input"
    
    print("  [PASS] Hash function")


def test_proof_verification():
    """Test proof card verification"""
    print("Testing proof verification...")
    
    sim = IBM650Simulator()
    miner = RustChainMiner650("RTC4325af95d26d59c3ef025963656d22af638bb96b", sim)
    
    # Generate and verify proof
    proof_card = miner.run_mining_cycle()
    assert miner.verify_proof(proof_card), "Valid proof failed verification"
    
    # Tamper with proof
    tampered = proof_card[:20] + '0' + proof_card[21:]
    assert not miner.verify_proof(tampered), "Tampered proof passed verification"
    
    print("  [PASS] Proof verification")


def test_card_format():
    """Test proof card format"""
    print("Testing card format...")
    
    sim = IBM650Simulator()
    miner = RustChainMiner650("RTC4325af95d26d59c3ef025963656d22af638bb96b", sim)
    
    proof_card = miner.run_mining_cycle()
    
    # Check length
    assert len(proof_card) == 80, f"Card length should be 80, got {len(proof_card)}"
    
    # Check all digits
    assert proof_card.isdigit(), "Card should contain only digits"
    
    # Check wallet part (first 10 digits)
    wallet_part = proof_card[0:10]
    assert wallet_part == "4325952659", f"Wallet part incorrect: {wallet_part}"
    
    print("  [PASS] Card format")


def test_instruction_parsing():
    """Test instruction word parsing"""
    print("Testing instruction parsing...")
    
    sim = IBM650Simulator()
    
    # Create instruction: OP=15 (AL), DA=0100, IA=0200
    # Word format: 001501000200 (with leading zeros)
    word = 15 * (10**8) + 100 * (10**4) + 200
    opcode, data_addr, next_addr = sim.parse_instruction(word)
    
    assert opcode == 15, f"Opcode should be 15, got {opcode}"
    assert data_addr == 100, f"Data addr should be 100, got {data_addr}"
    assert next_addr == 200, f"Next addr should be 200, got {next_addr}"
    
    print("  [PASS] Instruction parsing")


def test_program_execution():
    """Test simple program execution"""
    print("Testing program execution...")
    
    sim = IBM650Simulator()
    
    # Simple program: Load value, add, store
    # Address 100: RAL 200 -> 105  (Load from 200, next at 105)
    # Address 105: AL  201 -> 110  (Add from 201, next at 110)
    # Address 110: STOP
    
    program = [
        (100, 65 * (10**8) + 200 * (10**4) + 105),  # RAL 200, next 105
        (105, 15 * (10**8) + 201 * (10**4) + 110),  # AL 201, next 110
    ]
    
    sim.load_program(program)
    sim.write_word(200, 100)
    sim.write_word(201, 50)
    
    sim.run(start_addr=100, max_instructions=10)
    
    assert sim.accumulator_lo == 150, f"Expected 150, got {sim.accumulator_lo}"
    
    print("  [PASS] Program execution")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("IBM 650 MINER TEST SUITE")
    print("=" * 60)
    print()
    
    tests = [
        test_simulator_basic,
        test_arithmetic,
        test_hash_function,
        test_proof_verification,
        test_card_format,
        test_instruction_parsing,
        test_program_execution,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
