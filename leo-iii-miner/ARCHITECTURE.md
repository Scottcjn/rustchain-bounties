# LEO III Miner Architecture

## Executive Summary

This document describes the architectural design for porting the RustChain miner to the **LEO III** (1961), the world's first mass-produced commercial computer.

**Key Challenge**: The LEO III has approximately **8-16 KB** of core memory and **no networking capabilities**. This implementation is a **conceptual adaptation** that demonstrates the spirit of Proof-of-Antiquity on this historic business computer.

---

## 1. Hardware Architecture

### 1.1 LEO III Specifications

```
┌─────────────────────────────────────────────────────────────────┐
│                         LEO III (1961)                           │
├─────────────────────────────────────────────────────────────────┤
│  Technology:     Solid-state (transistors)                      │
│  Cycle Time:     13.2 μs (~75,000 instructions/sec)             │
│  Memory:         Ferrite core memory, 8-16 KB typical           │
│  Word Size:      32 bits                                        │
│  Instructions:   Variable-length, microprogrammed               │
│  OS:             Master Program (multi-tasking, 12 jobs)        │
│  I/O:            Paper tape, punched cards, magnetic tape       │
│  Storage:        Magnetic tape units                            │
│  Special:        Loudspeaker for program monitoring             │
│  Production:     ~60 units (1961-1969)                          │
│  Power:          ~5-10 kW (estimated)                           │
│  Size:           Multiple cabinets, room-sized                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Memory Organization

```
Ferrite Core Memory Layout:
┌────────────────────────────────────────┐
│ Total: 8K-16K words × 32 bits          │
│                                        │
│ ┌──────────────────────────────────┐   │
│ │ Word 0:     System bootstrap     │   │
│ │ Words 1-100: Master Program OS   │   │
│ │ Words 101-500: Job 1 (Payroll)   │   │
│ │ Words 501-900: Job 2 (Inventory) │   │
│ │ ...                              │   │
│ │ Words 6000-6500: Job 7 (Miner)   │   │
│ │ ...                              │   │
│ │ Words 7500-8191: I/O buffers     │   │
│ └──────────────────────────────────┘   │
└────────────────────────────────────────┘

Word Format (32 bits):
┌────────┬────────┬────────┬────────┐
│ Byte 0 │ Byte 1 │ Byte 2 │ Byte 3 │
│ 8 bits │ 8 bits │ 8 bits │ 8 bits │
└────────┴────────┴────────┴────────┘
```

### 1.3 Instruction Set (Simplified)

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| 0x01 | LOAD | Load accumulator from memory | 2 |
| 0x02 | STORE | Store accumulator to memory | 2 |
| 0x03 | ADD | Add memory to accumulator | 2 |
| 0x04 | SUB | Subtract memory from accumulator | 2 |
| 0x05 | MUL | Multiply accumulator by memory | 8 |
| 0x06 | DIV | Divide accumulator by memory | 12 |
| 0x07 | JUMP | Unconditional jump | 1 |
| 0x08 | JPOS | Jump if accumulator positive | 1 |
| 0x09 | JNEG | Jump if accumulator negative | 1 |
| 0x0A | JZER | Jump if accumulator zero | 1 |
| 0x0B | INPUT | Input from paper tape | 50 |
| 0x0C | OUTPUT | Output to printer/tape | 50 |
| 0x0D | MASTER | Master Program OS call | 10 |
| 0x0E | AND | Logical AND | 2 |
| 0x0F | OR | Logical OR | 2 |
| 0x10 | XOR | Logical XOR | 2 |
| 0x11 | SOUND | Generate audio tone | 1 |
| 0x12 | PUNCH | Punch paper tape | 100 |
| 0x00 | STOP | Halt execution | 1 |

### 1.4 Master Program OS

The LEO III's **Master Program** was revolutionary for its time:

```
Master Program Architecture:
┌─────────────────────────────────────────────────────────────┐
│                      MASTER PROGRAM                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Job Scheduler:                                              │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐  │
│  │ Job 1│ Job 2│ Job 3│ Job 4│ Job 5│ Job 6│ Job 7│ ...  │  │
│  │Payrol│Invent│Billing│ ... │ ... │ ... │Miner │      │  │
│  └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘  │
│                                                              │
│  Time Slice: 100ms per job (round-robin)                    │
│  Priority Levels: High, Medium, Low                         │
│  Max Concurrent Jobs: 12                                    │
│                                                              │
│  Memory Management:                                          │
│  - Fixed partition allocation                               │
│  - Each job gets dedicated memory region                    │
│  - No virtual memory                                        │
│                                                              │
│  I/O Management:                                             │
│  - Spooled I/O via magnetic tape                            │
│  - Shared printer/reader access                             │
│  - Job-specific tape units                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Proof-of-Antiquity Adaptation

