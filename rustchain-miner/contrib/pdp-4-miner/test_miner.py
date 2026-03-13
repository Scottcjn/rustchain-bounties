#!/usr/bin/env python3
"""
Test script for PDP-4 Miner
Runs the miner in demo mode and verifies output.
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run PDP-4 miner tests"""
    print("=" * 60)
    print("PDP-4 Miner Test Suite")
    print("=" * 60)
    
    # Test 1: Run miner in demo mode
    print("\n[Test 1] Running miner in demo mode...")
    result = subprocess.run(
        [sys.executable, 'pdp4_miner.py', '--demo', '-n', '3'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Miner executed successfully")
        print(f"Output:\n{result.stdout[:500]}...")
    else:
        print(f"✗ Miner failed: {result.stderr}")
        return False
    
    # Test 2: Check wallet file created
    print("\n[Test 2] Checking wallet file...")
    wallet_file = Path('wallet.dat')
    if wallet_file.exists():
        print(f"✓ Wallet file created: {wallet_file}")
        with open(wallet_file, 'r') as f:
            wallet_id = f.readline().strip()
            print(f"  Wallet ID: {wallet_id}")
    else:
        print("✗ Wallet file not found")
        return False
    
    # Test 3: Check attestations directory
    print("\n[Test 3] Checking attestations...")
    attest_dir = Path('attestations')
    if attest_dir.exists():
        attestations = list(attest_dir.glob('*.txt'))
        print(f"✓ Found {len(attestations)} attestation files")
        if attestations:
            print(f"  Latest: {attestations[-1].name}")
    else:
        print("✗ Attestations directory not found")
        return False
    
    # Test 4: Verify attestation format
    print("\n[Test 4] Verifying attestation format...")
    if attestations:
        with open(attestations[-1], 'r') as f:
            content = f.read()
            required_fields = [
                'PDP4-ATTESTATION-V1',
                'Wallet:',
                'Miner:',
                'Machine: PDP-4/1962',
                'CoreMem:',
                'Timestamp:',
                'Signature:'
            ]
            missing = [f for f in required_fields if f not in content]
            if not missing:
                print("✓ Attestation format valid")
            else:
                print(f"✗ Missing fields: {missing}")
                return False
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
