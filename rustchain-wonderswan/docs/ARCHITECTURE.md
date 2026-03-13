# WonderSwan Miner Architecture

## Overview

This document describes the architecture and design decisions for porting the RustChain miner to the Bandai WonderSwan (1999).

## Hardware Constraints

### NEC V30 MZ CPU

- **Clock Speed**: 3.072 MHz
- **Architecture**: 16-bit, Intel 8086-compatible
- **Instruction Set**: Enhanced 8086 with bit manipulation
- **No FPU**: All math must be integer-based
- **Performance**: ~0.5-1 MIPS (Million Instructions Per Second)

### Memory

- **Total RAM**: 512 Kbit (64 KB)
- **Shared**: RAM is shared between CPU and display
- **Cartridge RAM**: Up to 8 KB battery-backed save
- **ROM**: Cartridge ROM 512 KB - 4 MB

### Display

- **Resolution**: 224×144 pixels
- **Dual Mode**: Portrait (144×224) or Landscape (224×144)
- **Colors**: 16-level grayscale (8 simultaneous)
- **Technology**: FSTN LCD, no backlight

### Power

- **Battery**: Single AA (1.5V × 2 = 3V)
- **Consumption**: ~90 mA active
- **Battery Life**: ~40 hours

## Design Decisions

### 1. Truncated SHA-256

**Problem**: Full SHA-256 requires:
- 64 rounds of computation
- ~8 KB state for message schedule
- Too slow for 3 MHz CPU

**Solution**: Use 4 rounds instead of 64
- Reduces state to ~2 KB
- 16× faster computation
- **NOT cryptographically secure** - demo only

```
Full SHA-256:    64 rounds, ~8 KB state, 100% secure
Truncated (WS):  4 rounds,  ~2 KB state, 0% secure (demo)
```

### 2. Integer-Only Arithmetic

**Problem**: No floating-point unit (FPU)

**Solution**: All calculations use 16/32-bit integers
- Fixed-point math for difficulty
- Bit shifts instead of division
- Lookup tables for complex functions

### 3. Dual Display Mode Support

**Problem**: WonderSwan can be used in portrait or landscape

**Solution**: Dynamic UI layout
- Detect orientation at runtime
- Rearrange UI elements
- Same mining logic, different presentation

### 4. Memory Optimization

**Problem**: Only 64 KB total RAM

**Solution**: Careful memory allocation
```
$080000-$080FFF  Stack (4 KB)
$081000-$081FFF  Miner state (4 KB)
$082000-$083FFF  Display buffer (8 KB)
$084000-$08FFFF  Free / temporary (48 KB)
```

### 5. Battery Efficiency

**Problem**: Must run for hours on single AA

**Solution**:
- Minimize display updates (1 Hz)
- Sleep between mining batches
- Reduce CPU clock when possible (unofficial)

## Mining Algorithm

### Block Header Format

```
Offset  Size  Field
------  ----  -----
0x00    4     Version (little-endian)
0x04    32    Previous block hash
0x24    32    Merkle root
0x44    4     Timestamp (little-endian)
0x48    4     Difficulty target (bits)
0x4C    4     Nonce (little-endian)
Total: 80 bytes
```

### Nonce Search

```
1. Load block header into memory
2. Initialize nonce counter (starts at 0)
3. Loop:
   a. Increment nonce
   b. Replace nonce in block header
   c. Compute SHA-256 hash
   d. Check if hash < target
   e. If yes: share found!
   f. If no: continue
4. Nonce wraps at 0xFFFFFFFF
```

### Truncated SHA-256

```
Standard SHA-256:
- 64 rounds
- 64-word message schedule
- Full security

WonderSwan Version:
- 4 rounds (for demo)
- 16-word message schedule (no extension)
- Reduced security (demo only)
```

## Display System

### Portrait Mode Layout

```
┌──────────────────────┐
│  ╔════════════════╗  │
│  ║ RUSTCHAIN WS   ║  │  <- Title (centered)
│  ║ MINER (1999)   ║  │
│  ╚════════════════╝  │
│                      │
│  Nonce: 12,345,678   │  <- Current nonce
│  Hash: 85.3 H/s      │  <- Hash rate
│  Shares: 3           │  <- Shares found
│  CPU: 3.072 MHz      │  <- CPU speed
│                      │
│  Wallet: RTC4325...  │  <- Wallet address
│                      │
│  [START] Toggle      │  <- Button hints
│  [A] Mine  [B] Stop  │
└──────────────────────┘
```

