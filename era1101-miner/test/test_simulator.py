#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for ERA 1101 Simulator
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from era1101_simulator import (
    ERA1101Simulator, Instruction, Opcode, 
    ones_complement_negate, to_signed, to_unsigned,
    MEMORY_SIZE, WORD_SIZE
)


def test_ones_complement():
    """Test ones' complement arithmetic."""
    print("Testing ones' complement arithmetic...")
    
    # Test negation
    assert ones_complement_negate(0) == 0xFFFFFF
    assert ones_complement_negate(1) == 0xFFFFFF - 1
    assert ones_complement_negate(0x123456) == (0xFFFFFF ^ 0x123456)
    
    # Test signed conversion
    assert to_signed(0) == 0
    assert to_signed(1) == 1
    assert to_signed(0x7FFFFF) == 0x7FFFFF  # Max positive
    assert to_signed(0x800000) < 0  # Negative
    assert to_signed(0xFFFFFF) == -0  # Negative zero in ones' complement
    
    print("  [OK] Ones' complement tests passed")


def test_instruction_encoding():
    """Test instruction encoding/decoding."""
    print("Testing instruction encoding...")
    
    # Test INS instruction
    instr = Instruction(opcode=Opcode.INS, skip=3, address=0x1234)
    word = instr.to_word()
    decoded = Instruction.from_word(word)
    
    assert decoded.opcode == Opcode.INS
    assert decoded.skip == 3
    assert decoded.address == 0x1234
    
    # Test ADD instruction
    instr = Instruction(opcode=Opcode.ADD, skip=2, address=0x00FF)
    word = instr.to_word()
    decoded = Instruction.from_word(word)
    
    assert decoded.opcode == Opcode.ADD
    assert decoded.skip == 2
    assert decoded.address == 0x00FF
    
    print("  [OK] Instruction encoding tests passed")


def test_simulator_basic():
    """Test basic simulator operations."""
    print("Testing basic simulator operations...")
    
    sim = ERA1101Simulator()
    
    # Test memory load/store
    sim.store_word(0x1000, 0x123456)
    value = sim.load_word(0x1000)
    assert value == 0x123456
    
    # Test register operations
    sim.A = 0x100
    sim.Q = 0x200
    sim.X = 0x300
    
    assert sim.A == 0x100
    assert sim.Q == 0x200
    assert sim.X == 0x300
    
    print("  [OK] Basic simulator tests passed")


def test_simulator_instructions():
    """Test individual instruction execution."""
    print("Testing instruction execution...")
    
    sim = ERA1101Simulator()
    
    # Test INS (Insert)
    sim.store_word(0x1000, 0x123456)
    instr = Instruction(opcode=Opcode.INS, skip=0, address=0x1000)
    sim.execute_instruction(instr)
    assert sim.A == 0x123456
    
    # Test ADD
    sim.store_word(0x1001, 0x000001)
    instr = Instruction(opcode=Opcode.ADD, skip=0, address=0x1001)
    sim.execute_instruction(instr)
    assert sim.A == 0x123457
    
    # Test STO (Store)
    instr = Instruction(opcode=Opcode.STO, skip=0, address=0x1002)
    sim.execute_instruction(instr)
    value = sim.load_word(0x1002)
    assert value == 0x123457
    
    # Test TRA (Transfer A to Q)
    sim.A = 0xABCDEF
    instr = Instruction(opcode=Opcode.TRA, skip=0, address=0x0000)
    sim.execute_instruction(instr)
    assert sim.Q == 0xABCDEF
    
    # Test AND
    sim.A = 0xFF00FF
    sim.store_word(0x1003, 0x00FFFF)
    instr = Instruction(opcode=Opcode.AND, skip=0, address=0x1003)
    sim.execute_instruction(instr)
    assert sim.A == 0x0000FF
    
    # Test SHL (Shift Left)
    sim.A = 0x000001
    instr = Instruction(opcode=Opcode.SHL, skip=0, address=0x0000)
    sim.execute_instruction(instr)
    assert sim.A == 0x000002
    
    print("  [OK] Instruction execution tests passed")


def test_simulator_program():
    """Test running a complete program."""
    print("Testing complete program execution...")
    
    sim = ERA1101Simulator()
    
    # Create a simple program: add two numbers
    program = [
        Instruction(Opcode.INS, skip=0, address=0x0004).to_word(),
        Instruction(Opcode.ADD, skip=0, address=0x0005).to_word(),
        Instruction(Opcode.STO, skip=0, address=0x0006).to_word(),
        Instruction(Opcode.HLT, skip=0, address=0x0000).to_word(),
        0x000123,  # VALUE1
        0x000456,  # VALUE2
        0x000000,  # RESULT
    ]
    
    sim.load_program(program, start_address=0)
    sim.run(start_address=0, max_cycles=100)
    
    # Check result
    result = sim.load_word(0x0006)
    expected = 0x123 + 0x456
    assert result == expected, f"Expected {expected:06X}, got {result:06X}"
    
    print("  [OK] Complete program test passed")


def test_drum_memory():
    """Test drum memory simulation."""
    print("Testing drum memory simulation...")
    
    sim = ERA1101Simulator()
    
    # Test track calculation
    sim.load_word(0x0000)
    assert sim.drum[0].current_position == 0
    
    # Address 0x0052 (82 words per track) -> Track 1, Position 0
    sim.load_word(0x0052)
    assert sim.drum[1].current_position == 0
    
    # Test rotational delay statistics
    initial_delays = sim.stats['rotational_delays']
    
    # Access non-sequential addresses to cause delays
    sim.load_word(0x0000)
    sim.load_word(0x0005)
    
    assert sim.stats['rotational_delays'] >= initial_delays
    
    print("  [OK] Drum memory tests passed")


def test_memory_bounds():
    """Test memory boundary handling."""
    print("Testing memory bounds...")
    
    sim = ERA1101Simulator()
    
    # Test valid addresses
    sim.store_word(0x0000, 0x111111)
    sim.store_word(0x3FFF, 0x222222)  # Last valid address
    
    assert sim.load_word(0x0000) == 0x111111
    assert sim.load_word(0x3FFF) == 0x222222
    
    # Test invalid addresses
    try:
        sim.load_word(0x4000)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    try:
        sim.store_word(0xFFFF, 0x123456)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("  [OK] Memory bounds tests passed")


def run_all_tests():
    """Run all simulator tests."""
    print("=" * 60)
    print("ERA 1101 Simulator Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_ones_complement,
        test_instruction_encoding,
        test_simulator_basic,
        test_simulator_instructions,
        test_simulator_program,
        test_drum_memory,
        test_memory_bounds,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {test.__name__} ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
