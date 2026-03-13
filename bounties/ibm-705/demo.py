"""
IBM 705 Mining Demo - Simplified Version

This demo shows the core mining functionality on the IBM 705 simulator.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ibm705_simulator import IBM705CPU, IBM705Config


def run_mining_demo():
    """Run a simplified mining demonstration."""
    print("=" * 60)
    print("IBM 705 RustChain Miner - Demonstration")
    print("=" * 60)
    print()
    
    # Create CPU
    cpu = IBM705CPU()
    
    # Simple mining program - increment nonce and check against target
    mining_program = """
* Initialize nonce to 0
START:   ZT  0100
         LD  0150
         ST  0100

* Mining loop
LOOP:    LD  0100
         AD  0150
         ST  0100
         
* Check if reached target (10)
         LD  0100
         CO  0120
         JF  FOUND
         
         J   LOOP

* Found solution
FOUND:   WR  0100
         SW  0000

* Constants
ONE      0000000001
TARGET   0000000010
"""
    
    # Load program
    cpu.load_program(mining_program, start=200)
    
    # Initialize memory
    cpu.memory.write_string(100, "0000000000")  # NONCE
    cpu.memory.write_string(120, "0000000010")  # TARGET = 10
    cpu.memory.write_string(150, "0000000001")  # ONE
    
    print("Initial State:")
    print(cpu.get_status())
    print()
    
    print("Memory (before mining):")
    print(f"  NONCE (0100): {cpu.memory.read_string(100, 10)}")
    print(f"  TARGET (0120): {cpu.memory.read_string(120, 10)}")
    print()
    
    print("Starting mining operation...")
    print("-" * 60)
    
    # Run mining
    cpu.run(max_instructions=1000)
    
    print()
    print("Mining Complete!")
    print("-" * 60)
    print()
    
    print("Final State:")
    print(cpu.get_status())
    print()
    
    print("Memory (after mining):")
    print(f"  NONCE (0100): {cpu.memory.read_string(100, 10)}")
    print(f"  TARGET (0120): {cpu.memory.read_string(120, 10)}")
    print()
    
    print("Output Records:")
    output = cpu.io.get_output()
    if output:
        for record in output:
            print(f"  {record}")
    else:
        print("  (no output)")
    print()
    
    # Verify result
    nonce_str = cpu.memory.read_string(100, 10).strip()
    nonce = int(nonce_str) if nonce_str.isdigit() else 0
    
    print("=" * 60)
    print("Results:")
    print(f"  Final Nonce: {nonce}")
    print(f"  Target: 10")
    print(f"  Success: {nonce == 10}")
    print(f"  Instructions Executed: {cpu.state.instructions_executed}")
    print(f"  CPU Cycles: {cpu.state.cycles}")
    print("=" * 60)
    
    return nonce == 10


def run_hash_demo():
    """Demonstrate hash computation."""
    print()
    print("=" * 60)
    print("IBM 705 Hash Computation Demo")
    print("=" * 60)
    print()
    
    cpu = IBM705CPU()
    
    # Hash computation: ((block * nonce) + constant) mod prime
    # For demo: ((5 * 3) + 2) = 17
    
    print("Computing hash: ((block_data * nonce) + constant)")
    print("  block_data = 5")
    print("  nonce = 3")
    print("  constant = 2")
    print("  Expected: 17")
    print()
    
    # Set up values
    cpu.memory.write_string(100, "0000000003")  # nonce
    cpu.memory.write_string(110, "0000000005")  # block_data
    cpu.memory.write_string(160, "0000000002")  # constant
    
    # Manual computation
    cpu.instruction_set._load(110)  # Load block_data
    print(f"Loaded block_data: {cpu.instruction_set._get_accumulator_value()}")
    
    cpu.instruction_set._multiply(100)  # Multiply by nonce
    print(f"After multiply by nonce: {cpu.instruction_set._get_accumulator_value()}")
    
    cpu.instruction_set._add(160)  # Add constant
    result = cpu.instruction_set._get_accumulator_value()
    print(f"After add constant: {result}")
    print()
    
    print(f"Hash Result: {result}")
    print(f"Expected: 17")
    print(f"Match: {result == 17}")
    print("=" * 60)
    
    return result == 17


if __name__ == "__main__":
    mining_success = run_mining_demo()
    hash_success = run_hash_demo()
    
    print()
    print("=" * 60)
    print("DEMO SUMMARY")
    print("=" * 60)
    print(f"Mining Demo: {'PASS' if mining_success else 'FAIL'}")
    print(f"Hash Demo: {'PASS' if hash_success else 'FAIL'}")
    print()
    
    if mining_success and hash_success:
        print("All demos passed! IBM 705 miner is functional.")
    else:
        print("Some demos failed. Check implementation.")
    
    print("=" * 60)
