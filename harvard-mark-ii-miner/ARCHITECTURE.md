# Harvard Mark II Miner - Architecture Specification

## 1. System Overview

This document describes the technical architecture for implementing a RustChain Proof-of-Antiquity miner on the Harvard Mark II (ASCC) electromechanical relay computer from 1947.

### 1.1 Design Goals

1. **Historical Accuracy**: Respect the actual capabilities and constraints of the Harvard Mark II
2. **Conceptual Completeness**: Demonstrate all aspects of the RustChain protocol
3. **Educational Value**: Serve as a teaching tool about early computing
4. **Bounty Compliance**: Meet all requirements for LEGENDARY tier bounty #393

### 1.2 Key Constraints

| Constraint | Harvard Mark II | Impact on Design |
|------------|-----------------|------------------|
| **Number System** | Decimal (base-10) | All arithmetic in BCD |
| **Memory** | Relay registers (~20 words) | Minimal state storage |
| **Storage** | Paper tape (sequential) | No random access |
| **Speed** | ~3 Hz relay switching | Extremely slow operations |
| **I/O** | Paper tape reader/punch | Batch processing only |
| **Control** | Hardwired sequence | No stored programs |

---

## 2. Hardware Abstraction

### 2.1 Relay Bank Organization

The Harvard Mark II had approximately 3,300 relays organized into functional units:

```
┌─────────────────────────────────────────────────────────┐
│                    HARVARD MARK II                       │
├─────────────────────────────────────────────────────────┤
│  ACCUMULATOR (23 digits + sign)        [384 relays]    │
│  MULTIPLIER REGISTER                    [384 relays]    │
│  MULTIPLICAND REGISTER                  [384 relays]    │
│  CONSTANT REGISTER                      [384 relays]    │
│  C REGISTER (results)                   [384 relays]    │
│  SEQUENCE CONTROL                       [500 relays]    │
│  INPUT/OUTPUT CONTROL                   [300 relays]    │
│  INTERCONNECT WIRING                     [~600 relays]  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Miner State Allocation

For the mining implementation, we allocate relay registers as follows:

```
Register Name        Purpose                    Relays Used
───────────────────────────────────────────────────────────
EPOCH_COUNTER        Current epoch number       24 relays (2 digits + sign)
MINER_STATE          State machine (0-2)        12 relays (1 digit)
WALLET_PTR           Pointer to wallet string   24 relays (address)
TEMP_1               Temporary calculation      24 relays
TEMP_2               Temporary calculation      24 relays
───────────────────────────────────────────────────────────
TOTAL                                         108 relays
```

---

## 3. Data Representation

### 3.1 Decimal Encoding

The Harvard Mark II used **binary-coded decimal (BCD)** with 4 bits per decimal digit:

```
Decimal Digit    BCD Encoding
─────────────────────────────
0                0000
1                0001
2                0010
3                0011
4                0100
5                0101
6                0110
7                0111
8                1000
9                1001
```

### 3.2 Number Format

Numbers were stored in **23 decimal digits plus sign**:

```
┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ S │ D1│ D2│ D3│ D4│ D5│ D6│ D7│ D8│ D9│D10│D11│D12│D13│D14│D15│D16│D17│D18│D19│D20│D21│D22│D23│
└───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
  S = Sign (0=positive, 9=negative)
  D1-D23 = Decimal digits (most significant first)
