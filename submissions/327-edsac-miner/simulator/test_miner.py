#!/usr/bin/env python3
"""
Test harness for EDSAC Miner.

Runs comprehensive tests on the EDSAC simulator and mining algorithm.
"""

import sys
from edsac import EDSACSimulator, mine_python, parse_assembly


def test_basic_operations():
    """Test basic EDSAC operations."""
    print("Testing basic EDSAC operations...")
    
    sim = EDSACSimulator()
    
    # Test ZERO
    sim.reset()
    sim.load_word(0, 0b011010 << 5)  # Z
    sim.run()
    assert sim.state.accumulator == 0, "ZERO failed"
    print("  ✓ ZERO instruction")
    
    # Test LOAD
    sim.reset()
    sim.load_word(10, 42)
    sim.load_word(0, (0b01100 << 5) | 10)  # L 10
    sim.run()
    assert sim.state.accumulator == 42, "LOAD failed"
    print("  ✓ LOAD instruction")
    
    # Test ADD
    sim.reset()
    sim.load_word(10, 100)
    sim.load_word(11, 50)
    sim.load_word(0, (0b01100 << 5) | 10)  # L 10
    sim.load_word(1, (0b00001 << 5) | 11)  # A 11
    sim.run()
    assert sim.state.accumulator == 150, "ADD failed"
    print("  ✓ ADD instruction")
    
    # Test SUB
    sim.reset()
    sim.load_word(10, 100)
    sim.load_word(11, 30)
    sim.load_word(0, (0b01100 << 5) | 10)  # L 10
    sim.load_word(1, (0b10011 << 5) | 11)  # S 11
    sim.run()
    assert sim.state.accumulator == 70, "SUB failed"
    print("  ✓ SUB instruction")
    
    # Test MULTIPLY
    sim.reset()
    sim.load_word(10, 12)
    sim.load_word(11, 11)
    sim.load_word(0, (0b01100 << 5) | 10)  # L 10
    sim.load_word(1, (0b01101 << 5) | 11)  # M 11
    sim.run()
    assert sim.state.accumulator == 132, "MULTIPLY failed"
    print("  ✓ MULTIPLY instruction")
    
    # Test STORE
    sim.reset()
    sim.load_word(10, 999)
    sim.load_word(0, (0b01100 << 5) | 10)  # L 10
    sim.load_word(1, (0b10100 << 5) | 20)  # T 20
    sim.run()
    assert sim.state.memory[20] == 999, "STORE failed"
    assert sim.state.accumulator == 0, "STORE should clear accumulator"
    print("  ✓ STORE instruction")
    
    # Test conditional jumps
    sim.reset()
    sim.load_word(10, 5)
    sim.load_word(0, (0b01100 << 5) | 10)  # L 10
    sim.load_word(1, (0b00101 << 5) | 5)   # E 5 (jump if >= 0)
    sim.load_word(2, (0b01100 << 5) | 10)  # L 10 (should skip)
    sim.load_word(3, (0b01100 << 5) | 10)  # L 10 (should skip)
    sim.load_word(4, (0b01100 << 5) | 10)  # L 10 (should skip)
    sim.load_word(5, (0b01000 << 5))       # H
    sim.run()
    assert sim.state.pc == 6, "Conditional jump failed"
    print("  ✓ Conditional jumps")
    
    print("All basic operations passed!\n")


def test_mining_algorithm():
    """Test the mining algorithm with various inputs."""
    print("Testing mining algorithm...")
    
    # Test 1: Easy difficulty (target = 16384, any nonce works)
    header = 1234
    target = 16384
    nonce, hash_val = mine_python(header, target)
    assert nonce == 0, "Easy difficulty should find nonce=0"
    assert hash_val < target, "Hash should be less than target"
    print(f"  ✓ Easy difficulty: nonce={nonce}, hash={hash_val}")
    
    # Test 2: Medium difficulty
    header = 1234
    target = 1638  # ~10% success rate
    nonce, hash_val = mine_python(header, target)
    assert nonce >= 0, "Should find a solution"
    assert hash_val < target, "Hash should be less than target"
    # Verify
    verify_hash = (header * 7919 + nonce * 104729) % 16384
    assert verify_hash == hash_val, "Hash verification failed"
    assert verify_hash < target, "Solution invalid"
    print(f"  ✓ Medium difficulty: nonce={nonce}, hash={hash_val}, target={target}")
    
    # Test 3: Hard difficulty
    header = 5678
    target = 164  # ~1% success rate
    nonce, hash_val = mine_python(header, target)
    assert nonce >= 0, "Should find a solution"
    verify_hash = (header * 7919 + nonce * 104729) % 16384
    assert verify_hash < target, "Solution invalid"
    print(f"  ✓ Hard difficulty: nonce={nonce}, hash={hash_val}, target={target}")
    
    # Test 4: Multiple headers
    for header in [0, 1, 100, 1000, 10000, 16383]:
        target = 1638
        nonce, hash_val = mine_python(header, target)
        verify_hash = (header * 7919 + nonce * 104729) % 16384
        assert verify_hash < target, f"Failed for header={header}"
    print(f"  ✓ Multiple headers tested")
    
    print("All mining algorithm tests passed!\n")


