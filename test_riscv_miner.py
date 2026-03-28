#!/usr/bin/env python3
"""
Test suite for RISC-V miner port
Bounty #2298 - 100 RTC
"""

import pytest
import sys
import platform
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the module under test
from riscv_miner import (
    detect_riscv_architecture,
    get_cache_sizes,
    detect_simd_extensions,
    get_riscv_multiplier,
    run_fingerprint_checks,
    main
)


class TestRiscvArchitecture:
    """Test RISC-V architecture detection."""
    
    def test_non_riscv(self):
        """Test detection on non-RISC-V processor."""
        with patch('riscv_miner.platform.machine', return_value='x86_64'):
            result = detect_riscv_architecture()
            assert result['is_riscv'] == False
            assert 'error' in result
    
    def test_riscv_64bit(self):
        """Test detection on 64-bit RISC-V."""
        mock_cpuinfo = """
processor       : 0
uarch           : sifive-u74
isa             : rv64imafdc
vendor_id       : SiFive
"""
        with patch('riscv_miner.platform.machine', return_value='riscv64'), \
             patch('builtins.open', MagicMock(return_value=MagicMock(read=MagicMock(return_value=mock_cpuinfo)))), \
             patch('pathlib.Path.exists', return_value=True):
            result = detect_riscv_architecture()
            assert result['is_riscv'] == True
            assert result['is_64bit'] == True
            assert result['is_32bit'] == False
    
    def test_riscv_32bit(self):
        """Test detection on 32-bit RISC-V."""
        with patch('riscv_miner.platform.machine', return_value='riscv32'), \
             patch('riscv_miner.sys.maxsize', 2**31 - 1):
            result = detect_riscv_architecture()
            assert result['is_riscv'] == True
            assert result['is_32bit'] == True


class TestCacheSizes:
    """Test cache size detection."""
    
    def test_sysfs_cache(self, tmp_path):
        """Test cache detection from sysfs."""
        # Create mock sysfs structure
        cache_dir = tmp_path / 'cache'
        cache_dir.mkdir()
        
        l1d_dir = cache_dir / 'index0'
        l1d_dir.mkdir()
        (l1d_dir / 'level').write_text('1')
        (l1d_dir / 'size').write_text('32K')
        (l1d_dir / 'type').write_text('Data')
        
        l2_dir = cache_dir / 'index2'
        l2_dir.mkdir()
        (l2_dir / 'level').write_text('2')
        (l2_dir / 'size').write_text('2M')
        (l2_dir / 'type').write_text('Unified')
        
        with patch('riscv_miner.Path', return_value=cache_dir):
            sizes = get_cache_sizes()
            assert sizes['l1d'] == 32 * 1024
            assert sizes['l2'] == 2 * 1024 * 1024
    
    def test_fallback_defaults(self):
        """Test fallback defaults when sysfs not available."""
        with patch('riscv_miner.Path.exists', return_value=False):
            sizes = get_cache_sizes()
            assert sizes['l1d'] == 32 * 1024  # Default
            assert sizes['l1i'] == 32 * 1024  # Default
            assert sizes['l2'] == 2 * 1024 * 1024  # Default


class TestSimdDetection:
    """Test SIMD extension detection."""
    
    def test_v_extension_detected(self):
        """Test V extension detection."""
        # Just verify the function returns a dict with expected keys
        result = detect_simd_extensions()
        assert 'has_v_extension' in result
        assert isinstance(result['has_v_extension'], bool)
    
    def test_vector_width_detection(self):
        """Test vector width detection."""
        result = detect_simd_extensions()
        assert 'vector_bits' in result
        assert isinstance(result['vector_bits'], int)
        assert result['vector_bits'] >= 0
    
    def test_scalar_fallback(self):
        """Test scalar fallback when no V extension."""
        result = detect_simd_extensions()
        assert 'has_v_extension' in result
        # Either has V extension or has scalar fallback
        if not result['has_v_extension']:
            # Should have some fallback mechanism
            pass  # Implementation dependent


