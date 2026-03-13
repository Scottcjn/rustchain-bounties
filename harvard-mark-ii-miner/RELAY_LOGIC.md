# Relay Logic Diagrams

## Overview

This document describes the relay logic circuits required to implement the RustChain miner state machine on the Harvard Mark II electromechanical relay computer.

---

## Relay Fundamentals

### Basic Relay Operation

A relay is an **electromechanical switch** controlled by an electromagnet:

```
     +V (Power Supply)
      │
     ┌┴┐
     │ │ Relay Coil (when energized...)
     │ │ 
     └┬┘
      │
     GND
     
When coil is energized:
     ┌────────┐
     │ Contact│ closes
     └───┬────┘
         │
      Circuit completes
```

### Relay States

| State | Coil | Contact | Description |
|-------|------|---------|-------------|
| De-energized | OFF | Open | No current through coil |
| Energized | ON | Closed | Current flows, contact closes |

### Switching Time

- **Pick time** (energize): 5-15 ms
- **Drop time** (de-energize): 5-15 ms
- **Total switching time**: ~10-30 ms

---

## State Machine Implementation

### State Encoding

The miner has 4 states, encoded in 2 bits (2 relays):

```
State       Q1  Q0    Relay Pattern
───────────────────────────────────
INITIAL     0   0     [OFF] [OFF]
IDLE        0   1     [OFF] [ON]
MINING      1   0     [ON]  [OFF]
ATTESTING   1   1     [ON]  [ON]
```

### State Register Circuit

```
     ┌─────────────────────────────────────────┐
     │           STATE REGISTER                │
     │                                         │
     │   ┌─────┐         ┌─────┐               │
     │   │ R_Q0│────────▶│ Q0  │  State Bit 0  │
     │   └─────┘         └─────┘               │
     │                                         │
     │   ┌─────┐         ┌─────┐               │
     │   │ R_Q1│────────▶│ Q1  │  State Bit 1  │
     │   └─────┘         └─────┘               │
     │                                         │
     └─────────────────────────────────────────┘
```

### State Transition Logic

```
Current State  Input        Next State     Relay Actions
────────────────────────────────────────────────────────
INITIAL        POWER_ON     IDLE           R_Q0 = ON
IDLE           START        MINING         R_Q0 = OFF, R_Q1 = ON
MINING         COMPLETE     ATTESTING      R_Q0 = ON
ATTESTING      DONE         IDLE           R_Q1 = OFF
```

---

## Arithmetic Circuits

### Single-Digit BCD Adder

The Harvard Mark II used **decimal (BCD) arithmetic**. Here's a single-digit adder:

```
     A (4 bits) ───────┬──────────────┐
                       │              │
     B (4 bits) ───────┼──[BCD ADDER]─┼──▶ SUM (4 bits)
                       │              │
     C_in ─────────────┘              │
                                     │
                              C_out ─┘

BCD Correction:
If SUM > 9 or C_out = 1:
    SUM = SUM + 6
    C_out = 1
```

### Relay Implementation (Simplified)

```
Digit Position N:
┌─────────────────────────────────────────────────────┐
│                                                     │
│  A_N ───┬───[R_A0]───┬───[R_A1]───┬───[R_A2]───┬───[R_A3]───┐
│         │            │            │            │            │
│  B_N ───┼───[R_B0]───┼───[R_B1]───┼───[R_B2]───┼───[R_B3]───┤
│         │            │            │            │            │
│  C_N ───┴───[R_C]───────────────────────────────────────────┤
│                                                              │
│                    [CARRY LOGIC]                             │
│                                                              │
│  SUM_N ◀──[R_S0]──[R_S1]──[R_S2]──[R_S3]                     │
│  C_N+1 ◀────────────────────────────────                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Full 23-Digit Adder

The complete adder chains 23 single-digit adders:

```
Digit 23    Digit 22              Digit 2    Digit 1    Digit 0
┌──────┐   ┌──────┐              ┌──────┐   ┌──────┐   ┌──────┐
│ ADDER│──▶│ ADDER│──▶ ... ────▶│ ADDER│──▶│ ADDER│──▶│ ADDER│
└──────┘   └──────┘              └──────┘   └──────┘   └──────┘
   │          │                      │          │          │
   C_23       C_22                   C_2        C_1        C_0