### 2.1 Original RustChain PoA

The modern RustChain miner performs:
1. **Hardware Fingerprinting**: CPU, MAC addresses, serial numbers
2. **Attestation**: Submit fingerprint to network
3. **Enrollment**: Register for current epoch
4. **Mining**: Submit shares based on hardware uniqueness
5. **Verification**: Network validates hardware authenticity

### 2.2 LEO III Adaptation

| Original Component | LEO III Equivalent |
|-------------------|-------------------|
| CPU ID | Core memory residual magnetization pattern |
| MAC Address | Tape unit serial numbers |
| Network Attestation | Paper tape / punched card output |
| Epoch Enrollment | Master Program time slice allocation |
| Share Submission | Line printer output + loudspeaker proof |
| Hardware Verification | Unique core memory signature |

### 2.3 Hardware Fingerprinting

Each LEO III's ferrite core memory has a unique **residual magnetization pattern**:

```python
class CoreMemory:
    def __init__(self, size_words=8192):
        self.size = size_words
        self.words = [0] * size_words
        # Unique residual pattern from manufacturing
        self.residual_pattern = self._generate_residual()
    
    def _generate_residual(self) -> int:
        # Simulated residual magnetization pattern
        # In reality, this would be measured from physical hardware
        import random
        return random.randint(0, 0xFFFFFFFF)
    
    def get_fingerprint(self) -> str:
        # Core memory signature
        return f"{self.residual_pattern:08X}"

def generate_system_fingerprint(memory: CoreMemory, tape_units: list) -> str:
    # Combine core memory pattern with tape unit IDs
    core_fp = memory.get_fingerprint()
    tape_fp = sum(tape_units) & 0xFFFFFFFF
    combined = (int(core_fp, 16) ^ tape_fp) & 0xFFFFFFFFFFFFFFFF
    return f"{combined:016X}"
```

### 2.4 Mining Algorithm

```
┌─────────────────────────────────────────────────────────────┐
│                    LEO III MINING ALGORITHM                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. INITIALIZATION (Master Program Job Start)                │
│     - READ core_memory residual → FINGERPRINT                │
│     - INITIALIZE NONCE = 0                                   │
│     - LOAD DIFFICULTY threshold                              │
│     - REGISTER with Master Program                           │
│                                                              │
│  2. MINING LOOP (per time slice)                             │
│     LOOP:                                                    │
│       a. NONCE ← NONCE + 1                                   │
│       b. HASH ← FINGERPRINT XOR NONCE                        │
│       c. IF HASH < DIFFICULTY THEN                           │
│            - SHARE FOUND!                                    │
│            - OUTPUT "SHARE" to line printer                  │
│            - SOUND loudspeaker (audio proof)                 │
│            - PUNCH share details to paper tape               │
│            - LOG to magnetic tape                            │
│       d. CHECK Master Program time slice                     │
│       e. JUMP LOOP                                           │
│                                                              │
│  3. SHARE SUBMISSION                                         │
│     - Paper tape serves as "submission"                      │
│     - Loudspeaker tone provides audio proof-of-work          │
│     - Printer output provides human-readable record          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.5 Difficulty Calculation

The difficulty is adjusted based on LEO III's computational capacity:

```
Base Difficulty: 0x00100 (256 out of 4,294,967,296 possible values)
Probability: ~0.000006% per attempt
Expected Attempts: ~16,777,216
Expected Time: 16,777,216 × 13.2μs ≈ 221 seconds per share

Adjusted Difficulty (for practical mining): 0x01000
Probability: ~0.000095% per attempt
Expected Attempts: ~1,048,576
Expected Time: 1,048,576 × 13.2μs ≈ 13.8 seconds per share
```

---

## 3. Intercode Program

### 3.1 Program Encoding

LEO III used **Intercode**, a low-level assembly language:

```
Intercode Instruction Format:
    OPCODE  ADDRESS     ; Comment
    
Example:
    LOAD    FINGERPRINT ; Load hardware fingerprint into A
    ADD     NONCE       ; Add nonce
    STORE   HASH        ; Store result
```

### 3.2 Mining Program (Intercode)

```
         TITLE   RUSTCHAIN MINER FOR LEO III
         ORG     6000            ; Job 7 memory region
         
; ============================================================
; CONSTANTS
; ============================================================
DIFFICULTY  EQU     01000          ; Mining difficulty
ONE         EQU     1              ; Constant: 1
FINGERPRINT EQU     7000           ; Core memory fingerprint location

; ============================================================
; VARIABLES
; ============================================================
NONCE       DS      1              ; Current nonce (word)
HASH        DS      1              ; Hash result (word)
SHARE_COUNT DS      1              ; Shares found counter

