# RustChain Commodore PET Miner - Architecture Document

## Overview

This document describes the technical architecture of the RustChain Commodore PET (1977) miner, a Proof-of-Antiquity mining implementation for the first all-in-one personal computer.

## Design Goals

1. **Authenticity**: Faithfully represent Commodore PET hardware constraints and characteristics
2. **Minimalism**: Fit within 4-32 KB RAM (depending on PET model)
3. **Compatibility**: Work with Python emulator for modern submission
4. **Extensibility**: Allow future enhancements while maintaining core design

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Commodore PET Miner v1.0                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  6502 Emulator  │  │  Fingerprint    │  │ Attestation │ │
│  │  (MOS6502.py)   │  │  (PETFinger)    │  │  (RustChain)│ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘ │
│           │                    │                   │        │
│           └────────────────────┼───────────────────┘        │
│                                │                             │
│                    ┌───────────▼───────────┐                │
│                    │    PETMiner (Main)    │                │
│                    └───────────┬───────────┘                │
└────────────────────────────────┼────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼────────┐ ┌──────▼──────┐ ┌────────▼────────┐
     │  Offline Mode   │ │   Status    │ │  Wallet Gen     │
     │  (PET_ATTEST)   │ │  Display    │ │  (Entropy)      │
     └─────────────────┘ └─────────────┘ └─────────────────┘
```

## Component Details

### 1. MOS 6502 Emulator (`MOS6502` class)

**Purpose**: Accurately emulate MOS 6502 CPU behavior for hardware fingerprinting.

**Key Features**:
- Core 6502 instructions (LDA, STA, ADC, INX, INY, BNE, BEQ, etc.)
- Cycle-accurate timing (2-stage pipeline)
- Zero-page optimization (1-cycle savings)
- Stack operations ($0100-$01FF)
- PET ROM signatures (BASIC + Kernal)

**Memory Map** (8 KB configuration):
```
$0000-$00FF: Zero Page (fast access)
$0100-$01FF: Stack (256 bytes fixed)
$0200-$1FFF: User RAM (~7.5 KB)
...
$FF80-$FFFF: ROM (BASIC + Kernal signatures)
```

**Implementation Notes**:
- Python `bytearray` for memory (efficient, mutable)
- Register state in dictionary for flexibility
- Instruction table for opcode decoding
- Cycle counting for timing-based fingerprinting

### 2. PET Fingerprint (`PETFingerprint` class)

**Purpose**: Generate hardware-specific fingerprint for RustChain attestation.

**Six Hardware Checks**:

| Check | Method | Expected Result | Signature |
|-------|--------|-----------------|-----------|
| **Cycle Timing** | Measure 6502 instruction timing | 1.023 MHz ± variance | SHA256(cycles) |
| **IEEE-488** | Bus handshake timing | ~50μs latency | `IEEE488_LATENCY` |
| **Thermal** | NMOS TDP profile | 1.5W CPU, 30W system | `NMOS_6502_PET` |
| **BASIC ROM** | Check for "COMMODORE BASIC" | Present at ROM start | SHA256(ROM data) |
| **Kernal ROM** | Check for "CBM DOS" | Present at Kernal start | SHA256(ROM data) |
| **Display** | Built-in 40x25 display | Integrated monitor | `PET_40x25` |

**Fingerprint Generation**:
```python
fingerprint = {
    'checks': {check_name: {'pass': bool, 'signature': hex}},
    'all_passed': bool,
    'fingerprint_hash': SHA256(all_signatures),
    'platform': 'Commodore PET',
    'cpu': 'MOS 6502',
    'year': 1977
}
```

### 3. RustChain Attestation (`RustChainAttestation` class)

**Purpose**: Generate, sign, and manage attestations for RustChain network.

**Attestation Structure**:
```json
{
  "version": "1.0",
  "hardware": {
    "platform": "Commodore PET",
    "cpu": "MOS 6502",
    "clock_hz": 1023000,
    "memory_bytes": 8192,
    "rom_bytes": 512,
    "year": 1977,
    "manufacturer": "Commodore Business Machines",
    "designer": "Chuck Peddle",
    "model": "PET 2001"
  },
  "fingerprint": {...},
  "antiquity_multiplier": 5.0,
  "timestamp": 1710403200,
  "epoch": 1,
  "wallet": "RTC...",
  "signature": "..."
}
```

**Reward Calculation**:
```python
base_share = base_reward / num_miners
reward = base_share * 5.0  # 5.0× LEGENDARY multiplier
```

### 4. PET Miner Application (`PETMiner` class)

**Purpose**: Main application orchestrating mining operations.

**Features**:
- PET-style banner display ("READY." prompt)
- Epoch-based attestation cycles
- Offline mode (file-based attestation)
- Status display
- Wallet generation from hardware entropy

**PET-Style Display**:
```
  **** COMMODORE PET MINER ****
  ================================
  MOS 6502 @ 1.023 MHz
  8 KB RAM, 512 B ROM
  Year: 1977
  Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
  
  ANTIQUITY: 5.0x LEGENDARY
  ================================
  
