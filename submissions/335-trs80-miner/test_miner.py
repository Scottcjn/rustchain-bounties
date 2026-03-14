#!/usr/bin/env python3
"""
TRS-80 Miner Test Suite
Comprehensive tests for the TRS-80 mining implementation
"""

import unittest
import time
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulator import (
    Z80CPU, TRS80Memory, MiniHash8, TRS80Miner, BlockHeader
)


class TestMiniHash8(unittest.TestCase):
    """Test MiniHash-8 hash function"""
    
    def setUp(self):
        self.hasher = MiniHash8()
    
    def test_empty_input(self):
        """Test hashing empty input"""
        result = self.hasher.update(b'')
        self.assertEqual(len(result), 4)
        print(f"  Empty input hash: {result.hex()}")
    
    def test_consistency(self):
        """Test that same input produces same hash"""
        data = b'RUSTCHAIN'
        hash1 = self.hasher.update(data)
        hash2 = self.hasher.update(data)
        self.assertEqual(hash1, hash2)
        print(f"  Consistent hash: {hash1.hex()}")
    
    def test_different_inputs(self):
        """Test that different inputs produce different hashes"""
        hash1 = self.hasher.update(b'BLOCK1')
        hash2 = self.hasher.update(b'BLOCK2')
        self.assertNotEqual(hash1, hash2)
        print(f"  BLOCK1 hash: {hash1.hex()}")
        print(f"  BLOCK2 hash: {hash2.hex()}")
    
    def test_avalanche_effect(self):
        """Test that small input changes cause large output changes"""
        hash1 = self.hasher.update(b'TEST')
        hash2 = self.hasher.update(b'tEST')  # One bit different
        # At least one byte should be different
        differences = sum(1 for a, b in zip(hash1, hash2) if a != b)
        self.assertGreaterEqual(differences, 1)
        print(f"  Avalanche: {differences} bytes different")
    
    def test_hash_distribution(self):
        """Test hash distribution (should be roughly uniform)"""
        hashes = []
        for i in range(256):
            data = bytes([i])
            h = self.hasher.update(data)
            hashes.append(h[0])  # Check first byte distribution
        
        # Check that we get varied results
        unique_values = len(set(hashes))
        self.assertGreater(unique_values, 200)  # Should have good distribution
        print(f"  Distribution: {unique_values}/256 unique first bytes")


class TestBlockHeader(unittest.TestCase):
    """Test block header serialization"""
    
    def test_serialization(self):
        """Test block header to bytes conversion"""
        block = BlockHeader(
            version=1,
            prev_hash=b'\x01\x02\x03\x04\x05\x06\x07\x08',
            timestamp=1234567890,
            difficulty=0x00FFFFFF,
            nonce=42
        )
        
        data = block.to_bytes()
        self.assertEqual(len(data), 32)
        
        # Check nonce position
        self.assertEqual(data[28], 42 & 0xFF)
        self.assertEqual(data[29], (42 >> 8) & 0xFF)
        print(f"  Block serialization: {data.hex()[:64]}...")


class TestZ80CPU(unittest.TestCase):
    """Test Z80 CPU emulation"""
    
    def setUp(self):
        self.cpu = Z80CPU()
    
    def test_register_init(self):
        """Test CPU registers initialize to expected values"""
        self.assertEqual(self.cpu.a, 0)
        self.assertEqual(self.cpu.pc, 0x4400)
        self.assertEqual(self.cpu.sp, 0x47FF)
        print("  CPU registers initialized correctly")
    
    def test_inc_de(self):
        """Test INC DE instruction"""
        self.cpu.set_de(0)
        self.cpu.inc_de()
        self.assertEqual(self.cpu.get_de(), 1)
        
        self.cpu.set_de(255)
        self.cpu.inc_de()
        self.assertEqual(self.cpu.get_de(), 256)
        
        self.cpu.set_de(65535)
        self.cpu.inc_de()
        self.assertEqual(self.cpu.get_de(), 0)  # Wrap around
        print("  INC DE works correctly (including wrap-around)")
    
    def test_cycle_counting(self):
        """Test that cycles are counted"""
        initial_cycles = self.cpu.cycles
        self.cpu.inc_de()
        self.assertGreater(self.cpu.cycles, initial_cycles)
        print(f"  Cycle counting: {self.cpu.cycles - initial_cycles} cycles")


