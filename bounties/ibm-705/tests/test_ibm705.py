"""
IBM 705 Simulator - Test Suite

Tests for CPU, Memory, and Mining functionality.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ibm705_simulator import (
    IBM705CPU, 
    IBM705Memory, 
    CPUState, 
    InstructionSet,
    VirtualIO,
    IBM705Config
)


class TestIBM705Memory(unittest.TestCase):
    """Test IBM 705 Memory operations."""
    
    def setUp(self):
        self.memory = IBM705Memory(size=1000)
    
    def test_memory_initialization(self):
        """Memory should initialize with spaces."""
        for i in range(1000):
            self.assertEqual(self.memory.read(i), ' ')
    
    def test_memory_write_read(self):
        """Write and read single characters."""
        self.memory.write(100, 'A')
        self.assertEqual(self.memory.read(100), 'A')
    
    def test_memory_string_write_read(self):
        """Write and read strings."""
        test_string = "Hello, IBM 705!"
        self.memory.write_string(200, test_string)
        result = self.memory.read_string(200, len(test_string))
        self.assertEqual(result, test_string)
    
    def test_memory_bounds_checking(self):
        """Memory access should check bounds."""
        with self.assertRaises(ValueError):
            self.memory.read(-1)
        with self.assertRaises(ValueError):
            self.memory.read(1000)
        with self.assertRaises(ValueError):
            self.memory.write(-1, 'A')
        with self.assertRaises(ValueError):
            self.memory.write(1000, 'A')
    
    def test_memory_clear(self):
        """Clear should reset memory to spaces."""
        self.memory.write_string(0, "Test Data")
        self.memory.clear()
        self.assertEqual(self.memory.read(0), ' ')
        self.assertEqual(self.memory.read(5), ' ')
    
    def test_memory_load_program(self):
        """Program loading should work correctly."""
        program = "LD  0100\nST  0200"
        self.memory.load_program(program, start=200)
        # First line should be at 200
        self.assertEqual(self.memory.read_string(200, 12).strip(), "LD  0100")


class TestVirtualIO(unittest.TestCase):
    """Test IBM 705 Virtual I/O system."""
    
    def setUp(self):
        self.io = VirtualIO()
    
    def test_tape_load_read(self):
        """Load and read tape records."""
        records = ["Record 1", "Record 2", "Record 3"]
        self.io.load_tape(records)
        
        self.assertEqual(self.io.read_record(), "Record 1")
        self.assertEqual(self.io.read_record(), "Record 2")
        self.assertEqual(self.io.read_record(), "Record 3")
        self.assertIsNone(self.io.read_record())  # End of tape
    
    def test_tape_write(self):
        """Write records to output tape."""
        self.io.write_record("Output 1")
        self.io.write_record("Output 2")
        
        output = self.io.get_output()
        self.assertEqual(len(output), 2)
        self.assertEqual(output[0], "Output 1")
        self.assertEqual(output[1], "Output 2")
    
    def test_tape_clear_output(self):
        """Clear output buffer."""
        self.io.write_record("Test")
        self.io.clear_output()
        self.assertEqual(len(self.io.get_output()), 0)


class TestCPUState(unittest.TestCase):
    """Test IBM 705 CPU state."""
    
    def setUp(self):
        self.state = CPUState()
    
    def test_initial_state(self):
        """CPU should start in STOP state."""
        self.assertEqual(self.state.program_status, "STOP")
        self.assertEqual(self.state.instruction_address, 0)
        self.assertFalse(self.state.overflow_indicator)
        self.assertFalse(self.state.check_indicator)
        self.assertEqual(self.state.comparison_indicator, 0)
    
    def test_register_sizes(self):
        """Registers should have correct sizes."""
        self.assertEqual(len(self.state.accumulator), IBM705Config.ACCUMULATOR_SIZE)
        self.assertEqual(len(self.state.buffer), IBM705Config.BUFFER_SIZE)
        self.assertEqual(len(self.state.counter), IBM705Config.COUNTER_SIZE)


class TestInstructionSet(unittest.TestCase):
    """Test IBM 705 instruction set."""
    
    def setUp(self):
        self.cpu = IBM705CPU()
        self.cpu.state.program_status = "RUN"
    
    def test_load_store(self):
        """LD and ST instructions."""
        test_data = "TESTDATA12"  # 10 characters (standard field length)
        self.cpu.memory.write_string(100, test_data)
        
        # Load
        self.cpu.instruction_set._load(100, field_length=10)
        
        # Verify accumulator contains data
        acc_str = ''.join(self.cpu.state.accumulator[:len(test_data)])
        self.assertEqual(acc_str.strip(), test_data.strip())
        
        # Store to new location
        self.cpu.instruction_set._store(200, field_length=10)
        
        # Verify memory contains data
        result = self.cpu.memory.read_string(200, len(test_data))
        self.assertEqual(result.strip(), test_data.strip())
    
    def test_add(self):
        """AD instruction."""
        # Set up values
        self.cpu.memory.write_string(100, "0000000050")
        self.cpu.memory.write_string(110, "0000000030")
        
        # Load first value
        self.cpu.instruction_set._load(100)
        
        # Add second value
        self.cpu.instruction_set._add(110)
        
        # Result should be 80
        acc_val = self.cpu.instruction_set._get_accumulator_value()
        self.assertEqual(acc_val, 80)
    
    def test_subtract(self):
        """SU instruction."""
        self.cpu.memory.write_string(100, "0000000100")
        self.cpu.memory.write_string(110, "0000000040")
        
        self.cpu.instruction_set._load(100)
        self.cpu.instruction_set._subtract(110)
        
        acc_val = self.cpu.instruction_set._get_accumulator_value()
        self.assertEqual(acc_val, 60)
    
    def test_multiply(self):
        """MU instruction."""
        self.cpu.memory.write_string(100, "0000000012")
        self.cpu.memory.write_string(110, "0000000010")
        
        self.cpu.instruction_set._load(100)
        self.cpu.instruction_set._multiply(110)
        
        acc_val = self.cpu.instruction_set._get_accumulator_value()
        self.assertEqual(acc_val, 120)
    
    def test_divide(self):
        """DV instruction."""
        self.cpu.memory.write_string(100, "0000000100")
        self.cpu.memory.write_string(110, "0000000025")
        
        self.cpu.instruction_set._load(100)
        self.cpu.instruction_set._divide(110)
        
        acc_val = self.cpu.instruction_set._get_accumulator_value()
        self.assertEqual(acc_val, 4)
    
    def test_divide_by_zero(self):
        """DV by zero should set check indicator."""
        self.cpu.memory.write_string(100, "0000000100")
        self.cpu.memory.write_string(110, "0000000000")
        
        self.cpu.instruction_set._load(100)
        result = self.cpu.instruction_set._divide(110)
        
        self.assertFalse(result)  # Should fail
        self.assertTrue(self.cpu.state.check_indicator)
    
    def test_compare_less_than(self):
        """CO instruction - less than."""
        self.cpu.memory.write_string(100, "0000000050")
        self.cpu.memory.write_string(110, "0000000100")
        
        self.cpu.instruction_set._load(100)
        self.cpu.instruction_set._compare(110)
        
        self.assertEqual(self.cpu.state.comparison_indicator, -1)
    
    def test_compare_equal(self):
        """CO instruction - equal."""
        self.cpu.memory.write_string(100, "0000000050")
        self.cpu.memory.write_string(110, "0000000050")
        
        self.cpu.instruction_set._load(100)
        self.cpu.instruction_set._compare(110)
        
        self.assertEqual(self.cpu.state.comparison_indicator, 0)
    
    def test_compare_greater_than(self):
        """CO instruction - greater than."""
        self.cpu.memory.write_string(100, "0000000100")
        self.cpu.memory.write_string(110, "0000000050")
        
        self.cpu.instruction_set._load(100)
        self.cpu.instruction_set._compare(110)
        
        self.assertEqual(self.cpu.state.comparison_indicator, 1)
    
    def test_jump(self):
        """J instruction."""
        initial_addr = self.cpu.state.instruction_address
        self.cpu.instruction_set._jump(500)
        self.assertEqual(self.cpu.state.instruction_address, 500)
    
    def test_jump_true(self):
        """JT instruction."""
        self.cpu.state.comparison_indicator = 1
        self.cpu.instruction_set._jump_true(500)
        self.assertEqual(self.cpu.state.instruction_address, 500)
    
    def test_jump_true_no_jump(self):
        """JT instruction - should not jump when false."""
        self.cpu.state.comparison_indicator = -1
        initial_addr = self.cpu.state.instruction_address
        self.cpu.instruction_set._jump_true(500)
        self.assertEqual(self.cpu.state.instruction_address, initial_addr)
    
    def test_jump_false(self):
        """JF instruction."""
        self.cpu.state.comparison_indicator = -1
        self.cpu.instruction_set._jump_false(500)
        self.assertEqual(self.cpu.state.instruction_address, 500)
    
    def test_jump_false_no_jump(self):
        """JF instruction - should not jump when true."""
        self.cpu.state.comparison_indicator = 1
        initial_addr = self.cpu.state.instruction_address
        self.cpu.instruction_set._jump_false(500)
        self.assertEqual(self.cpu.state.instruction_address, initial_addr)
    
    def test_stop(self):
        """SW instruction."""
        result = self.cpu.instruction_set._stop(0)
        self.assertEqual(self.cpu.state.program_status, "HALT")
        self.assertFalse(result)  # Should stop execution
    
    def test_nop(self):
        """NOP instruction."""
        initial_addr = self.cpu.state.instruction_address
        result = self.cpu.instruction_set._nop(0)
        self.assertTrue(result)  # Should continue
        self.assertEqual(self.cpu.state.instruction_address, initial_addr)


class TestCPUIntegration(unittest.TestCase):
    """Test full CPU integration."""
    
    def setUp(self):
        self.cpu = IBM705CPU()
    
    def test_program_load_and_run(self):
        """Load and run a simple program."""
        # Program with explicit 12-character instruction words
        program = """LD  0100    
