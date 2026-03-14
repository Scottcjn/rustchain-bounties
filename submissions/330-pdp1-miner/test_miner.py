#!/usr/bin/env python3
"""
Test Suite for RustChain PDP-1 Miner
=====================================

Comprehensive tests for:
- PDP-1 CPU simulator
- SHA-256 implementation
- Mining functionality
- Attestation generation

Run with: python test_miner.py
"""

import unittest
import json
import sys
from io import StringIO

from pdp1_cpu import PDP1CPU, PDP1Display, PDP1Tape
from sha256_pdp1 import SHA256_PDP1, sha256_pdp1
from attestation import PDP1Attestation
from pdp1_miner import PDP1Miner


class TestPDP1CPU(unittest.TestCase):
    """Test PDP-1 CPU simulator"""
    
    def setUp(self):
        self.cpu = PDP1CPU()
    
    def test_initialization(self):
        """Test CPU initialization"""
        self.assertEqual(self.cpu.ac, 0)
        self.assertEqual(self.cpu.mq, 0)
        self.assertEqual(self.cpu.pc, 0)
        self.assertEqual(len(self.cpu.memory), 4096)
    
    def test_load_and_store(self):
        """Test memory load and store"""
        self.cpu.write_memory(100, 0o123456)
        self.assertEqual(self.cpu.read_memory(100), 0o123456)
    
    def test_add_instruction(self):
        """Test ADD instruction"""
        # LDA 1, ADD 2, STA 3, HALT
        program = [
            0o0600001,  # LDA 1
            0o0400002,  # ADD 2
            0o0620003,  # STA 3
            0o1020000,  # HALT
            0, 25, 17, 0  # Data
        ]
        self.cpu.load_program(program)
        self.cpu.run()
        
        self.assertEqual(self.cpu.read_memory(3), 42)  # 25 + 17
    
    def test_subtract_instruction(self):
        """Test SUB instruction"""
        program = [
            0o0600001,  # LDA 1
            0o0420002,  # SUB 2
            0o0620003,  # STA 3
            0o1020000,  # HALT
            0, 50, 20, 0
        ]
        self.cpu.load_program(program)
        self.cpu.run()
        
        self.assertEqual(self.cpu.read_memory(3), 30)  # 50 - 20
    
    def test_jump_instruction(self):
        """Test JMP instruction"""
        program = [
            0o0020003,  # JMP 3
            0o1020000,  # HALT (skipped)
            0,
            0o0640055,  # LDI 55
            0o1020000,  # HALT
        ]
        self.cpu.load_program(program)
        self.cpu.run()
        
        self.assertEqual(self.cpu.ac, 0o55)
    
    def test_conditional_jump(self):
        """Test conditional jumps"""
        # Test JEQ (jump if equal)
        program = [
            0o0640000,  # LDI 0
            0o0140004,  # JEQ 4
            0o0640077,  # LDI 77 (skipped)
            0o1020000,  # HALT
            0o0640055,  # LDI 55 (executed)
            0o1020000,  # HALT
        ]
        self.cpu.load_program(program)
        self.cpu.run()
        
        self.assertEqual(self.cpu.ac, 0o55)
    
    def test_shift_operations(self):
        """Test shift operations"""
        program = [
            0o0640100,  # LDI 0o100
            0o0740001,  # SHL 1
            0o0620010,  # STA 10
            0o1020000,  # HALT
        ]
        self.cpu.load_program(program)
        self.cpu.run()
        
        self.assertEqual(self.cpu.read_memory(10), 0o200)  # 0o100 << 1
    
    def test_18bit_mask(self):
        """Test 18-bit word masking"""
        value = 0o777777  # Max 18-bit value
        masked = self.cpu.to_18bit(value)
        self.assertLessEqual(masked, 0o777777)
    
    def test_cycle_counting(self):
        """Test cycle counting"""
        program = [
            0o0640001,  # LDI 1
            0o1020000,  # HALT
        ]
        self.cpu.load_program(program)
        self.cpu.run()
        
        self.assertGreater(self.cpu.cycles, 0)


class TestPDP1Display(unittest.TestCase):
    """Test Type 30 CRT display"""
    
    def test_plot_points(self):
        """Test point plotting"""
        display = PDP1Display()
        display.plot(512, 512)
        
        points = display.get_points()
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0], (512, 512, 1.0))
    
    def test_clear_display(self):
        """Test display clear"""
        display = PDP1Display()
        display.plot(100, 100)
        display.clear()
        
        self.assertEqual(len(display.get_points()), 0)
    
    def test_ascii_render(self):
        """Test ASCII rendering"""
        display = PDP1Display()
        display.plot(512, 512)
        
        ascii_art = display.render_ascii(40, 20)
        self.assertIsInstance(ascii_art, str)
        self.assertIn('\n', ascii_art)