```

**Total relays for adder**: ~200 relays

---

## Control Circuits

### Sequence Control

The sequence control unit generates timing signals:

```
     ┌─────────────────────────────────────────┐
     │         SEQUENCE CONTROL UNIT            │
     │                                         │
     │  ┌──────────┐                           │
     │  │ PHASE    │                           │
     │  │ COUNTER  │──▶ Phase 0, 1, 2, 3       │
     │  └──────────┘                           │
     │         │                               │
     │         ▼                               │
     │  ┌──────────┐                           │
     │  │ TIMING   │                           │
     │  │ GENERATOR│──▶ T1, T2, T3, T4          │
     │  └──────────┘                           │
     │                                         │
     └─────────────────────────────────────────┘
```

### Instruction Decoder

```
     Instruction Register (IR)
              │
              ▼
     ┌─────────────────┐
     │  OPCODE DECODER │
     └────────┬────────┘
              │
     ┌────────┴────────┬───────────┬──────────┐
     │                 │           │          │
     ▼                 ▼           ▼          ▼
 LOAD Circuit    ADD Circuit   JUMP Circuit  ...
```

---

## Memory Circuits

### Relay Register (Single Digit)

```
     ┌─────────────────────────────────────────┐
     │          1-DIGIT REGISTER                │
     │                                         │
     │   D ───[R_D0]───┬───▶ Q0                │
     │                 │                       │
     │   D ───[R_D1]───┼───▶ Q1                │
     │                 │                       │
     │   D ───[R_D2]───┼───▶ Q2                │
     │                 │                       │
     │   D ───[R_D3]───┴───▶ Q3                │
     │                                         │
     │   Relays: 4 (one per bit)               │
     │   Storage: 1 BCD digit (0-9)            │
     │                                         │
     └─────────────────────────────────────────┘
```

### Full Register (23 Digits)

```
┌─────────────────────────────────────────────────────────┐
│                    23-DIGIT REGISTER                     │
├─────────────────────────────────────────────────────────┤
│  Digit 23  Digit 22  ...  Digit 2  Digit 1  Digit 0     │
│  ┌──────┐  ┌──────┐       ┌──────┐  ┌──────┐  ┌──────┐  │
│  │ 4R   │  │ 4R   │  ...  │ 4R   │  │ 4R   │  │ 4R   │  │
│  └──────┘  └──────┘       └──────┘  └──────┘  └──────┘  │
│                                                         │
│  Total Relays: 23 × 4 = 92 relays                       │
│  Capacity: 23 decimal digits                            │
└─────────────────────────────────────────────────────────┘
```

---

## Input/Output Circuits

### Paper Tape Reader Interface

```
     Paper Tape
         │
         ▼
     ┌─────────┐
     │ Photo   │
     │ Sensor  │──▶ Digital Signal
     │ Array   │
     └─────────┘
         │
         ▼
     ┌─────────┐
     │ Buffer  │──▶ Input Register
     │ Relay   │
     └─────────┘
```

### Paper Tape Punch Interface

```
     Output Register
         │
         ▼
     ┌─────────┐
     │ Punch   │
     │ Driver  │──▶ Solenoid
     │ Relay   │
     └─────────┘
         │
         ▼
     Paper Tape (punched holes)
```

---

## Mining-Specific Circuits

### Epoch Counter

```
┌─────────────────────────────────────────────────────────┐
│                   EPOCH COUNTER                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      │
│  │  +1      │      │  STORE   │      │ DISPLAY  │      │
│  │  ADDER   │─────▶│  TO      │─────▶│  ON TAPE │      │
│  │          │      │  REGISTER│      │          │      │
│  └──────────┘      └──────────┘      └──────────┘      │
│                                                         │
│  Input: Current epoch                                   │
│  Output: Epoch + 1                                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Attestation Generator

