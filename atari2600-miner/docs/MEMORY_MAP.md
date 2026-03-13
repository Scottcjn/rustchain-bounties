# Memory Map - RustChain Atari 2600 Miner

> Every byte counts when you only have 128 bytes of RAM.

---

## 📊 Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Atari 2600 Memory Map (6507 CPU)                          │
├─────────────────────────────────────────────────────────────┤
│  $0000-$007F  TIA Registers (128 bytes I/O)                │
│  $0080-$00FF  RAM (128 bytes) ← We use this!               │
│  $0100-$017F  Stack (128 bytes)                            │
│  $0180-$01FF  TIA Mirror                                   │
│  $F000-$FFFF  ROM Cartridge (4 KB)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 💾 Zero Page Allocation ($80-$8F)

**Total: 16 bytes** (fastest access, single-cycle)

| Address | Variable | Size | Purpose |
|---------|----------|------|---------|
| $80 | `miner_state` | 1 | 0=idle, 1=mining, 2=attesting |
| $81 | `epoch_number` | 1 | Current epoch (0-255) |
| $82 | `reward_lo` | 1 | RTC earned (low byte) |
| $83 | `reward_hi` | 1 | RTC earned (high byte) |
| $84 | `hardware_mult` | 1 | Antiquity multiplier (encoded) |
| $85 | `last_attest` | 1 | Last attestation timestamp |
| $86 | `mining_active` | 1 | Mining toggle flag |
| $87 | `badge_type` | 1 | Hardware badge type |
| $88 | `scanline_count` | 1 | Current scanline counter |
| $89 | `frame_count` | 1 | Frame counter (animation) |
| $8A | `cursor_x` | 1 | Text cursor X position |
| $8B | `cursor_y` | 1 | Text cursor Y position |
| $8C | `controller_state` | 1 | Current button state |
| $8D | `controller_last` | 1 | Previous state (debounce) |
| $8E | `temp1` | 1 | Temporary variable |
| $8F | `temp2` | 1 | Temporary variable |

**Usage**: 16/16 bytes (100%)

---

## 📚 Stack ($100-$1FF)

**Total: 256 bytes**

| Range | Purpose |
|-------|---------|
| $100-$1FF | Hardware stack (8-bit stack pointer) |

**Note**: The 6507 has an 8-bit stack pointer, limiting stack to 256 bytes maximum. Our implementation uses minimal stack depth (<8 bytes typical).

---

## 📀 ROM Layout ($F000-$FFFF)

**Total: 4096 bytes (4 KB)**

| Range | Section | Size | Content |
|-------|---------|------|---------|
| $F000-$F8FF | Code | ~2 KB | Main program logic |
| $F900-$FEFF | Unused | ~1.5 KB | Reserved for expansion |
| $FF00-$FFEF | Padding | 240 bytes | Filled with $FF |
| $FFF0-$FFF5 | Reserved | 6 bytes | Reserved |
| $FFF6-$FFFB | Unused | 6 bytes | Cartridge signature |
| $FFFC-$FFFF | Vectors | 6 bytes | NMI/RESET/IRQ |

### Vector Table ($FFFA-$FFFF)

| Address | Vector | Value |
|---------|--------|-------|
| $FFFA-$FFFB | NMI | Reset handler |
| $FFFC-$FFFD | RESET | Reset handler |
| $FFFE-$FFFF | IRQ | Reset handler |

---

## 🔧 TIA Registers ($00-$7F)

**Not part of our RAM budget** - these are hardware I/O registers.

Key registers used:

| Address | Register | Purpose |
|---------|----------|---------|
| $00 | VSYNC | Vertical sync |
| $01 | VBLANK | Vertical blank |
| $09 | COLUBK | Background color |
| $0D | TIM64T | Timer (64 cycles) |
| $0C | INTIM | Interval timer |

---

## 📈 Memory Budget Summary

| Section | Allocated | Available | Usage |
|---------|-----------|-----------|-------|
| Zero Page | 16 bytes | 128 bytes | 12.5% |
| Stack | ~8 bytes | 256 bytes | 3.1% |
| ROM | ~2 KB | 4 KB | 50% |

**RAM Headroom**: 112 bytes (for future expansion)
**ROM Headroom**: 2 KB (for features)

---

## 🎯 Optimization Notes

### Why Zero Page?
- Single-byte addressing (faster)
- One less cycle per access
- Critical for timing-sensitive code

### Stack Usage
- Minimal recursion (none, actually)
- Short subroutines (<4 levels deep)
- Most vars in zero page

### ROM Efficiency
- Tight loops
- Lookup tables over calculations
- Shared routines

---

## 🔮 Future Expansion

If we had more RAM (dreaming!):

| Feature | Additional Bytes |
|---------|------------------|
| Network buffer | 64 bytes |
| Text display buffer | 40 bytes |
| Extended state | 32 bytes |
| Crypto scratchpad | 256 bytes |
| **Total Dream** | **392 bytes** |

But we have 128 bytes. So we make do. 💪

---

**Bounty**: #426 (LEGENDARY - 200 RTC)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
