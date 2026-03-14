# Amiga 500 Miner - RustChain Port

## 🎯 Bounty Claim
**Wallet Address:** `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Tier:** LEGENDARY (200 RTC / $20)  
**Issue:** #412 - Port Miner to Amiga 500 (1987)

---

## 🖥️ Amiga 500 Architecture Overview

### Hardware Specifications (1987)

| Component | Specification |
|-----------|---------------|
| **CPU** | Motorola 68000 @ 7.14 MHz |
| **Architecture** | 16/32-bit hybrid (32-bit registers, 16-bit data bus) |
| **RAM** | 512 KB Chip RAM (expandable to 1 MB) |
| **ROM** | 256 KB Kickstart ROM |
| **Graphics** | OCS (Original Chip Set), 4096 colors |
| **Sound** | 4-channel Paula chip |
| **Storage** | 3.5" floppy disk (880 KB) |
| **Network** | None built-in (serial port available) |

### Motorola 68000 Key Features

- **Registers:** 8 data registers (D0-D7), 8 address registers (A0-A7)
- **Address Space:** 24-bit (16 MB max)
- **Instruction Set:** CISC, orthogonal design
- **No FPU:** All math must be integer-based
- **Endianness:** Big-endian

---

## 📐 Mining Feasibility Analysis

### SHA-256 on 68000

**Challenges:**
1. **No hardware crypto acceleration** - All operations in software
2. **Limited registers** - Must spill to memory frequently
3. **16-bit data bus** - 32-bit operations require multiple cycles
4. **7.14 MHz clock** - ~100x slower than modern CPUs
5. **512 KB RAM** - Cannot store full blockchain, must use simplified proof-of-work

**Estimated Performance:**
- SHA-256 requires 64 rounds of complex operations
- On 68000: ~50,000 cycles per hash (optimistic)
- Hashes per second: 7,140,000 / 50,000 ≈ **143 H/s**
- Modern GPU: ~100 GH/s (1 billion times faster)

### Conclusion

Real mining is **not economically viable**. This is a **proof-of-concept/educational port** demonstrating:
1. Understanding of 68000 assembly
2. SHA-256 implementation in constrained environment
3. Historical computing preservation
4. Cross-architecture cryptocurrency concepts

---

## 📁 Project Structure

```
amiga500-miner/
├── README.md                 # This file
├── docs/
│   ├── ARCHITECTURE.md       # Amiga 500 technical details
│   ├── SHA256_68K.md         # SHA-256 implementation notes
│   └── BOUNTY_CLAIM.md       # Bounty submission details
├── src/
│   ├── sha256.asm            # 68000 assembly SHA-256
│   ├── miner.asm             # Main miner loop
│   └── miner.c               # C implementation (vbcc)
├── simulator/
│   ├── amiga_emulator.py     # Python Amiga 68000 emulator
│   ├── sha256_ref.py         # Reference SHA-256
│   └── test_vectors.py       # Test cases
└── build/
    ├── Makefile              # Cross-compiler makefile
    └── linkscript.ld         # Linker script
```

---

## 🔧 Development Environment

### Cross-Compilation Tools

```bash
# Required tools
- m68k-amigaos-gcc (GNU toolchain)
- vbcc (Volker Barthelmann C Compiler)
- vasm (macro assembler)
```

### Building

```bash
cd build
make clean
make miner
```

### Testing with Simulator

```bash
cd simulator
python amiga_emulator.py --test
```

---

## 📝 Implementation Notes

### Memory Layout

```
$000000 - $07FFFF  Chip RAM (512 KB)
  $000000          System vectors
  $000400          Exec base
  $080000          Our miner code
  $0C0000          Stack
  $0FFFFF          End of RAM
```

### Optimizations

1. **Loop unrolling** - Reduce branch overhead
2. **Register allocation** - Keep hot data in D0-D7
3. **Bit manipulation** - Use 68000 bitfield instructions
4. **Look-up tables** - Pre-compute SHA-256 constants in ROM

---

## 🏆 Bounty Completion Checklist

- [x] Amiga 500 architecture research
- [x] SHA-256 algorithm analysis for 68000
- [x] Python simulator created
- [x] Assembly reference implementation
- [x] Documentation complete
- [x] Wallet address included for bounty claim

---

## 📚 References

- [Motorola 68000 Programmer's Reference Manual](https://www.nxp.com/docs/en/reference-manual/M68000PRM.pdf)
- [Amiga Hardware Reference Manual](http://amigadev.elowar.com/read/ADCD_2.1/Hardware_Manual_guide.html)
- [SHA-256 Specification (FIPS 180-4)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)

---

*This project is for educational and historical preservation purposes. Actual mining on Amiga 500 is not economically viable.*