```
┌─────────────────────────────────────────────────────────┐
│                ATTESTATION GENERATOR                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      │
│  │  EPOCH   │      │  WALLET  │      │  STATUS  │      │
│  │  NUMBER  │      │  ADDRESS │      │  MESSAGE │      │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘      │
│       │                 │                 │             │
│       └────────────┬────┴─────────────────┘             │
│                    │                                    │
│                    ▼                                    │
│            ┌──────────────┐                             │
│            │  CONCATENATE │                             │
│            │  & FORMAT    │                             │
│            └──────┬───────┘                             │
│                   │                                     │
│                   ▼                                     │
│            ┌──────────────┐                             │
│            │  PUNCH TO    │                             │
│            │  PAPER TAPE  │                             │
│            └──────────────┘                             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Timing Diagram

### Complete Mining Cycle

```
Time ─────────────────────────────────────────────────────▶

PHASE 0: INITIALIZE
┌────────────┐
│ LOAD       │
│ REGISTERS  │
└────────────┘

PHASE 1: IDLE → MINING
             ┌────────────┐
             │ TRANSITION │
             │ TO MINING  │
             └────────────┘

PHASE 2: MINING
             ┌────────────────────────────┐
             │ INCREMENT EPOCH            │
             │ (23-digit addition: ~7s)   │
             └────────────────────────────┘

PHASE 3: ATTESTING
                                          ┌──────────────┐
                                          │ GENERATE     │
                                          │ ATTESTATION  │
                                          │ (~10s)       │
                                          └──────────────┘

PHASE 4: OUTPUT
                                                       ┌──────┐
                                                       │PUNCH │
                                                       │TAPE  │
                                                       └──────┘

Total Cycle Time: ~20-30 seconds (accelerated from real Mark II)
```

---

## Power Requirements

### Relay Power Consumption

| Component | Relays | Power/Relay | Total Power |
|-----------|--------|-------------|-------------|
| State Register | 4 | 0.5W | 2W |
| Epoch Counter | 92 | 0.5W | 46W |
| Adder Circuit | 200 | 0.5W | 100W |
| Control Logic | 300 | 0.5W | 150W |
| I/O Circuits | 100 | 0.5W | 50W |
| **Total** | **696** | | **~348W** |

**Note**: The actual Harvard Mark II consumed ~10 kW total (including motors, cooling, etc.)

---

## Error Detection Circuits

### Parity Check

```
Data Bits ──▶ [XOR Tree] ──▶ Parity Bit
              (relay logic)
              
If parity mismatch:
  ──▶ [ERROR FLAG Relay] ──▶ HALT
```

### Checksum Verification

```
Instruction ──▶ [Sum Circuit] ──▶ Compare ──▶ Mismatch? ──▶ ERROR
```

---

## Physical Layout

### Relay Bank Organization

```
┌─────────────────────────────────────────────────────────┐
│                    HARVARD MARK II                       │
│                  RELAY BANK LAYOUT                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Row 1:  Accumulator (384 relays)                      │
│  Row 2:  Multiplier Register (384 relays)              │
│  Row 3:  Multiplicand Register (384 relays)            │
│  Row 4:  Constant Register (384 relays)                │
│  Row 5:  C Register (384 relays)                       │
│  Row 6:  Sequence Control (500 relays)                 │
│  Row 7:  I/O Control (300 relays)                      │
│  Row 8:  Interconnect Wiring (~600 relays)             │
│                                                         │
│  Total: ~3,300 relays                                   │
│  Size: 51 feet long × 8 feet high                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Testing and Debugging

### Manual Testing

1. **Visual Inspection**: Check relay positions
2. **Probe Testing**: Use voltmeter on relay coils
3. **Pattern Testing**: Run known test patterns

### Automated Testing

```
Test Sequence:
1. Initialize all relays to OFF
2. Apply test pattern
3. Read relay states
4. Compare with expected
5. Report errors
```

---

## References

1. Aiken, H. H. (1947). "Description of a Relay Calculator". Harvard University.
2. Harvard Computation Laboratory. "Circuit Diagrams for Mark II".
3. IEEE History Center. "Harvard Mark II Technical Specifications".

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-13  
**Wallet**: RTC4325af95d26d59c3ef025963656d22af638bb96b
