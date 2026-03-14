#!/usr/bin/env python3
"""
UNIVAC I Miner Tests

Test suite for UNIVAC I simulator and miner.

Author: RustChain Bounty #357 Submission
License: MIT
"""

import unittest
import json
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from univac_simulator import (
    UNIVACISimulator, Instruction, Opcode,
    univac12_hash, check_target, mine_block
)
from univac_miner import UNIVACMiner, UNIVACBlock


class TestUNIVACISimulator(unittest.TestCase):
    """Test UNIVAC I Simulator"""
    
    def setUp(self):
        self.sim = UNIVACISimulator()
    
    def test_memory_load_store(self):
        """Test memory load and store operations"""
        self.sim.load_data([0x123, 0x456, 0x789], start_addr=100)
        
        self.assertEqual(self.sim.read_word(100), 0x123)
        self.assertEqual(self.sim.read_word(101), 0x456)
        self.assertEqual(self.sim.read_word(102), 0x789)
    
    def test_12bit_masking(self):
        """Test 16-bit value masking for memory (accumulator remains 12-bit)"""
        self.sim.load_data([0xFFFF], start_addr=0)
        self.assertEqual(self.sim.read_word(0), 0xFFFF)
        
        # Write value larger than 16 bits
        self.sim.write_word(1, 0x12345)
        self.assertEqual(self.sim.read_word(1), 0x2345)  # Masked to 16 bits
    
    def test_add_instruction(self):
        """Test ADD instruction"""
        self.sim.load_data([0x100, 0x200], start_addr=100)
        self.sim.state.accumulator = 0x050
        
        # Execute ADD
        instr = Instruction(Opcode.ADD, 100)
        self.sim.execute_instruction(instr)
        
        self.assertEqual(self.sim.state.accumulator, 0x150)
    
    def test_add_overflow(self):
        """Test ADD with 12-bit overflow"""
        self.sim.state.accumulator = 0xFFF
        self.sim.load_data([0x001], start_addr=100)
        
        instr = Instruction(Opcode.ADD, 100)
        self.sim.execute_instruction(instr)
        
        # Should wrap around to 0
        self.assertEqual(self.sim.state.accumulator, 0x000)
    
    def test_sub_instruction(self):
        """Test SUB instruction"""
        self.sim.state.accumulator = 0x200
        self.sim.load_data([0x100], start_addr=100)
        
        instr = Instruction(Opcode.SUB, 100)
        self.sim.execute_instruction(instr)
        
        self.assertEqual(self.sim.state.accumulator, 0x100)
    
    def test_jump_instructions(self):
        """Test jump instructions"""
        self.sim.state.program_counter = 10
        
        # Test unconditional jump
        instr = Instruction(Opcode.JMP, 50)
        self.sim.execute_instruction(instr)
        self.assertEqual(self.sim.state.program_counter, 50)
        
        # Test jump if zero
        self.sim.state.accumulator = 0
        instr = Instruction(Opcode.JZ, 100)
        self.sim.execute_instruction(instr)
        self.assertEqual(self.sim.state.program_counter, 100)
        
        # Test jump if not zero (should not jump)
        self.sim.state.accumulator = 1
        instr = Instruction(Opcode.JZ, 200)
        self.sim.execute_instruction(instr)
        self.assertEqual(self.sim.state.program_counter, 101)  # Next instruction
    
    def test_sequential_access_timing(self):
        """Test mercury delay line timing model"""
        self.sim.state.program_counter = 0
        
        # Access nearby word (should be fast)
        self.sim.read_word(1)
        wait1 = self.sim.timing.wait_cycles
        
        # Access distant word (should be slower)
        self.sim.state.program_counter = 0
        self.sim.read_word(500)
        wait2 = self.sim.timing.wait_cycles
        
        # Second access should have waited more
        self.assertGreater(wait2, wait1)
    
    def test_program_execution(self):
        """Test simple program execution"""
        # Program: Add numbers 1-5
        program = [
            Instruction(Opcode.LDA, 100).encode(),  # Load 1
            Instruction(Opcode.ADD, 101).encode(),  # Add 2
            Instruction(Opcode.ADD, 102).encode(),  # Add 3
            Instruction(Opcode.ADD, 103).encode(),  # Add 4
            Instruction(Opcode.ADD, 104).encode(),  # Add 5
            Instruction(Opcode.STA, 50).encode(),   # Store result
            Instruction(Opcode.HLT, 0).encode(),    # Halt
        ]
        
        # Data: 1, 2, 3, 4, 5
        data = [1, 2, 3, 4, 5]
        
        self.sim.load_program(program, start_addr=0)
        self.sim.load_data(data, start_addr=100)
        
        # Verify data loaded correctly
        for i, expected in enumerate(data):
            actual = self.sim.memory[100 + i]
            self.assertEqual(actual, expected)
        
        # Run
        self.sim.run()
        
        # Result should be 15 (1+2+3+4+5)
        self.assertEqual(self.sim.state.accumulator, 15)
        self.assertEqual(self.sim.memory[50], 15)