class TestTRS80Memory(unittest.TestCase):
    """Test TRS-80 memory system"""
    
    def setUp(self):
        self.memory = TRS80Memory()
    
    def test_memory_write_read(self):
        """Test basic memory read/write"""
        self.memory.write_byte(0x4500, 0xAB)
        value = self.memory.read_byte(0x4500)
        self.assertEqual(value, 0xAB)
        print("  Memory read/write works")
    
    def test_word_operations(self):
        """Test 16-bit word operations"""
        self.memory.write_word(0x4500, 0x1234)
        value = self.memory.read_word(0x4500)
        self.assertEqual(value, 0x1234)
        print("  Word read/write works (little-endian)")
    
    def test_video_ram_clear(self):
        """Test screen clear"""
        self.memory.clear_screen()
        # Check a few video RAM locations
        for addr in [0x4000, 0x4040, 0x43FF]:
            value = self.memory.read_byte(addr)
            self.assertEqual(value, 0x20)  # Space character
        print("  Video RAM clear works")
    
    def test_string_display(self):
        """Test string display on video RAM"""
        self.memory.clear_screen()
        self.memory.write_string(0, 0, "HELLO TRS-80!")
        
        # Read back first few characters
        for i, char in enumerate("HELLO TRS-80!"):
            addr = 0x4000 + i
            value = self.memory.read_byte(addr)
            self.assertEqual(value, ord(char))
        print("  String display works")


class TestTRS80Miner(unittest.TestCase):
    """Test complete miner system"""
    
    def test_miner_initialization(self):
        """Test miner initializes correctly"""
        miner = TRS80Miner()
        
        # Check display initialized
        display = miner.get_display()
        self.assertIn("RUSTCHAIN", display)
        self.assertIn("TRS-80", display)
        print("  Miner initialization works")
    
    def test_block_initialization(self):
        """Test block initialization"""
        miner = TRS80Miner()
        miner.init_block()
        
        # Check nonce reset
        self.assertEqual(miner.cpu.get_de(), 0)
        print("  Block initialization works")
    
    def test_mining_finds_blocks(self):
        """Test that mining actually finds blocks"""
        miner = TRS80Miner()
        
        # Mine for a short time
        start_hashes = miner.hash_count
        start_time = time.time()
        
        # Run mining step multiple times (with easier difficulty, should find quickly)
        found = False
        for _ in range(1000):
            if miner.mine_step():
                found = True
                break
        
        elapsed = time.time() - start_time
        hashes = miner.hash_count - start_hashes
        
        self.assertTrue(found, "Should find at least one block")
        print(f"  Mining works: found block in {hashes} hashes ({elapsed:.3f}s)")
    
    def test_hash_rate_calculation(self):
        """Test hash rate calculation"""
        miner = TRS80Miner()
        
        # Mine for a bit
        for _ in range(1000):
            miner.mine_step()
        
        elapsed = time.time() - miner.start_time
        if elapsed > 0:
            expected_rate = miner.hash_count / elapsed
            self.assertGreater(expected_rate, 0)
            print(f"  Hash rate: {int(expected_rate)} H/s")


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_mining_cycle(self):
        """Test complete mining cycle"""
        miner = TRS80Miner()
        
        # Mine 3 blocks
        miner.run(max_blocks=3)
        
        self.assertEqual(miner.blocks_found, 3)
        self.assertGreater(miner.hash_count, 0)
        print(f"\n  Integration test passed: {miner.blocks_found} blocks, {miner.hash_count} hashes")
    
    def test_display_updates(self):
        """Test that display updates during mining"""
        miner = TRS80Miner()
        
        initial_display = miner.get_display()
        
        # Mine for a bit
        for _ in range(100):
            miner.mine_step()
        
        updated_display = miner.get_display()
        
        # Display should have changed (nonce at least)
        self.assertNotEqual(initial_display, updated_display)
        print("  Display updates correctly during mining")


def run_tests():
    """Run all tests with verbose output"""
    print("\n" + "=" * 60)
    print("TRS-80 MINER TEST SUITE")
    print("=" * 60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMiniHash8))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockHeader))
    suite.addTests(loader.loadTestsFromTestCase(TestZ80CPU))
    suite.addTests(loader.loadTestsFromTestCase(TestTRS80Memory))
    suite.addTests(loader.loadTestsFromTestCase(TestTRS80Miner))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"TESTS RUN: {result.testsRun}")
    print(f"FAILURES: {len(result.failures)}")
    print(f"ERRORS: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
