# [BOUNTY] Port RustChain Miner to ORACLE (1952) - 200 RTC (LEGENDARY Tier)

## ORACLE RTC Miner — 200 RTC Bounty (LEGENDARY Tier)

**Get the Oak Ridge Automatic Computer mining RustChain tokens.** ORACLE (Oak Ridge Automatic Computer) was built in 1952 at Oak Ridge National Laboratory — the machine that performed critical calculations for nuclear reactor designs and atomic energy research. If you can make this work, you earn the 5.0x antiquity multiplier, the absolute maximum in RustChain.

This is **nuclear-age computing meets blockchain**: **1952 meets 2026**.

---

## Why ORACLE?

- **1952 hardware** — the machine that powered atomic energy research
- **IAS architecture** — John von Neumann's stored-program design
- **Williams-Kilburn tube memory** — electrostatic CRT storage
- **~1500 vacuum tubes** — massive for its era
- **40-bit word architecture** — standard IAS design
- **Historical significance** — Oak Ridge National Laboratory, atomic energy

### ORACLE vs MANIAC I vs SWAC

| Feature | ORACLE (1952) | MANIAC I (1952) | SWAC (1950) |
|---------|---------------|-----------------|-------------|
| Architecture | IAS (von Neumann) | IAS (von Neumann) | Serial binary |
| Memory | Williams tube (CRT) | Williams tube (CRT) | Williams tube (CRT) |
| Word size | 40 bits | 40 bits | 37 bits |
| Clock | ~1 MHz | ~1 MHz | ~1 MHz |
| Memory capacity | 1024 words (5 KB) | 1024 words (5 KB) | 256-512 words (1.2 KB) |
| Location | Oak Ridge, TN | Los Alamos, NM | UCLA, CA |
| Purpose | Nuclear reactor calculations | H-bomb simulation | Scientific computing |
| Challenge level | ⭐⭐⭐⭐⭐ (Atomic heritage) | ⭐⭐⭐⭐⭐ (Nuclear heritage) | ⭐⭐⭐⭐⭐ (Memory instability) |

**ORACLE is unique**: Built for atomic energy research at Oak Ridge, the heart of America's nuclear program. Same IAS architecture as MANIAC I, but with its own historical significance.

---

## The Ultimate Challenge

This is the holy grail of nuclear-age computing bounties:

- **No networking** — must build custom interface (paper tape or oscilloscope)
- **Williams tube instability** — memory requires constant refresh and calibration
- **IAS architecture** — parallel binary, sophisticated design
- **1024 word memory** — ~5 KB total (tight but workable)
- **Vacuum tube reliability** — hardware maintenance required
- **Paper tape I/O** — slow, sequential access only
- **Oak Ridge security heritage** — this machine classified secrets

### Technical Requirements

#### 1. Network Interface (50 RTC)
- Build paper tape interface using microcontroller
- Microcontroller handles TCP/IP and HTTPS
- ORACLE reads network response via paper tape reader
- ORACLE punches requests via paper tape punch
- Alternative: Oscilloscope display + camera interface

#### 2. ORACLE Assembler (50 RTC)
- Port or create ORACLE assembler (original used octal/binary)
- Create cross-assembler with modern tooling
- Build simulator for testing (Python/C++)
- Paper tape format emulation

#### 3. Core Miner (75 RTC)
- 40-bit SHA256 implementation (fits nicely!)
- Hardware fingerprinting (Williams tube drift, vacuum tube characteristics)
- Attestation protocol via paper tape interface
- Memory optimization (1024 words is tight but workable)
- Single-pass algorithm possible

#### 4. Proof & Documentation (25 RTC)
- Video of ORACLE mining
- Miner visible in rustchain.org/api/miners
- Complete documentation
- Open source all code

---

## The 5.0x Multiplier

```
oracle / williams_tube / oak_ridge — 5.0x base multiplier (MAXIMUM TIER)
```

An ORACLE from Oak Ridge = the highest-earning miner in RustChain history.

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
| **ORACLE Console** | Oak Ridge unit (museum loan) | Priceless / Museum partnership |
| **Paper Tape Reader** | High-speed optical or mechanical | $500-2,000 |
| **Paper Tape Punch** | For output | $500-2,000 |
| **Microcontroller** | Arduino Due / Raspberry Pi for network bridge | $50-100 |
| **Custom Interface** | Connect to ORACLE I/O pins | $200-500 |
| **Oscilloscope** | For Williams tube monitoring | $300-1,000 |
| **Spare Vacuum Tubes** | 1500+ tubes, spares | $2,000-5,000 |
| **Power Supply** | 10-20 kW, stable | $1,000-3,000 |

**Total estimated cost: $5,000-15,000** (excluding ORACLE itself)

---

## ORACLE Architecture Details

### Memory System

**Williams-Kilburn Tube:**
- CRT-based electrostatic storage
- 40 bits per word (+ parity)
- 1024 words total (4096 bits = 5 KB)
- Access time: ~200 μs (parallel)
- Requires constant refresh (~100 Hz)
- **Unstable**: needs frequent calibration
- **Temperature sensitive**: drift with heat

