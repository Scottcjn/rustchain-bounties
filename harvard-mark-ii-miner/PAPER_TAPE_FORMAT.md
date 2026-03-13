# Paper Tape Format Specification

## Overview

The Harvard Mark II used **8-channel paper tape** for program input and data output. This document specifies the exact format used for encoding RustChain miner programs.

---

## Physical Specifications

### Tape Dimensions

| Property | Value |
|----------|-------|
| Width | 1 inch (25.4 mm) |
| Thickness | 0.003 inch (0.076 mm) |
| Pitch (hole spacing) | 10 holes per inch |
| Material | Paper or Mylar |
| Color | Natural (cream/white) |

### Channel Layout

```
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ 8 │ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │
├───┼───┼───┼───┼───┼───┼───┼───┤
│ S │ D7│ D6│ D5│ D4│ D3│ D2│ D1│
└───┴───┴───┴───┴───┴───┴───┴───┘

S  = Sprocket hole (always punched)
D1-D7 = Data bits (D1 = LSB, D7 = MSB)
```

---

## Encoding Scheme

### Character Encoding

Each character is encoded as 7-bit ASCII with the sprocket bit set:

```
Character Code = (ASCII Value) OR 0x80
```

#### Examples

| Character | ASCII (decimal) | ASCII (binary) | Tape Code (hex) | Tape Pattern |
|-----------|-----------------|----------------|-----------------|--------------|
| 'A' | 65 | 1000001 | 0xC1 | ●●○○○○○● |
| '0' | 48 | 0110000 | 0xB0 | ●●○●○○○○ |
| ' ' | 32 | 0100000 | 0xA0 | ●●○○○○○○ |
| '\n' | 10 | 0001010 | 0x8A | ●○○○○●○● |

**Pattern Legend**: ● = punched, ○ = not punched

### Sprocket Channel

Channel 8 (the sprocket channel) is **always punched** for valid data characters. This serves two purposes:

1. **Synchronization**: The tape reader uses the sprocket hole to advance the tape
2. **Error Detection**: Missing sprocket holes indicate tape damage or read errors

---

## Program Structure

A complete miner program on paper tape has the following structure:

```
┌─────────────────────────────────────────────────────────┐
│ [LEADER: 100 blank characters]                          │
│   - All channels punched (0x80)                         │
│   - Allows tape to thread through reader                │
├─────────────────────────────────────────────────────────┤
│ [HEADER: Program identification]                        │
│   - "HARVARD MARK II MINER"                             │
│   - "RUSTCHAIN PROOF-OF-ANTIQUITY"                      │
│   - "EPOCH: 1947"                                       │
├─────────────────────────────────────────────────────────┤
│ [PROGRAM: Machine instructions]                         │
│   - Opcodes and operands                                │
│   - One instruction per line                            │
├─────────────────────────────────────────────────────────┤
│ [DATA SECTION: Constants and variables]                 │
│   - Epoch counter initial value                         │
│   - State machine constants                             │
│   - Message strings                                     │
├─────────────────────────────────────────────────────────┤
│ [WALLET ADDRESS: ASCII encoded]                         │
│   - Format: "WALLET:RTC..."                             │
│   - 42 characters total                                 │
├─────────────────────────────────────────────────────────┤
│ [ATTESTATION TEMPLATE]                                  │
│   - Output format for attestation                       │
├─────────────────────────────────────────────────────────┤
│ [TRAILER: 50 blank characters]                          │
│   - Allows tape to exit reader cleanly                  │
└─────────────────────────────────────────────────────────┘
```

---

## Instruction Format

Each machine instruction is encoded as a fixed-format record:

```
┌────────┬────────┬────────┬────────┬────────┐
│ OPCODE │ ADDR1  │ ADDR2  │ ADDR3  │ CHECK  │
│ (1 ch) │ (4 ch) │ (4 ch) │ (4 ch) │ (2 ch) │
└────────┴────────┴────────┴────────┴────────┘
Total: 15 characters per instruction
```

### Opcode Table

| Opcode | Mnemonic | Operation | Example |
|--------|----------|-----------|---------|
| L | LOAD | Load from address | `L 0050` |
| S | STORE | Store to address | `S 0100` |
| A | ADD | Add to accumulator | `A 0001` |
| M | MULTIPLY | Multiply | `M 0025` |
| D | DIVIDE | Divide | `D 0010` |
| C | COMPARE | Compare with address | `C 0200` |
| J | JUMP | Unconditional jump | `J 0050` |
| Z | JUMP_IF_ZERO | Jump if zero | `Z 0100` |
| P | PRINT | Output to tape | `P 0300` |
| H | HALT | Stop execution | `H` |

### Example Instructions

