# RustChain PDP-1 Miner (1959) - LEGENDARY Tier

**Bounty**: #1845 - 200 RTC ($20)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Multiplier**: 5.0x (Maximum - LEGENDARY Tier)

> *"The PDP-1 was DEC's first computer (1959) and launched the minicomputer industry"*

## Historical Significance

The PDP-1 (Programmed Data Processor-1) is one of the most important computers in history:

- **First interactive computer** - Users could interact in real-time
- **First video game** - Spacewar! (1962) was created on the PDP-1
- **Birthplace of hacker culture** - MIT's Tech Model Railroad Club
- **Transistor-based** - ~2,700 transistors, 3,000 diodes
- **18-bit architecture** - Unique word size that defined early computing
- **Magnetic-core memory** - 4K words standard (expandable to 64K)

## Technical Specifications

| Component | Specification |
|-----------|---------------|
| **Year** | 1959 |
| **Word Size** | 18 bits |
| **Memory** | 4,096 words (9.2 KB) |
| **Technology** | Discrete transistors |
| **Clock Speed** | 187 kHz (5.35μs cycle) |
| **Performance** | ~100,000 instructions/sec |
| **Number Representation** | One's complement |
| **I/O** | Punched tape, Type 30 CRT display |

## Project Structure

```
pdp1-miner/
├── README.md              # This file
├── pdp1_cpu.py            # PDP-1 CPU simulator (18-bit)
├── pdp1_miner.py          # RustChain miner for PDP-1
├── sha256_pdp1.py         # SHA-256 optimized for 18-bit words
├── attestation.py         # Hardware attestation generator
├── test_miner.py          # Test suite
└── docs/
    └── PDP1_ARCHITECTURE.md  # Detailed architecture docs
```

## Quick Start

```bash
# Run the PDP-1 simulator with miner
python pdp1_miner.py --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b

# Run tests
python test_miner.py

# Generate attestation
python attestation.py --output attestation.json
```

## How It Works

### PDP-1 CPU Simulator

The simulator emulates the core PDP-1 architecture:

- **18-bit accumulator (AC)** - Main arithmetic register
- **18-bit multiplier quotient (MQ)** - For multiply/divide
- **4K word memory** - Magnetic-core memory simulation
- **Program counter (PC)** - 18-bit address space
- **Instruction register (IR)** - Holds current instruction
- **One's complement arithmetic** - Historical accuracy

### SHA-256 on 18-bit Architecture

Implementing SHA-256 on an 18-bit machine requires creative bit manipulation:

```python
# 32-bit values stored as two 18-bit words
# High 14 bits in one word, low 18 bits in another
# All operations respect 18-bit boundaries
```

### Mining Algorithm

The miner performs "Proof-of-Antiquity" attestations:

1. **Hardware fingerprinting** - Simulated PDP-1 unique characteristics
2. **Epoch generation** - Create mining epoch with timestamp
3. **SHA-256 computation** - Hash using 18-bit optimized implementation
4. **Attestation signing** - Sign with hardware-derived entropy
5. **Submission** - Format for RustChain network

## Antiquity Multiplier

| Era | Machine | Multiplier |
|-----|---------|------------|
| 1959-1965 | PDP-1 | **5.0x** (LEGENDARY) |
| 1965-1970 | PDP-8 | 4.5x |
| 1978-1982 | 8086 | 4.0x |
| 1982-1985 | 286 | 3.8x |
| 1985-1989 | 386 | 3.5x |

## Files

### `pdp1_cpu.py`
Complete PDP-1 CPU emulator with:
- All original instructions (JMP, JSP, JRN, JLT, etc.)
- I/O device simulation
- Memory management
- Cycle-accurate timing

### `pdp1_miner.py`
Main miner program that:
- Runs on simulated PDP-1
- Generates wallets from hardware entropy
- Performs mining attestations
- Displays status on simulated Type 30 CRT

### `sha256_pdp1.py`
SHA-256 implementation optimized for 18-bit:
- Respects 18-bit word boundaries
- Efficient bit rotation
- Minimal memory footprint

### `attestation.py`
Hardware attestation generator:
- PDP-1 specific fingerprints
- Epoch-based challenges
- RustChain-compatible format

## Testing

```bash
# Run full test suite
python test_miner.py -v

# Test SHA-256 implementation
python test_miner.py::test_sha256

# Test CPU simulator
python test_miner.py::test_pdp1_cpu
```

## License

MIT License - See LICENSE file

## Credits

- **Digital Equipment Corporation** - Original PDP-1 (1959)
- **RustChain** - Proof-of-Antiquity blockchain
- **Computer History Museum** - PDP-1 preservation

## Resources

- [PDP-1 Handbook (1963)](http://bitsavers.org/pdf/dec/pdp1/F-15_PDP-1_Handbook_1963.pdf)
- [Computer History Museum PDP-1](https://computerhistory.org/collections/catalog/102643816)
- [Spacewar! Source Code](https://github.com/tannerdolby/spacewar)

---

*"Every vintage computer has historical potential"* 🖥️