AD  0110    
ST  0120    
SW  0000    
"""
        self.cpu.load_program(program, start=200)
        
        # Set up data
        self.cpu.memory.write_string(100, "0000000050")
        self.cpu.memory.write_string(110, "0000000030")
        
        # Run
        self.cpu.run(max_instructions=100)
        
        # Check result
        result = self.cpu.memory.read_string(120, 10)
        # Result is left-justified 10-char field: "0000000080"
        self.assertIn("80", result)
        self.assertIn(self.cpu.state.program_status, ["HALT", "STOP"])
    
    def test_cpu_status(self):
        """Get CPU status string."""
        status = self.cpu.get_status()
        self.assertIn("IBM 705 CPU Status", status)
        self.assertIn("Program Status", status)
        self.assertIn("Instructions Executed", status)


class TestMiningProgram(unittest.TestCase):
    """Test mining program integration."""
    
    def setUp(self):
        self.cpu = IBM705CPU()
    
    def test_mining_loop_basic(self):
        """Test basic mining loop execution."""
        # Simple mining program - count from 1 to 10
        # Logic: increment nonce, compare to target, continue if nonce < target
        # Addresses: 200, 212, 224, 236, 248, 260, 272, 284, 296, 308
        # JF jumps when comparison <= 0, so we use JT to continue when nonce > target
        program = """ZT  0100    
