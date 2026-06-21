#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for hardware_eulogy generator"""

import json
import sys
import io
import tempfile
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from hardware_eulogy import (
    HardwareRecord,
    EulogyGenerator,
    load_hardware_data
)


def test_hardware_record():
    """Test HardwareRecord data class"""
    hw = HardwareRecord(
        model="PowerBook G4",
        year_purchased=2003,
        year_retired=2024,
        processors=4,
        cores_failed=1,
        hashes_completed=12_500_000,
        earnings_rtc=2.34,
        standout_moments=["Survived heatwave", "First RTC earned"]
    )

    assert hw.total_years == 21
    assert hw.lifespan_days > 0
    print("[OK] test_hardware_record passed")


def test_efficiency_calculation():
    """Test efficiency metrics"""
    hw = HardwareRecord(
        model="Test Rig",
        year_purchased=2020,
        year_retired=2024,
        processors=4,
        cores_failed=1,
        hashes_completed=10_000_000,
        earnings_rtc=1.0,
        standout_moments=[]
    )

    efficiency = hw.calculate_efficiency()

    assert "hashes_per_day" in efficiency
    assert "rtc_per_hash" in efficiency
    assert "uptime_percent" in efficiency
    assert efficiency["uptime_percent"] == 0.75  # 3/4 cores working
    print("[OK] test_efficiency_calculation passed")


def test_eulogy_generation():
    """Test full eulogy generation"""
    hw = HardwareRecord(
        model="PowerBook G4",
        year_purchased=2003,
        year_retired=2024,
        processors=4,
        cores_failed=1,
        hashes_completed=12_500_000,
        earnings_rtc=2.34,
        standout_moments=["Survived 2023 heatwave", "First RTC earned 2024-01-15"]
    )

    gen = EulogyGenerator(hw)
    eulogy = gen.generate_full_eulogy()

    assert "PowerBook G4" in eulogy
    assert "2003" in eulogy
    assert "2024" in eulogy
    assert "12,500,000" in eulogy
    assert "2.34" in eulogy
    assert "R.I.P." in eulogy
    assert "Survived 2023 heatwave" in eulogy
    assert "---" in eulogy  # YAML front-matter
    print("[OK] test_eulogy_generation passed")


def test_opening_section():
    """Test opening paragraph generation"""
    hw = HardwareRecord(
        model="Test Model",
        year_purchased=2000,
        year_retired=2023,
        processors=2,
        cores_failed=0,
        hashes_completed=1_000_000,
        earnings_rtc=0.5,
        standout_moments=[]
    )

    gen = EulogyGenerator(hw)
    opening = gen.generate_opening()

    assert "Test Model" in opening
    assert "2000" in opening
    assert "2023" in opening
    assert "23 years" in opening
    print("[OK] test_opening_section passed")


def test_body_section():
    """Test service record and moments"""
    hw = HardwareRecord(
        model="Miner X",
        year_purchased=2020,
        year_retired=2024,
        processors=8,
        cores_failed=2,
        hashes_completed=50_000_000,
        earnings_rtc=10.0,
        standout_moments=["Peak hash rate: 5M/s", "Survived power failure"]
    )

    gen = EulogyGenerator(hw)
    body = gen.generate_body()

    assert "50,000,000" in body
    assert "10.0000" in body or "10.00" in body
    assert "Peak hash rate: 5M/s" in body
    assert "Survived power failure" in body
    assert "2 of 8 cores" in body
    print("[OK] test_body_section passed")


def test_load_hardware_data():
    """Test loading hardware data from JSON file"""
    data = {
        "hardware": {
            "model": "Test Rig",
            "year_purchased": 2020,
            "year_retired": 2024,
            "processors": 4,
            "cores_failed": 0,
            "hashes_completed": 5_000_000,
            "total_earnings_rtc": 1.5,
            "standout_moments": ["Stable performer"]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_file = f.name

    try:
        hw = load_hardware_data(temp_file)
        assert hw.model == "Test Rig"
        assert hw.year_purchased == 2020
        assert hw.cores_failed == 0
        print("[OK] test_load_hardware_data passed")
    finally:
        Path(temp_file).unlink()


def test_load_hardware_missing_field():
    """Test error handling for missing fields"""
    data = {
        "hardware": {
            "model": "Incomplete Rig",
            # Missing year_purchased, year_retired, etc.
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(data, f)
        temp_file = f.name

    try:
        try:
            hw = load_hardware_data(temp_file)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Missing required field" in str(e)
            print("[OK] test_load_hardware_missing_field passed")
    finally:
        Path(temp_file).unlink()


def test_closing_section():
    """Test closing tribute"""
    hw = HardwareRecord(
        model="Test",
        year_purchased=2000,
        year_retired=2024,
        processors=2,
        cores_failed=0,
        hashes_completed=1_000_000,
        earnings_rtc=1.0,
        standout_moments=[]
    )

    gen = EulogyGenerator(hw)
    closing = gen.generate_closing()

    assert "In Memoriam" in closing
    assert "Rest" in closing
    assert "friend" in closing.lower()
    assert "R.I.P." in closing
    print("[OK] test_closing_section passed")


if __name__ == "__main__":
    test_hardware_record()
    test_efficiency_calculation()
    test_eulogy_generation()
    test_opening_section()
    test_body_section()
    test_load_hardware_data()
    test_load_hardware_missing_field()
    test_closing_section()
    print("\n[OK] All tests passed!")
