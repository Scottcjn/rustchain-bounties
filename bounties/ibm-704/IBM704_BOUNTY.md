# [BOUNTY] Port RustChain Miner to IBM 704 (1954) - 200 RTC (LEGENDARY Tier)

## IBM 704 RTC Miner — 200 RTC Bounty (LEGENDARY Tier)

**Get the IBM 704 mining RustChain tokens.** The IBM 704 was introduced in **1954** — **IBM's first mass-produced computer with hardware floating-point arithmetic**. Designed by John Backus and Gene Amdahl, this is the machine that gave birth to FORTRAN and LISP. If you can make this work, you earn the **5.0x antiquity multiplier**, the absolute maximum in RustChain.

This is **scientific computing heritage meets blockchain**: **1954 meets 2026**.

---

## Why IBM 704?

- **1954 hardware** — the first mass-produced computer with floating-point hardware
- **Magnetic-core memory** — 4,096 words (18,432 bytes) of reliable core storage
- **36-bit word architecture** — sophisticated scientific computing design
- **12,000 floating-point additions per second** — blazing fast for its era
- **Vacuum-tube logic** — ~2,000 vacuum tubes
- **Historical significance** — FORTRAN and LISP were developed for this machine
- **123 systems produced** (1955-1960) — rare but more common than contemporaries
- **5.0x multiplier** — the highest reward tier possible
- **John Backus & Gene Amdahl design** — legendary computer architects

### IBM 704 vs IBM 702 vs IBM 650

| Feature | IBM 704 (1954) | IBM 702 (1953) | IBM 650 (1953) |
|---------|----------------|----------------|----------------|
| Architecture | Scientific (binary) | Business (character) | Business (decimal) |
| Memory | Magnetic-core (4K words) | Williams tube (2K-10K chars) | Magnetic drum (2K words) |
| Word size | 36 bits | 7-bit characters | 10-digit decimal |
| Floating-point | **Hardware support** | Software only | Software only |
| Clock | ~220 kHz | ~200 kHz | ~12.5 kHz |
| Add time | ~24 μs | ~250 μs | ~10 ms |
| Memory capacity | 18,432 bytes | ~10,000 bytes | ~2,000 bytes |
| Production | 123 units | 14 units | ~2,000 units |
| Purpose | Scientific computing | Business data processing | Business accounting |
| Challenge level | ⭐⭐⭐⭐⭐ (FP hardware) | ⭐⭐⭐⭐⭐ (Character arch) | ⭐⭐⭐⭐⭐ (Drum memory) |

**IBM 704 is unique**: First computer with hardware floating-point, birthplace of FORTRAN and LISP, the machine that made scientific computing practical.

---

## The Ultimate Challenge

This is one of the most prestigious bounties in RustChain:

- **No networking** — must build custom interface (punched cards or magnetic tape)
- **Magnetic-core memory** — reliable but requires precise timing
- **36-bit architecture** — non-standard word size
- **Floating-point hardware** — unique format (8-bit excess-128 exponent, 27-bit fraction)
- **Vacuum tube reliability** — MTBF ~8 hours, requires maintenance
- **Punched card I/O** — IBM 711 card reader, IBM 721 card punch
- **Magnetic tape option** — IBM 727 tape units for faster I/O
- **Console programming** — 36 toggle switches for manual input

### Technical Requirements

#### 1. Network Interface (50 RTC)

- Build punched card or magnetic tape interface using microcontroller
- Microcontroller handles TCP/IP and HTTPS
- IBM 704 reads network response via card reader or tape
- IBM 704 punches requests via card punch or tape
- Alternative: IBM 740 CRT display + camera interface

#### 2. IBM 704 Assembler (50 RTC)

- Create cross-assembler for IBM 704 instruction set (SAP - Symbolic Assembly Program)
- Build simulator for testing (Python/C++)
- Support Type A and Type B instruction formats
- Index register (decrement register) handling
- Punched card format emulation

#### 3. Core Miner (75 RTC)

- 36-bit SHA256 implementation (optimized for word size)
- Hardware floating-point utilization (if beneficial)
- Hardware fingerprinting (core memory timing, tube characteristics)
- Attestation protocol via card/tape interface
- Memory optimization (4,096 words = plenty of space!)

#### 4. Proof & Documentation (25 RTC)

- Video of IBM 704 mining
- Miner visible in rustchain.org/api/miners
- Complete documentation
- Open source all code

---

## The 5.0x Multiplier