def test_edsac_miner():
    """Test the EDSAC simulator with mining program."""
    print("Testing EDSAC miner simulation...")
    
    sim = EDSACSimulator()
    
    # Test case 1: Easy difficulty
    header = 1234
    target = 16384
    state = sim.run_mining_demo(header, target)
    
    # Get Python reference solution
    ref_nonce, ref_hash = mine_python(header, target)
    
    assert state.nonce_found == ref_nonce, f"Nonce mismatch: {state.nonce_found} != {ref_nonce}"
    print(f"  ✓ Easy: EDSAC found nonce={state.nonce_found}")
    
    # Test case 2: Medium difficulty
    sim.reset()
    header = 1234
    target = 1638
    state = sim.run_mining_demo(header, target)
    
    ref_nonce, ref_hash = mine_python(header, target)
    assert state.nonce_found == ref_nonce, f"Nonce mismatch: {state.nonce_found} != {ref_nonce}"
    
    # Verify the solution
    verify_hash = (header * 7919 + state.nonce_found * 104729) % 16384
    assert verify_hash < target, "Solution invalid"
    print(f"  ✓ Medium: EDSAC found nonce={state.nonce_found}, hash={verify_hash}")
    
    # Test case 3: Different header
    sim.reset()
    header = 9999
    target = 819
    state = sim.run_mining_demo(header, target)
    
    ref_nonce, ref_hash = mine_python(header, target)
    assert state.nonce_found == ref_nonce, f"Nonce mismatch: {state.nonce_found} != {ref_nonce}"
    
    verify_hash = (header * 7919 + state.nonce_found * 104729) % 16384
    assert verify_hash < target, "Solution invalid"
    print(f"  ✓ Different header: nonce={state.nonce_found}, hash={verify_hash}")
    
    print("All EDSAC miner tests passed!\n")


def test_performance():
    """Test performance characteristics."""
    print("Testing performance...")
    
    import time
    
    # Python reference performance
    header = 1234
    target = 164  # Hard difficulty
    
    start = time.time()
    for _ in range(100):
        mine_python(header, target)
    elapsed = time.time() - start
    
    print(f"  Python: 100 mines in {elapsed:.3f}s ({100/elapsed:.0f} mines/s)")
    
    # EDSAC simulator performance (much slower due to instruction-level simulation)
    sim = EDSACSimulator()
    
    start = time.time()
    for _ in range(10):
        sim.reset()
        sim.run_mining_demo(header, target)
    elapsed = time.time() - start
    
    print(f"  EDSAC Sim: 10 mines in {elapsed:.3f}s ({10/elapsed:.1f} mines/s)")
    print(f"  Average cycles per mine: {sim.state.cycles}")
    
    print("Performance tests completed!\n")


def test_assembly_parser():
    """Test the assembly language parser."""
    print("Testing assembly parser...")
    
    # Simple test program
    source = """
    START   Z           ; Clear accumulator
            T 10        ; Store to address 10
            L 10        ; Load from address 10
            H           ; Halt
    """
    
    program = parse_assembly(source)
    assert len(program) == 4, f"Expected 4 instructions, got {len(program)}"
    print(f"  ✓ Parsed {len(program)} instructions")
    
    # Test with labels
    source2 = """
    LOOP    L 10
            A 11
            E LOOP
            H
    """
    
    program2 = parse_assembly(source2)
    assert len(program2) == 4, f"Expected 4 instructions, got {len(program2)}"
    print(f"  ✓ Parsed program with labels")
    
    print("Assembly parser tests passed!\n")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("EDSAC Miner Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_basic_operations()
        test_mining_algorithm()
        test_edsac_miner()
        test_performance()
        test_assembly_parser()
        
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
