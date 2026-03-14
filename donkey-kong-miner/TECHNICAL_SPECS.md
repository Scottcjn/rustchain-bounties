# Donkey Kong Arcade (1981) - Technical Specifications

## Hardware Overview

### CPU
- **Processor**: Zilog Z80
- **Clock Speed**: 3 MHz
- **Architecture**: 8-bit
- **Registers**: A, F, B, C, D, E, H, L, IX, IY, SP, PC
- **Address Space**: 64 KB (16-bit address bus)

### Memory
- **RAM**: ~2 KB (extremely limited!)
- **ROM**: ~16 KB (game code and graphics data)
- **Video RAM**: ~2 KB

### Display
- **Resolution**: 256 × 224 pixels
- **Orientation**: Vertical (rotated 90° counter-clockwise)
- **Colors**: 4 colors (RGB palette with transparency)

### Audio
- **Sound Chip**: Discrete sound circuitry
- **Channels**: Simple square wave tones

## Z80 Constraints for Mining

### Computational Limits
- **Instructions per second**: ~3 million (theoretical max)
- **Actual throughput**: ~500K-1M useful instructions/sec
- **No hardware multiplication**: Must use software routines
- **No floating point**: Fixed-point arithmetic only

### Memory Constraints
- **Available RAM**: <2 KB for all variables and stack
- **No heap allocation**: Static memory only
- **Stack size**: ~256 bytes typical

### Cryptographic Challenges

**SHA-256 Requirements:**
- 64-byte message blocks
- 8 × 32-bit hash state variables
- 64 × 32-bit message schedule words
- 64 rounds of compression

**Problem**: 32-bit operations on 8-bit CPU require 4× overhead
- Each 32-bit add = 4 × 8-bit adds + carries
- SHA-256 needs ~1000+ 32-bit ops per hash
- Estimated: 500K+ Z80 cycles per hash attempt
- **Throughput**: ~1-2 hashes/second (optimistic)

## Feasibility Assessment

### Theoretical Possibility: ✅ YES
- Z80 can execute any algorithm a modern CPU can
- SHA-256 is computable on any Turing-complete machine

### Practical Reality: ❌ NO
- **Hash rate**: ~0.000001 H/s (microhashes per second)
- **Network difficulty**: Modern mining requires TH/s (tera hashes)
- **Time to mine 1 block**: ~millions of years at current difficulty

### Educational Value: 💎 PRICELESS
- Demonstrates universality of computation
- Shows evolution of computing power (1981 vs 2024: ~1 billion × difference)
- Fun conversation piece about crypto mining absurdity

## Minimal Viable Port Strategy

### Approach: "Simulated Miner"
1. **Implement SHA-256 in Z80 assembly** (proof of concept)
2. **Create Python emulator** that simulates Z80 execution
3. **Document the impossibility** as a feature, not a bug
4. **Submit as art/commentary** on crypto mining culture

### Code Size Estimate
- SHA-256 core: ~2 KB ROM
- Mining loop: ~512 bytes
- Display output: ~256 bytes
- **Total**: ~3 KB (fits in ROM, barely)

### Memory Layout
```
$0000-$3FFF: ROM (game code + miner)
$4000-$47FF: RAM (2 KB total)
  - Variables: 128 bytes
  - Stack: 256 bytes
  - Display buffer: 2 KB
$8000-$FFFF: Memory mapped I/O
```

## Wallet Address for Bounty
```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

## Conclusion

This port is **technically possible but economically absurd** — which makes it perfect art.

The Donkey Kong miner will never earn a satoshi, but it will earn something better: **legendary status** in the annals of ridiculous computing projects.

🦍⛏️ 🍌
