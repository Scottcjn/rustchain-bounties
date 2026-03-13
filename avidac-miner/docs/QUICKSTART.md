# AVIDAC Miner Quick Start Guide

Get the AVIDAC miner running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for network bridge)

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/avidac-miner.git
cd avidac-miner
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify Installation

Run the test suite:

```bash
python run_tests.py
```

Expected output: `81 passed`

## Quick Test

### Run Simulator

```bash
cd simulator
python cpu.py
```

This runs a simple test program on the AVIDAC CPU simulator.

### Test SHA256

```bash
cd simulator
python sha256.py
```

Expected output: All NIST test vectors pass.

## Mining Demo

### 1. Start Mining (Offline Mode)

```bash
python simulator/mining_demo.py
```

This demonstrates the mining loop without network connection.

### 2. Connect to Network (Optional)

If you have a RustChain wallet:

```bash
python bridge/main.py --wallet YOUR_WALLET_ADDRESS
```

Example:
```bash
python bridge/main.py --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
```

## Assembly Development

### 1. Write Assembly Code

Create `my_program.asm`:

```assembly
; Hello World for AVIDAC
        ORG 0x000
START:  LD  MESSAGE
        OUT DISPLAY
        HLT
        
MESSAGE: DEC 0x48454C4C4F  ; "HELLO"
DISPLAY: EQU 0xFF0

        END START
```

### 2. Assemble

```bash
python simulator/assembler.py my_program.asm -o my_program.bin
```

### 3. Run

```bash
python simulator/cpu.py --load my_program.bin
```

## Architecture Overview

```
avidac-miner/
├── simulator/          # AVIDAC simulator
│   ├── cpu.py         # CPU (40-bit, IAS architecture)
│   ├── williams_tube.py # Memory (5 KB CRT tubes)
│   ├── paper_tape.py  # I/O (paper tape simulation)
│   ├── assembler.py   # Cross-assembler
│   ├── arithmetic.py  # 40-bit math primitives
│   └── sha256.py      # SHA256 hash function
├── assembly/           # Assembly source code
│   └── mining_loop.asm # Mining implementation
├── bridge/             # Network bridge
│   ├── main.py        # Bridge firmware
│   └── protocol.py    # Communication protocol
└── docs/               # Documentation
    ├── IMPLEMENTATION.md
    ├── QUICKSTART.md   # This file
    └── VIDEO.md
```

## Common Commands

### Run Tests
```bash
python -m pytest simulator/tests/ -v
```

### Assemble Code
```bash
python simulator/assembler.py source.asm -o output.bin
```

### CPU Debug Mode
```bash
python simulator/cpu.py --debug
```

### Memory Inspection
```python
from simulator import AVIDACCPU
cpu = AVIDACCPU()
print(cpu.memory.dump_memory(0x000, 16))
```

## Performance

| Metric | Value |
|--------|-------|
| Hash Rate | ~1.0 H/s |
| Instructions/Hash | ~7,100 |
| Memory Usage | 160/1024 words |
| Power (simulated) | ~500W |

## Troubleshooting

### Import Errors

```bash
# Make sure you're in the avidac-miner directory
cd avidac-miner

# Add to PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH  # Linux/Mac
set PYTHONPATH=%CD%;%PYTHONPATH%    # Windows
```

### Test Failures

If tests fail:
1. Check Python version: `python --version` (need 3.8+)
2. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
3. Clear cache: `rm -rf .pytest_cache __pycache__/`

### Network Bridge Issues

Check connectivity:
```bash
curl https://api.rustchain.io/api/v1/mining/job
```

## Next Steps

1. **Read the docs**: `docs/IMPLEMENTATION.md`
2. **Write assembly**: Try modifying `assembly/mining_loop.asm`
3. **Optimize**: Can you make it faster?
4. **Share**: Submit your improvements!

## Resources

- [AVIDAC History](https://www.anl.gov/about/history)
- [IAS Architecture](https://www.computerhistory.org/collections/catalog/102644906)
- [SHA256 Standard](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- [RustChain Bounties](https://github.com/Scottcjn/rustchain-bounties)

## Support

- **GitHub Issues**: [Report bugs](https://github.com/Scottcjn/rustchain-bounties/issues)
- **Discord**: [RustChain Community](https://discord.gg/VqVVS2CW9Q)
- **Documentation**: `docs/` folder

---

**Happy Mining! 🎉**

_The year is 1953. The computer is AVIDAC. The mission is blockchain._