; ============================================================
; MINING ROUTINE
; ============================================================
START:    LOAD    FINGERPRINT    ; A ← core memory fingerprint
          ADD     NONCE          ; A ← A + nonce
          STORE   HASH           ; Store hash result
          
          SUB     DIFFICULTY     ; A ← A - difficulty
          JPOS    CONTINUE       ; If A > 0, no share
          
          ; SHARE FOUND!
          LOAD    SHARE_COUNT
          ADD     ONE
          STORE   SHARE_COUNT
          
          OUTPUT  SHARE_MSG      ; Print "SHARE FOUND"
          SOUND   440            ; Audio proof (A4 tone)
          PUNCH   SHARE_DATA     ; Punch details to tape
          
CONTINUE: LOAD    NONCE
          ADD     ONE
          STORE   NONCE
          
          ; Check Master Program time slice
          MASTER  CHECK_TIME     ; OS call
          JZER    START          ; Continue if time remains
          
          ; Time slice expired, yield to Master Program
          MASTER  YIELD
          JUMP    START
          
; ============================================================
; DATA
; ============================================================
SHARE_MSG:  TXT     'SHARE FOUND - '
SHARE_DATA: DS      10             ; Share data buffer

          END     START
```

### 3.3 Paper Tape Output Format

```
Paper Tape Share Record:
┌────────────────────────────────────────┐
│ Format: Fixed 80 characters            │
│                                        │
│ Columns 1-16:  Wallet address          │
│ Columns 17-32: Hardware fingerprint    │
│ Columns 33-40: Nonce (hex)             │
│ Columns 41-48: Hash value (hex)        │
│ Columns 49-56: Difficulty (hex)        │
│ Columns 57-72: Timestamp (decimal)     │
│ Columns 73-80: Job number + checksum   │
└────────────────────────────────────────┘

Example:
RTC4325AF95D26D5B4E8C3D2F1A0987600A4F20000F800100017103345670074A
```

---

## 4. Implementation Details

### 4.1 Simulator Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PYTHON SIMULATOR                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐    ┌──────────────────┐               │
│  │  CoreMemory      │    │  MagneticTape    │               │
│  │  - 8K words      │    │  - Share logs    │               │
│  │  - residual_pat  │    │  - Persistent    │               │
│  └──────────────────┘    └──────────────────┘               │
│           │                       │                          │
│           └───────────┬───────────┘                          │
│                       │                                      │
│              ┌────────▼────────┐                             │
│              │ LEOIII          │                             │
│              │ - core_memory   │                             │
│              │ - accumulator   │                             │
│              │ - instruction   │                             │
│              │ - pc            │                             │
│              │ - master_prog   │                             │
│              └────────┬────────┘                             │
│                       │                                      │
│              ┌────────▼────────┐                             │
│              │ RustChainMiner  │                             │
│              │ - fingerprint   │                             │
│              │ - difficulty    │                             │
│              │ - shares        │                             │
│              │ - job_number    │                             │
│              └─────────────────┘                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Key Classes

#### LEOIII
- `core_memory`: CoreMemory instance (8K words)
- `tape_units`: List of magnetic tape unit IDs
- `accumulator`: 32-bit accumulator register
- `program_counter`: Current instruction address
- `master_program`: MasterProgram OS simulator
- Methods: `load_program()`, `execute_instruction()`, `run()`, `get_fingerprint()`

#### MasterProgram
- `jobs`: List of active jobs (max 12)
- `time_slice_ms`: Time slice per job (default 100ms)
- `current_job`: Currently executing job
- Methods: `register_job()`, `schedule()`, `yield_cpu()`, `check_time()`

#### RustChainMiner
- `computer`: LEOIII instance
- `job_number`: Master Program job number (1-12)
- `difficulty`: Mining difficulty threshold
- `shares_found`: List of valid shares
- `nonce`: Current nonce value
- Methods: `generate_fingerprint()`, `compute_hash()`, `mine_share()`, `submit_share()`

### 4.3 Mining Share Structure

```python
@dataclass
class MiningShare:
    timestamp: int      # Unix timestamp
    wallet: str         # RTC wallet address
    fingerprint: str    # 16-character hex hardware fingerprint
    nonce: int          # 32-bit nonce used
    hash_value: int     # Computed hash (must be < difficulty)
    difficulty: int     # Difficulty threshold
    job_number: int     # Master Program job number (1-12)
    
    def is_valid(self) -> bool:
        return self.hash_value < self.difficulty
    
    def to_paper_tape(self) -> str:
        """Format share as 80-character paper tape record"""
        return (
            f"{self.wallet:<16}"
            f"{self.fingerprint:<16}"
            f"{self.nonce:08X}"
            f"{self.hash_value:08X}"
            f"{self.difficulty:08X}"
            f"{self.timestamp:016d}"
            f"{self.job_number:02d}"
        )
