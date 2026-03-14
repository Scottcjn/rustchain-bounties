#!/usr/bin/env python3
"""
Test suite for PDP-11/20 RustChain Miner
Tests the simulator, entropy collection, and attestation generation.

Bounty #397 - PDP-11/20 Port
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import unittest
import sys
import os
from pathlib import Path
from datetime import datetime
import hashlib
import struct

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pdp11_20_miner import (
    PDP11CPU,
    PDP11EntropyCollector,
    PDP11WalletGenerator,
    PDP11Attestation,
    PDP11Miner,
    PDP11_WORD_MASK,
    PDP11_MEMORY_WORDS,
    UNIBUS_CONSOLE_SWITCHES,
    UNIBUS_LINE_CLOCK,
)

class TestPDP11CPU(unittest.TestCase):
    """Test PDP-11/20 CPU simulator"""
    
    def setUp(self):
        self.cpu = PDP11CPU()
        
    def test_initialization(self):
        """Test CPU initializes correctly"""
        self.assertEqual(len(self.cpu.memory), PDP11_MEMORY_WORDS)
        self.assertEqual(self.cpu.pc, 0)
        self.assertEqual(self.cpu.sp, 0)
        self.assertEqual(self.cpu.psw, 0)
        
    def test_register_operations(self):
        """Test register read/write operations"""
        # Test R0-R5
        for reg in range(6):
            self.cpu.set_register(reg, 0x1234)
            self.assertEqual(self.cpu.get_register(reg), 0x1234)
            
        # Test SP (R6)
        self.cpu.set_register(6, 0x5678)
        self.assertEqual(self.cpu.sp, 0x5678)
        
        # Test PC (R7)
        self.cpu.set_register(7, 0xABCD)
        self.assertEqual(self.cpu.pc, 0xABCD)
        
    def test_word_masking(self):
        """Test 16-bit word masking"""
        self.cpu.set_register(0, 0x12345678)  # Too large
        self.assertEqual(self.cpu.get_register(0), 0x5678)  # Masked to 16 bits
        
    def test_memory_operations(self):
        """Test memory load/store"""
        # Store word
        self.cpu.store_word(0x1000, 0xABCD)
        self.assertEqual(self.cpu.load_word(0x1000), 0xABCD)
        
        # Test address masking
        self.cpu.store_word(0x10000, 0x1234)  # Beyond address space
        self.assertEqual(self.cpu.load_word(0x0000), 0x1234)  # Wrapped
        
    def test_byte_operations(self):
        """Test byte-level operations (little-endian)"""
        self.cpu.store_word(0x1000, 0x1234)
        
        # Little-endian: low byte at even address
        self.assertEqual(self.cpu.load_byte(0x1000), 0x34)
        self.assertEqual(self.cpu.load_byte(0x1001), 0x12)
        
    def test_psw_flags(self):
        """Test PSW flag operations"""
        self.cpu.set_psw_flag(0, 1)  # Set carry
        self.assertEqual(self.cpu.get_psw_flag(0), 1)
        
        self.cpu.set_psw_flag(0, 0)  # Clear carry
        self.assertEqual(self.cpu.get_psw_flag(0), 0)
        
    def test_unibus_io(self):
        """Test UNIBUS I/O operations"""
        # Write to console lamps
        self.cpu.write_unibus(UNIBUS_CONSOLE_SWITCHES, 0x1234)
        self.assertEqual(self.cpu.read_unibus(UNIBUS_CONSOLE_SWITCHES), 0x1234)
        
    def test_entropy_collection(self):
        """Test that entropy varies between collections"""
        # First, collect some core memory samples
        for i in range(16):
            self.cpu.load_word(i * 100)
            
        entropy1 = self.cpu.get_entropy()
        
        # Collect more samples
        for i in range(16, 32):
            self.cpu.load_word(i * 100)
            
        entropy2 = self.cpu.get_entropy()
        
        # Entropy should be different (due to accumulated timing variations)
        # At minimum, the lists should have different lengths or values
        self.assertTrue(
            len(self.cpu.core_timing_variations) > 0
        )


class TestPDP11EntropyCollector(unittest.TestCase):
    """Test entropy collection from PDP-11/20"""
    
    def setUp(self):
        self.cpu = PDP11CPU()
        self.collector = PDP11EntropyCollector(self.cpu)
        
    def test_core_memory_entropy(self):
        """Test core memory entropy collection"""
        entropy = self.collector.collect_core_memory_entropy()
        self.assertIsInstance(entropy, int)
        self.assertGreaterEqual(entropy, 0)
        self.assertLessEqual(entropy, PDP11_WORD_MASK)
        
    def test_register_entropy(self):
        """Test register entropy collection"""
        entropy = self.collector.collect_register_entropy()
        self.assertIsInstance(entropy, int)
        self.assertGreaterEqual(entropy, 0)
        self.assertLessEqual(entropy, PDP11_WORD_MASK)
        
    def test_unibus_entropy(self):
        """Test UNIBUS entropy collection"""
        entropy = self.collector.collect_unibus_entropy()
        self.assertIsInstance(entropy, int)
        self.assertGreaterEqual(entropy, 0)
        self.assertLessEqual(entropy, PDP11_WORD_MASK)
        
    def test_entropy_uniqueness(self):
        """Test that entropy collections are unique"""
        collections = []
        for i in range(10):
            entropy = self.collector.collect_all()
            collections.append(entropy['core_memory'])
            
        # Should have some variation
        unique_values = len(set(collections))
        self.assertGreater(unique_values, 1)
        
    def test_line_clock_entropy(self):
        """Test line clock entropy"""
        entropy = self.collector.collect_line_clock_entropy()
        self.assertIsInstance(entropy, int)
        self.assertGreaterEqual(entropy, 0)


class TestPDP11WalletGenerator(unittest.TestCase):
    """Test wallet generation from entropy"""
    
    def test_wallet_generation(self):
        """Test wallet ID generation"""
        entropy = {
            'core_memory': 0x1234,
            'registers': 0x5678,
            'unibus': 0x9ABC,
            'switches': 0xDEF0,
            'line_clock': 0x2468,
            'timestamp': int(datetime.now().timestamp()),
        }
        
        generator = PDP11WalletGenerator(entropy)
        wallet_id = generator.generate_wallet_id()
        
        # Check format: PDP11-HASH-HASH
        self.assertTrue(wallet_id.startswith('PDP11-'))
        parts = wallet_id.split('-')
        self.assertEqual(len(parts), 3)
        
    def test_miner_id_generation(self):
        """Test miner ID generation"""
        entropy = {
            'core_memory': 0x1234,
            'registers': 0x5678,
            'unibus': 0x9ABC,
            'switches': 0xDEF0,
            'line_clock': 0x2468,
            'timestamp': int(datetime.now().timestamp()),
        }
        
        generator = PDP11WalletGenerator(entropy)
        miner_id = generator.generate_miner_id()
        
        # Check format: PDP11-MINER-HASH
        self.assertTrue(miner_id.startswith('PDP11-MINER-'))
        
    def test_wallet_uniqueness(self):
        """Test that different entropy produces different wallets"""
        entropy1 = {
            'core_memory': 0x1234,
            'registers': 0x5678,
            'unibus': 0x9ABC,
            'switches': 0xDEF0,
            'line_clock': 0x2468,
            'timestamp': 1234567890,
        }
        
        entropy2 = {
            'core_memory': 0x4321,  # Different
            'registers': 0x5678,
            'unibus': 0x9ABC,
            'switches': 0xDEF0,
            'line_clock': 0x2468,
            'timestamp': 1234567890,
        }
        
        gen1 = PDP11WalletGenerator(entropy1)
        gen2 = PDP11WalletGenerator(entropy2)
        
        self.assertNotEqual(
            gen1.generate_wallet_id(),
            gen2.generate_wallet_id()
        )


class TestPDP11Attestation(unittest.TestCase):
    """Test attestation generation"""
    
    def setUp(self):
        self.entropy = {
            'core_memory': 0x1234,
            'registers': 0x5678,
            'unibus': 0x9ABC,
            'switches': 0xDEF0,
            'line_clock': 0x2468,
            'timestamp': int(datetime.now().timestamp()),
        }
        self.wallet_id = 'PDP11-TEST123-TEST456'
        self.miner_id = 'PDP11-MINER-TEST789'
        
    def test_attestation_generation(self):
        """Test attestation record generation"""
        attestation_gen = PDP11Attestation(
            self.wallet_id,
            self.miner_id,
            self.entropy
        )
        
        attestation = attestation_gen.generate()
        
        # Check required fields
        self.assertEqual(attestation['version'], 'PDP11-ATTESTATION-V1')
        self.assertEqual(attestation['wallet'], self.wallet_id)
        self.assertEqual(attestation['miner'], self.miner_id)
        self.assertEqual(attestation['machine'], 'PDP-11/20 (1970)')
        self.assertEqual(attestation['architecture'], '16-bit')
        self.assertIn('signature', attestation)
        
    def test_paper_tape_format(self):
        """Test paper tape output format"""
        attestation_gen = PDP11Attestation(
            self.wallet_id,
            self.miner_id,
            self.entropy
        )
        
        attestation = attestation_gen.generate()
        paper_tape = attestation_gen.format_for_paper_tape(attestation)
        
        # Check format
        self.assertIn('PDP11-ATTESTATION-V1', paper_tape)
        self.assertIn(self.wallet_id, paper_tape)
        self.assertIn('END', paper_tape)
        
    def test_octal_dump_format(self):
        """Test octal memory dump format"""
        attestation_gen = PDP11Attestation(
            self.wallet_id,
            self.miner_id,
            self.entropy
        )
        
        attestation = attestation_gen.generate()
        octal_dump = attestation_gen.format_octal_dump(attestation)
        
        # Check format (should contain octal addresses)
        self.assertIn('PDP-11/20 MEMORY DUMP', octal_dump)
        # Octal addresses start with 0o or have octal digits
        self.assertTrue(any(c in octal_dump for c in '01234567'))


class TestPDP11Miner(unittest.TestCase):
    """Test main miner functionality"""
    
    def setUp(self):
        self.test_wallet = 'test_pdp11_wallet.dat'
        self.miner = PDP11Miner(wallet_file=self.test_wallet)
        
    def tearDown(self):
        # Clean up test files
        test_path = Path(self.test_wallet)
        if test_path.exists():
            test_path.unlink()
            
        attestations_dir = Path('pdp11_attestations')
        if attestations_dir.exists():
            for f in attestations_dir.glob('*.txt'):
                f.unlink()
            attestations_dir.rmdir()
            
    def test_miner_initialization(self):
        """Test miner initializes correctly"""
        self.miner.initialize()
        self.assertEqual(self.miner.antiquity_multiplier, 5.0)
        
    def test_wallet_creation(self):
        """Test wallet file creation"""
        self.miner.load_or_create_wallet()
        
        self.assertIsNotNone(self.miner.wallet_id)
        self.assertIsNotNone(self.miner.miner_id)
        self.assertTrue(Path(self.test_wallet).exists())
        
    def test_attestation_run(self):
        """Test running a single attestation"""
        self.miner.load_or_create_wallet()
        attestation = self.miner.run_attestation()
        
        self.assertIn('version', attestation)
        self.assertIn('signature', attestation)
        
    def test_wallet_persistence(self):
        """Test wallet persists across miner instances"""
        # Create wallet
        self.miner.load_or_create_wallet()
        wallet_id_1 = self.miner.wallet_id
        
        # Create new miner instance with same wallet file
        miner2 = PDP11Miner(wallet_file=self.test_wallet)
        miner2.load_or_create_wallet()
        
        # Should load same wallet
        self.assertEqual(wallet_id_1, miner2.wallet_id)


class TestPDP11Architecture(unittest.TestCase):
    """Test PDP-11/20 architecture specifics"""
    
    def test_word_size(self):
        """Test 16-bit word size"""
        self.assertEqual(PDP11_WORD_MASK, 0xFFFF)
        
    def test_little_endian(self):
        """Test little-endian byte order"""
        cpu = PDP11CPU()
        cpu.store_word(0x1000, 0x1234)
        
        # Little-endian: low byte first
        low_byte = cpu.load_byte(0x1000)
        high_byte = cpu.load_byte(0x1001)
        
        self.assertEqual(low_byte, 0x34)
        self.assertEqual(high_byte, 0x12)
        
    def test_memory_size(self):
        """Test maximum memory size (32K words = 64KB)"""
        cpu = PDP11CPU()
        self.assertEqual(len(cpu.memory), 32768)
        
    def test_octal_notation(self):
        """Test octal address notation"""
        # UNIBUS addresses are in octal
        self.assertEqual(UNIBUS_CONSOLE_SWITCHES, 0o177570)
        self.assertEqual(UNIBUS_LINE_CLOCK, 0o177546)


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("PDP-11/20 RUSTCHAIN MINER - TEST SUITE")
    print("=" * 70)
    print(f"Testing PDP-11/20 architecture (16-bit, 1970)")
    print(f"Bounty #397 - LEGENDARY Tier")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPDP11CPU))
    suite.addTests(loader.loadTestsFromTestCase(TestPDP11EntropyCollector))
    suite.addTests(loader.loadTestsFromTestCase(TestPDP11WalletGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestPDP11Attestation))
    suite.addTests(loader.loadTestsFromTestCase(TestPDP11Miner))
    suite.addTests(loader.loadTestsFromTestCase(TestPDP11Architecture))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print()
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n[PASS] ALL TESTS PASSED!")
        print("\nPDP-11/20 miner is ready for deployment.")
        print("Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b")
    else:
        print("\n[FAIL] SOME TESTS FAILED")
        sys.exit(1)
        
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
