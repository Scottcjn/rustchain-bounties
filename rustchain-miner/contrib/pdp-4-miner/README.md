# RustChain PDP-4 Miner (1962) - "Core Memory Edition"

## Overview

This is the **RustChain miner ported to the PDP-4**, DEC's 18-bit minicomputer from 1962. This represents one of the oldest architectures ever to run RustChain, earning the **maximum antiquity multiplier**.

## PDP-4 Architecture

| Specification | Value |
|--------------|-------|
| **Word Size** | 18 bits |
| **Memory** | Magnetic core memory |
| **Memory Cycle** | 8 microseconds |
| **Address Space** | 32K words (18-bit addressing) |
| **I/O** | Paper tape, Teletype Model 28 |
| **Year** | 1962 |
| **Original Price** | $65,000 (~$691,832 in 2025) |
| **Units Sold** | ~54 |

## Antiquity Multiplier

The PDP-4 earns the **highest multiplier** in the RustChain ecosystem:

| Architecture | Year | Multiplier |
|-------------|------|------------|
| **PDP-4** | **1962** | **5.0x** ⭐ |
| PDP-8 | 1965 | 4.5x |
| 8086/8088 | 1978 | 4.0x |
| 286 | 1982 | 3.8x |
| 386 | 1985 | 3.5x |
| 486 | 1989 | 3.0x |
| Pentium | 1993 | 2.5x |

## Files

```
pdp-4-miner/
├── README.md              # This file
├── pdp4_miner.py          # Python PDP-4 simulator with miner
├── pdp4_miner.asm         # PDP-4 assembly source
├── pdp4_entropy.asm       # Entropy collection routines
├── boot_paper_tape.tap    # Bootable paper tape image
├── wallet.dat             # Generated wallet (created on first run)
└── attestations/          # Saved attestation records
```

## Quick Start

### Using the Python Simulator (Recommended)

```bash
# Run the PDP-4 miner simulator
python pdp4_miner.py

# First run will generate a wallet
# Wallet saved to: wallet.dat
```

### On Real Hardware (or SIMH Emulator)

1. Load the paper tape image:
   ```
   simh> load boot_paper_tape.tap
   simh> run
   ```

2. The miner will:
   - Collect hardware entropy from core memory timing
   - Generate a unique wallet ID
   - Run attestation loop every 10 minutes
   - Save attestations to paper tape

## How It Works

### Entropy Sources

The PDP-4 miner collects entropy from:

1. **Core Memory Timing Variations** - Magnetic core memory has unique access patterns
2. **Program Counter Skew** - 18-bit PC timing variations
3. **I/O Register States** - Paper tape reader/punch timing
4. **Real-Time Clock** - If equipped with clock option
5. **Manual Switch Settings** - Operator-entered entropy via console switches

### Attestation Format

```
PDP4-ATTESTATION-V1
Wallet: <wallet_id>
Machine: PDP-4/1962
CoreMem: <core_memory_hash>
PCTime: <program_counter_entropy>
IOState: <io_register_state>
Timestamp: <octal_timestamp>
Signature: <hardware_signature>
```

## Configuration

Edit `pdp4_miner.cfg`:

```
# Node configuration
NODE_HOST=50.28.86.131
NODE_PORT=8088

# Mining interval (seconds)
EPOCH_TIME=600

# Dev fee (RTC per epoch)
DEV_FEE=0.001
DEV_WALLET=founder_dev_fund

# Output mode
OUTPUT_MODE=paper_tape  # or: tty, saved_file
```

## Network Connectivity

The PDP-4 can submit attestations via:

1. **Paper Tape Transfer** - Save to tape, transfer to modern system
2. **Acoustic Coupler** - 110/300 baud modem (if equipped)
3. **Current Loop Interface** - Direct serial connection

For offline systems, attestations are saved locally and can be submitted later via the `dos_bridge.py` utility.

## Building

### Assembler

The PDP-4 uses a one-pass assembler (no macros):

```
> macro12 pdp4_miner.asm
> paper_tape_punch pdp4_miner.bin
```

### Memory Requirements

- **Minimum**: 8K words (144 Kbit core memory)
- **Recommended**: 16K words (288 Kbit core memory)
- **Full Features**: 32K words (576 Kbit core memory)

## Wallet Management

### First Run

On first execution, the miner generates a wallet:

```
PDP-4 MINER - Fossil Edition
Initializing core memory entropy...
Collecting PC timing variations...
Reading console switches...
Wallet generated: PDP4-WALLET-XXXXXXXX
SAVE THIS TO PAPER TAPE!
```

### Backup Your Wallet

```bash
# Punch wallet to paper tape
pdp4> punch wallet.dat

# Or save to DECtape
pdp4> save wallet.dat dt0:wallet.bak
```

**⚠️ WARNING**: If you lose your wallet, you lose your RTC! Backup to multiple paper tapes.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Core memory parity error | Run memory diagnostic, replace bad cores |
| Paper tape read error | Clean tape reader, check tape tension |
| Attestation fails | Verify clock settings, check entropy sources |
| Wallet not found | Restore from backup tape |

## Historical Context

The PDP-4 was DEC's second minicomputer, introduced in 1962 as a slower, cheaper alternative to the PDP-1. Despite its modest sales (~54 units), it established the 18-bit architecture that would power the PDP-7, PDP-9, and PDP-15.

Running RustChain on a PDP-4 represents **the absolute peak of Proof-of-Antiquity mining** - a 1962 computer earning crypto on a 2025+ blockchain.

## License

Apache 2.0 - See LICENSE

## Credits

- Original RustChain DOS Miner: Scott Boudreaux (@Scottcjn)
- PDP-4 Port: [Your Name]
- PDP-4 Architecture: Digital Equipment Corporation (1962)

## Resources

- [PDP-4 Wikipedia](https://en.wikipedia.org/wiki/PDP-4)
- [SIMH PDP-4 Emulator](https://simh.trailing-edge.com/)
- [RustChain Documentation](https://rustchain.org/docs)
- [BCOS Certification](https://github.com/nicholaelaw/awesome-bcos)

---

*"Every vintage computer has historical potential"*

**Wallet Address for Bounty**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