```

---

## 5. Performance Analysis

### 5.1 Theoretical Performance

| Metric | LEO III | Modern CPU |
|--------|---------|------------|
| Cycle Time | 13.2 μs | ~0.3 ns |
| Instructions/sec | ~75,000 | ~3,000,000,000 |
| Memory Access | 13.2 μs | ~0.5 ns |
| Multiplication | ~100 μs | ~3 cycles |
| Hash Attempts/sec | ~10,000 | ~1,000,000,000 |

### 5.2 Expected Mining Rate

```
Difficulty 0x01000:
- Probability per attempt: 4096 / 4,294,967,296 ≈ 0.000095%
- Expected attempts per share: ~1,048,576
- Expected time per share: 1,048,576 × 13.2μs ≈ 13.8 seconds
- Shares per hour: ~260

Difficulty 0x00100:
- Probability per attempt: 256 / 4,294,967,296 ≈ 0.000006%
- Expected attempts per share: ~16,777,216
- Expected time per share: 16,777,216 × 13.2μs ≈ 221 seconds
- Shares per hour: ~16

Note: Actual rate limited by Master Program time slicing
(100ms time slice = ~10% CPU time for miner job)
```

---

## 6. Testing

### 6.1 Unit Tests

```bash
# Run test suite
python test_miner.py

# Test individual components
python -c "from leo_iii_simulator import *; c = LEOIII(); print(c.get_fingerprint())"
```

### 6.2 Integration Tests

```bash
# Run mining demonstration
python leo_iii_simulator.py --demo

# Run extended mining session
python leo_iii_simulator.py --mine --duration 60 --difficulty 0x01000

# Test Master Program integration
python leo_iii_simulator.py --master-program --jobs 4
```

### 6.3 Expected Output

```
============================================================
LEO III Simulator
RustChain Proof-of-Antiquity Miner
============================================================

🔨 Starting RustChain Mining Session on LEO III
Difficulty: 0x01000
Duration:   10.0s
Wallet:     RTC4325af95d26d59c3ef025963656d22af638bb96b
Master Program Job: 7
============================================================

[LOUDSPEAKER] ♫ Tone 440 Hz
============================================================
SHARE FOUND!
============================================================
Wallet:     RTC4325af95d26d59c3ef025963656d22af638bb96b
Fingerprint: B4E8C3D2F1A09876
Nonce:      00A4F2
Hash:       0000F8
Difficulty: 001000
Timestamp:  1710334567
Job:        7
============================================================

============================================================
MINING SESSION COMPLETE
============================================================
Duration:     10.15s
Attempts:     10000
Shares Found: 1
Instructions: 85000
Cycles:       85000
Master Program Time Slices: 102
============================================================
```

---

## 7. Limitations and Future Work

### 7.1 Current Limitations

1. **No Real Hardware**: This is a simulation; no actual LEO III exists that can run this code
2. **Simplified Hash**: Uses XOR instead of cryptographic hash (SHA-256 impractical on LEO III)
3. **No Networking**: Paper tape/card output simulates network submission
4. **No Persistence**: Shares not persisted to magnetic tape in current implementation
5. **Master Program Simulation**: Simplified OS simulation
6. **No CLEO Implementation**: Only Intercode (assembly) version provided

### 7.2 Potential Enhancements

1. **Magnetic Tape Storage**: Implement share persistence to tape
2. **Multi-Job Mining**: Parallel mining across multiple Master Program jobs
3. **Paper Tape Output**: Physical paper tape output (with vintage hardware emulator)
4. **Audio Verification**: Record loudspeaker tones as proof-of-work
5. **CLEO Implementation**: High-level CLEO language version
6. **Museum Display**: Run on LEO III emulator in computer museum
7. **Intercode Assembler**: Build a working Intercode assembler
8. **Master Program Emulation**: Full Master Program OS emulation

---

## 8. Conclusion

This implementation demonstrates that while the LEO III cannot run a modern blockchain miner, the **core concepts of Proof-of-Antiquity** can be adapted to any computational substrate, no matter how historically constrained.

The LEO III's unique characteristics—ferrite core memory patterns, Master Program multi-tasking, paper tape I/O, and the iconic loudspeaker—provide a fascinating analogy to modern hardware fingerprinting and network attestation.

**Historical Significance**: The LEO III was the first computer to bring computing to ordinary businesses. By adapting RustChain mining to this platform, we honor the legacy of democratizing computation.

**Bounty Claim**: Wallet `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

*"From tea shop accounting to crypto mining—the LEO III's journey spans the entire history of commercial computing."*