```
ibm704 / magnetic_core / floating_point — 5.0x base multiplier (MAXIMUM TIER)
```

An IBM 704 from a museum = the highest-earning miner in RustChain history.

### Expected Earnings

| Metric | Value |
|--------|-------|
| Base reward | 0.12 RTC/epoch |
| With 5.0× multiplier | 0.60 RTC/epoch |
| Per day (144 epochs) | 86.4 RTC |
| Per month | ~2,592 RTC |
| Per year | ~31,104 RTC |

At $0.10/RTC: **~$3,110/year** in mining rewards.

---

## Hardware Required

| Component | Notes | Estimated Cost |
|-----------|-------|----------------|
| **IBM 704 Console** | Museum loan or private collector | Priceless / Museum partnership |
| **IBM 711 Card Reader** | High-speed optical or mechanical | $500-2,000 |
| **IBM 721 Card Punch** | For output | $500-2,000 |
| **IBM 727 Magnetic Tape** | Optional, faster I/O | $1,000-3,000 |
| **Microcontroller** | Arduino Due / Raspberry Pi for network bridge | $50-100 |
| **Custom Interface** | Connect to IBM 704 I/O pins | $200-500 |
| **Spare Vacuum Tubes** | ~2,000 tubes, spares | $2,000-5,000 |
| **Power Supply** | 10-15 kW, stable | $1,000-3,000 |

**Total estimated cost: $5,000-15,000** (excluding IBM 704 itself)

---

## IBM 704 Architecture Details

### Memory System

**Magnetic-Core Memory:**
- 4,096 words × 36 bits = 147,456 bits (18,432 bytes)
- Access time: ~6 μs (much faster than Williams tube!)
- **Reliable**: no refresh needed, non-volatile
- **Cycle time**: ~12 μs
- Core memory was revolutionary — no calibration needed like Williams tubes

### CPU Registers

| Register | Size | Purpose |
|----------|------|---------|
| **AC (Accumulator)** | 38 bits | Primary arithmetic register (2 extra bits for overflow) |
| **MQ (Multiplier-Quotient)** | 36 bits | Multiply/divide operations |
| **XR1, XR2, XR4** | 15 bits each | Index registers (called "decrement registers") |
| **IC (Instruction Counter)** | 15 bits | Program counter |
| **SI (Sense Indicators)** | 36 bits | Status flags |

### Instruction Formats

**Type A** (Index operations):
```
| 3-bit prefix | 15-bit decrement | 3-bit tag | 15-bit address |
```

**Type B** (Most instructions):
```
| 12-bit opcode | 2-bit flag | 4-bit unused | 3-bit tag | 15-bit address |
```

### Instruction Set (Key Operations)

```
Opcode  Mnemonic  Description
CLA     Clear and Add      Load accumulator from memory
ADD     Add                Add memory to accumulator
SUB     Subtract           Subtract memory from accumulator
MPY     Multiply           Multiply AC by memory → MQ
DVH     Divide             Divide AC:MQ by memory
STO     Store              Store AC to memory
STQ     Store MQ           Store MQ to memory
LXA     Load Index         Load index register
AXT     Address to Index   Transfer address to index
TXI     Transfer on Index  Conditional jump based on index
TZE     Transfer on Zero   Jump if AC = 0
TPL     Transfer on Plus   Jump if AC > 0
TMI     Transfer on Minus  Jump if AC < 0
CAS     Compare AC to Store Compare and skip
PAI     Print and Input    I/O operation
```

### Floating-Point Format

**Single-precision (36 bits):**
```
| Sign (1 bit) | Exponent (8 bits, excess-128) | Fraction (27 bits) |
```

- No hidden bit (explicit fraction)
- Range: ~10^-38 to 10^38
- Precision: ~8 decimal digits
- Hardware implementation: ~24 μs add, ~240 μs multiply

### Fixed-Point Format

- Binary sign/magnitude
- 35 bits magnitude + 1 bit sign
- Can represent integers up to 2^35 - 1

---

## Implementation Plan

### Phase 1: Simulator Development (50 RTC)

**Goal**: Create fully functional IBM 704 simulator

- [ ] Implement IBM 704 CPU simulator (Python/C++)
  - 36-bit word emulation
  - Magnetic-core memory model (fast, reliable)
  - Index register (decrement) handling
  - Floating-point hardware emulation
  - Punched card and tape I/O simulation
- [ ] Create SAP assembler
  - IBM 704 assembly syntax (Symbolic Assembly Program)
  - Symbolic label support
  - Index register optimization
  - Punched card format output (80-column)
