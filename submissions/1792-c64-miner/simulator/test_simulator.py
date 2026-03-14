#!/usr/bin/env python3
"""
Quick test script for RustChain C64 Miner Simulator

Usage: python test_simulator.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from c64_miner_sim import (
    C64HardwareFingerprint,
    MinerState,
    NetworkClient,
    build_attestation_payload,
    MinerSimulator
)

def test_fingerprint():
    """Test hardware fingerprint generation"""
    print("=" * 60)
    print("TEST 1: Hardware Fingerprint Generation")
    print("=" * 60)
    
    fp = C64HardwareFingerprint.generate()
    
    print(f"CIA Jitter:   {fp.cia_jitter}")
    print(f"VIC Raster:   {fp.vic_raster}")
    print(f"SID Offset:   {fp.sid_offset}")
    print(f"ROM Checksum: 0x{fp.rom_checksum:04X}")
    print(f"Combined:     0x{fp.combined:08X}")
    print(f"Miner ID:     {fp.to_miner_id()}")
    print(f"Is Emulated:  {fp.is_emulated()}")
    print()
    
    # Verify fingerprint is not emulated
    assert not fp.is_emulated(), "Real fingerprint should not be emulated"
    assert fp.cia_jitter >= 10, "CIA jitter should be >= 10"
    assert fp.sid_offset > 0, "SID offset should be > 0"
    
    print("[PASS] Fingerprint test PASSED")
    print()
    return True

def test_miner_state():
    """Test miner state initialization"""
    print("=" * 60)
    print("TEST 2: Miner State Initialization")
    print("=" * 60)
    
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    state = MinerState(wallet)
    
    print(f"Wallet:       {state.wallet}")
    print(f"Miner ID:     {state.miner_id}")
    print(f"Hardware:     CIA={state.hardware.cia_jitter}, VIC={state.hardware.vic_raster}, SID={state.hardware.sid_offset}")
    print(f"Network:      {'Ready' if state.network_ready else 'Not Ready'}")
    print()
    
    assert state.wallet == wallet, "Wallet should match"
    assert state.miner_id.startswith("c64-"), "Miner ID should start with c64-"
    assert state.network_ready, "Network should be ready"
    
    print("[PASS] Miner state test PASSED")
    print()
    return True

def test_attestation_payload():
    """Test attestation payload building"""
    print("=" * 60)
    print("TEST 3: Attestation Payload Building")
    print("=" * 60)
    
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    state = MinerState(wallet)
    
    payload = build_attestation_payload(state)
    
    print("Payload:")
    import json
    print(json.dumps(payload, indent=2))
    print()
    
    # Verify payload structure
    assert "miner_id" in payload, "Payload should have miner_id"
    assert "device" in payload, "Payload should have device"
    assert "signals" in payload, "Payload should have signals"
    assert "fingerprint" in payload, "Payload should have fingerprint"
    assert "report" in payload, "Payload should have report"
    
    # Verify device info
    assert payload["device"]["arch"] == "6510", "Device arch should be 6510"
    assert payload["device"]["family"] == "commodore_64", "Device family should be commodore_64"
    assert payload["device"]["cpu_speed"] == 1023000, "CPU speed should be 1023000"
    assert payload["device"]["total_ram_kb"] == 64, "RAM should be 64 KB"
    
    print("[PASS] Attestation payload test PASSED")
    print()
    return True

def test_network_simulation():
    """Test network simulation"""
    print("=" * 60)
    print("TEST 4: Network Simulation")
    print("=" * 60)
    
    network = NetworkClient(simulate=True)
    
    payload = {
        "miner_id": "c64-TEST",
        "device": {"arch": "6510"}
    }
    
    response = network.post_attestation(payload)
    
    print(f"Response: {response}")
    print()
    
    assert response is not None, "Response should not be None"
    assert response["status"] == "ok", "Status should be ok"
    assert "reward" in response, "Response should have reward"
    assert response["multiplier"] == 4.0, "Multiplier should be 4.0"
    
    print("[PASS] Network simulation test PASSED")
    print()
    return True

def test_full_simulation():
    """Test full simulation run"""
    print("=" * 60)
    print("TEST 5: Full Simulation (5 seconds)")
    print("=" * 60)
    
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    simulator = MinerSimulator(wallet)
    
    # Run for 5 seconds (simulated time is accelerated)
    simulator.run(duration=5)
    
    print()
    print("[PASS] Full simulation test PASSED")
    print()
    return True

def main():
    """Run all tests"""
    print()
    print("=" * 60)
    print("RustChain C64 Miner - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_fingerprint,
        test_miner_state,
        test_attestation_payload,
        test_network_simulation,
        test_full_simulation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[FAIL] Test FAILED: {e}")
            print()
            failed += 1
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    print()
    
    if failed == 0:
        print("[SUCCESS] All tests PASSED! Ready for deployment.")
        print()
        return 0
    else:
        print("[FAILURE] Some tests FAILED. Please fix issues.")
        print()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
