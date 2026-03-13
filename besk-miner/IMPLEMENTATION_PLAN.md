# BESK (1953) RustChain Miner - Implementation Plan

## Executive Summary

**Project**: Port RustChain miner to BESK (Binär Elektronisk SekvensKalkylator)  
**Bounty**: 200 RTC (LEGENDARY Tier)  
**Issue**: #1815  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Multiplier**: 5.0x (Maximum)  
**Timeline**: 8-12 weeks  

BESK was Sweden's first electronic computer, completed in 1953. For a brief period, it was the **fastest computer in the world**. This document provides a complete implementation plan for porting the RustChain miner to this historic machine.

---

## Architecture Overview

### BESK Specifications

| Component | Specification |
|-----------|---------------|
| **Year** | 1953 (completed), inaugurated April 1, 1954 |
| **Location** | Swedish Board for Computing Machinery, Stockholm |
| **Architecture** | IAS (von Neumann) derivative |
| **Word Size** | 40 bits (parallel binary) |
| **Memory** | 512 words × 40 bits = 2.5 KB (Williams tubes) |
| **Memory Upgrade** | Ferrite core memory (1956) |
| **Vacuum Tubes** | 2,400 radio tubes |
| **Diodes** | 400 germanium diodes (partly solid-state) |
| **Add Time** | 56 microseconds |
| **Multiply Time** | 350 microseconds |
| **Instruction Length** | 20 bits (2 per word) |
| **Power** | 15 kVA |
| **MTBF** | Initially 5 minutes (1953), improved 1954 |

### IAS Architecture Heritage

BESK was closely modeled on the **IAS machine** from the Institute for Advanced Study. The design team retrieved drawings during a scholarship to IAS and MIT.