- [ ] Develop debugging tools
  - Memory dump (core plane visualization)
  - Register display
  - Single-step execution
  - Breakpoint support

**Deliverables**:
- `ibm704-sim/` — Simulator source code
- `ibm704-assembler/` — Cross-assembler (SAP)
- Documentation: Architecture reference

### Phase 2: SHA256 Implementation (75 RTC)

**Goal**: Implement SHA256 on IBM 704

- [ ] Implement 36-bit arithmetic primitives
  - Addition/subtraction (~24 μs each)
  - Bit rotation (circular shift)
  - XOR/AND/OR — bitwise operations
  - 64-bit operations — multi-word (2 words)
- [ ] Implement SHA256 message scheduling
  - Single-pass approach (4,096 words is PLENTY!)
  - Constant table in memory (64 words × 32 bits = fits easily!)
- [ ] Implement SHA256 compression function
  - Optimize critical path (Σ0, Σ1, Ch, Maj)
  - Use lookup tables where possible
  - Leverage floating-point hardware if beneficial
- [ ] Test vector validation
  - NIST SHA256 test vectors
  - Performance measurement

**Memory Layout** (4,096 words):
```
Address   Usage
0x000-0x03F   Boot loader and initialization
0x040-0x07F   SHA256 constants (64 words, only 1.5% of memory!)
0x080-0x08F   Hash state (H0-H7, 8 words)
0x090-0x0AF   Message schedule buffer (32 words)
0x0B0-0x0FF   Working variables (a-h, 8 words)
0x100-0x1FF   Network I/O buffer
0x200-0x3FF   Stack and variables
0x400-0xFFF   Free space / optimization (90% available!)
```

**Estimated Performance**:
- Single SHA256 hash: ~1-5 seconds (much faster than Williams tube machines!)
- Hash rate: 0.2-1.0 H/s
- Card reader throughput: ~150-300 cards/minute
- Tape throughput: ~112,500 characters/second (much faster!)

### Phase 3: Network Bridge (50 RTC)

**Goal**: Build IBM 704-to-internet network interface

- [ ] Hardware interface
  - Card reader sensor (optical or mechanical)
  - Card punch control
  - Optional: Tape drive interface (IBM 727)
  - Microcontroller (ESP32/Arduino Due)
  - Level shifters
- [ ] Firmware development
  - TCP/IP stack
  - HTTPS client (TLS 1.2/1.3)
  - Card/tape encoding/decoding
- [ ] Protocol design
  - IBM 704 → Microcontroller: Mining request (punched card)
  - Microcontroller → IBM 704: Pool response (punched card)
  - Error handling and retry logic

**Card Protocol** (80-column cards):
```
Columns 1-10:   START marker
Columns 11-20:  Command code
Columns 21-50:  Nonce (30 digits)
Columns 51-60:  Difficulty
Columns 61-70:  Checksum
Columns 71-80:  END marker
```

### Phase 4: Hardware Fingerprint & Attestation (25 RTC)

**Goal**: Implement IBM 704-specific hardware fingerprint

- [ ] Magnetic-core characteristic extraction
  - Core memory access timing signature
  - Cycle time variance
  - Temperature drift (minimal, but measurable)
- [ ] Vacuum tube characteristics
  - Power consumption pattern (~2,000 tubes)
  - Thermal signature
  - Warm-up curve
- [ ] Floating-point unit signature
  - FP operation timing variance
  - Rounding behavior
- [ ] Attestation generation
  - Hardware signature computation
  - Timestamping
  - Node verification
- [ ] RustChain API integration
  - POST /api/miners/attest
  - Include IBM 704-specific fields

**Fingerprint Data**:
```json
{
  "hardware_type": "ibm704",
  "year": 1954,
  "location": "museum_or_collection",
  "technology": "vacuum_tube",
  "memory_type": "magnetic_core",
  "core_timing_signature": {...},
  "tube_power_signature": {...},
  "thermal_profile": {...},
  "fp_unit_signature": {...}
}
```

### Phase 5: Documentation & Verification (25 RTC)

**Goal**: Complete documentation and public verification

- [ ] Video recording
  - IBM 704 running miner (visible vacuum tubes)
  - Console lights showing activity
  - Card reader/punch or tape drive operation
- [ ] Technical documentation
  - Architecture design document
  - Code comments
  - User setup guide
- [ ] API verification
  - Miner appears in `rustchain.org/api/miners`
  - Hardware fingerprint verified