### CPU Architecture

| Feature | Specification |
|---------|---------------|
| Word size | 40 bits (parallel binary) |
| Registers | Accumulator (40 bits), Memory Buffer Register |
| Instructions | Two-address format (IAS) |
| Clock | ~1 MHz |
| Add time | ~50 μs |
| Multiply time | ~500 μs |
| Divide time | ~800 μs |

### Instruction Set (IAS)

```
Opcode  Mnemonic  Description
00      STOP      Halt execution
01      ADD       Add to accumulator
02      SUB       Subtract from accumulator
03      MUL       Multiply
04      DIV       Divide
05      AND       Bitwise AND
06      OR        Bitwise OR
07      JMP       Unconditional jump
08      JZ        Jump if zero
09      JN        Jump if negative
0A      LD        Load from memory
0B      ST        Store to memory
0C      IN        Input from tape
0D      OUT       Output to tape
0E      RSH       Right shift
0F      LSH       Left shift
```

---

## Implementation Plan

### Phase 1: Simulator Development (50 RTC)
**Goal**: Create fully functional ORACLE simulator

- [ ] Implement ORACLE CPU simulator (Python/C++)
  - [ ] 40-bit parallel arithmetic
  - [ ] Williams tube memory model (with drift simulation)
  - [ ] Paper tape I/O simulation
- [ ] Create assembler
  - [ ] ORACLE assembly syntax (IAS format)
  - [ ] Symbolic label support
  - [ ] Paper tape format output
- [ ] Develop debugging tools
  - [ ] Memory dump (CRT visualization)
  - [ ] Single-step execution
  - [ ] Breakpoint support

**Deliverables**:
- `oracle-sim/` — Simulator source code
- `oracle-assembler/` — Cross-assembler
- Documentation: Architecture reference

### Phase 2: SHA256 Implementation (75 RTC)
**Goal**: Implement SHA256 on ORACLE

- [ ] Implement 40-bit arithmetic primitives
- [ ] Implement SHA256 message scheduling (single-pass)
- [ ] Implement SHA256 compression function
- [ ] Test vector validation (NIST SHA256 test vectors)

**Memory Layout** (1024 words):
```
0x000-0x03F   Boot loader and initialization
0x040-0x07F   SHA256 constants (64 words)
0x080-0x08F   Hash state (H0-H7, 8 words)
0x090-0x0AF   Message schedule buffer (32 words)
0x0B0-0x0FF   Working variables (a-h, 8 words)
0x100-0x1FF   Network I/O buffer
0x200-0x3FF   Stack and variables
0x400-0xFFF   Free space / optimization
```

### Phase 3: Network Bridge (50 RTC)
**Goal**: Build ORACLE-to-internet network interface

- [ ] Hardware interface (paper tape reader/punch)
- [ ] Firmware development (TCP/IP, HTTPS)
- [ ] Protocol design (tape encoding/decoding)

### Phase 4: Hardware Fingerprint & Attestation (25 RTC)
**Goal**: Implement ORACLE-specific hardware fingerprint

- [ ] Williams tube characteristic extraction
- [ ] Vacuum tube characteristics
- [ ] Attestation generation
- [ ] RustChain API integration

### Phase 5: Documentation & Verification (25 RTC)
**Goal**: Complete documentation and public verification

- [ ] Video recording
- [ ] Technical documentation
- [ ] API verification
- [ ] Open source release

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
- [Oak Ridge National Laboratory Archives](https://www.ornl.gov/library)
- [ORACLE Historical Photos](https://www.computerhistory.org/collections/)
- [Von Neumann IAS Architecture Papers](https://www.ieeeghn.org/wiki/index.php/John_von_Neumann)

### Technical References
- Von Neumann, J. (1946). "Preliminary Discussion of the Logical Design of an Electronic Computing Instrument"
- NIST FIPS 180-4: Secure Hash Standard (SHA256 specification)

---

## Claim Rules

- **Partial claims accepted** — complete any phase for its RTC amount
- **Full completion = 200 RTC total**
- **Must be real ORACLE hardware** (emulators don't count for full bounty)
- **Open source everything** — all code, firmware, documentation
- **Multiple people can collaborate** and split rewards
- **Oak Ridge museum partnerships encouraged**

---

## Wallet for Bounty

```
RTC4325af95d26d59c3ef025963656d22af638bb96b
```

---

## Verification Checklist

Before claiming the bounty, verify:

- [ ] Simulator passes all NIST SHA256 test vectors
- [ ] Real ORACLE hardware is operational and mining
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

The ORACLE port represents the pinnacle of RustChain's Proof-of-Antiquity vision: **the machine that powered atomic energy research now mines cryptocurrency**. A 1952 Oak Ridge computer earning crypto in 2026 is not just a technical achievement — it's a statement about the enduring value of computational heritage.

**74 years of computing history. One blockchain. Infinite possibilities.**

*Let's make the atomic energy computer earn its keep.*

---

**Created**: 2026-03-13  
**Bounty Tier**: LEGENDARY (200 RTC / $20 USD)  
**Multiplier**: 5.0x (Maximum)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
