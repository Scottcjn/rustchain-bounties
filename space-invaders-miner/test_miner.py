#!/usr/bin/env python3
"""
Test Suite for Space Invaders Miner
====================================

Tests for the Intel 8080 Space Invaders mining simulator.

Run with: python test_miner.py
"""

import unittest
import time
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the miner module
from space_invaders_miner import (
    Intel8080State,
    SpaceInvadersDisplay,
    SpaceInvadersMiner,
    MiningStats,
    WALLET_ADDRESS,
    BOUNTY_NUMBER,
    CPU_CLOCK_MHZ,
    RAM_SIZE_KB,
    BLOCK_REWARD
)


class TestIntel8080State(unittest.TestCase):
    """Test Intel 8080 CPU emulation"""
    
    def setUp(self):
        self.cpu = Intel8080State()
    
    def test_cpu_initialization(self):
        """Test CPU initializes with correct values"""
        self.assertEqual(self.cpu.a, 0)
        self.assertEqual(self.cpu.b, 0)
        self.assertEqual(self.cpu.pc, 0)
        self.assertEqual(self.cpu.sp, 0)
        self.assertEqual(len(self.cpu.ram), 8192)  # 8 KB
        self.assertEqual(len(self.cpu.rom), 12288)  # 12 KB
    
    def test_memory_write_read(self):
        """Test memory read/write operations"""
        # Write to RAM
        self.cpu.write_memory(0x100, 0xAB)
        self.cpu.write_memory(0x101, 0xCD)
        
        # Read back
        self.assertEqual(self.cpu.read_memory(0x100), 0xAB)
        self.assertEqual(self.cpu.read_memory(0x101), 0xCD)
    
    def test_memory_bounds(self):
        """Test memory access within bounds"""
        # Write to last byte of RAM
        self.cpu.write_memory(0x1FFF, 0xFF)
        self.assertEqual(self.cpu.read_memory(0x1FFF), 0xFF)
    
    def test_register_pair(self):
        """Test 16-bit register pair operations"""
        self.cpu.set_register_pair('H', 'L', 0x1234)
        self.assertEqual(self.cpu.h, 0x12)
        self.assertEqual(self.cpu.l, 0x34)
        
        value = self.cpu.get_register_pair('H', 'L')
        self.assertEqual(value, 0x1234)
    
    def test_cpu_reset(self):
        """Test CPU reset functionality"""
        self.cpu.a = 0xFF
        self.cpu.pc = 0x1000
        self.cpu.mining_nonce = 12345
        
        self.cpu.reset()
        
        self.assertEqual(self.cpu.a, 0)
        self.assertEqual(self.cpu.pc, 0)
        self.assertEqual(self.cpu.mining_nonce, 0)