LD  0150    
ST  0100    
LD  0100    
AD  0150    
ST  0100    
LD  0120    
CO  0100    
JT  0308    
J   0236    
SW  0000    
"""
        self.cpu.load_program(program, start=200)
        
        # Set up: count to 10
        self.cpu.memory.write_string(100, "0000000000")  # NONCE
        self.cpu.memory.write_string(120, "0000000010")  # TARGET
        self.cpu.memory.write_string(150, "0000000001")  # ONE
        
        # Run
        self.cpu.run(max_instructions=1000)
        
        # Nonce should be 10 (stored as 10-char field: "0000000010")
        nonce = self.cpu.memory.read_string(100, 10)
        self.assertEqual(int(nonce.strip()), 10)
    
    def test_mining_hash_computation(self):
        """Test hash computation steps."""
        # Set up test values
        self.cpu.memory.write_string(110, "0000000005")  # BLOCK_DATA
        self.cpu.memory.write_string(100, "0000000003")  # NONCE
        self.cpu.memory.write_string(160, "0000000002")  # CONSTANT
        self.cpu.memory.write_string(170, "0000000010")  # PRIME
        
        # Manual hash computation: ((5 * 3) + 2) mod 10 = 17 mod 10 = 7
        self.cpu.instruction_set._load(110)  # Load block data
        self.cpu.instruction_set._multiply(100)  # Multiply by nonce
        self.cpu.instruction_set._add(160)  # Add constant
        
        # Get intermediate result
        intermediate = self.cpu.instruction_set._get_accumulator_value()
        self.assertEqual(intermediate, 17)


class TestInstructionParsing(unittest.TestCase):
    """Test instruction parsing."""
    
    def setUp(self):
        self.cpu = IBM705CPU()
    
    def test_parse_two_char_opcode(self):
        """Parse 2-character opcode."""
        opcode, address = self.cpu.parse_instruction("LD  0100")
        self.assertEqual(opcode, "LD")
        self.assertEqual(address, 100)
    
    def test_parse_with_spaces(self):
        """Parse instruction with various spacing."""
        opcode, address = self.cpu.parse_instruction("ST  0200")
        self.assertEqual(opcode, "ST")
        self.assertEqual(address, 200)
    
    def test_parse_unknown_opcode(self):
        """Unknown opcode should default to NOP."""
        opcode, address = self.cpu.parse_instruction("XX  0100")
        self.assertEqual(opcode, "NOP")


if __name__ == "__main__":
    unittest.main(verbosity=2)