```
Instruction: LOAD from address 50
Encoded:    L  050            
Tape:       0xC3 0xA0 0xB0 0xB5 0xB0 ...

Instruction: ADD 1
Encoded:    A  001            
Tape:       0xC1 0xA0 0xB0 0xB0 0xB1 ...

Instruction: HALT
Encoded:    H                 
Tape:       0xC8 0xA0 0xA0 0xA0 0xA0 ...
```

---

## Data Encoding

### Numeric Data

Numbers are stored in **decimal** format, one digit per character:

```
Value: 42
Encoded: '4' '2'
Tape:    0xB4 0xB2
```

### Negative Numbers

Negative numbers use a sign prefix:

```
Value: -17
Encoded: '-' '1' '7'
Tape:    0xAD 0xB1 0xB7
```

### Text Strings

Strings are encoded as ASCII characters, terminated by newline:

```
String: "IDLE"
Encoded: 'I' 'D' 'L' 'E' '\n'
Tape:    0xC9 0xC4 0xCC 0xC5 0x8A
```

---

## Wallet Address Format

The wallet address is encoded as ASCII text with a prefix:

```
Format: WALLET:<address>
Example: WALLET:RTC4325af95d26d59c3ef025963656d22af638bb96b
```

### Encoding

```
Position  Characters        Tape Codes
────────────────────────────────────────
0-5       "WALLET:"         0xC7 0xC1 0xCC 0xCC 0xC5 0xC4 0xAE
6-47      Address           (42 characters)
48        '\n'              0x8A
Total:    49 characters
```

---

## Error Detection

### Checksum

Each instruction includes a 2-character checksum:

```
Checksum = (Sum of all character codes) MOD 100
```

Example:
```
Instruction: L 050
Characters:  'L' ' ' '0' '5' '0'
Codes:       76 + 32 + 48 + 53 + 48 = 257
Checksum:    257 MOD 100 = 57
Encoded:     '5' '7'
```

### Parity

Some implementations used odd parity on channel 7:

```
If (number of 1s in channels 1-6) is even:
    Channel 7 = 1 (punched)
Else:
    Channel 7 = 0 (not punched)
```

---

## Reading Paper Tape

### Manual Reading

Paper tape can be read manually using a **tape reader template**:

```
Template:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ 8 │ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │
├───┼───┼───┼───┼───┼───┼───┼───┤
│ ● │ ● │ ○ │ ● │ ○ │ ○ │ ○ │ ● │  → 'A' (0xC1)
│ ● │ ● │ ○ │ ● │ ○ │ ○ │ ○ │ ○ │  → '0' (0xB0)
└───┴───┴───┴───┴───┴───┴───┴───┘
```

### Machine Reading

The Harvard Mark II tape reader operated at approximately **10 characters per second**:

```
Read Speed: 10 chars/sec
Tape Speed: 1 inch/sec
Latency: ~100ms per character
```

---

## Writing Paper Tape

### Manual Punching

For short programs, tape can be punched manually:

1. Mark tape with pencil using template
2. Use hand punch to create holes
3. Verify with reader template

### Machine Punching

The Mark II could punch output tape at **5 characters per second**:

```
Punch Speed: 5 chars/sec
Time for 1000 chars: ~200 seconds (3.3 minutes)
```

---

## Example: Complete Program

Here's a complete example of a minimal miner program:

```
[Leader: 100 x 0x80]

HARVARD MARK II MINER
RUSTCHAIN PROOF-OF-ANTIQUITY

L  000            
A  001            
S  100            
P  200            
H               

[Data]
000: 0
001: 1
100: (epoch counter)
200: "ATTESTED"

WALLET:RTC4325af95d26d59c3ef025963656d22af638bb96b

[Trailer: 50 x 0x80]
```

---

## File Formats

### Binary Format (.pt)

Raw binary file with one byte per tape position:

```python
with open('program.pt', 'rb') as f:
    tape_data = f.read()  # bytes object
```

### Text Format (.txt)

Human-readable hex dump:

```
# Paper Tape Data (8-channel)
# Total characters: 250
# Format: Position | Code (hex) | Code (bin) | Char
#------------------------------------------------------------
0000 | 0x80 | 10000000 | '.'
0001 | 0x80 | 10000000 | '.'
...
0100 | 0xC8 | 11001000 | 'H'
0101 | 0xC1 | 11000001 | 'A'
...
```

---

## Tools

### Encoder

```bash
python simulation/paper_tape_encoder.py --miner output.pt
```

### Decoder

```bash
python simulation/paper_tape_decoder.py input.pt --verbose
```

### Simulator

```bash
python simulation/mark2_miner.py
```

---

## References

1. Aiken, H. H. (1947). "Description of a Relay Calculator". Harvard University.
2. IBM (1949). "IBM Punch Card and Tape Specifications".
3. Computer History Museum. "Paper Tape Formats".

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-13  
**Wallet**: RTC4325af95d26d59c3ef025963656d22af638bb96b
