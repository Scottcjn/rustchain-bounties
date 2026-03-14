#!/usr/bin/env python3
"""
Test script for Pong Miner Simulator
"""

import sys
sys.path.insert(0, '.')

from pong_miner_simulator import PongMinerSimulator

def test_simulator():
    """Test basic simulator functionality."""
    print("Testing Pong Miner Simulator...")
    
    # Create simulator
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    sim = PongMinerSimulator(wallet)
    
    # Test initialization
    assert sim.wallet_address == wallet, "Wallet address mismatch"
    assert sim.blocks_found == 0, "Initial blocks should be 0"
    assert sim.difficulty == 1, "Initial difficulty should be 1"
    print("[OK] Initialization test passed")
    
    # Test simulation tick
    sim.simulate_mining_tick()
    assert sim.total_hashes >= 0, "Hashes should be non-negative"
    print("[OK] Simulation tick test passed")
    
    # Test report generation
    report = sim.generate_report()
    assert "RustChain Pong Miner" in report, "Report should contain title"
    assert wallet in report, "Report should contain wallet address"
    print("[OK] Report generation test passed")
    
    print("\nAll tests passed! [SUCCESS]")
    return True

if __name__ == "__main__":
    test_simulator()
