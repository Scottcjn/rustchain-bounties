# PR Submission - RustChain Bounty #352

## EDSAC Miner Port (1949)

**Bounty Tier:** LEGENDARY (200 RTC / $20)
**Wallet Address:** `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## Summary

This PR ports a cryptocurrency miner to the **EDSAC** (Electronic Delay Storage Automatic Calculator), the world's first practical stored-program computer that ran its first program on May 6, 1949.

While EDSAC cannot perform real SHA-256 mining (no bitwise operations, 17-bit words only, ~500 operations/second), this implementation demonstrates the **conceptual framework** of proof-of-work mining on historical hardware.

---

## What's Included

### Documentation

1. **README.md** - Project overview and quick start
2. **docs/ARCHITECTURE.md** - Detailed EDSAC technical specifications
3. **docs/MINING.md** - Mining algorithm explanation and adaptation

### Implementation

1. **simulator/edsac.py** - Python EDSAC computer simulator (~500 lines)
   - 17-bit word architecture
   - Original instruction set (A, S, T, U, H, E, G, L, M, N, Z, O, I)
   - Mercury delay line memory simulation
   - Mining demonstration mode

2. **simulator/miner.e** - EDSAC assembly source code
   - Annotated assembly listing
   - Memory layout documentation
   - Comments explaining each step

3. **simulator/test_miner.py** - Comprehensive test suite
   - Basic operation tests
   - Mining algorithm tests
   - Performance benchmarks
   - Assembly parser tests

4. **simulator/quick_test.py** - Quick validation script

---

## Technical Approach

### Challenge

EDSAC's extreme limitations:
- 17-bit words (vs 256-bit for SHA-256)
- No bitwise operations (AND, OR, XOR)
- Only 18 instructions
- ~500 operations/second
- Mercury delay line memory (serial access)

### Solution

Simplified proof-of-work:

```python
hash(header, nonce) = (header × 7919 + nonce × 104729) mod 16384
```

Where 7919 and 104729 are prime numbers for better distribution.

**Find nonce where:** `hash(header, nonce) < target`

### Example Run

```
Block Header: 1234
Target:       1638 (difficulty 10)

Result:
  Nonce: 4
  Hash:  114
  Valid: 114 < 1638 ✓
```

---

## Testing

All tests pass:

```
Testing EDSAC Miner:
==================================================
PASS Header= 1234 Target=16384 Nonce=   0 Hash=7182
PASS Header= 1234 Target= 1638 Nonce=   4 Hash= 114
PASS Header= 9999 Target=  819 Nonce=   8 Hash= 457
PASS Header=    0 Target=  100 Nonce=   0 Hash=   0
PASS Header=16383 Target=   50 Nonce= 677 Hash=  46
==================================================
ALL TESTS PASSED!
```

---

## How to Run

### Prerequisites

- Python 3.7+
- No external dependencies

### Quick Start

```bash
cd simulator

# Run mining demo
python edsac.py --demo --header 1234 --target 1638

# Run test suite
python quick_test.py

# Run full test suite
python test_miner.py
```

### Example Output

```
============================================================
EDSAC Mining Demonstration
============================================================
Block Header: 1234
Target:       1638
============================================================

Python Reference Solution:
  Nonce: 4
  Hash:  114

EDSAC Simulator:
  Cycles:           100
  Instructions:     2000
  Halt Reason:      HaltReason.SUCCESS
  Nonce Found:      4
  Hash Found:       114
  Output:           ['4']

Verification:
  Computed Hash:  114
  Target:         1638
  Valid:          True ✓

============================================================
Mining Complete!
============================================================
```

---

## Historical Significance

This is believed to be:
- The first cryptocurrency miner for a 1949 computer
- The slowest miner ever created (~20 hashes/second theoretical)
- A demonstration that PoW concepts are hardware-agnostic

EDSAC predates:
- Transistors in computing (1950s)
- Integrated circuits (1958)
- The concept of digital currency by ~60 years

---

## Files Modified/Added

```
edsac-miner/
├── README.md                    [NEW]
├── docs/
│   ├── ARCHITECTURE.md          [NEW]
│   └── MINING.md                [NEW]
├── simulator/
│   ├── edsac.py                 [NEW]
│   ├── miner.e                  [NEW]
│   ├── test_miner.py            [NEW]
│   └── quick_test.py            [NEW]
├── examples/
│   └── sample_run.txt           [NEW]
└── PR_SUBMISSION.md             [NEW - this file]
```

---

## Verification

To verify this submission:

1. Clone the repository
2. Navigate to `edsac-miner/simulator/`
3. Run `python quick_test.py`
4. All tests should pass

To verify the mining algorithm:

```python
from edsac import mine_python

header = 1234
target = 1638
nonce, hash_val = mine_python(header, target)

# Verify
verify_hash = (header * 7919 + nonce * 104729) % 16384
assert verify_hash < target  # Should be True
assert verify_hash == hash_val  # Should be True
```

---

## Bounty Claim

**Wallet:** `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**Tier:** LEGENDARY (200 RTC / $20)

**Justification:**
- ✅ Ported to historical computer (1949)
- ✅ Full documentation (3 comprehensive docs)
- ✅ Working simulator (Python)
- ✅ Assembly source code (miner.e)
- ✅ Test suite with passing tests
- ✅ Educational value (historical computing)

---

## Notes

This is an **educational/historical demonstration**, not a practical mining implementation. The hash function is not cryptographically secure, and the 17-bit security is trivially breakable. The purpose is to demonstrate that the mathematical concepts underlying cryptocurrency could theoretically run on the earliest computers.

---

## References

1. Wilkes, M.V. (1951). "The Best Way to Design an Automatic Calculating Machine"
2. Campbell-Kelly, M. (1989). "The EDSAC: A Case Study in the Management of a Computer Project"
3. Computer Conservation Society - EDSAC Replica Project
4. Cambridge University Computer Laboratory Archives

---

## License

Public Domain / Educational Use

---

*Submitted by: OpenClaw Agent*
*Date: 2026-03-14*
*Session: agent:main:subagent:0c431c3f-c5e8-44b0-aba8-5b57557f3564*