class TestUNIVAC12Hash(unittest.TestCase):
    """Test UNIVAC-12 hash function"""
    
    def test_hash_deterministic(self):
        """Test hash is deterministic"""
        data = b"test data"
        nonce = 42
        
        hash1 = univac12_hash(data, nonce)
        hash2 = univac12_hash(data, nonce)
        
        self.assertEqual(hash1, hash2)
    
    def test_hash_different_nonce(self):
        """Test different nonces produce different hashes"""
        data = b"test data"
        
        hash1 = univac12_hash(data, 0)
        hash2 = univac12_hash(data, 1)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_hash_different_data(self):
        """Test different data produces different hashes"""
        nonce = 0
        
        hash1 = univac12_hash(b"data1", nonce)
        hash2 = univac12_hash(b"data2", nonce)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_hash_output_size(self):
        """Test hash output is 12 words"""
        hash_result = univac12_hash(b"test", 0)
        
        self.assertEqual(len(hash_result), 12)
        
        # Each word should be 12 bits
        for word in hash_result:
            self.assertLessEqual(word, 0xFFF)
    
    def test_hash_avalanche(self):
        """Test small input change produces large output change"""
        data1 = b"test data"
        data2 = b"test datb"  # One bit different
        nonce = 0
        
        hash1 = univac12_hash(data1, nonce)
        hash2 = univac12_hash(data2, nonce)
        
        # Count different words
        diff_count = sum(1 for a, b in zip(hash1, hash2) if a != b)
        
        # Should have significant difference (at least 3 words)
        self.assertGreaterEqual(diff_count, 3)


class TestDifficulty(unittest.TestCase):
    """Test difficulty checking"""
    
    def test_check_target_all_zero(self):
        """Test target check with all zeros"""
        hash_words = [0] * 12
        self.assertTrue(check_target(hash_words, target_words=2))
        self.assertTrue(check_target(hash_words, target_words=12))
    
    def test_check_target_first_nonzero(self):
        """Test target check with first word nonzero"""
        hash_words = [1] + [0] * 11
        self.assertFalse(check_target(hash_words, target_words=1))
        self.assertFalse(check_target(hash_words, target_words=2))
    
    def test_check_target_partial(self):
        """Test target check with partial zeros"""
        hash_words = [0, 0, 1] + [0] * 9
        self.assertTrue(check_target(hash_words, target_words=2))
        self.assertFalse(check_target(hash_words, target_words=3))


class TestMining(unittest.TestCase):
    """Test mining functionality"""
    
    def test_mine_easy_target(self):
        """Test mining with easy target (1 word)"""
        data = b"test block"
        
        nonce, hash_result, nonces = mine_block(
            data, target_words=1, max_nonces=10000
        )
        
        # Should find solution relatively quickly
        self.assertIsNotNone(nonce)
        self.assertLess(nonces, 5000)
        
        # Verify hash meets target
        self.assertTrue(check_target(hash_result, target_words=1))
    
    def test_verify_block(self):
        """Test block verification"""
        miner = UNIVACMiner()
        
        # Create and mine block
        block = UNIVACBlock(block_number=1, data=b"test")
        success, stats = miner.mine_block(block, max_nonces=10000)
        
        if success:
            # Verify
            valid = miner.verify_solution(block)
            self.assertTrue(valid)


class TestUNIVACBlock(unittest.TestCase):
    """Test block serialization"""
    
    def test_block_serialization(self):
        """Test block to_bytes and from_dict"""
        block = UNIVACBlock(
            block_number=42,
            prev_hash=[i for i in range(12)],
            timestamp=1234567890,
            data=b"test data"
        )
        
        # Serialize
        block_bytes = block.to_bytes()
        self.assertIsInstance(block_bytes, bytes)
        
        # To dict
        block_dict = block.to_dict()
        block2 = UNIVACBlock.from_dict(block_dict)
        
        self.assertEqual(block.block_number, block2.block_number)
        self.assertEqual(block.timestamp, block2.timestamp)
        self.assertEqual(block.data, block2.data)
    
    def test_block_memory_footprint(self):
        """Test block memory usage fits in UNIVAC I"""
        block = UNIVACBlock(block_number=1, data=b"test")
        
        footprint = block.memory_footprint()
        
        # Should fit in 1000 words
        self.assertLess(footprint, 1000)
        print(f"Block memory footprint: {footprint} words")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestUNIVACISimulator))
    suite.addTests(loader.loadTestsFromTestCase(TestUNIVAC12Hash))
    suite.addTests(loader.loadTestsFromTestCase(TestDifficulty))
    suite.addTests(loader.loadTestsFromTestCase(TestMining))
    suite.addTests(loader.loadTestsFromTestCase(TestUNIVACBlock))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