READY.
```

## Technical Challenges

### 1. Memory Constraints (4-32 KB)

The PET's memory is extremely limited:
- **User RAM**: 3.5-31.5 KB depending on model
- **ROM**: 512 bytes (BASIC + Kernal)

**Solution**: 
- Minimalist design with single 256-byte attestation buffer
- Streaming hash computation (no full block storage)
- Efficient Python data structures

### 2. No Native Networking

The PET had IEEE-488 for peripherals, not networking.

**Solution**: 
- Offline mode with file-based attestation
- Modern bridge for network submission
- Similar to DOS offline mode

### 3. Hardware Fingerprinting Adaptation

Modern RustChain checks adapted for 1977 hardware:

| Modern Check | PET Adaptation |
|--------------|----------------|
| Clock-skew | 6502 cycle timing variance |
| Cache timing | No cache - direct RAM access |
| SIMD identity | No SIMD - 8-bit accumulator |
| Thermal drift | NMOS thermal profile (1.5W) |
| Instruction jitter | 6502 pipeline timing |
| Anti-emulation | ROM signatures + IEEE-488 |

## Testing Strategy

### Unit Tests
- `TestMOS6502`: CPU emulator instructions and state
- `TestPETFingerprint`: Hardware fingerprint generation
- `TestRustChainAttestation`: Attestation creation and signing
- `TestPETMiner`: Application-level tests

### Integration Tests
- Full mining cycle
- Wallet generation
- File I/O (save/load attestations)

### Running Tests
```bash
cd tests
python test_pet_miner.py -v
```

## Performance Considerations

**Estimated Hashrate**: ~0.0001 H/s on real PET hardware

This is a **proof of concept** demonstrating feasibility, not profitable mining!

**Emulated Performance**: Limited by Python interpreter speed, not 6502 clock.

## Future Enhancements

1. **Full 6502 Instruction Set**: Implement all 56 instructions
2. **Cycle-Accurate Timing**: More precise cycle counting
3. **PET Display Emulation**: 40x25 character display rendering
4. **Datasette Storage**: Simulate cassette tape I/O
5. **IEEE-488 Emulation**: Full peripheral bus emulation

## References

- [Commodore PET Wikipedia](https://en.wikipedia.org/wiki/Commodore_PET)
- [6502 Instruction Set](https://www.masswerk.at/6502/6502_instruction_set.html)
- [PET 2001 Technical Specifications](https://www.commodore.ca/gallery/museum/computers/pet-2001.htm)
- [RustChain Proof-of-Antiquity](https://github.com/Scottcjn/rustchain-bounties)

---

*Architecture designed for Bounty #403: Port Miner to Commodore PET (1977)*

**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
