#!/usr/bin/env python3
"""
Test suite for LEO III RustChain Miner

Run with: python test_miner.py
"""

import unittest
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from leo_iii_simulator import (
    CoreMemory, MagneticTape, MiningShare, MasterProgram,
    LEOIII, RustChainMiner
)


class TestCoreMemory(unittest.TestCase):
    """Test CoreMemory class"""
    
    def test_initialization(self):
        """Test memory initialization"""
        mem = CoreMemory(size_words=1024)
        self.assertEqual(len(mem.words), 1024)
        self.assertTrue(0 <= mem.residual_pattern <= 0xFFFFFFFF)
    
    def test_read_write(self):
        """Test memory read/write operations"""
        mem = CoreMemory(size_words=1024)
        mem.write(100, 0xDEADBEEF)
        self.assertEqual(mem.read(100), 0xDEADBEEF)
    
    def test_read_out_of_bounds(self):
        """Test reading out of bounds returns 0"""
        mem = CoreMemory(size_words=1024)
        self.assertEqual(mem.read(2000), 0)
    
    def test_fingerprint(self):
        """Test fingerprint generation"""
        mem = CoreMemory()
        fp = mem.get_fingerprint()
        self.assertEqual(len(fp), 8)  # 8 hex characters
        self.assertTrue(all(c in '0123456789ABCDEF' for c in fp))


class TestMiningShare(unittest.TestCase):
    """Test MiningShare class"""
    
    def test_valid_share(self):
        """Test valid share detection"""
        share = MiningShare(
            timestamp=1710334567,
            wallet='RTC4325af95d26d59c3ef025963656d22af638bb96b',
            fingerprint='B4E8C3D2F1A09876',
            nonce=12345,
            hash_value=100,
            difficulty=1000,
            job_number=7
        )
        self.assertTrue(share.is_valid())
    
    def test_invalid_share(self):
        """Test invalid share detection"""
        share = MiningShare(
            timestamp=1710334567,
            wallet='RTC4325af95d26d59c3ef025963656d22af638bb96b',
            fingerprint='B4E8C3D2F1A09876',
            nonce=12345,
            hash_value=2000,
            difficulty=1000,
            job_number=7
        )
        self.assertFalse(share.is_valid())
    
    def test_paper_tape_format(self):
        """Test paper tape output format"""
        share = MiningShare(
            timestamp=1710334567,
            wallet='RTC4325af95d26d59c3ef025963656d22af638bb96b',
            fingerprint='B4E8C3D2F1A09876',
            nonce=0xA4F2,
            hash_value=0xF8,
            difficulty=0x1000,
            job_number=7
        )
        tape = share.to_paper_tape()
        self.assertEqual(len(tape), 80)  # Fixed 80 characters


class TestMasterProgram(unittest.TestCase):
    """Test MasterProgram OS simulation"""
    
    def test_register_job(self):
        """Test job registration"""
        mp = MasterProgram()
        job_num = mp.register_job("Test Job")
        self.assertEqual(job_num, 1)
    
    def test_max_jobs(self):
        """Test maximum job limit"""
        mp = MasterProgram(max_jobs=3)
        mp.register_job("Job 1")
        mp.register_job("Job 2")
        mp.register_job("Job 3")
        with self.assertRaises(RuntimeError):
            mp.register_job("Job 4")
    
    def test_time_slice(self):
        """Test time slice management"""
        mp = MasterProgram(time_slice_ms=100)
        job_num = mp.register_job("Test Job")
        mp.current_job = 0
        mp.jobs[0]['time_remaining'] = 100
        
        self.assertTrue(mp.check_time())
        
        mp.jobs[0]['time_remaining'] = 0
        self.assertFalse(mp.check_time())
    
    def test_round_robin(self):
        """Test round-robin scheduling"""
        mp = MasterProgram()
        mp.register_job("Job 1")
        mp.register_job("Job 2")
        mp.register_job("Job 3")
        
        mp.current_job = 0
        mp.schedule_next()
        self.assertEqual(mp.current_job, 1)
        
        mp.schedule_next()
        self.assertEqual(mp.current_job, 2)
        
        mp.schedule_next()
        self.assertEqual(mp.current_job, 0)  # Wrap around


