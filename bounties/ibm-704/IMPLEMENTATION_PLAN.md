# IBM 704 (1954) Miner Implementation Plan

## Overview

This document outlines the complete implementation plan for porting the RustChain miner to the IBM 704, IBM's first mass-produced computer with hardware floating-point arithmetic (1954).

**Bounty**: 200 RTC (LEGENDARY Tier)  
**Multiplier**: 5.0x (Maximum)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## Phase 1: Simulator Development (50 RTC)

### Goal
Create a fully functional IBM 704 simulator for development and testing.

### Tasks

#### 1.1 CPU Emulation ✅
- [x] 36-bit word architecture
- [x] 38-bit accumulator (AC) with overflow bits
- [x] 36-bit multiplier-quotient register (MQ)
- [x] Three 15-bit index registers (XR1, XR2, XR4)
- [x] 15-bit instruction counter (IC)
- [x] 36-bit sense indicators (SI)
- [x] Type A instruction format support
- [x] Type B instruction format support

#### 1.2 Memory System
- [ ] 4,096-word magnetic-core memory emulation
- [ ] Memory access timing simulation (6 μs access, 12 μs cycle)
- [ ] Memory protection (optional)
- [ ] Core dump visualization

#### 1.3 Instruction Set Implementation
- [ ] Complete Type B opcodes (30+ instructions)
  - CLA, ADD, SUB, MPY, DVH
  - STO, STQ, STS, SLW
  - CAS, ANA, ORS
  - LXA, AXT, TIX, TXI
  - TZE, TPL, TMI, TRA
  - FAS, FBS, FMS, FDS (floating-point)
  - PAI, PRI (I/O)
- [ ] Complete Type A opcodes (index operations)
- [ ] Instruction timing simulation

#### 1.4 SAP Assembler
- [ ] Symbolic Assembly Program parser
- [ ] Label support and symbol table
- [ ] Macro support (optional)
- [ ] Punched card output format (80-column)
- [ ] Cross-reference listing

#### 1.5 Debugging Tools
- [ ] Single-step execution
- [ ] Breakpoint support
- [ ] Memory dump (octal/hex)
- [ ] Register display
- [ ] Instruction trace
- [ ] Core plane visualization (GUI optional)

### Deliverables
- `ibm704-sim/ibm704_cpu.py` - CPU emulator ✅
- `ibm704-sim/core_memory.py` - Memory model
- `ibm704-sim/sap_assembler.py` - Assembler
- `ibm704-sim/debugger.py` - Debugging tools
- Documentation: Architecture reference manual

### Estimated Time: 2-3 weeks

---

## Phase 2: SHA256 Implementation (75 RTC)

### Goal
Implement SHA256 hashing algorithm on IBM 704.

### Tasks

#### 2.1 Arithmetic Primitives
- [ ] 36-bit addition/subtraction
- [ ] Bit rotation (circular shift left/right)
- [ ] Bitwise operations (AND, OR, XOR, NOT)
- [ ] 64-bit operations (multi-word)
  - Split across two 36-bit words
  - High word + Low word handling
- [ ] Byte extraction and manipulation

#### 2.2 SHA256 Constants
- [ ] First 32 bits of fractional parts of cube roots of first 64 primes
- [ ] Store in memory (64 words × 32 bits = fits easily!)
- [ ] Octal representation for IBM 704

```
Memory Layout for K constants (64 words):
Address 0x040-0x07F: K[0] through K[63]
Each word: 0 | K_value (32 bits, right-justified)
```

#### 2.3 Message Schedule
- [ ] W[0..15]: Direct from message block
- [ ] W[16..63]: Computed using σ0 and σ1
- [ ] Single-pass optimization (process as computed)
- [ ] Buffer management (32 words = 0x090-0x0AF)

#### 2.4 Compression Function
- [ ] Initialize hash values (H0-H7)
  ```
  H0 = 0x6a09e667
  H1 = 0xbb67ae85
  H2 = 0x3c6ef372
  H3 = 0xa54ff53a
  H4 = 0x510e527f
  H5 = 0x9b05688c
  H6 = 0x1f83d9ab
  H7 = 0x5be0cd19
  ```
- [ ] Working variables (a, b, c, d, e, f, g, h)
- [ ] 64 rounds of compression
- [ ] Functions: Ch, Maj, Σ0, Σ1, σ0, σ1
- [ ] Add compressed chunk to hash value

