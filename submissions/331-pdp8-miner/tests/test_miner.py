#!/usr/bin/env python3
"""
Tests for PDP-8 RustChain Miner
================================

Run with: python -m pytest tests/test_miner.py -v
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdp8_simulator import PDP8CPU, RustChainMiner, MEMORY_SIZE, WORD_MASK


class TestPDP8CPU:
    """Test PDP-8 CPU implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.cpu = PDP8CPU()
    
    def test_initial_state(self):
        """Test CPU initializes correctly"""
        assert self.cpu.ac == 0
        assert self.cpu.pc == 0
        assert self.cpu.l == 0
        assert len(self.cpu.memory) == MEMORY_SIZE
    
    def test_memory_read_write(self):
        """Test memory operations"""
        self.cpu.write_memory(100, 0x123)
        assert self.cpu.read_memory(100) == 0x123
        
        # Test word masking
        self.cpu.write_memory(0, 0xFFFF)
        assert self.cpu.read_memory(0) == WORD_MASK
    
    def test_memory_wraparound(self):
        """Test memory address wraparound"""
        self.cpu.write_memory(MEMORY_SIZE, 0x100)
        assert self.cpu.read_memory(0) == 0x100
    
    def test_instruction_and(self):
        """Test AND instruction"""
        self.cpu.ac = 0xFFF
        self.cpu.write_memory(0x100, 0x0F0)
        instruction = 0o0000 | 0x100  # AND 0x100
        self.cpu.execute(instruction)
        assert self.cpu.ac == 0x0F0
    
    def test_instruction_tad(self):
        """Test TAD (add) instruction"""
        self.cpu.ac = 0x100
        self.cpu.write_memory(0x100, 0x050)
        instruction = 0o1000 | 0x100  # TAD 0x100
        self.cpu.execute(instruction)
        assert self.cpu.ac == 0x150
    
    def test_instruction_tad_carry(self):
        """Test TAD with carry"""
        self.cpu.ac = WORD_MASK
        self.cpu.l = 0
        self.cpu.write_memory(0x100, 1)
        instruction = 0o1000 | 0x100  # TAD 0x100
        self.cpu.execute(instruction)
        assert self.cpu.ac == 0
        assert self.cpu.l == 1
    
    def test_instruction_isz(self):
        """Test ISZ (increment and skip if zero)"""
        self.cpu.write_memory(0x100, WORD_MASK - 1)
        initial_pc = self.cpu.pc
        instruction = 0o2000 | 0x100  # ISZ 0x100
        self.cpu.execute(instruction)
        assert self.cpu.read_memory(0x100) == 0
        assert self.cpu.pc == (initial_pc + 1) & WORD_MASK  # Skipped
    
    def test_instruction_dca(self):
        """Test DCA (deposit and clear AC)"""
        self.cpu.ac = 0xABC
        instruction = 0o3000 | 0x100  # DCA 0x100
        self.cpu.execute(instruction)
        assert self.cpu.read_memory(0x100) == 0xABC
        assert self.cpu.ac == 0
    
    def test_instruction_jmp(self):
        """Test JMP instruction"""
        instruction = 0o5000 | 0x200  # JMP 0x200
        self.cpu.execute(instruction)
        assert self.cpu.pc == 0x200
    
    def test_opr_iac(self):
        """Test OPR IAC (increment AC)"""
        self.cpu.ac = 0x100
        instruction = 0o7001  # IAC
        self.cpu.execute(instruction)
        assert self.cpu.ac == 0x101
    
    def test_opr_cma(self):
        """Test OPR CMA (complement AC)"""
        self.cpu.ac = 0x0F0
        instruction = 0o7040  # CMA
        self.cpu.execute(instruction)
        assert self.cpu.ac == (~0x0F0) & WORD_MASK
    
    def test_opr_ral(self):
        """Test OPR RAL (rotate left)"""
        self.cpu.ac = 0x400  # Bit 10 set
        self.cpu.l = 0
        instruction = 0o7011  # RAL
        self.cpu.execute(instruction)
        assert self.cpu.ac == 0x800
        assert self.cpu.l == 0
    
    def test_hardware_fingerprint(self):
        """Test hardware fingerprint generation"""
        fp1 = self.cpu.generate_hardware_fingerprint()
        fp2 = self.cpu.generate_hardware_fingerprint()
        
        # Fingerprints should be consistent within same session
        assert fp1 == fp2
        assert 0 <= fp1 <= WORD_MASK