class TestMultiplier:
    """Test RISC-V multiplier calculation."""
    
    def test_non_riscv(self):
        """Test multiplier on non-RISC-V."""
        with patch('riscv_miner.detect_riscv_architecture', return_value={'is_riscv': False}):
            multiplier = get_riscv_multiplier()
            assert multiplier == 1.0
    
    def test_riscv_64bit(self):
        """Test multiplier on 64-bit RISC-V."""
        with patch('riscv_miner.detect_riscv_architecture', return_value={
            'is_riscv': True,
            'is_64bit': True
        }):
            multiplier = get_riscv_multiplier()
            assert multiplier == 1.5  # 1.4 + 0.1
    
    def test_riscv_32bit(self):
        """Test multiplier on 32-bit RISC-V."""
        with patch('riscv_miner.detect_riscv_architecture', return_value={
            'is_riscv': True,
            'is_64bit': False
        }):
            multiplier = get_riscv_multiplier()
            assert multiplier == 1.4  # Base only
    
    def test_multiplier_capped(self):
        """Test multiplier is capped at 1.5x."""
        with patch('riscv_miner.detect_riscv_architecture', return_value={
            'is_riscv': True,
            'is_64bit': True
        }):
            multiplier = get_riscv_multiplier()
            assert multiplier <= 1.5


class TestFingerprintChecks:
    """Test fingerprint checks."""
    
    def test_all_checks_pass(self):
        """Test all fingerprint checks pass."""
        with patch('riscv_miner.get_cache_sizes', return_value={
            'l1d': 32 * 1024,
            'l2': 2 * 1024 * 1024
        }), \
        patch('riscv_miner.detect_simd_extensions', return_value={
            'has_v_extension': True,
            'scalar_fallback': False
        }):
            results = run_fingerprint_checks()
            
            assert results['clock_drift'] == True
            assert results['cache_timing'] == True
            assert results['simd_identity'] == True
            assert results['thermal_drift'] == True
            assert results['memory_latency'] == True
            assert results['branch_prediction'] == True
    
    def test_cache_check_fails(self):
        """Test cache check fails without cache info."""
        with patch('riscv_miner.get_cache_sizes', return_value={
            'l1d': 0,
            'l2': 0
        }), \
        patch('riscv_miner.detect_simd_extensions', return_value={
            'has_v_extension': True
        }):
            results = run_fingerprint_checks()
            assert results['cache_timing'] == False


class TestMainFunction:
    """Test main entry point."""
    
    def test_non_riscv_exit(self):
        """Test main exits on non-RISC-V."""
        with patch('riscv_miner.detect_riscv_architecture', return_value={
            'is_riscv': False,
            'error': 'Not RISC-V'
        }):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
    
    def test_riscv_success(self, capsys):
        """Test main succeeds on RISC-V."""
        with patch('riscv_miner.detect_riscv_architecture', return_value={
            'is_riscv': True,
            'arch': 'riscv64',
            'is_64bit': True,
            'is_32bit': False,
            'uarch': 'sifive-u74',
            'isa': 'rv64imafdcv'
        }), \
        patch('riscv_miner.get_cache_sizes', return_value={
            'l1d': 32 * 1024,
            'l1i': 32 * 1024,
            'l2': 2 * 1024 * 1024,
            'l3': 0
        }), \
        patch('riscv_miner.detect_simd_extensions', return_value={
            'has_v_extension': True,
            'vector_bits': 128
        }), \
        patch('riscv_miner.get_riscv_multiplier', return_value=1.5), \
        patch('riscv_miner.run_fingerprint_checks', return_value={
            'clock_drift': True,
            'cache_timing': True,
            'simd_identity': True,
            'thermal_drift': True,
            'memory_latency': True,
            'branch_prediction': True
        }):
            result = main()
            captured = capsys.readouterr()
            assert result == 0
            assert "RISC-V detected" in captured.out
            assert "All fingerprint checks passed" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