#### 2.5 Optimization Strategies
- [ ] Use floating-point hardware for large additions (if beneficial)
- [ ] Lookup tables for frequently used operations
- [ ] Loop unrolling for critical sections
- [ ] Index register optimization for array access

#### 2.6 Test Vectors
- [ ] NIST SHA256 test vectors
  - "abc" → ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
  - "" (empty) → e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
  - "The quick brown fox jumps over the lazy dog"
- [ ] Performance measurement
- [ ] Correctness validation

### Memory Layout (4,096 words total)

```
Address Range   Size    Usage
0x000-0x03F     64      Boot loader and initialization
0x040-0x07F     64      SHA256 K constants (64 words)
0x080-0x087     8       Hash state H0-H7
0x088-0x08F     8       Working variables a-h
0x090-0x0AF     32      Message schedule W[0..63] (reuse buffer)
0x0B0-0x0BF     16      Temporary storage
0x0C0-0x0FF     64      I/O buffer (card/tape)
0x100-0x1FF     256     Stack and local variables
0x200-0x3FF     512     Subroutines and utilities
0x400-0xFFF     3,072   Free space / optimization (75% available!)
```

### Estimated Performance
- Single SHA256 hash: ~1-5 seconds
- Hash rate: 0.2-1.0 H/s
- Much faster than Williams tube machines due to core memory!

### Deliverables
- `ibm704-miner/sha256_ibm704.s` - SHA256 in SAP assembly
- `ibm704-miner/sha256_test.s` - Test vectors
- `ibm704-miner/constants.s` - SHA256 constants
- Test results showing NIST vector validation

### Estimated Time: 3-4 weeks

---

## Phase 3: Network Bridge (50 RTC)

### Goal
Build interface between IBM 704 and modern internet.

### Tasks

#### 3.1 Hardware Interface
- [ ] Card reader interface
  - IBM 711 card reader sensor (optical/mechanical)
  - Detect card presence and column data
  - 80-column card format
- [ ] Card punch interface
  - IBM 721 card punch control
  - Punch column data
- [ ] Alternative: Magnetic tape interface
  - IBM 727 tape unit control
  - Much faster than cards (112,500 chars/sec)
- [ ] Microcontroller bridge
  - ESP32 or Arduino Due
  - Level shifters (IBM 704 used different voltage levels)
  - Isolation (optocouplers)

#### 3.2 Communication Protocol
- [ ] Card format specification
  ```
  Columns 1-10:   START marker "IBM704MINE"
  Columns 11-20:  Command code (GET_WORK, SUBMIT)
  Columns 21-50:  Nonce (30 digits, zero-padded)
  Columns 51-60:  Difficulty target
  Columns 61-70:  Checksum (CRC16)
  Columns 71-80:  END marker "ENDCARD"
  ```
- [ ] Error detection and correction
- [ ] Retry logic
- [ ] Flow control

#### 3.3 Network Firmware
- [ ] TCP/IP stack (microcontroller)
- [ ] HTTPS client (TLS 1.2/1.3)
- [ ] RustChain API integration
  - GET /api/mining/work
  - POST /api/mining/submit
- [ ] JSON parsing (minimal)
- [ ] Card/tape encoding/decoding

#### 3.4 Software Integration
- [ ] IBM 704 I/O routines
  - PAI (Print and Input) instruction handling
  - Card read subroutine
  - Card punch subroutine
- [ ] Buffer management
- [ ] Error handling

### Deliverables
- `network-bridge/card_interface.py` - Microcontroller firmware
- `network-bridge/tape_interface.py` - Tape interface (optional)
- `ibm704-miner/io_routines.s` - IBM 704 I/O subroutines
- Hardware schematics and wiring diagrams

### Estimated Time: 2-3 weeks

---

## Phase 4: Hardware Fingerprint & Attestation (25 RTC)

### Goal
Implement IBM 704-specific hardware fingerprinting.

### Tasks

#### 4.1 Core Memory Signature
- [ ] Access timing measurement
  - Read/write cycle time variance
  - Temperature drift effects
- [ ] Core plane characteristics
  - Remanence pattern
  - Switching threshold variance

#### 4.2 Vacuum Tube Signature
- [ ] Power consumption pattern
  - ~2,000 tubes × ~1W each = ~2kW
  - Current draw measurement
- [ ] Thermal signature
  - Warm-up curve
  - Operating temperature profile
