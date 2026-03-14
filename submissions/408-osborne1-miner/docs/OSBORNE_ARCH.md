# Osborne 1 Architecture Deep Dive

## 🖥️ System Overview

The Osborne 1 (1981) was the first commercially successful portable computer.

### Physical Specifications
- **Weight**: 10.7 kg (23.5 lbs)
- **Dimensions**: 23 × 33 × 18 cm
- **Display**: 5" CRT, 52 columns × 24 rows
- **Keyboard**: Detachable, full-travel

### Technical Specifications

| Component | Detail |
|-----------|--------|
| CPU | Zilog Z80 @ 4.0 MHz |
| RAM | 64 KB (65,536 bytes) |
| ROM | 10 KB (BIOS) |
| OS | CP/M 2.2 |
| Storage | 2× 5¼" floppy drives (90 KB each) |
| Serial | 2× RS-232 (1200 baud) |
| Parallel | 1× Centronics printer port |

---

## 🔌 Z80 CPU Architecture

### Register Set

```
8-bit registers:  A  (accumulator)
                  F  (flags)
                  B, C, D, E, H, L (general purpose)

16-bit pairs:     AF (accumulator + flags)
                  BC (counter/data)
                  DE (data pointer)
                  HL (memory pointer - most versatile)
                  IX, IY (index registers)
                  SP (stack pointer)
                  PC (program counter)
```

### Key Instructions for Mining

| Instruction | Cycles | Use Case |
|-------------|--------|----------|
| `ADD A, r` | 4 | Addition |
| `ADC A, r` | 4 | Addition with carry |
| `XOR r` | 4 | XOR operation |
| `AND r` | 4 | AND operation |
| `RLCA` | 4 | Rotate left |
| `RRCA` | 4 | Rotate right |
| `LD (HL), A` | 7 | Memory store |
| `LD A, (HL)` | 7 | Memory load |
| `DJNZ label` | 13/8 | Loop decrement |
| `CP r` | 4 | Compare |

### Timing Considerations

- 4 MHz clock = 250 ns per cycle
- Typical instruction: 4-16 cycles (1-4 μs)
- Memory access: 3 cycles minimum
- **No cache, no pipeline, no branch prediction**

---

## 💾 Memory Map

```
0x0000-0x00FF:  Interrupt vectors / Zero page
0x0100-0xFFFF:  Available RAM (64 KB total)

CP/M Memory Layout:
0x0000-0x00FF:  BDOS/BIOS entry points
0x0100-0x01FF:  Transient Program Area (TPA) start
0x0100:         Program load address (.COM files)
...
High memory:    CCP + BDOS + BIOS (resident)
```

### Available for User Program
- **~60 KB** for application code + data
- Must fit: code, stack, heap, buffers

---

## 📀 CP/M 2.2 System

### File System
- 8.3 filename format (e.g., `MINER.COM`)
- 128-byte sectors
- Block-based allocation

### System Calls (BDOS)

| Function | C Register | Description |
|----------|------------|-------------|
| 1 | Console input | Wait for keypress |
| 2 | Console output | Print character |
| 9 | Print string | `$`-terminated string |
| 14 | Select disk | A=0, B=1, etc. |
| 15 | Open file | FCB in DE |
| 16 | Close file | FCB in DE |
| 20 | Read file | Sequential read |
| 21 | Write file | Sequential write |

### .COM File Format
- Raw binary, loaded at 0x0100
- Entry point: 0x0100
- Exit: `JP 0x0000` (return to CCP)
- Maximum size: ~60 KB

---

## ⚡ Power Consumption

- **AC Adapter**: 120V AC, 60 Hz
- **Power Draw**: ~45 watts
- **Battery**: None (not battery powered!)
- **Heat**: Significant (CRT + electronics)

---

## 🎯 Mining Feasibility Analysis

### Modern SHA-256 Requirements
- 32-bit arithmetic ✓ (emulated, slow)
- 64-bit counters ✓ (emulated, very slow)
- Large state (8× 32-bit = 32 bytes) ✓
- 64 rounds × 64 ops = 4096 ops/block ✗ (too slow)

### Estimated SHA-256 Performance on Z80
- One round: ~500 instructions × 8 cycles = 4000 cycles
- 64 rounds: 256,000 cycles
- At 4 MHz: 64 ms per hash
- **~15 hashes/second** (optimistic)

### OsborneHash Performance
- One hash: ~200 instructions × 6 cycles = 1200 cycles
- At 4 MHz: 300 μs per hash
- **~3,300 hashes/second** ✓

### Conclusion
SHA-256 is impractical. Custom 16-bit PoW is feasible and educational.

---

## 📝 Development Tools

### Cross-Assembly (Modern)
- **z80asm**: Cross-assembler for Z80
- **sjasmplus**: Modern Z80 assembler
- **pasmo**: Multi-platform Z80 assembler

### Emulation
- **MAME**: Full Osborne 1 emulation
- **Z80Pack**: CP/M emulation
- **RunCPM**: Arduino/ESP32 CP/M

### Debugging
- **Z80SIM**: Z80 simulator with debugging
- **B2E**: Binary to EPROM burner software

---

## 🔗 References

1. Osborne 1 Technical Manual (1981)
2. Z80 CPU User Manual (Zilog)
3. CP/M 2.2 Interface Guide (Digital Research)
4. "The Osborne 1: A Retrospective" - IEEE Annals (2006)
