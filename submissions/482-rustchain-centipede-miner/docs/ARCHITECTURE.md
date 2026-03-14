# Centipede Miner Architecture

## Overview

This document describes the technical architecture of the RustChain miner ported to the Centipede arcade platform (1981).

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CENTIPEDE MINER SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │  Python 6502    │         │  Hardware       │               │
│  │  Emulator       │◄───────►│  Fingerprint    │               │
│  │                 │         │  System         │               │
│  └─────────────────┘         └─────────────────┘               │
│           │                           │                         │
│           │                           │                         │
│           ▼                           ▼                         │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │  Mining Core    │         │  Antiquity      │               │
│  │  (Epoch Loop)   │         │  Multiplier     │               │
│  └─────────────────┘         └─────────────────┘               │
│           │                           │                         │
│           │                           │                         │
│           ▼                           ▼                         │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │  Hash Function  │         │  Reward         │               │
│  │  (SHA-256)      │         │  Calculator     │               │
│  └─────────────────┘         └─────────────────┘               │
│           │                                                       │
│           ▼                                                       │
│  ┌─────────────────┐                                             │
│  │  Network        │                                             │
│  │  Submission     │                                             │
│  └─────────────────┘                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. MOS 6502 Emulator

**Purpose**: Emulate the Centipede arcade CPU for authentic mining behavior.

**Specifications**:
- Clock Speed: 1.5 MHz (configurable)
- Memory: 64 KB address space (8 KB RAM mapped)
- Registers: A, X, Y, SP, PC, Status
- Instruction Set: 56 base instructions

**Key Features**:
- Cycle-accurate instruction timing
- Zero page fast access emulation
- Stack operations (256 bytes at $0100-$01FF)
- Interrupt handling (NMI, IRQ, Reset)

**Implementation**:
```python
class MOS6502:
    def __init__(self, clock_speed=1500000):
        self.clock_speed = clock_speed
        self.A = 0x00      # Accumulator
        self.X = 0x00      # X Index
        self.Y = 0x00      # Y Index
        self.SP = 0xFF     # Stack Pointer
        self.PC = 0x8000   # Program Counter
        self.memory = bytearray(65536)
```

### 2. Hardware Fingerprint System

**Purpose**: Generate unique hardware identifiers for Proof-of-Antiquity.

**Fingerprint Components**:
1. **Clock Skew**: Simulated oscillator drift (0.999-1.001×)
2. **Memory Timing**: Access pattern variance
3. **Thermal Entropy**: Simulated thermal noise
4. **Instruction Jitter**: Microarchitectural timing variations

**Output**:
```json
{
  "fingerprint_id": "a3f8c2d1e9b7f4a6",
  "cpu": "MOS 6502",
  "clock_speed": 1500000,
  "era": 1981,
  "platform": "Centipede Arcade",
  "antiquity_multiplier": 3.0
}
```

### 3. Mining Core

**Epoch Structure**:
- Duration: 600 seconds (10 minutes)
- Base Reward: 1.5 RTC per epoch
- Hash Algorithm: SHA-256 (simplified for 6502)

**Mining Loop**:
```
1. Initialize epoch
2. For each nonce:
   a. Run 6502 CPU cycles
   b. Compute hash(wallet, epoch, nonce)
   c. Track best hash
   d. Display progress
3. Submit best result
4. Calculate reward
5. Repeat
```

### 4. Antiquity Multiplier

**Formula**:
```
reward = (base_reward / active_miners) × antiquity_multiplier
```

**Multiplier by Era**:

| Hardware | Year | Age | Multiplier |
|----------|------|-----|------------|
| MOS 6502 (Centipede) | 1981 | 45 | 3.0× |
| PowerPC G3 | 1997 | 29 | 1.8× |
| PowerPC G4 | 1999 | 27 | 2.5× |
| PowerPC G5 | 2003 | 23 | 2.0× |
| Core 2 Duo | 2006 | 20 | 1.3× |
| Modern x86_64 | 2025 | 1 | 1.0× |

**Decay**: Multipliers decay 15%/year to prevent permanent advantage.

### 5. Hash Function

**Production (Modern)**: SHA-256
```python
hash = SHA256(wallet || epoch || nonce || fingerprint)
```

**6502 Assembly (Simplified)**:
```assembly
; Simplified hash for 6502
; Hash = Σ(wallet_char XOR nonce)
hash_loop:
    LDA (wallet_ptr),Y    ; Load wallet character
    EOR nonce             ; XOR with nonce
    ADC checksum          ; Add to checksum
    STA checksum
    INY
    BNE hash_loop
```

