# PDP-1 (1959) Miner Implementation Plan

## Overview

This document outlines the complete implementation plan for porting the RustChain miner to the PDP-1, DEC's first computer and the machine that launched the minicomputer revolution (1959).

**Bounty**: 200 RTC (LEGENDARY Tier)  
**Multiplier**: 5.0x (Maximum)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## Phase 1: Simulator Development (50 RTC)

### Goal
Create a fully functional PDP-1 simulator for development and testing.

### Tasks

#### 1.1 CPU Emulation ✅
- [x] 18-bit word architecture
- [x] 18-bit Accumulator (AC)
- [x] 18-bit Input-Output register (IO)
- [x] 18-bit Program Counter (PC)
- [x] 18-bit Memory Buffer (MB)
- [x] 18-bit Memory Address (MA)
- [x] Link bit (L) for extended arithmetic

#### 1.2 Memory System
- [ ] 4,096-word magnetic-core memory emulation
- [ ] Memory access timing simulation (5 μs access time)
- [ ] Memory protection (optional)
- [ ] Core dump visualization

#### 1.3 Instruction Set Implementation
- [ ] Complete PDP-1 instruction set (72+ instructions)
  - **Memory Reference**: AND, IOR, XOR, JMS, JMP, ISZ, DCA, TAD
  - **Microinstructions**: CLA, CLL, CMA, CML, RAR, RAL, RTR, RTL
  - **I/O**: IOT instructions for Type 30, paper tape, typewriter
  - **Arithmetic**: Multi-word operations
- [ ] Indirect addressing support
- [ ] Index register support (B bit)
- [ ] Instruction timing simulation

#### 1.4 MACRO Assembler
- [ ] PDP-1 MACRO assembly parser
- [ ] Label support and symbol table
- [ ] Macro support
- [ ] Paper tape output format
- [ ] Cross-reference listing

#### 1.5 Debugging Tools
- [ ] Single-step execution
- [ ] Breakpoint support
- [ ] Memory dump (octal/hex)
- [ ] Register display
- [ ] Instruction trace
- [ ] Core plane visualization (GUI optional)

### Deliverables
- `pdp1-sim/pdp1_cpu.py` - CPU emulator ✅
- `pdp1-sim/core_memory.py` - Memory model
- `pdp1-sim/macro_assembler.py` - Assembler
- `pdp1-sim/debugger.py` - Debugging tools
- Documentation: Architecture reference manual

### Estimated Time: 2-3 weeks

---

## Phase 2: SHA256 Implementation (75 RTC)

### Goal
Implement SHA256 hashing algorithm on PDP-1.

### Tasks

#### 2.1 Arithmetic Primitives
- [ ] 18-bit addition/subtraction
- [ ] Bit rotation (circular shift left/right)
- [ ] Bitwise operations (AND, OR, XOR, NOT)
- [ ] 32-bit operations (multi-word)
  - Split across two 18-bit words
  - High word + Low word handling
- [ ] Byte extraction and manipulation

#### 2.2 SHA256 Constants
- [ ] First 32 bits of fractional parts of cube roots of first 64 primes
- [ ] Store in memory (64 words × 32 bits = fits easily!)
- [ ] Octal representation for PDP-1

```
Memory Layout for K constants (64 words):
Address 0x040-0x07F: K[0] through K[63]
Each word: K_value (32 bits, split across two 18-bit words)
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
- [ ] Use link bit for extended arithmetic
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
0x040-0x07F     64      SHA256 K constants (64 words × 2 = 128 words for 32-bit values)
0x080-0x08F     16      Hash state H0-H7 (8 values × 2 words each)
0x090-0x09F     16      Working variables a-h (8 values × 2 words each)
0x0A0-0x0BF     32      Message schedule W[0..63] (reuse buffer)
0x0C0-0x0DF     32      Temporary storage
0x0E0-0x0FF     32      I/O buffer (paper tape)
0x100-0x1FF     256     Stack and local variables
0x200-0x3FF     512     Subroutines and utilities
0x400-0xFFF     3,072   Free space / optimization (75% available!)
```

### Estimated Performance
- Single SHA256 hash: ~0.5-2 seconds
- Hash rate: 0.5-2.0 H/s
- Much faster than vacuum tube machines due to transistor speed!

### Deliverables
- `pdp1-miner/sha256_pdp1.mac` - SHA256 in PDP-1 MACRO assembly
- `pdp1-miner/sha256_test.mac` - Test vectors
- `pdp1-miner/constants.mac` - SHA256 constants
- Test results showing NIST vector validation

### Estimated Time: 3-4 weeks

---

## Phase 3: Network Bridge (50 RTC)

### Goal
Build interface between PDP-1 and modern internet.

### Tasks