class TestSHA256PDP1(unittest.TestCase):
    """Test SHA-256 implementation"""
    
    def setUp(self):
        self.hasher = SHA256_PDP1()
    
    def test_empty_string(self):
        """Test empty string hash"""
        self.hasher.reset()
        self.hasher.update("")
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        self.assertEqual(self.hasher.hexdigest(), expected)
    
    def test_abc(self):
        """Test 'abc' hash"""
        self.hasher.reset()
        self.hasher.update("abc")
        expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        self.assertEqual(self.hasher.hexdigest(), expected)
    
    def test_quick_brown_fox(self):
        """Test 'The quick brown fox...' hash"""
        self.hasher.reset()
        self.hasher.update("The quick brown fox jumps over the lazy dog")
        expected = "d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592"
        self.assertEqual(self.hasher.hexdigest(), expected)
    
    def test_deterministic(self):
        """Test hash is deterministic"""
        data = "test data"
        
        self.hasher.reset()
        self.hasher.update(data)
        hash1 = self.hasher.hexdigest()
        
        self.hasher.reset()
        self.hasher.update(data)
        hash2 = self.hasher.hexdigest()
        
        self.assertEqual(hash1, hash2)
    
    def test_different_inputs(self):
        """Test different inputs produce different hashes"""
        self.hasher.reset()
        self.hasher.update("hello")
        hash1 = self.hasher.hexdigest()
        
        self.hasher.reset()
        self.hasher.update("world")
        hash2 = self.hasher.hexdigest()
        
        self.assertNotEqual(hash1, hash2)
    
    def test_18bit_conversion(self):
        """Test 18-bit word conversion"""
        high, low = self.hasher._from_32bit(0x12345678)
        value = self.hasher._to_32bit(high, low)
        self.assertEqual(value, 0x12345678)


class TestAttestation(unittest.TestCase):
    """Test attestation generation"""
    
    def setUp(self):
        self.attester = PDP1Attestation("RTC4325af95d26d59c3ef025963656d22af638bb96b")
    
    def test_generate_attestation(self):
        """Test attestation generation"""
        attestation = self.attester.generate_attestation()
        
        self.assertEqual(attestation['version'], '1.0.0')
        self.assertEqual(attestation['tier'], 'LEGENDARY')
        self.assertEqual(attestation['hardware']['architecture'], 'PDP-1')
        self.assertEqual(attestation['hardware']['year'], 1959)
        self.assertEqual(attestation['mining']['multiplier'], 5.0)
    
    def test_verify_attestation(self):
        """Test attestation verification"""
        attestation = self.attester.generate_attestation()
        self.assertTrue(self.attester.verify_attestation(attestation))
    
    def test_hardware_id_uniqueness(self):
        """Test hardware IDs are unique"""
        attester1 = PDP1Attestation("wallet1")
        attester2 = PDP1Attestation("wallet2")
        
        # Hardware IDs should be different (random components)
        # Note: There's a tiny chance they could be the same
        self.assertNotEqual(
            attester1.hardware_id['profile']['serial_number'],
            attester2.hardware_id['profile']['serial_number']
        )
    
    def test_attestation_structure(self):
        """Test attestation has all required fields"""
        attestation = self.attester.generate_attestation()
        
        required_fields = [
            'version', 'type', 'tier', 'timestamp',
            'hardware', 'mining', 'signature'
        ]
        
        for field in required_fields:
            self.assertIn(field, attestation)
        
        # Check hardware fields
        hw_fields = ['architecture', 'year', 'word_size_bits', 'hardware_id']
        for field in hw_fields:
            self.assertIn(field, attestation['hardware'])


class TestPDP1Miner(unittest.TestCase):
    """Test PDP-1 miner"""
    
    def test_miner_initialization(self):
        """Test miner initialization"""
        miner = PDP1Miner("RTC4325af95d26d59c3ef025963656d22af638bb96b")
        
        self.assertEqual(miner.ANTIQUITY_MULTIPLIER, 5.0)
        self.assertEqual(miner.PDP1_YEAR, 1959)
        self.assertIsNotNone(miner.wallet)
        self.assertIsNotNone(miner.hardware_id)
    
    def test_create_epoch(self):
        """Test epoch creation"""
        miner = PDP1Miner()
        epoch = miner.create_epoch()
        
        self.assertIn('epoch_id', epoch)
        self.assertIn('timestamp', epoch)
        self.assertEqual(epoch['multiplier'], 5.0)
        self.assertEqual(epoch['pdp1_year'], 1959)
    
    def test_compute_hash(self):
        """Test hash computation"""
        miner = PDP1Miner()
        
        hash1 = miner.compute_hash(b"test", 1)
        hash2 = miner.compute_hash(b"test", 2)
        
        self.assertNotEqual(hash1, hash2)
        self.assertEqual(len(hash1), 32)  # SHA-256 produces 32 bytes
    
    def test_get_stats(self):
        """Test statistics"""
        miner = PDP1Miner()
        stats = miner.get_stats()
        
        self.assertIn('wallet', stats)
        self.assertIn('multiplier', stats)
        self.assertIn('total_hashes', stats)
        self.assertEqual(stats['multiplier'], 5.0)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_mining_cycle(self):
        """Test complete mining cycle"""
        miner = PDP1Miner("RTC4325af95d26d59c3ef025963656d22af638bb96b")
        
        # Mine a few attempts
        result = miner.mine_epoch(max_attempts=100)
        
        self.assertIn('epoch', result)
        self.assertIn('attestation', result)
        self.assertIn('hashes', result)
        self.assertGreater(result['hashes'], 0)
    
    def test_cpu_with_miner(self):
        """Test CPU simulator works with miner"""
        miner = PDP1Miner()
        
        # Run some CPU cycles
        for _ in range(1000):
            miner.cpu.step()
        
        self.assertGreater(miner.cpu.cycles, 0)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPDP1CPU))
    suite.addTests(loader.loadTestsFromTestCase(TestPDP1Display))
    suite.addTests(loader.loadTestsFromTestCase(TestSHA256PDP1))
    suite.addTests(loader.loadTestsFromTestCase(TestAttestation))
    suite.addTests(loader.loadTestsFromTestCase(TestPDP1Miner))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