- [ ] Tube aging characteristics

#### 4.3 Floating-Point Unit Signature
- [ ] FP operation timing variance
- [ ] Rounding behavior
- [ ] Exponent/fraction handling quirks

#### 4.4 Attestation Protocol
- [ ] Hardware signature computation
- [ ] Timestamping
- [ ] Digital signature
- [ ] RustChain API submission
  ```json
  {
    "hardware_type": "ibm704",
    "year": 1954,
    "technology": "vacuum_tube",
    "memory_type": "magnetic_core",
    "core_timing_signature": [...],
    "tube_power_signature": {...},
    "thermal_profile": {...},
    "fp_unit_signature": {...},
    "timestamp": "2026-03-13T12:00:00Z",
    "signature": "0x..."
  }
  ```

### Deliverables
- `ibm704-miner/fingerprint.s` - Fingerprint generation
- `ibm704-miner/attestation.s` - Attestation protocol
- Signature measurement tools

### Estimated Time: 1-2 weeks

---

## Phase 5: Documentation & Verification (25 RTC)

### Goal
Complete documentation and public verification.

### Tasks

#### 5.1 Video Documentation
- [ ] IBM 704 running miner
  - Console lights showing activity
  - Vacuum tubes visible (if possible)
- [ ] I/O operation
  - Card reader/punch or tape drive
- [ ] Results display
  - Mining statistics
  - Successful share submission

#### 5.2 Technical Documentation
- [ ] Architecture design document
- [ ] Code comments (all assembly code)
- [ ] User setup guide
- [ ] API reference
- [ ] Troubleshooting guide

#### 5.3 API Verification
- [ ] Miner appears in `rustchain.org/api/miners`
- [ ] Hardware fingerprint verified
- [ ] Shares accepted by network
- [ ] Rewards distributed

#### 5.4 Open Source Release
- [ ] GitHub repository
- [ ] MIT/Apache 2.0 license
- [ ] README with setup instructions
- [ ] Example programs

### Deliverables
- YouTube video (public)
- GitHub repository with all source code
- Technical documentation (PDF/Markdown)
- Verification: miner in RustChain API

### Estimated Time: 1-2 weeks

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| IBM 704 unavailable | Medium | High | Partner with museum; use simulator for development |
| Card reader/punch failure | Medium | Medium | Tape drive alternative; simulator testing |
| SHA256 too slow | Low | Medium | 36-bit arch is efficient; optimize critical path |
| Network interface unstable | Medium | Medium | Robust error handling; offline batch mode |
| Vacuum tube failure | Medium | High | Spare tubes; regular maintenance schedule |
| Core memory degradation | Low | High | Gentle handling; environmental controls |

---

## Timeline Summary

| Phase | Duration | RTC | Dependencies |
|-------|----------|-----|--------------|
| Phase 1: Simulator | 2-3 weeks | 50 | None |
| Phase 2: SHA256 | 3-4 weeks | 75 | Phase 1 complete |
| Phase 3: Network | 2-3 weeks | 50 | Phase 2 complete |
| Phase 4: Fingerprint | 1-2 weeks | 25 | Phase 3 complete |
| Phase 5: Documentation | 1-2 weeks | 25 | All phases complete |
| **Total** | **9-14 weeks** | **200** | |

---

## Resources

### Historical Documentation
- [IBM 704 Manual of Operation (1955)](http://bitsavers.org/pdf/ibm/704/24-6661-2_704_Manual_1955.pdf)
- [Bitsavers IBM 704 Collection](http://bitsavers.org/pdf/ibm/704/)
- [Columbia University: The IBM 704](https://www.columbia.edu/cu/computinghistory/704.html)

### Technical References
- NIST FIPS 180-4: Secure Hash Standard
- IBM 704 Principles of Operation
- SHARE Assembly Program (SAP) documentation

### Known IBM 704 Locations
- MIT Computation Center (historical)
- Columbia University
- Museo Nazionale Scienza e Tecnologia, Milan
- Computer History Museum, Mountain View

---

## Conclusion

The IBM 704 miner port is a challenging but achievable project that bridges 72 years of computing history. With its magnetic-core memory and hardware floating-point, the IBM 704 is actually one of the more capable vintage machines for this task.

**Let's make the first floating-point computer earn its keep!**

---

**Created**: 2026-03-13  
**Issue**: [#1834](https://github.com/Scottcjn/rustchain-bounties/issues/1834)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