```

### 3.3 Character Encoding

For ASCII output on paper tape, we use a simple mapping:

```
Character    Paper Tape Code (octal)
────────────────────────────────────
A-Z          101-132 (65-90 decimal)
0-9          060-071 (48-57 decimal)
Space        040 (32 decimal)
Newline      012 (10 decimal)
```

---

## 4. State Machine Design

### 4.1 State Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│    ┌─────────────┐                                               │
│    │   INITIAL   │                                               │
│    │   STATE     │                                               │
│    │   (0)       │                                               │
│    └──────┬──────┘                                               │
│           │ [START]                                              │
│           ▼                                                      │
│    ┌─────────────┐      [EPOCH COMPLETE]      ┌─────────────┐   │
│    │    IDLE     │───────────────────────────▶│   MINING    │   │
│    │   STATE     │                            │   STATE     │   │
│    │   (1)       │                            │   (2)       │   │
│    └──────┬──────┘                            └──────┬──────┘   │
│           │                                          │           │
│           │                                          │ [DONE]    │
│           │                                          ▼           │
│           │                                   ┌─────────────┐   │
│           │                                   │  ATTESTING  │   │
│           │                                   │   STATE     │   │
│           │                                   │   (3)       │   │
│           │                                   └──────┬──────┘   │
│           │                                          │           │
│           └──────────────────────────────────────────┘           │
│                      [RESET]                                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 State Encoding

```
State          Code    Relay Pattern (4-bit)
────────────────────────────────────────────
INITIAL        0       0000
IDLE           1       0001
MINING         2       0010
ATTESTING      3       0011
```

### 4.3 State Transitions

| Current State | Input/Condition | Next State | Action |
|---------------|-----------------|------------|--------|
| INITIAL | Power-on | IDLE | Initialize registers |
| IDLE | Operator START | MINING | Load epoch counter |
| MINING | Count complete | ATTESTING | Punch attestation |
| ATTESTING | Output complete | IDLE | Reset for next epoch |

---

## 5. Paper Tape Format

### 5.1 Physical Format

- **Width**: 1 inch (25.4 mm)
- **Channels**: 8 (7 data + 1 sprocket)
- **Pitch**: 10 holes per inch
- **Material**: Paper or mylar

### 5.2 Channel Assignment

```
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ 8 │ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │
├───┼───┼───┼───┼───┼───┼───┼───┤
│ S │ D7│ D6│ D5│ D4│ D3│ D2│ D1│
└───┴───┴───┴───┴───┴───┴───┴───┘
S = Sprocket hole (always punched)
D1-D7 = Data bits (LSB to MSB)
```

### 5.3 Program Structure

```
┌─────────────────────────────────────────────────────────┐
│                    PAPER TAPE LAYOUT                     │
├─────────────────────────────────────────────────────────┤
│ [LEADER: 100 blank characters]                          │
│ [PROGRAM: Machine instructions]                         │
│ [DATA: Constants and variables]                         │
│ [WALLET: ASCII wallet address]                          │
│ [TRAILER: 50 blank characters]                          │
└─────────────────────────────────────────────────────────┘
```

### 5.4 Instruction Encoding

Each instruction is encoded as a fixed-format record:

```
┌────────┬────────┬────────┬────────┬────────┐
│ OPCODE │ ADDR1  │ ADDR2  │ ADDR3  │ CHECK  │
│ (1 ch) │ (4 ch) │ (4 ch) │ (4 ch) │ (2 ch) │
└────────┴────────┴────────┴────────┴────────┘
Total: 15 characters per instruction
```

#### Opcode Table

```
Opcode  Mnemonic     Operation
─────────────────────────────────────────
L       LOAD         Load from address
S       STORE        Store to address
A       ADD          Add to accumulator
M       MULTIPLY     Multiply
D       DIVIDE       Divide
C       COMPARE      Compare with address
J       JUMP         Unconditional jump
Z       JUMP_IF_ZERO Jump if zero
P       PRINT        Output to tape
H       HALT         Stop execution
```

---

## 6. Mining Algorithm (Conceptual)

### 6.1 Proof-of-Antiquity on Mark II

Since the Mark II cannot perform SHA-256, we use a **symbolic proof**:

```
Proof = H(EPOCH_NUMBER || WALLET_ADDRESS || TIMESTAMP)

Where:
- EPOCH_NUMBER: Current RustChain epoch (decimal)
- WALLET_ADDRESS: Miner's wallet (ASCII)
- TIMESTAMP: Time of attestation (decimal)
- H(): Symbolic hash (identity function for Mark II)
```

### 6.2 Algorithm Steps

```
1. LOAD epoch_number from input tape
2. ADD 1 to epoch_number
3. STORE new epoch_number
4. LOAD wallet_address
5. PRINT "EPOCH: " + epoch_number
6. PRINT "WALLET: " + wallet_address
7. PRINT "STATUS: ATTESTED"
8. PRINT "ANTIQUITY: MUSEUM_TIER (2.5x)"
9. HALT
```

### 6.3 Timing Analysis

```
Operation               Relays    Time (est.)
─────────────────────────────────────────────
Load register           ~50       0.05s
Add two numbers         ~200      0.3s
Store register          ~50       0.05s
Compare values          ~100      0.15s
Jump (sequence change)  ~300      0.1s
Print character         ~150      0.5s
─────────────────────────────────────────────
Total per epoch         ~850      ~5 seconds
```

---

## 7. Relay Logic Implementation

### 7.1 Basic Relay Circuit

```
     +V
      │
     ┌┴┐
     │ │ Relay Coil
     └┬┘
      │
     ┌┴┐
     │ │ Contact (NO)
     └┬┘
      │
     GND