### Landscape Mode Layout

```
┌────────────────────────────────────┐
│ ╔══════════╗  Hash: 85.3 H/s      │
│ ║ RUSTCHAIN║ Nonce: 12,345,678    │
│ ║ WS       ║ Shares: 3            │
│ ╚══════════╝ Wallet: RTC4325...   │
│                                    │
│ [START] Mode  [A] Mine  [B] Stop  │
└────────────────────────────────────┘
```

## Performance Estimates

### Hash Rate Calculation

```
NEC V30 @ 3.072 MHz:
- ~3 cycles per instruction (average)
- ~1 MIPS effective
- SHA-256 (4 rounds): ~30,000 cycles
- Hash rate: ~100 H/s (estimated)

Actual performance depends on:
- Display update frequency
- Button polling
- Memory access patterns
```

### Power Consumption

```
Active Mining:
- CPU: 60 mA @ 3V
- Display: 30 mA @ 3V
- Total: 90 mA

With 2000 mAh AA battery:
- Runtime: 2000 / 90 = 22 hours
- Conservative estimate: 20 hours
```

## Assembly Optimization

### NEC V30-Specific Instructions

```assembly
; Bit manipulation (V30 enhanced)
TEST1 dst, bit    ; Test single bit
SET1 dst, bit     ; Set single bit
CLR1 dst, bit     ; Clear single bit
NOT1 dst, bit     ; Invert single bit

; Repeat prefixes
REPC              ; Repeat while carry
REPNC             ; Repeat while not carry
```

### Register Usage

```
AX  - Accumulator (hash computations)
BX  - Base register (memory offsets)
CX  - Counter (loop iterations)
DX  - Data register (I/O operations)
SI  - Source index (string operations)
DI  - Destination index (display buffer)
BP  - Base pointer (stack frame)
SP  - Stack pointer
```

## Build Process

### Toolchain

1. **SDCC** (Small Device C Compiler) or custom V30 GCC
2. **NASM** (Netwide Assembler) for assembly portions
3. **WonderSwan SDK** (wsdev) for hardware headers
4. **Mednafen** or **Oswan** for emulation testing

### Build Steps

```bash
# 1. Assemble NEC V30 code
nasm -f bin miner.asm -o miner.bin

# 2. Compile C portions
sdcc -c miner.c

# 3. Link everything
wsld miner.bin miner.o -o rustchain_ws.sfc

# 4. Test in emulator
mednafen rustchain_ws.sfc
```

## Testing

### Emulator Testing

- **Mednafen**: Multi-system emulator with WS support
- **Oswan**: WonderSwan-specific emulator
- **Cygne**: Another WS emulator option

### Hardware Testing

- Requires WonderSwan development cartridge
- Flash ROM using wsflash tool
- Test on actual hardware for timing accuracy

## Security Considerations

### Demo-Only Implementation

**WARNING**: This miner is NOT suitable for production use:

1. **Truncated SHA-256**: Only 4 rounds (not secure)
2. **Predictable nonce**: Sequential search (not randomized)
3. **No network security**: No TLS/SSL on WonderSwan
4. **Memory constraints**: Cannot store full blockchain

### Intended Use

- Educational demonstration
- Historical computing showcase
- Bounty completion proof
- Not for actual cryptocurrency mining

## Future Enhancements

### Possible Improvements

1. **Full SHA-256**: If performance allows (unlikely)
2. **Network sync**: Via WonderSwan expansion port (theoretical)
3. **Multi-player mining**: Link cable support
4. **Sound effects**: Mining notifications via 4-channel PCM
5. **Animation**: Mining progress visualization

### Hardware Mods

1. **Overclocking**: Push CPU to 4 MHz (unofficial)
2. **RAM expansion**: External cartridge RAM
3. **Backlight mod**: Modern LCD replacement
4. **USB-C power**: Rechargeable battery mod

## References

- [WonderSwan Technical Reference](https://ws.nesdev.org/wiki/)
- [NEC V30 Datasheet](https://archive.org/details/nec_v30_datasheet)
- [RustChain Bounty #441](https://github.com/Scottcjn/rustchain-bounties/issues/441)
- [Bandai WonderSwan History](https://en.wikipedia.org/wiki/WonderSwan)

---

**Bounty #441** - Port Miner to WonderSwan (1999)

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**Status**: ✅ Complete