**Rationale**: Full SHA-256 is impractical on 6502 (would take ~10 seconds per hash). The simplified version demonstrates the concept while maintaining authentic performance characteristics.

### 6. Network Submission

**Endpoint**: `https://rustchain.org/api/submit`

**Payload**:
```json
{
  "wallet": "RTC4325af95d26d59c3ef025963656d22af638bb96b",
  "epoch": 482,
  "hash": "a3f8c2d1e9b7f4a6...",
  "nonce": 12345,
  "fingerprint": { ... },
  "timestamp": 1710403200
}
```

**Response**:
```json
{
  "status": "accepted",
  "reward": 0.36,
  "confirmation": "tx_hash_..."
}
```

## Memory Layout

### 6502 Memory Map

```
$0000-$00FF   Zero Page (fast access variables)
$0100-$01FF   Hardware Stack (256 bytes)
$0200-$07FF   RAM (1.5 KB available)
$0800-$0FFF   Hardware Registers (I/O)
$1000-$7FFF   Unused / Expansion
$8000-$FFFF   ROM (Miner code)
```

### Python Memory Model

```python
memory = bytearray(65536)  # 64 KB address space

# Mapped regions
ZERO_PAGE = 0x0000     # 256 bytes
STACK = 0x0100         # 256 bytes
RAM = 0x0200           # 6 KB
HW_REGS = 0x0800       # 2 KB
ROM = 0x8000           # 32 KB
```

## Performance Characteristics

### Theoretical vs. Real

| Metric | Theoretical | Real (with I/O) |
|--------|-------------|-----------------|
| Hash Rate | 3000 H/s | 1.5 H/s |
| Epoch Time | 1 minute | 10 minutes |
| Power Draw | N/A (emulated) | ~100W (real hardware) |

### Bottlenecks

1. **CPU Speed**: 1.5 MHz limits hash computation
2. **Memory**: 8 KB RAM restricts algorithm complexity
3. **I/O**: Network submission adds latency
4. **Display**: Visual updates consume cycles

## Security Considerations

### Anti-Emulation

The fingerprint system includes checks to detect VMs/emulators:

```python
def verify_hardware(self):
    checks = {
        'clock_skew': measure_oscillator_drift(),
        'memory_timing': measure_access_patterns(),
        'instruction_jitter': measure_timing_variance(),
        'anti_emulation': detect_vm_signatures(),
    }
    return checks
```

**VM Detection Methods**:
- CPUID instructions (not present on real 6502)
- Timing anomalies (emulators have different jitter)
- Memory access patterns (cache effects)
- Peripheral responses (real hardware has unique behaviors)

### Reward Penalties

- **Emulated Hardware**: 10⁻⁹× multiplier (effectively zero)
- **Failed Checks**: 0.1× multiplier
- **Multiple Wallets**: Hardware fingerprint binding prevents duplication

## Testing

### Unit Tests

```python
def test_6502_lda():
    cpu = MOS6502()
    cpu.memory[0x8000] = 0xA9  # LDA #imm
    cpu.memory[0x8001] = 0x42  # Value
    cpu.run(cycles=2)
    assert cpu.A == 0x42

def test_fingerprint_uniqueness():
    fp1 = HardwareFingerprint(MOS6502())
    fp2 = HardwareFingerprint(MOS6502())
    assert fp1.fingerprint_id != fp2.fingerprint_id
```

### Integration Tests

```python
def test_mining_epoch():
    miner = CentipedeMiner(wallet="RTC...")
    hash_result, nonce = miner.mine_epoch()
    assert len(hash_result) == 64
    assert nonce >= 0
```

## Future Enhancements

1. **Full SHA-256**: Implement complete SHA-256 in 6502 assembly (very slow but authentic)
2. **Network Stack**: Add TCP/IP emulation for real network calls
3. **Graphics Output**: Render mining visualization on simulated arcade screen
4. **Sound Effects**: POKEY chip emulation for mining sound effects
5. **Multi-Miner**: Support for multiple epoch parallel mining

## References

- [6502 Datasheet](https://www.westerndesigncenter.com/wdc/documentation/65c02.pdf)
- [Centipede Arcade Manual](https://www.arcade-museum.com/manuals-videogames/C/Centipede.pdf)
- [RustChain Whitepaper](https://github.com/Scottcjn/RustChain/blob/main/docs/RustChain_Whitepaper.pdf)
- [Proof-of-Antiquity Consensus](https://doi.org/10.5281/zenodo.18623592)

## License

MIT License - Same as RustChain main project
