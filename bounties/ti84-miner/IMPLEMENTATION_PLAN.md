# TI-84 Miner Implementation Plan

## Project Overview

**Goal**: Port RustChain miner to TI-84 calculator (Z80 architecture)

**Bounty**: 50 RTC (legendary hardware tier - Z80 from 1974)

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

**Repository**: `yifan19860831-hub/rustchain-bounties`

**Issue**: #1156 (Vintage Hardware Speed Run)

---

## Technical Specifications

### Target Hardware
- **Primary**: TI-84 Plus (Z80 @ 15 MHz, 128 KB RAM)
- **Secondary**: TI-84 Plus CE (eZ80 @ 48 MHz, 256 KB RAM)

### Memory Budget
- **Total Available**: 24 KB user RAM
- **Target Usage**: 18-20 KB
- **Safety Margin**: 4-6 KB

### Performance Targets
- **Attestation Time**: < 60 seconds
- **SHA-512**: < 1 second per block
- **Ed25519 Sign**: < 30 seconds
- **Fingerprint**: < 10 seconds

---

## Implementation Phases

### Phase 1: Development Environment Setup (Days 1-2)

#### Tasks
- [ ] Install CEmu emulator
- [ ] Set up Z80 toolchain (SPASM or TASM)
- [ ] Configure C compiler (sdcc with Z80 target)
- [ ] Create project structure
- [ ] Set up build system (Makefile)

#### Deliverables
- Working development environment
- Hello World program running on emulator
- Build pipeline automated

#### Files
```
ti84-miner/
├── Makefile
├── src/
│   └── main.asm
├── include/
├── lib/
├── test/
└── docs/
```

### Phase 2: SHA-512 Implementation (Days 3-7)

#### Tasks
- [ ] Implement 64-bit arithmetic primitives (add, sub, mul, rot)
- [ ] Port SHA-512 compression function
- [ ] Optimize critical loops (unroll where possible)
- [ ] Create test vectors
- [ ] Benchmark on emulator

#### Technical Approach
```z80
; 64-bit addition example
add64:
    ; HLDE = BCIX + SP
    ; Add low 16 bits
    ld a, c
    add a, e
    ld e, a
    ld a, b
    adc a, d
    ld d, a
    ; ... continue for all 64 bits
    ret
```

#### Memory Budget: 3.5 KB
#### Performance Target: 800ms per block

### Phase 3: Hardware Fingerprint (Days 8-12)

#### TI-84 Specific Fingerprint Checks

##### 1. CPU Frequency Measurement
```z80
; Measure actual CPU frequency via timer
measure_cpu_freq:
    ld hl, $8A4C  ; Timer counter
    ; Count cycles over fixed period
    ret
```

##### 2. RAM Timing Pattern
- Access memory in specific patterns
- Measure timing variations
- Create unique signature

##### 3. Display Controller ID
- LCD timing characteristics
- Contrast control response

##### 4. Battery Voltage Entropy
- Read ADC values (if available)
- Use as entropy source

##### 5. Button Press Jitter
- Measure human interaction timing
- Collect entropy from keypresses

##### 6. Crystal Oscillator Drift
- Long-term timing measurement
- Compare to expected frequency

##### 7. Device Age Markers
- OS version detection
- Memory wear patterns

#### Memory Budget: 2.5 KB
#### Performance Target: 5 seconds

### Phase 4: Ed25519 Implementation (Days 13-20)

#### Approach
- Use existing public domain Ed25519 implementations as reference
- Optimize for Z80:
  - Pre-computed multiplication tables
  - Fixed-base comb method for point multiplication
  - Montgomery ladder for scalar multiplication

#### Components
- [ ] Field arithmetic (mod 2^255-19)
- [ ] Point addition/doubling
- [ ] Scalar multiplication
- [ ] SHA-512 for hashing (reuse Phase 2)
- [ ] Signature generation
- [ ] Signature verification (optional)

#### Optimization Strategies
1. **Table-driven multiplication**: Trade memory for speed
2. **Windowed arithmetic**: Reduce operation count
3. **Assembly hot paths**: Critical loops in pure Z80

#### Memory Budget: 7 KB
#### Performance Target: 25 seconds per signature

### Phase 5: Mining Logic Integration (Days 21-24)

#### Components
- [ ] Epoch timer management
- [ ] Work unit parsing
- [ ] Attestation creation
- [ ] USB communication layer
- [ ] Error handling

#### USB Communication
```z80
; Send attestation via USB
usb_send:
    ; Use TI-USB protocol
    ; Transfer to PC bridge application
    ret
```

#### PC Bridge Application (Python)
```python
# usb_bridge.py
# Listens for TI-84 USB connection
# Forwards attestations to RustChain node
# Returns work units
```

#### Memory Budget: 4 KB

### Phase 6: Testing & Optimization (Days 25-28)

#### Testing
- [ ] Unit tests for SHA-512
- [ ] Unit tests for Ed25519
- [ ] Integration tests
- [ ] Real hardware testing
- [ ] Performance profiling

#### Optimization
- Profile hot paths
- Hand-tune critical assembly
- Reduce memory footprint
- Optimize for power consumption

---

## Code Structure

