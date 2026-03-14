# Space Invaders Miner - Quick Start Guide

## 🚀 Run the Miner Demo

```bash
cd space-invaders-miner

# Run 10-second mining demo
python space_invaders_miner.py --demo --duration 10

# Run test suite
python test_miner.py

# View 8080 assembly code
python space_invaders_miner.py --asm

# Show help
python space_invaders_miner.py --help
```

## 📁 Project Structure

```
space-invaders-miner/
├── README.md                 # Full documentation
├── space_invaders_miner.py   # Main simulator (600+ lines)
├── miner_8080.asm            # 8080 assembly reference
├── test_miner.py             # Test suite (24 tests)
├── COMPLETION_REPORT.md      # Bounty completion report
└── QUICK_START.md            # This file
```

## ✅ Test Results

```
Ran 24 tests in 0.404s
OK
Tests run: 24
Failures: 0
Errors: 0
```

## 🎮 Demo Output

The miner displays a Space Invaders-themed interface:

```
+==========================================================+
|                   SPACE INVADERS MINER                   |
|       Intel 8080 @ 2.0 MHz | 8KB RAM | Bounty #476       |
+==========================================================+
| Status: MINING                                           |
| Nonce:        999                                        |
| Hash: 5fd4a46c4a0e4fb13c4854ba5ac715fa                   |
+==========================================================+
| Blocks Found:      0                                     |
| Total Hashes:        1000                                |
| Hash Rate:     9600.00 H/s                               |
| RTC Earned:      0 RTC                                   |
+==========================================================+
```

## 🏆 Bounty Information

- **Issue**: #476
- **Reward**: 200 RTC ($20) - LEGENDARY Tier
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
- **Status**: ✅ COMPLETE

## 📚 Hardware Specifications

| Component | Specification |
|-----------|---------------|
| CPU | Intel 8080 @ 2.0 MHz |
| Architecture | 8-bit |
| RAM | 8 KB |
| ROM | 12 KB |
| Display | 224×256 monochrome |

## 🔧 Key Features

- ✅ Intel 8080 CPU emulation
- ✅ SHA-256 mining (simplified difficulty)
- ✅ Space Invaders visual theme
- ✅ Real-time statistics
- ✅ Block found celebration
- ✅ 8080 assembly reference code
- ✅ Comprehensive test suite

---

For full documentation, see [README.md](README.md) and [COMPLETION_REPORT.md](COMPLETION_REPORT.md).