#### 3.1 Hardware Interface
- [ ] Paper tape reader interface
  - Friden Flexowriter or similar
  - Detect tape presence and hole patterns
  - 8-level paper tape format
- [ ] Paper tape punch interface
  - Punch hole patterns
- [ ] Alternative: Type 30 CRT display interface
  - Point light pen for input
  - Display output
- [ ] Microcontroller bridge
  - ESP32 or Arduino Due
  - Level shifters (PDP-1 used different voltage levels)
  - Isolation (optocouplers)

#### 3.2 Communication Protocol
- [ ] Paper tape format specification
  ```
  Row 1-8:    START marker "PDP1MINE"
  Row 9-16:   Command code (GET_WORK, SUBMIT)
  Row 17-24:  Nonce (8 characters)
  Row 25-32:  Difficulty target
  Row 33-40:  Checksum (CRC16)
  Row 41-48:  END marker "ENDTAPE"
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
- [ ] Paper tape encoding/decoding

#### 3.4 Software Integration
- [ ] PDP-1 I/O routines
  - IOT instruction handling
  - Paper tape read subroutine
  - Paper tape punch subroutine
- [ ] Buffer management
- [ ] Error handling

### Deliverables
- `network-bridge/paper_tape_interface.py` - Microcontroller firmware
- `pdp1-miner/io_routines.mac` - PDP-1 I/O subroutines
- Hardware schematics and wiring diagrams

### Estimated Time: 2-3 weeks

---

## Phase 4: Hardware Fingerprint & Attestation (25 RTC)

### Goal
Implement PDP-1-specific hardware fingerprinting.

### Tasks

#### 4.1 Core Memory Signature
- [ ] Access timing measurement
  - Read/write cycle time variance
  - Temperature drift effects
- [ ] Core plane characteristics
  - Remanence pattern
  - Switching threshold variance

#### 4.2 Transistor Signature
- [ ] Power consumption pattern
  - ~500 transistors × ~100mW each = ~50W
  - Current draw measurement
- [ ] Thermal signature
  - Warm-up curve
  - Operating temperature profile
- [ ] Transistor switching characteristics

#### 4.3 CRT Display Signature (Type 30)
- [ ] Phosphor persistence pattern
- [ ] Beam positioning accuracy
- [ ] Display timing characteristics

#### 4.4 Attestation Protocol
- [ ] Hardware signature computation
- [ ] Timestamping
- [ ] Digital signature
- [ ] RustChain API submission
  ```json
  {
    "hardware_type": "pdp1",
    "year": 1959,
    "technology": "transistor",
    "memory_type": "magnetic_core",
    "core_timing_signature": [...],
    "transistor_power_signature": {...},
    "thermal_profile": {...},
    "crt_signature": {...},
    "timestamp": "2026-03-13T12:00:00Z",
    "signature": "0x..."
  }
  ```

### Deliverables
- `pdp1-miner/fingerprint.mac` - Fingerprint generation
- `pdp1-miner/attestation.mac` - Attestation protocol
- Signature measurement tools

### Estimated Time: 1-2 weeks

---

## Phase 5: Documentation & Verification (25 RTC)

### Goal
Complete documentation and public verification.

### Tasks

#### 5.1 Video Documentation
- [ ] PDP-1 running miner
  - Console lights showing activity
  - Type 30 CRT display showing output
- [ ] I/O operation
  - Paper tape reader/punch
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
| PDP-1 unavailable | Medium | High | Partner with museum; use simulator for development |
| Paper tape reader/punch failure | Medium | Medium | Alternative interfaces; simulator testing |
| SHA256 too slow | Low | Medium | 18-bit arch is efficient; optimize critical path |
| Network interface unstable | Medium | Medium | Robust error handling; offline batch mode |
| Transistor failure | Low | High | Spare transistors; regular maintenance |
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
- [PDP-1 Handbook (1963)](http://bitsavers.org/pdf/dec/pdp1/F-15_PDP-1_Handbook_1963.pdf)
- [Bitsavers PDP-1 Collection](http://bitsavers.org/pdf/dec/pdp1/)
- [Computer History Museum: PDP-1](https://computerhistory.org/collections/catalog/102643816)

### Technical References
- NIST FIPS 180-4: Secure Hash Standard
- PDP-1 Programming Manual
- PDP-1 MACRO Assembly Language

### Known PDP-1 Locations
- Computer History Museum, Mountain View (operational!)
- MIT Museum
- The National Museum of American History, Washington DC
- Centre for Computing History, Cambridge UK

---

## Conclusion

The PDP-1 miner port is a challenging but achievable project that bridges 67 years of computing history. As DEC's first computer and the grandfather of personal computing, the PDP-1 represents a pivotal moment in computing history.

**Let's make the first minicomputer earn its keep!**

---

**Created**: 2026-03-13  
**Issue**: #337  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
