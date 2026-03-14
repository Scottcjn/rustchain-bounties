# Pac-Man Arcade Hardware Analysis (1980)

## Technical Specifications

### CPU: Zilog Z80

| Parameter | Value |
|-----------|-------|
| Model | Zilog Z80 |
| Clock Speed | 3.072 MHz |
| Architecture | 8-bit |
| Instruction Set | 178 base instructions |
| Registers | A, F, B, C, D, E, H, L, IX, IY, SP, PC |
| Address Bus | 16-bit (64 KB addressable) |
| Data Bus | 8-bit |
| Manufacturing Process | ~3.5 μm |
| Transistor Count | ~8,500 |
| Package | 40-pin DIP |

### Memory Map

```
┌─────────────────────────────────────────────────────────────┐
│ Memory Map - Pac-Man Arcade Board                           │
├─────────────────────────────────────────────────────────────┤
│ 0x0000 - 0x0FFF  : Main CPU ROM (4 KB) - Game Code         │
│ 0x1000 - 0x1FFF  : Character ROM (4 KB) - Graphics         │
│ 0x2000 - 0x27FF  : Sprite ROM (2 KB) - Object Graphics     │
│ 0x2800 - 0x2BFF  : Color PROM (1 KB) - Palette Data        │
│ 0x4000 - 0x4FFF  : Video RAM (4 KB) - Display Buffer       │
│ 0x5000 - 0x57FF  : Sprite RAM (2 KB) - Sprite Attributes   │
│ 0x6000 - 0x6003  : Input Ports (4 bytes) - Controls        │
│ 0x6004 - 0x6005  : Watchdog Timer                          │
│ 0x7000 - 0x7001  : Sound Control                           │
│ 0x8000 - 0x83FF  : Main RAM (1 KB) - Game State            │
│ 0x8400 - 0x87FF  : Additional RAM (1 KB) - Working Memory  │
│ 0x8800 - 0xFFFF  : Unmapped / Expansion                    │
└─────────────────────────────────────────────────────────────┘
```

### Total Available Resources

| Resource | Amount | Modern Equivalent |
|----------|--------|-------------------|
| **Total RAM** | 4 KB | 0.000004 GB |
| **Total ROM** | 48 KB | 0.000048 GB |
| **CPU Speed** | 3.072 MHz | 0.003072 GHz |
| **Instructions/sec** | ~500,000 | Billions/sec (modern) |

### Video System

| Parameter | Value |
|-----------|-------|
| Resolution | 256 × 224 pixels |
| Colors | 16 (from palette) |
| Refresh Rate | 60 Hz |
| Orientation | Vertical (counterclockwise 90°) |
| Video Chip | Custom Namco |

### Audio System

| Component | Function |
|-----------|----------|
| Namco WSG | Waveform generator (music) |
| Discrete | Sound effects (waka waka, etc.) |
| Speaker | Mono, 8-bit DAC |

## RustChain Miner Feasibility Analysis

### Challenge 1: Memory Constraints

**Problem**: RustChain miner typically requires 64+ MB RAM
**Pac-Man**: Only 4 KB available (16,000× less!)

**Solution Approach**:
- Extreme code optimization (assembly language)
- External co-processor for heavy computation
- Minimal state storage (attestation only)

### Challenge 2: Network Connectivity

**Problem**: Original Pac-Man has no network hardware
**Solution**: Add UART/Serial interface

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Pac-Man     │─────▶│  UART/Serial │─────▶│  WiFi Module │
│  Z80 CPU     │      │  Interface   │      │  (ESP8266)   │
└──────────────┘      └──────────────┘      └──────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │  RustChain   │
                       │  Node        │
                       └──────────────┘
```

### Challenge 3: Cryptographic Operations

**Problem**: SHA-256 hashing is computationally expensive
**Z80**: No hardware crypto acceleration

**Solution**:
- Use simplified attestation (timing-based)
- Offload heavy crypto to co-processor
- Focus on hardware fingerprint, not PoW

## Hardware Fingerprint Strategy

### 1. CPU Timing Signature

The Z80's exact timing varies due to:
- Manufacturing tolerances
- Age-related degradation
- Temperature characteristics
- Voltage variations

```python
# Measure instruction execution time
def measure_z80_timing():
    start = read_timer()
    for i in range(1000):
        execute_nop()  # 4 cycles each
    elapsed = read_timer() - start
    return elapsed  # Unique to this specific CPU
```

### 2. ROM Checksum

Original Pac-Man ROMs have known checksums:
- Verify authenticity against database
- Prove hardware is original, not reproduction

### 3. Hardware Revision ID

Different Pac-Man board revisions exist:
- Midway (US) vs Namco (Japan)
- Board revision numbers
- Component date codes

## Modified Hardware Requirements

To make a functional miner, add:

| Component | Purpose | Estimated Cost |
|-----------|---------|----------------|
| ESP8266/ESP32 | WiFi connectivity | $5-10 |
| Level Shifter | 5V ↔ 3.3V logic | $2 |
| External RAM | Additional storage | $5 |
| UART Interface | Serial communication | $3 |
| **Total** | | **~$15-20** |

## Power Consumption

| Component | Power Draw |
|-----------|------------|
| Original Pac-Man | ~50W |
| Added Electronics | ~2W |
| **Total** | **~52W** |

## Environmental Impact

By mining on vintage hardware:
- ✅ Preserves computing history
- ✅ No e-waste (reusing existing hardware)
- ✅ Educational value
- ✅ Lower energy than modern ASIC miners

## Comparison: Pac-Man vs Modern Miner

| Metric | Pac-Man (1980) | Modern GPU Miner |
|--------|----------------|------------------|
| **Age** | 44 years | <5 years |
| **Power Efficiency** | 0.0001 H/W | High H/W |
| **Antiquity Multiplier** | 3.5× | 1.0× |
| **Cultural Value** | ⭐⭐⭐⭐⭐ | ⭐ |
| **Educational Value** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Raw Hashrate** | Very Low | Very High |
| **Fun Factor** | 🎮🎮🎮🎮🎮 | 🎮 |

## Conclusion

While a fully functional Pac-Man miner is technically challenging due to extreme resource constraints, the **conceptual port** demonstrates:

1. **Proof-of-Antiquity Philosophy**: Valuing old hardware over raw performance
2. **Technical Creativity**: Pushing boundaries of what's possible
3. **Community Engagement**: Fun, educational project
4. **Historical Preservation**: Celebrating computing history

The Python simulator provides a working demonstration of the attestation concept, while the documentation shows the path to a real hardware implementation.

---

**"The best miner isn't the fastest—it's the one with the best story."**