```
ti84-miner/
├── src/
│   ├── main.asm           # Entry point, mining loop
│   ├── sha512.asm         # SHA-512 implementation
│   ├── ed25519.asm        # Ed25519 signatures
│   ├── fingerprint.asm    # Hardware fingerprinting
│   ├── usb.asm            # USB communication
│   ├── math64.asm         # 64-bit arithmetic
│   └── utils.asm          # Utilities, memory ops
├── include/
│   ├── constants.inc      # Constants, magic numbers
│   ├── macros.inc         # Common macros
│   └── memory.inc         # Memory map definitions
├── lib/
│   └── ti84os.inc         # TI-84 OS calls
├── tools/
│   ├── usb_bridge.py      # PC-side USB bridge
│   └── test_vectors.py    # Test vector generator
├── test/
│   ├── sha512_test.asm
│   └── ed25519_test.asm
├── docs/
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION.md
│   └── BOUNTY_CLAIM.md
└── Makefile
```

---

## Memory Map

```
$8000-$8FFF: Code (SHA-512, Ed25519)
$9000-$9FFF: Code (Mining logic, USB)
$A000-$AFFF: Data (buffers, state)
$B000-$B7FF: Stack
$B800-$BFFF: System variables
```

---

## Build System

### Makefile
```makefile
CC = sdcc -mz80
ASM = spasm
EMU = cemu

all: miner.8xp

miner.8xp: src/main.asm src/*.asm include/*.inc
	$(ASM) src/main.asm miner.8xp

test: test.8xp
	$(EMU) test.8xp

clean:
	rm -f *.8xp *.bin *.o
```

---

## Testing Strategy

### Unit Tests
- SHA-512: NIST test vectors
- Ed25519: RFC 8032 test vectors
- Fingerprint: Deterministic mock tests

### Integration Tests
- Full attestation cycle on emulator
- USB communication loopback

### Real Hardware Tests
- TI-84 Plus (physical device)
- Performance benchmarking
- Battery life measurement

---

## Bounty Claim Deliverables

### Required Proof
1. **Screenshot**: Miner running on TI-84
2. **Hardware Info**: Photo of physical calculator
3. **Attestation Hash**: From RustChain network
4. **Miner ID**: Unique identifier
5. **RTC Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

### Documentation
- [ ] README.md with setup instructions
- [ ] BOUNTY_CLAIM.md with proof links
- [ ] Video demonstration (optional but recommended)

### GitHub PR
- [ ] Fork `yifan19860831-hub/rustchain-bounties`
- [ ] Create branch: `ti84-miner-bounty-claim`
- [ ] Add documentation to `bounties/ti84-miner/`
- [ ] Submit PR referencing issue #1156

---

## Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Memory overflow | Medium | High | Aggressive optimization, code overlays |
| Performance too slow | Medium | Medium | Accept longer epochs, optimize critical paths |
| Ed25519 too large | Low | High | Use reduced implementation, pre-computed tables |
| USB communication fails | Low | Medium | Fallback to SD card (CE model only) |

### Mitigation Strategies

1. **Memory**: Use overlay technique - load code sections as needed
2. **Performance**: Profile early, optimize hot paths first
3. **Complexity**: Start with minimal viable implementation
4. **Testing**: Test on emulator frequently, real hardware weekly

---

## Success Criteria

### Minimum Viable Product (MVP)
- [ ] SHA-512 working (< 2s per block)
- [ ] Hardware fingerprint collected
- [ ] Ed25519 signature generated (< 60s)
- [ ] Attestation submitted successfully
- [ ] Proof documented for bounty claim

### Stretch Goals
- [ ] Performance optimization (< 30s total)
- [ ] TI-84 CE support (faster eZ80)
- [ ] Video demonstration
- [ ] Tutorial blog post

---

## Timeline Summary

| Phase | Duration | End Date |
|-------|----------|----------|
| 1. Environment Setup | 2 days | Day 2 |
| 2. SHA-512 | 5 days | Day 7 |
| 3. Hardware Fingerprint | 5 days | Day 12 |
| 4. Ed25519 | 8 days | Day 20 |
| 5. Integration | 4 days | Day 24 |
| 6. Testing & Optimization | 4 days | Day 28 |
| **Total** | **28 days** | **~4 weeks** |

---

## Resources & References

### Development Tools
- [CEMu Emulator](https://github.com/CE-Programming/CEmu)
- [SPASM Assembler](https://github.com/SPASMDev/SPASM)
- [SDCC Compiler](http://sdcc.sourceforge.net/)
- [TI Connect CE](https://education.ti.com/en/products/computer-software/ti-connect-ce-sw)

### Documentation
- [TI-84 Plus Hardware Spec](https://ti-calc.org/)
- [Z80 Instruction Reference](http://www.z80.info/)
- [Ed25519 Paper](https://ed25519.cr.yp.to/)
- [SHA-512 FIPS 180-4](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)

### Community
- [Cemetech Forums](https://www.cemetech.net/)
- [TI-Dev Discord](https://discord.gg/8K3qGvq)

---

## Notes

- **Z80 architecture dates to 1974** → qualifies for 50 RTC legendary tier
- **First blockchain miner on a calculator** → significant milestone
- **Educational value**: demonstrates extreme constraints programming
- **Open source**: all code will be publicly available

---

**Status**: Ready to begin implementation

**Next Action**: Set up development environment and create project structure
