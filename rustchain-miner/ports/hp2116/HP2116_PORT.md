# HP 2116 (1966) Port - RustChain Miner

## Overview

This port brings the RustChain RIP-PoA miner to the **HP 2116**, Hewlett-Packard's first computer released in 1966. This is a **LEGENDARY Tier** bounty target (200 RTC / $20).

**Wallet Address**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## HP 2116 Architecture

| Feature | Specification |
|---------|---------------|
| **Word Size** | 16 bits |
| **Memory** | Magnetic-core, 4K-32K words (8-64 KB) |
| **Clock** | 10 MHz |
| **Cycle Time** | 1.6 μs |
| **Registers** | A, B (accumulators), P (program counter) |
| **Instructions** | 68 basic instructions |
| **I/O** | 60 interrupt vectors, DMA controller |
| **Weight** | 230 pounds (104 kg) |

## Files

- `hp2116_simulator.py` - Full HP 2116 instruction set simulator
- `hp2116_miner.py` - Adapted miner for HP 2116
- `assembly/miner.asm` - Original-style assembly source code
- `README.md` - Quick start guide

## Running

```bash
# Run simulator test
python hp2116_simulator.py

# Run miner (simulated)
python hp2116_miner.py --wallet YOUR_WALLET --simulated

# Run fingerprint tests
python hp2116_miner.py --test-only
```

## Bounty Claim

**Tier**: LEGENDARY  
**Reward**: 200 RTC ($20)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## License

MIT
