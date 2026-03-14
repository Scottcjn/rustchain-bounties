#!/usr/bin/env python3
"""Quick test of EDSAC miner."""
import sys
sys.path.insert(0, '.')

from edsac import EDSACSimulator, mine_python

tests = [
    (1234, 16384),
    (1234, 1638),
    (9999, 819),
    (0, 100),
    (16383, 50),
]

sim = EDSACSimulator()
print('Testing EDSAC Miner:')
print('=' * 50)
all_pass = True

for header, target in tests:
    sim.reset()
    state = sim.run_mining_demo(header, target)
    ref_nonce, ref_hash = mine_python(header, target)
    match = state.nonce_found == ref_nonce
    status = 'PASS' if match else 'FAIL'
    print(f'{status} Header={header:5d} Target={target:5d} Nonce={state.nonce_found:4d} Hash={state.hash_found:4d}')
    all_pass = all_pass and match

print('=' * 50)
print('ALL TESTS PASSED!' if all_pass else 'SOME TESTS FAILED')