class TestRustChainMiner:
    """Test RustChain Miner implementation"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.cpu = PDP8CPU()
        self.miner = RustChainMiner(self.cpu)
    
    def test_miner_initialization(self):
        """Test miner initializes correctly"""
        assert self.miner.cpu is self.cpu
        assert self.miner.wallet is None
        assert len(self.miner.attestations) == 0
    
    def test_entropy_collection(self):
        """Test entropy collection"""
        self.miner.collect_entropy(32)
        assert len(self.miner.entropy_pool) == 32
        assert all(0 <= e <= WORD_MASK for e in self.miner.entropy_pool)
    
    def test_wallet_generation(self):
        """Test wallet generation"""
        wallet = self.miner.generate_wallet()
        assert wallet.startswith("RTC")
        assert len(wallet) == 43  # RTC + 40 hex chars
    
    def test_attestation_creation(self):
        """Test attestation creation"""
        self.miner.collect_entropy(32)
        self.miner.generate_wallet()
        attestation = self.miner.create_attestation()
        
        assert 'epoch' in attestation
        assert 'timestamp' in attestation
        assert 'hardware_fingerprint' in attestation
        assert 'attestation_hash' in attestation
        assert 'antiquity_multiplier' in attestation
        assert attestation['antiquity_multiplier'] == 5.0
        assert attestation['platform'] == 'PDP-8 (1965)'
    
    def test_multiple_attestations(self):
        """Test multiple attestation generation"""
        self.miner.collect_entropy(32)
        self.miner.generate_wallet()
        
        attestations = []
        for _ in range(5):
            attestations.append(self.miner.create_attestation())
        
        # Each attestation should have unique epoch
        epochs = [a['epoch'] for a in attestations]
        assert len(set(epochs)) == 5
        
        # Epochs should be sequential
        for i in range(1, len(epochs)):
            assert epochs[i] == epochs[i-1] + 1
    
    def test_miner_run(self):
        """Test full miner run"""
        attestations = self.miner.run_miner(epochs=3)
        assert len(attestations) == 3
        
        # All attestations should have correct multiplier
        for att in attestations:
            assert att['antiquity_multiplier'] == 5.0
    
    def test_memory_map(self):
        """Test miner memory map"""
        # Check that memory locations are within bounds
        assert 0 <= self.miner.MEM_WALLET < MEMORY_SIZE
        assert 0 <= self.miner.MEM_ENTROPY < MEMORY_SIZE
        assert 0 <= self.miner.MEM_ATTEST < MEMORY_SIZE
        assert 0 <= self.miner.MEM_COUNTER < MEMORY_SIZE
        assert 0 <= self.miner.MEM_PROGRAM < MEMORY_SIZE


class TestIntegration:
    """Integration tests"""
    
    def test_full_mining_cycle(self):
        """Test complete mining cycle"""
        cpu = PDP8CPU()
        miner = RustChainMiner(cpu)
        
        # Run 10 epochs
        attestations = miner.run_miner(epochs=10)
        
        # Verify all attestations
        assert len(attestations) == 10
        
        for i, att in enumerate(attestations):
            assert att['epoch'] == i + 1
            assert att['wallet'] == miner.wallet
            assert att['antiquity_multiplier'] == 5.0
    
    def test_cpu_and_miner_integration(self):
        """Test CPU and miner work together"""
        cpu = PDP8CPU()
        
        # Run some CPU instructions
        cpu.write_memory(0x100, 0x123)
        cpu.write_memory(0x101, 0x456)
        
        instruction = 0o1000 | 0x100  # TAD 0x100
        cpu.execute(instruction)
        instruction = 0o1000 | 0x101  # TAD 0x101
        cpu.execute(instruction)
        
        assert cpu.ac == (0x123 + 0x456) & WORD_MASK
        
        # Now run miner
        miner = RustChainMiner(cpu)
        attestations = miner.run_miner(epochs=1)
        assert len(attestations) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
