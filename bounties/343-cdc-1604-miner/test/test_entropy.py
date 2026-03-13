#!/usr/bin/env python3
"""
Test suite for CDC 1604 entropy collection and attestation.

Run with: pytest test_entropy.py -v
"""

import pytest
import json
import sys
from pathlib import Path

# Add proxy directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'proxy'))

from cdc1604_proxy import (
    parse_text_output,
    build_attestation,
    validate_attestation,
    generate_demo_data,
    CDC1604_METADATA
)


# Sample CDC 1604 output for testing
SAMPLE_TEXT_OUTPUT = """
CDC 1604 Entropy Collector - RustChain
======================================

Phase 1: Core Memory Timing...
  Collected 32 timing samples
Phase 2: Instruction Jitter...
  Collected 16 jitter samples
Phase 3: Audio DAC Sampling...
  Collected 8 audio samples
Phase 4: Bank Interleave Delta...
  Bank delta measured
Phase 5: Generating entropy hash...
  Hash generated: 48 × 6-bit bytes
Phase 6: Generating wallet ID...

========================================
  WALLET GENERATED
========================================
Wallet:   RTC4325AF95D26D59C3EF025963656D22AF638BB96B
Miner ID: CDC1604-A3F7B2E1
========================================

WALLET:RTC4325AF95D26D59C3EF025963656D22AF638BB96B
MINER_ID:CDC1604-A3F7B2E1
ENTROPY_HASH:6f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c
TIMESTAMP:1960-03-13T20:30:00Z

========================================
  ENTROPY COLLECTION COMPLETE
========================================
"""


class TestEntropyParsing:
    """Test entropy output parsing."""
    
    def test_parse_valid_text_output(self, tmp_path):
        """Test parsing valid CDC 1604 text output."""
        output_file = tmp_path / "cdc1604_output.txt"
        output_file.write_text(SAMPLE_TEXT_OUTPUT)
        
        data = parse_text_output(str(output_file))
        
        assert data['wallet'] == 'RTC4325AF95D26D59C3EF025963656D22AF638BB96B'
        assert data['miner_id'] == 'CDC1604-A3F7B2E1'
        assert len(data['entropy_hash']) == 96  # 48 bytes = 96 hex chars
        assert 'timestamp' in data
    
    def test_parse_missing_wallet(self, tmp_path):
        """Test parsing output without wallet."""
        output_file = tmp_path / "bad_output.txt"
        output_file.write_text("No wallet here")
        
        with pytest.raises(ValueError, match="wallet"):
            parse_text_output(str(output_file))
    
    def test_parse_invalid_wallet_format(self, tmp_path):
        """Test parsing output with invalid wallet format."""
        output_file = tmp_path / "bad_wallet.txt"
        output_file.write_text("WALLET:INVALID123\nMINER_ID:CDC1604-A3F7B2E1")
        
        with pytest.raises(ValueError):
            parse_text_output(str(output_file))


class TestAttestation:
    """Test attestation building and validation."""
    
    def test_build_attestation_structure(self):
        """Test attestation has correct structure."""
        data = {
            'wallet': 'RTC4325AF95D26D59C3EF025963656D22AF638BB96B',
            'miner_id': 'CDC1604-A3F7B2E1',
            'entropy_hash': 'a' * 96,
            'timestamp': '2024-01-01T00:00:00Z',
            'source': 'test'
        }
        
        attestation = build_attestation(data)
        
        assert 'miner' in attestation
        assert 'miner_id' in attestation
        assert 'device' in attestation
        assert 'entropy' in attestation
        assert 'antiquity_multiplier' in attestation
        assert attestation['antiquity_multiplier'] == 5.0
    
    def test_cdc1604_metadata(self):
        """Test CDC 1604 metadata is correct."""
        assert CDC1604_METADATA['year'] == 1960
        assert CDC1604_METADATA['designer'] == 'Seymour Cray'
        assert CDC1604_METADATA['word_size'] == 48
        assert CDC1604_METADATA['clock_mhz'] == 0.208
        assert CDC1604_METADATA['antiquity_multiplier'] == 5.0
    
    def test_validate_attestation_success(self):
        """Test validation passes for valid attestation."""
        data = generate_demo_data()
        attestation = build_attestation(data)
        
        errors = validate_attestation(attestation)
        assert len(errors) == 0
    
    def test_validate_wrong_year(self):
        """Test validation fails for wrong year."""
        data = generate_demo_data()
        attestation = build_attestation(data)
        attestation['device']['year'] = 1970
        
        errors = validate_attestation(attestation)
        assert any('year' in err for err in errors)
    
    def test_validate_wrong_multiplier(self):
        """Test validation fails for wrong multiplier."""
        data = generate_demo_data()
        attestation = build_attestation(data)
        attestation['antiquity_multiplier'] = 2.0
        
        errors = validate_attestation(attestation)
        assert any('multiplier' in err for err in errors)


class TestDemoGeneration:
    """Test demo data generation."""
    
    def test_demo_data_format(self):
        """Test demo data has correct format."""
        data = generate_demo_data()
        
        assert data['wallet'].startswith('RTC')
        assert len(data['wallet']) == 43  # RTC + 40 hex chars
        assert data['miner_id'].startswith('CDC1604-')
        assert len(data['entropy_hash']) == 96  # 48 bytes hex
    
    def test_demo_data_uniqueness(self):
        """Test each demo generation produces unique data."""
        data1 = generate_demo_data()
        data2 = generate_demo_data()
        
        assert data1['wallet'] != data2['wallet']
        assert data1['entropy_hash'] != data2['entropy_hash']


class TestAntiEmulation:
    """Test anti-emulation checks."""
    
    def test_anti_emulation_flags(self):
        """Test anti-emulation flags are set correctly."""
        data = generate_demo_data()
        attestation = build_attestation(data)
        
        anti_emu = attestation['entropy']['anti_emulation']
        
        assert anti_emu['core_memory_decay'] == True
        assert anti_emu['transistor_switching_variance'] == True
        assert anti_emu['analog_audio_dac'] == True
        assert anti_emu['power_line_interference'] == True
        assert anti_emu['no_digital_clock_signature'] == True
    
    def test_quality_score(self):
        """Test entropy quality score is high for CDC 1604."""
        data = generate_demo_data()
        attestation = build_attestation(data)
        
        # CDC 1604 should have high quality score due to analog entropy
        assert attestation['entropy']['quality_score'] >= 0.9


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