**Key IAS Features in BESK**:
- Stored-program architecture (von Neumann)
- 40-bit word size
- Binary representation (two's complement)
- Two instructions per word
- Williams tube memory (later core memory)

### BESK vs Other IAS Derivatives

| Machine | Year | Location | Memory | Add Time | Notes |
|---------|------|----------|--------|----------|-------|
| **BESK** | 1953 | Sweden | 512 words | 56 μs | Fastest in world (briefly) |
| MANIAC I | 1952 | Los Alamos | 1024 words | 62 μs | Nuclear research |
| ILLIAC I | 1952 | Illinois | 1024 words | ~100 μs | University use |
| JOHNNIAC | 1954 | RAND | 1024 words | ~100 μs | Business applications |
| AVIDAC | 1953 | Argonne | 1024 words | 62 μs | Nuclear physics |
| IBM 701 | 1952 | Commercial | 1024 words | ~120 μs | First commercial |

**BESK Advantages**:
- **Fastest add time** (56 μs) among IAS derivatives
- **Pioneering core memory** upgrade (1956)
- **Partly solid-state** (germanium diodes)
- **Long operational life** (1953-1966)

---

## Phase 1: Simulator Development (50 RTC)

### 1.1 BESK CPU Simulator

**Goal**: Create a fully functional BESK/IAS simulator in Python

#### Core Components

```python
# besk_sim/cpu.py
class BESKCPU:
    def __init__(self):
        # 40-bit accumulator (AC)
        self.ac = 0
        # 40-bit multiplier/quotient register (MQ)
        self.mq = 0
        # Memory buffer register (MBR)
        self.mbr = 0
        # Instruction register (IR) - 20 bits
        self.ir = 0
        # Program counter (PC) - 9 bits for 512 words
        self.pc = 0
        # Memory: 512 words × 40 bits
        self.memory = [0] * 512
        # Status flags
        self.zero_flag = False
        self.negative_flag = False
        # Timing
        self.cycle_count = 0
        self.instruction_count = 0
        
    def execute_instruction(self):
        """Execute one instruction with BESK timing"""
        # Fetch: Get 40-bit word from memory
        word = self.memory[self.pc]
        
        # BESK format: two 20-bit instructions per word
        # Left instruction (bits 39-20), Right instruction (bits 19-0)
        if self.use_left_instruction:
            self.ir = (word >> 20) & 0xFFFFF
        else:
            self.ir = word & 0xFFFFF
            self.pc += 1  # Only advance PC after right instruction
            
        # Decode and execute
        opcode = (self.ir >> 15) & 0x1F  # 5-bit opcode
        address = self.ir & 0x7FFF  # 13-bit address
        
        cycles = self._execute_opcode(opcode, address)
        self.cycle_count += cycles
        self.instruction_count += 1
        return cycles
```

#### BESK Instruction Set

Based on IAS architecture with BESK-specific optimizations:

| Opcode | Mnemonic | Cycles | Time (μs) | Description |
|--------|----------|--------|-----------|-------------|
| 0x00 | `STOP` | 1 | ~12 | Halt execution |
| 0x01 | `ADD` | 5 | 56 | Add memory to AC |
| 0x02 | `SUB` | 5 | 56 | Subtract memory from AC |
| 0x03 | `MUL` | 30 | 350 | Multiply AC × MQ → MQ:AC |
| 0x04 | `DIV` | 35 | ~400 | Divide MQ:AC by memory |
| 0x05 | `AND` | 3 | ~40 | Bitwise AND |
| 0x06 | `OR` | 3 | ~40 | Bitwise OR |
| 0x07 | `XOR` | 3 | ~40 | Bitwise XOR |
| 0x08 | `JMP` | 2 | ~25 | Unconditional jump |
| 0x09 | `JZ` | 2 | ~25 | Jump if AC = 0 |
| 0x0A | `JN` | 2 | ~25 | Jump if AC < 0 |
| 0x0B | `JP` | 2 | ~25 | Jump if AC > 0 |
| 0x0C | `LD` | 3 | ~40 | Load memory to AC |
| 0x0D | `ST` | 3 | ~40 | Store AC to memory |
| 0x0E | `RSH` | 4 | ~50 | Right shift AC |
| 0x0F | `LSH` | 4 | ~50 | Left shift AC |
| 0x10 | `IN` | 100 | ~1500 | Input from paper tape |
| 0x11 | `OUT` | 100 | ~1500 | Output to paper tape |

### 1.2 Williams Tube Memory Model

```python
# besk_sim/williams_tube.py
import random
import time

class BESKWilliamsMemory:
    """
    Simulates BESK's original Williams tube memory
    512 words × 40 bits using 40 cathode ray tubes + 8 spares
    """
    
    def __init__(self, words=512, refresh_rate_hz=100):
        self.words = words
        self.refresh_rate = refresh_rate_hz
        self.data = [0] * words
        # BESK-specific drift patterns
        self.drift_pattern = self._generate_besk_drift()
        self.temperature = 25.0
        self.last_refresh_time = time.time()
        self.refresh_interval = 1.0 / refresh_rate_hz
        # BESK had ~5 minute MTBF initially
        self.base_error_rate = 0.0002  # 0.02% (higher than IAS)
        
    def _generate_besk_drift(self):
        """Generate BESK-specific drift pattern"""
        # BESK had unique Swedish-manufactured tubes
        return [random.randint(0, 0xFF) for _ in range(self.words)]
        
    def read(self, address):
        """Read with BESK Williams tube characteristics"""
        base_value = self.data[address]
        
        # Drift calculation
        time_since_refresh = time.time() - self.last_refresh_time
        drift_factor = min(1.0, time_since_refresh / self.refresh_interval)
        drift = int(self.drift_pattern[address] * drift_factor) & 0xFF
        drifted_value = base_value ^ (drift << 32)
        
        # BESK error rate (improved after 1954)
        if random.random() < self._calculate_error_rate():
            error_bit = random.randint(0, 39)
            drifted_value ^= (1 << error_bit)
            
        return drifted_value & self.MASK_40
        
    def write(self, address, value):
        """Write with BESK reliability"""
        reliability = self._calculate_reliability()
        
        if random.random() < reliability:
            self.data[address] = value & self.MASK_40
            return True
        return False
        
    def refresh(self):
        """Refresh BESK memory (required ~100 Hz)"""
        self.last_refresh_time = time.time()
        for i in range(self.words):
            self.data[i] = self.data[i]
```

### 1.3 Core Memory Upgrade (1956)

```python
# besk_sim/core_memory.py

class BESKCoreMemory:
    """
    Simulates BESK's 1956 ferrite core memory upgrade
    Built by housewives with knitting experience!
    More reliable than Williams tubes
    """
    
    def __init__(self, words=512):
        self.words = words
        self.data = [0] * words
        # Core memory is non-volatile and more reliable
        self.error_rate = 0.00001  # 0.001% (much better)
        self.access_time = 40e-6  # 40 μs access time
        
    def read(self, address):
        """Core memory read (destructive, requires rewrite)"""
        value = self.data[address]
        # Simulate destructive read
        self.data[address] = 0
        # Immediate rewrite
        self.data[address] = value
        return value
        
    def write(self, address, value):
        """Core memory write (very reliable)"""
        if random.random() < (1.0 - self.error_rate):
            self.data[address] = value & self.MASK_40
            return True
        return False
```

---

## Phase 2: SHA256 Implementation (75 RTC)

### 2.1 Memory Layout for SHA256

```
BESK Memory Map (512 words × 40 bits)
======================================

0x000-0x07F (0-127):    Program code (SHA256 implementation)
0x080-0x087 (128-135):  Hash state H0-H7 (8 words)
0x088-0x0C7 (136-199):  Round constants K0-K63 (64 words)
0x0C8-0x0FF (200-255):  Message schedule W0-W63 (64 words)
0x100-0x13F (256-319):  Working variables (a,b,c,d,e,f,g,h)
0x140-0x17F (320-383):  Input block buffer (512 bits = 16 words)
0x180-0x1BF (384-447):  Nonce space, temporary storage
0x1C0-0x1FF (448-511):  Control logic, I/O buffers

Total: 512 words (100% utilized - tight fit!)
```

**Note**: BESK's 512-word memory is half the size of IAS (1024 words), requiring careful optimization.

### 2.2 SHA256 Performance on BESK

**Calculations**:
- SHA256 operations per hash: ~7,100 instructions
- Average BESK instruction time: ~80 μs (weighted by 56 μs add, 350 μs mul)
- Time per hash: 7,100 × 80 μs = 568,000 μs = **0.57 seconds**
- **Hash rate: ~1.75 H/s** (theoretical)

**Realistic Performance** (memory refresh, errors, I/O):
- **0.8-1.5 H/s** (0.67-1.25 seconds per hash)

**Comparison**:

| Machine | Year | Memory | Hash Rate | Notes |
|---------|------|--------|-----------|-------|
| **BESK** | 1953 | 512 words | **0.8-1.5 H/s** | Fastest add time |
| BESK (core) | 1956 | 512 words | 1.0-1.8 H/s | More reliable |
| MANIAC I | 1952 | 1024 words | 0.5-1.0 H/s | More memory |
| AVIDAC | 1953 | 1024 words | 0.5-1.0 H/s | Similar |
| SWAC | 1950 | 256 words | 0.02-0.2 H/s | Slower |

---

## Phase 3: Network Bridge (50 RTC)

### 3.1 Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│    BESK     │───▶│ Paper Tape   │───▶│ Arduino/    │───▶│   Internet   │
│   (1953)    │◀───│   Reader     │◀───│  ESP32      │◀───│  (HTTPS)     │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
   Williams/Core      Optical          Microcontroller     Mining Pool
     Memory           Sensor           (Python/C++)
```

### 3.2 Paper Tape Protocol

Same as AVIDAC implementation (standard IAS derivative protocol).

---

## Phase 4: Hardware Fingerprint (25 RTC)

### 4.1 Unique BESK Characteristics

1. **Williams Tube Signature** (1953-1956)
   - 40 CRT tubes + 8 spares
   - Swedish manufacturing characteristics
   
2. **Core Memory Signature** (1956+)
   - Knitted by housewives (unique construction)
   - Ferrite core timing characteristics

3. **Vacuum Tube Array**
   - 2,400 radio tubes (more than IAS)
   - 400 germanium diodes (hybrid design)

4. **Power Signature**
   - 15 kVA consumption
   - Unique Swedish power grid characteristics

---

## Phase 5: Documentation (25 RTC)

### 5.1 Video Requirements

**Shots Needed**:
1. BESK control panel (Smithsonian or Tekniska museet)
2. Williams tube bank / core memory
3. Paper tape operation
4. Mining visualization
5. Historical context (Swedish computing heritage)

### 5.2 Repository Structure

```
besk-miner/
├── README.md
├── BESK_ARCHITECTURE.md
├── IMPLEMENTATION.md
├── SIMULATOR.md
├── besk_sim/
│   ├── cpu.py
│   ├── williams_tube.py
│   ├── core_memory.py
│   └── assembler.py
├── sha256/
│   ├── besk_sha256.py
│   └── test_vectors.py
├── bridge/
│   └── bridge_firmware.py
└── docs/
    ├── video/
    └── historical/
```

---

## Timeline

| Phase | Duration | RTC | Status |
|-------|----------|-----|--------|
| 1 | Simulator Development | 2-3 weeks | 50 | Not started |
| 2 | SHA256 Implementation | 3-4 weeks | 75 | Not started |
| 3 | Network Bridge | 2-3 weeks | 50 | Not started |
| 4 | Hardware Fingerprint | 1-2 weeks | 25 | Not started |
| 5 | Documentation | 1 week | 25 | Not started |
| **Total** | **9-13 weeks** | **225** | |

---

## Historical Significance

**BESK Achievements**:
- **Fastest computer in the world** (briefly, 1953-1954)
- **Sweden's first electronic computer**
- **Pioneered core memory** in Europe (1956)
- **Longest operational life** (1953-1966, 13 years)
- **Nuclear weapon program** calculations
- **First computer animation** (1960, car driving simulation)
- **Mersenne prime discovery** (1957, 969 digits)

**Why BESK Matters**:
BESK represents **Swedish engineering excellence** and the **democratization of computing** beyond superpowers (US, UK, USSR). It proved that smaller nations could build world-class computers and contribute to the digital revolution.

---

## Success Criteria

### MVP
- [ ] Working BESK simulator
- [ ] SHA256 validated against NIST vectors
- [ ] Network bridge prototype
- [ ] Basic documentation

### Full Implementation
- [ ] All MVP criteria
- [ ] Hardware fingerprint extraction
- [ ] Williams tube + core memory simulation
- [ ] Video documentation
- [ ] Historical accuracy verified

### Exceptional (Bonus)
- [ ] Partnership with Tekniska museet (Swedish National Museum of Science and Technology)
- [ ] Swedish media coverage
- [ ] Educational outreach in Nordic countries

---

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Issue**: #1815  
**Status**: Implementation Plan Created  
**Next**: Begin Phase 1 - Simulator Development
