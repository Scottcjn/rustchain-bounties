#!/usr/bin/env python3
"""
Unit tests for RustChain Commodore PET Miner
"""

import unittest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pet_miner import MOS6502, PETFingerprint, RustChainAttestation, PETMiner


class TestMOS6502(unittest.TestCase):
    """Test MOS 6502 CPU emulator"""
    
    def setUp(self):
        self.cpu = MOS6502(memory_size=8192)
    
    def test_initial_state(self):
        """Test CPU initial state"""
        state = self.cpu.get_state()
        self.assertEqual(state['A'], 0x00)
        self.assertEqual(state['X'], 0x00)
        self.assertEqual(state['Y'], 0x00)
        self.assertEqual(state['SP'], 0xFF)
        self.assertEqual(state['PC'], 0x0000)
    
    def test_memory_read_write(self):
        """Test memory read/write operations"""
        self.cpu.write_byte(0x0200, 0x42)
        self.assertEqual(self.cpu.read_byte(0x0200), 0x42)
    
    def test_zero_page_access(self):
        """Test zero page memory access"""
        self.cpu.write_byte(0x0050, 0xAA)
        self.assertEqual(self.cpu.read_byte(0x0050), 0xAA)
    
    def test_stack_operations(self):
        """Test stack push/pop"""
        self.cpu.push_stack(0x12)
        self.cpu.push_stack(0x34)
        val = self.cpu.pop_stack()
        self.assertEqual(val, 0x34)
        val = self.cpu.pop_stack()
        self.assertEqual(val, 0x12)
    
    def test_lda_immediate(self):
        """Test LDA immediate instruction"""
        self.cpu.memory[0x0000] = 0xA9  # LDA immediate
        self.cpu.memory[0x0001] = 0x42  # value
        self.cpu.registers['PC'] = 0x0000
        self.cpu.step()
        self.assertEqual(self.cpu.registers['A'], 0x42)
    
    def test_adc_basic(self):
        """Test ADC (Add with Carry)"""
        self.cpu.registers['A'] = 0x10
        self.cpu.memory[0x0000] = 0x69  # ADC immediate
        self.cpu.memory[0x0001] = 0x20
        self.cpu.registers['PC'] = 0x0000
        self.cpu.step()
        self.assertEqual(self.cpu.registers['A'], 0x30)
    
    def test_cycle_counting(self):
        """Test cycle counting"""
        initial_cycles = self.cpu.cycles
        self.cpu.step()
        self.assertGreater(self.cpu.cycles, initial_cycles)


class TestPETFingerprint(unittest.TestCase):
    """Test PET hardware fingerprinting"""
    
    def setUp(self):
        self.cpu = MOS6502(memory_size=8192)
        self.fingerprint = PETFingerprint(self.cpu)
    
    def test_cycle_timing(self):
        """Test cycle timing measurement"""
        timing = self.fingerprint.measure_cycle_timing()
        self.assertEqual(len(timing), 16)  # 16 hex chars
    
    def test_ieee488_latency(self):
        """Test IEEE-488 bus timing"""
        passed, signature = self.fingerprint.measure_ieee488_latency()
        self.assertTrue(passed)
        self.assertEqual(len(signature), 16)
    
    def test_thermal_profile(self):
        """Test thermal profile measurement"""
        thermal = self.fingerprint.measure_thermal_profile()
        self.assertEqual(len(thermal), 16)
    
    def test_basic_rom_check(self):
        """Test BASIC ROM verification"""
        passed, signature = self.fingerprint.check_basic_rom()
        self.assertTrue(passed)
        self.assertEqual(len(signature), 16)
    
    def test_kernal_rom_check(self):
        """Test Kernal ROM verification"""
        passed, signature = self.fingerprint.check_kernal_rom()
        self.assertTrue(passed)
        self.assertEqual(len(signature), 16)
    
    def test_display_check(self):
        """Test built-in display verification"""
        passed, signature = self.fingerprint.check_built_in_display()
        self.assertTrue(passed)
        self.assertEqual(len(signature), 16)
    
    def test_full_fingerprint(self):
        """Test complete fingerprint generation"""
        fp = self.fingerprint.generate_fingerprint()
        
        self.assertIn('checks', fp)
        self.assertIn('all_passed', fp)
        self.assertIn('fingerprint_hash', fp)
        self.assertEqual(fp['platform'], 'Commodore PET')
        self.assertEqual(fp['cpu'], 'MOS 6502')
        self.assertEqual(fp['year'], 1977)
        self.assertTrue(fp['all_passed'])


class TestRustChainAttestation(unittest.TestCase):
    """Test RustChain attestation generation"""
    
    def setUp(self):
        self.cpu = MOS6502(memory_size=8192)
        self.wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
        self.attestation = RustChainAttestation(self.wallet, self.cpu)
    
    def test_generate_attestation(self):
        """Test attestation generation"""
        att = self.attestation.generate_attestation(epoch=1)
        
        self.assertEqual(att['version'], '1.0')
        self.assertEqual(att['hardware']['platform'], 'Commodore PET')
        self.assertEqual(att['hardware']['cpu'], 'MOS 6502')
        self.assertEqual(att['antiquity_multiplier'], 5.0)
        self.assertEqual(att['wallet'], self.wallet)
        self.assertIn('signature', att)
    
    def test_reward_calculation(self):
        """Test reward calculation"""
        reward = self.attestation.calculate_reward(base_reward=1.5, num_miners=5)
        expected = (1.5 / 5) * 5.0  # base_share * multiplier
        self.assertEqual(reward, expected)
    
    def test_save_load_attestation(self):
        """Test saving and loading attestation"""
        att = self.attestation.generate_attestation(epoch=1)
        test_file = "test_pet_attest.json"
        
        try:
            self.attestation.save_to_file(att, test_file)
            loaded = self.attestation.load_from_file(test_file)
            
            self.assertEqual(loaded['epoch'], att['epoch'])
            self.assertEqual(loaded['wallet'], att['wallet'])
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


class TestPETMiner(unittest.TestCase):
    """Test PET miner application"""
    
    def setUp(self):
        self.wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
        self.miner = PETMiner(self.wallet, memory_kb=8, offline=True)
    
    def test_initialization(self):
        """Test miner initialization"""
        self.assertEqual(self.miner.wallet, self.wallet)
        self.assertEqual(self.miner.epoch, 0)
        self.assertFalse(self.miner.running)
        self.assertTrue(self.miner.offline)
    
    def test_cpu_memory(self):
        """Test CPU memory allocation"""
        self.assertEqual(len(self.miner.cpu.memory), 8 * 1024)
    
    def test_status(self):
        """Test status display (just ensure it doesn't crash)"""
        try:
            self.miner.status()
        except Exception as e:
            self.fail(f"Status display failed: {e}")


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_mining_cycle(self):
        """Test complete mining cycle"""
        wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
        miner = PETMiner(wallet, memory_kb=8, offline=True)
        
        # Run single attestation
        miner.epoch = 0
        miner.run_attestation()
        
        self.assertEqual(miner.epoch, 1)
    
    def test_wallet_generation(self):
        """Test wallet generation"""
        from pet_miner import generate_wallet
        
        wallet1 = generate_wallet()
        wallet2 = generate_wallet()
        
        self.assertTrue(wallet1.startswith('RTC'))
        self.assertTrue(wallet2.startswith('RTC'))
        self.assertNotEqual(wallet1, wallet2)  # Should be unique


if __name__ == '__main__':
    unittest.main()
