#!/usr/bin/env python3
"""Quick test of PDP-1 miner - simplified"""
import sys
sys.path.insert(0, '.')

print("="*60)
print("PDP-1 Miner Quick Test")
print("="*60)

# Test 1: CPU
print("\n[TEST 1] PDP-1 CPU Simulator")
from pdp1_cpu import PDP1CPU
cpu = PDP1CPU()
program = [
    0o0600001,  # LDA 1
    0o0400002,  # ADD 2
    0o0620003,  # STA 3
    0o1020000,  # HALT
    0, 25, 17, 0
]
cpu.load_program(program)
cpu.run()
result = cpu.read_memory(3)
print(f"  25 + 17 = {result}")
print(f"  Status: {'PASS' if result == 42 else 'FAIL'}")

# Test 2: SHA-256
print("\n[TEST 2] SHA-256 Implementation")
from sha256_pdp1 import SHA256_PDP1
sha = SHA256_PDP1()
sha.update("abc")
result = sha.hexdigest()
expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
print(f"  SHA256('abc') = {result}")
print(f"  Status: {'PASS' if result == expected else 'FAIL'}")

# Test 3: Attestation
print("\n[TEST 3] Attestation Generator")
from attestation import PDP1Attestation
attester = PDP1Attestation("RTC4325af95d26d59c3ef025963656d22af638bb96b")
attestation = attester.generate_attestation()
verified = attester.verify_attestation(attestation)
print(f"  Tier: {attestation['tier']}")
print(f"  Multiplier: {attestation['mining']['multiplier']}x")
print(f"  Verified: {verified}")
print(f"  Status: {'PASS' if verified else 'FAIL'}")

# Test 4: Miner initialization
print("\n[TEST 4] Miner Initialization")
from pdp1_miner import PDP1Miner
miner = PDP1Miner('RTC4325af95d26d59c3ef025963656d22af638bb96b')
print(f"  Wallet: {miner.wallet}")
print(f"  Multiplier: {miner.ANTIQUITY_MULTIPLIER}x")
print(f"  Hardware ID: {miner.hardware_id}")
print(f"  Status: PASS")

# Test 5: Hash computation
print("\n[TEST 5] Mining Hash Computation")
epoch = miner.create_epoch()
epoch_data = f"{epoch['epoch_id']}{miner.wallet}".encode()
hash_result = miner.compute_hash(epoch_data, 42)
print(f"  Hash (first 16 chars): {hash_result.hex()[:16]}...")
print(f"  Hash length: {len(hash_result)} bytes")
print(f"  Status: {'PASS' if len(hash_result) == 32 else 'FAIL'}")

print("\n" + "="*60)
print("All tests completed!")
print("="*60)