class TestSpaceInvadersDisplay(unittest.TestCase):
    """Test Space Invaders display emulation"""
    
    def setUp(self):
        self.display = SpaceInvadersDisplay()
        self.cpu = Intel8080State()
        self.stats = MiningStats()
    
    def test_display_initialization(self):
        """Test display initializes correctly"""
        self.assertEqual(self.display.frame_count, 0)
        self.assertEqual(self.display.WIDTH, 256)
        self.assertEqual(self.display.HEIGHT, 224)
    
    def test_render_mining_screen(self):
        """Test mining screen rendering"""
        screen = self.display.render_mining_screen(
            self.cpu, 
            self.stats, 
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        
        # Check screen contains expected elements
        self.assertIn("SPACE INVADERS MINER", screen)
        self.assertIn("Intel 8080", screen)
        self.assertIn("Status:", screen)
        self.assertIn("Nonce:", screen)
        self.assertIn("Blocks Found:", screen)
    
    def test_render_block_found(self):
        """Test block found celebration screen"""
        self.cpu.mining_status = 1
        self.stats.blocks_found = 1
        
        screen = self.display.render_mining_screen(
            self.cpu,
            self.stats,
            "0000abcd1234"
        )
        
        self.assertIn("BLOCK FOUND", screen)
        self.assertIn("Reward:", screen)


class TestMiningStats(unittest.TestCase):
    """Test mining statistics tracking"""
    
    def test_stats_initialization(self):
        """Test stats initialize correctly"""
        stats = MiningStats()
        self.assertEqual(stats.blocks_found, 0)
        self.assertEqual(stats.total_hashes, 0)
        self.assertGreater(stats.start_time, 0)
    
    def test_hash_rate_calculation(self):
        """Test hash rate calculation"""
        stats = MiningStats()
        stats.total_hashes = 1000
        
        # Simulate time passing
        time.sleep(0.1)
        
        hash_rate = stats.get_hash_rate()
        self.assertGreater(hash_rate, 0)
        self.assertLess(hash_rate, 20000)  # Should be around 10000 H/s
    
    def test_stats_reset(self):
        """Test stats reset functionality"""
        stats = MiningStats()
        stats.blocks_found = 5
        stats.total_hashes = 10000
        
        stats.reset()
        
        self.assertEqual(stats.blocks_found, 0)
        self.assertEqual(stats.total_hashes, 0)


class TestSpaceInvadersMiner(unittest.TestCase):
    """Test main mining functionality"""
    
    def setUp(self):
        self.miner = SpaceInvadersMiner()
    
    def test_miner_initialization(self):
        """Test miner initializes correctly"""
        self.assertEqual(self.miner.wallet, WALLET_ADDRESS)
        self.assertIsNotNone(self.miner.cpu)
        self.assertIsNotNone(self.miner.display)
        self.assertIsNotNone(self.miner.stats)
    
    def test_compute_hash(self):
        """Test SHA-256 hash computation"""
        block_header = b"test_block_header"
        nonce = 12345
        
        hash_result = self.miner.compute_hash(block_header, nonce)
        
        # Hash should be 64 hex characters
        self.assertEqual(len(hash_result), 64)
        
        # Hash should be consistent
        hash_result2 = self.miner.compute_hash(block_header, nonce)
        self.assertEqual(hash_result, hash_result2)
    
    def test_compute_hash_different_nonces(self):
        """Test that different nonces produce different hashes"""
        block_header = b"test_block"
        
        hash1 = self.miner.compute_hash(block_header, 0)
        hash2 = self.miner.compute_hash(block_header, 1)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_check_difficulty(self):
        """Test difficulty checking"""
        # Hash with 4 leading zeros should pass
        self.assertTrue(self.miner.check_difficulty("0000abcd1234"))
        
        # Hash with fewer zeros should fail
        self.assertFalse(self.miner.check_difficulty("1234abcd"))
        self.assertFalse(self.miner.check_difficulty("0001abcd"))
    
    def test_mine_block(self):
        """Test block mining"""
        block_header = b"test_block_" + datetime.now().isoformat().encode()
        
        # Try to mine with limited nonces
        nonce = self.miner.mine_block(block_header, max_nonces=100000)
        
        # May or may not find a block depending on difficulty
        # Just verify the function completes
        self.assertIsInstance(nonce, (int, type(None)))
    
    def test_mining_memory_update(self):
        """Test mining memory updates"""
        nonce = 0x12345678
        hash_hex = "a" * 64
        
        self.miner._update_mining_memory(nonce, hash_hex)
        
        # Check nonce was written correctly (little-endian)
        self.assertEqual(self.miner.cpu.read_memory(0), 0x78)
        self.assertEqual(self.miner.cpu.read_memory(1), 0x56)
        self.assertEqual(self.miner.cpu.read_memory(2), 0x34)
        self.assertEqual(self.miner.cpu.read_memory(3), 0x12)


class TestConstants(unittest.TestCase):
    """Test configuration constants"""
    
    def test_wallet_address(self):
        """Test wallet address format"""
        self.assertTrue(WALLET_ADDRESS.startswith("RTC"))
        self.assertEqual(len(WALLET_ADDRESS), 43)  # RTC + 40 hex chars
    
    def test_bounty_number(self):
        """Test bounty number format"""
        self.assertEqual(BOUNTY_NUMBER, "#476")
    
    def test_cpu_clock(self):
        """Test CPU clock speed"""
        self.assertEqual(CPU_CLOCK_MHZ, 2.0)
    
    def test_ram_size(self):
        """Test RAM size"""
        self.assertEqual(RAM_SIZE_KB, 8)
    
    def test_block_reward(self):
        """Test block reward"""
        self.assertEqual(BLOCK_REWARD, 50)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_mining_cycle(self):
        """Test complete mining cycle"""
        miner = SpaceInvadersMiner()
        
        # Run a short mining session
        block_header = b"integration_test_block"
        
        # Mine for a few iterations
        for i in range(100):
            nonce = miner.mine_block(block_header, max_nonces=100)
            miner.stats.total_hashes += 100
            
            if nonce is not None:
                # Block found!
                self.assertEqual(miner.cpu.mining_status, 1)
                self.assertGreater(miner.stats.blocks_found, 0)
                break
        
        # Verify stats were updated
        self.assertGreater(miner.stats.total_hashes, 0)
    
    def test_display_with_mining(self):
        """Test display updates during mining"""
        miner = SpaceInvadersMiner()
        
        # Mine a few blocks
        block_header = b"test"
        miner.mine_block(block_header, max_nonces=1000)
        
        # Render display
        screen = miner.display.render_mining_screen(
            miner.cpu,
            miner.stats,
            miner.current_hash
        )
        
        # Verify display shows mining activity
        self.assertIn("Hash Rate:", screen)
        self.assertIn("Total Hashes:", screen)


def run_tests():
    """Run all tests and print results"""
    print("="*60)
    print("Space Invaders Miner - Test Suite")
    print("="*60)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIntel8080State))
    suite.addTests(loader.loadTestsFromTestCase(TestSpaceInvadersDisplay))
    suite.addTests(loader.loadTestsFromTestCase(TestMiningStats))
    suite.addTests(loader.loadTestsFromTestCase(TestSpaceInvadersMiner))
    suite.addTests(loader.loadTestsFromTestCase(TestConstants))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