class TestLEOIII(unittest.TestCase):
    """Test LEOIII computer simulation"""
    
    def test_initialization(self):
        """Test computer initialization"""
        computer = LEOIII()
        self.assertEqual(computer.accumulator, 0)
        self.assertEqual(computer.program_counter, 0)
        self.assertFalse(computer.halted)
    
    def test_fingerprint(self):
        """Test system fingerprint generation"""
        computer = LEOIII()
        fp = computer.get_fingerprint()
        self.assertEqual(len(fp), 16)  # 16 hex characters
    
    def test_load_program(self):
        """Test program loading"""
        computer = LEOIII()
        program = [0x01000001, 0x02000002, 0x00000000]  # LOAD, STORE, STOP
        computer.load_program(program, start_address=0)
        
        self.assertEqual(computer.memory.read(0), 0x01000001)
        self.assertEqual(computer.memory.read(1), 0x02000002)
    
    def test_execute_load(self):
        """Test LOAD instruction"""
        computer = LEOIII()
        computer.memory.write(100, 0xDEADBEEF)
        computer.load_program([0x01000064])  # LOAD from address 100
        computer.execute_instruction()
        self.assertEqual(computer.accumulator, 0xDEADBEEF)
    
    def test_execute_store(self):
        """Test STORE instruction"""
        computer = LEOIII()
        computer.accumulator = 0xCAFEBABE
        computer.load_program([0x02000064])  # STORE to address 100
        computer.execute_instruction()
        self.assertEqual(computer.memory.read(100), 0xCAFEBABE)
    
    def test_execute_add(self):
        """Test ADD instruction"""
        computer = LEOIII()
        computer.accumulator = 100
        computer.memory.write(100, 50)
        computer.load_program([0x03000064])  # ADD from address 100
        computer.execute_instruction()
        self.assertEqual(computer.accumulator, 150)
    
    def test_execute_jump(self):
        """Test JUMP instruction"""
        computer = LEOIII()
        computer.load_program([0x07000005])  # JUMP to address 5
        computer.execute_instruction()
        self.assertEqual(computer.program_counter, 5)
    
    def test_execute_stop(self):
        """Test STOP instruction"""
        computer = LEOIII()
        computer.load_program([0x00000000])  # STOP
        computer.execute_instruction()
        self.assertTrue(computer.halted)
    
    def test_run_program(self):
        """Test running a complete program"""
        computer = LEOIII()
        # Simple program: LOAD 100, ADD 101, STORE 102, STOP
        computer.memory.write(100, 10)
        computer.memory.write(101, 20)
        program = [
            0x01000064,  # LOAD 100
            0x03000065,  # ADD 101
            0x02000066,  # STORE 102
            0x00000000   # STOP
        ]
        computer.load_program(program)
        computer.run()
        
        self.assertEqual(computer.memory.read(102), 30)
        self.assertTrue(computer.halted)


class TestRustChainMiner(unittest.TestCase):
    """Test RustChainMiner class"""
    
    def test_initialization(self):
        """Test miner initialization"""
        computer = LEOIII()
        miner = RustChainMiner(computer, 'RTC4325af95d26d59c3ef025963656d22af638bb96b')
        miner.initialize()
        
        self.assertEqual(miner.job_number, 1)
        self.assertEqual(len(computer.master_program.jobs), 1)
    
    def test_fingerprint_generation(self):
        """Test fingerprint generation"""
        computer = LEOIII()
        miner = RustChainMiner(computer, 'RTC4325af95d26d59c3ef025963656d22af638bb96b')
        miner.initialize()
        
        fp = miner.generate_fingerprint()
        self.assertEqual(len(fp), 16)
    
    def test_hash_computation(self):
        """Test hash computation"""
        computer = LEOIII()
        miner = RustChainMiner(computer, 'RTC4325af95d26d59c3ef025963656d22af638bb96b')
        
        fp = '00000000FFFFFFFF'
        hash1 = miner.compute_hash(fp, 0)
        hash2 = miner.compute_hash(fp, 1)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_mine_share_found(self):
        """Test mining with share found"""
        computer = LEOIII()
        # Set very low difficulty for guaranteed share
        miner = RustChainMiner(computer, 'RTC4325af95d26d59c3ef025963656d22af638bb96b', difficulty=0xFFFFFFFF)
        miner.initialize()
        
        share = miner.mine_share()
        self.assertIsNotNone(share)
        self.assertTrue(share.is_valid())
        self.assertEqual(len(miner.shares_found), 1)
    
    def test_mine_session(self):
        """Test mining session"""
        computer = LEOIII()
        miner = RustChainMiner(computer, 'RTC4325af95d26d59c3ef025963656d22af638bb96b', difficulty=0x10000000)
        miner.initialize()
        
        results = miner.mine(duration_seconds=0.1)
        
        self.assertGreater(results['attempts'], 0)
        self.assertIn('duration', results)
        self.assertIn('shares', results)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_full_mining_cycle(self):
        """Test complete mining cycle"""
        # Create computer
        computer = LEOIII(memory_size=8192)
        
        # Create miner with easy difficulty
        miner = RustChainMiner(
            computer=computer,
            wallet='RTC4325af95d26d59c3ef025963656d22af638bb96b',
            difficulty=0x10000000  # Easy difficulty
        )
        
        # Initialize
        miner.initialize()
        
        # Mine for a short period
        results = miner.mine(duration_seconds=0.5)
        
        # Verify results
        self.assertGreater(results['attempts'], 0)
        self.assertGreater(results['instructions'], 0)
        
        # Verify shares are valid
        for share in miner.shares_found:
            self.assertTrue(share.is_valid())
            self.assertEqual(len(share.to_paper_tape()), 80)


if __name__ == '__main__':
    unittest.main(verbosity=2)