- [ ] Open source release
  - GitHub repository
  - MIT/Apache 2.0 license

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| IBM 704 unavailable | Medium | High | Use simulator; partner with museum (MIT, Columbia, etc.) |
| Card reader/punch failure | Medium | Medium | Spare parts; tape drive alternative |
| SHA256 too slow | Low | Medium | 36-bit arch is efficient; accept moderate hash rate |
| Network interface unstable | Medium | Medium | Error handling; offline batch mode |
| Vacuum tube failure | Medium | High | Spare tubes; regular maintenance |

---

## Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Simulator Development | 2-3 weeks | None |
| SHA256 Implementation | 3-4 weeks | Simulator complete |
| Network Bridge | 2-3 weeks | SHA256 complete |
| Hardware Fingerprint | 1-2 weeks | Network bridge complete |
| Documentation & Verification | 1-2 weeks | All phases complete |
| **Total** | **9-14 weeks** | |

---

## Resources

### Historical Documentation

- [IBM 704 Manual of Operation (1955)](http://bitsavers.org/pdf/ibm/704/24-6661-2_704_Manual_1955.pdf)
- [Columbia University: The IBM 704](https://www.columbia.edu/cu/computinghistory/704.html)
- [IBM Archives: 704 Data Processing System](https://web.archive.org/web/20050114203037/http://www-03.ibm.com/ibm/history/exhibits/mainframe/mainframe_PP704.html)
- [Bitsavers IBM 704 Collection](http://bitsavers.org/pdf/ibm/704/)
- [Museo Nazionale Scienza e Tecnologia (Milan) - IBM 704](https://www.museoscienzetecnologia.org/)

### Technical References

- Backus, J. (1978). "The history of FORTRAN I, II, and III"
- McCarthy, J. (1960). "Recursive Functions of Symbolic Expressions and Their Computation by Machine, Part I" (LISP)
- NIST FIPS 180-4: Secure Hash Standard (SHA256 specification)
- IBM 704 Principles of Operation

### Similar Projects

- [IBM 704 Simulator Projects](https://github.com/topics/ibm-704)
- [SAP Assembler Historical Code](http://bitsavers.org/pdf/ibm/704/)
- [FORTRAN I Source Code](http://www.softwarepreservation.org/projects/FORTRAN/)

### Known IBM 704 Locations

- **MIT Computation Center** (used for Operation Moonwatch, Perceptron development)
- **Columbia University** (active in computing history)
- **Museo Nazionale Scienza e Tecnologia, Milan** (public display)
- **Computer History Museum, Mountain View** (possible artifacts)
- **Los Alamos National Laboratory** (historical use)

---

## Claim Rules

- **Partial claims accepted** — complete any phase for its RTC amount
- **Full completion = 200 RTC total**
- **Must be real IBM 704 hardware** (emulators don't count for full bounty)
- **Open source everything** — all code, firmware, documentation
- **Multiple people can collaborate** and split rewards
- **Museum partnerships encouraged**

---

## Wallet for Bounty

```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

---

## Verification Checklist

Before claiming the bounty, verify:

- [ ] Simulator passes all NIST SHA256 test vectors
- [ ] Real IBM 704 hardware is operational and mining
- [ ] Miner appears in `rustchain.org/api/miners`
- [ ] Hardware fingerprint is verified by the network
- [ ] Video documentation is complete and public
- [ ] All source code is open-sourced on GitHub
- [ ] Technical documentation is complete

---

## Contact & Support

- **Discord**: [RustChain Discord](https://discord.gg/VqVVS2CW9Q)
- **GitHub**: [Scottcjn/Rustchain](https://github.com/Scottcjn/Rustchain)
- **Documentation**: [RustChain Docs](https://rustchain.org/docs)

**Questions?** Post in the issue comments or join the Discord.

---

## Conclusion

The IBM 704 port represents a pinnacle achievement in RustChain's Proof-of-Antiquity vision: **the machine that birthed FORTRAN and LISP now mines cryptocurrency**. A 1954 scientific computer earning crypto in 2026 is not just a technical achievement — it's a bridge between the dawn of practical computing and the future of decentralized systems.

**72 years of computing history. One blockchain. Infinite possibilities.**

*Let's make the first floating-point computer earn its keep.*

---

**Created**: 2026-03-13  
**Bounty Tier**: LEGENDARY (200 RTC / $20 USD)  
**Multiplier**: 5.0x (Maximum)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