```

### 7.2 State Register (4-bit)

```
State Bit 0: ───[R1]───┬─── Output Q0
                       │
State Bit 1: ───[R2]───┼─── Output Q1
                       │
State Bit 2: ───[R3]───┼─── Output Q2
                       │
State Bit 3: ───[R4]───┴─── Output Q3
```

### 7.3 Adder Circuit (Single Digit)

```
A ───┬───[R_A]───┬─── Sum
     │           │
B ───┼───[R_B]───┼─── Carry
     │           │
C_in ─┴───[R_C]───┘
```

---

## 8. Simulation Architecture

### 8.1 Python Simulator Components

```
mark2_miner.py
├── RelayBank          # Simulates relay states
├── DecimalALU         # BCD arithmetic operations
├── PaperTapeReader    # Input tape emulation
├── PaperTapePunch     # Output tape emulation
├── SequenceControl    # Instruction sequencing
└── MinerStateMachine  # Mining logic
```

### 8.2 Simulation Accuracy

The simulator models:

- ✅ Relay switching delays (10ms per relay)
- ✅ Decimal arithmetic (BCD encoding)
- ✅ Paper tape I/O timing
- ✅ State machine transitions
- ✅ Error conditions (tape jams, relay failures)

---

## 9. Error Handling

### 9.1 Hardware Errors

| Error | Detection | Recovery |
|-------|-----------|----------|
| Relay stuck | Current monitoring | Manual reset |
| Tape jam | Motion sensor | Operator intervention |
| Power failure | Voltage monitor | Restart from checkpoint |
| Overflow | Carry detection | Halt and alert |

### 9.2 Software Errors

| Error | Detection | Recovery |
|-------|-----------|----------|
| Invalid opcode | Opcode decoder | Halt |
| Address error | Range check | Halt |
| Parity error | Checksum | Retry read |

---

## 10. Performance Metrics

### 10.1 Theoretical Performance

```
Metric                    Harvard Mark II    Modern CPU
────────────────────────────────────────────────────────
Instructions/second      ~3                 ~3,000,000,000
Addition time            0.3s               ~1ns
Memory access            0.01s              ~100ns
Energy per op            ~100J              ~1nJ
────────────────────────────────────────────────────────
Relative performance     1x                 1,000,000,000x
```

### 10.2 Mining Performance (Symbolic)

```
Epoch duration           10 minutes (real time)
Attestations per day     144 (theoretical max)
Power consumption        10 kW
Cost per attestation     ~$16 (electricity only)
```

**Note**: Real mining is not possible. This is a conceptual demonstration.

---

## 11. Testing Strategy

### 11.1 Unit Tests

- Test each relay bank independently
- Verify BCD arithmetic correctness
- Validate paper tape encoding/decoding

### 11.2 Integration Tests

- Full state machine cycle
- End-to-end paper tape processing
- Error condition handling

### 11.3 Historical Validation

- Compare with Harvard Mark II documentation
- Validate timing against historical records
- Cross-reference with computer museum specifications

---

## 12. Future Enhancements

### 12.1 Potential Additions

- [ ] Full relay-level simulation (individual relay modeling)
- [ ] 3D visualization of relay bank
- [ ] Sound effects (relay clicking)
- [ ] Paper tape image generation
- [ ] Integration with real RustChain node (symbolic only)

### 12.2 Educational Extensions

- [ ] Interactive tutorial mode
- [ ] Historical timeline integration
- [ ] Comparison with other vintage computers
- [ ] Classroom lesson plans

---

## 13. References

1. Aiken, H. H. (1947). "Description of a Relay Calculator". Harvard University.
2. Hopper, G. (1953). "The Education of a Computer". Proceedings of ACM.
3. IEEE History Center. "Harvard Mark II (ASCC)". https://ethw.org/
4. Computer History Museum. "Harvard Mark II Collection".
5. RustChain Documentation. "Proof-of-Antiquity Protocol".

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-13  
**Author**: RustChain Bounty Hunter  
**Wallet**: RTC4325af95d26d59c3ef025963656d22af638bb96b
