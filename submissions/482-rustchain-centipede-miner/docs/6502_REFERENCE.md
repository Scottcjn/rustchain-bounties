# MOS 6502 Instruction Reference

## Overview

The MOS Technology 6502 is an 8-bit microprocessor introduced in 1975. It was used in many classic systems including:
- Apple II
- Commodore 64
- Nintendo Entertainment System (NES)
- Atari 2600
- **Atari Centipede Arcade (1981)** ← Our target

## Specifications

| Property | Value |
|----------|-------|
| Clock Speed | 1-3 MHz (Centipede: 1.5 MHz) |
| Data Width | 8 bits |
| Address Width | 16 bits (64 KB) |
| Transistors | ~3,500 |
| Instructions | 56 base |
| Registers | A, X, Y, SP, PC, STATUS |

## Registers

```
┌────────────────────────────────────────────┐
│  A  - Accumulator (8 bits)                 │
│  X  - X Index Register (8 bits)            │
│  Y  - Y Index Register (8 bits)            │
│  SP - Stack Pointer (8 bits)               │
│  PC - Program Counter (16 bits)            │
│  STATUS - Status Register (8 bits)         │
└────────────────────────────────────────────┘
```

### Status Register Flags

```
Bit  Name  Description
───  ────  ───────────────────────────
7    N     Negative (result bit 7)
6    V     Overflow (arithmetic overflow)
5    -     Unused (always 1)
4    B     Break (software interrupt)
3    D     Decimal mode (BCD arithmetic)
2    I     Interrupt disable
1    Z     Zero (result is zero)
0    C     Carry (arithmetic carry/borrow)
```

## Instruction Set

### Load/Store Instructions

| Opcode | Mnemonic | Description | Cycles | Bytes |
|--------|----------|-------------|--------|-------|
| $A9 | LDA #imm | Load Accumulator | 2 | 2 |
| $AD | LDA abs | Load Accumulator (absolute) | 4 | 3 |
| $B5 | LDA zp | Load Accumulator (zero page) | 3 | 2 |
| $A1 | LDA (zp,X) | Load Accumulator (indexed indirect) | 6 | 2 |
| $B1 | LDA (zp),Y | Load Accumulator (indirect indexed) | 5 | 2 |
| $8D | STA abs | Store Accumulator | 4 | 3 |
| $85 | STA zp | Store Accumulator (zero page) | 3 | 2 |
| $91 | STA (zp),Y | Store Accumulator (indirect indexed) | 6 | 2 |
| $A2 | LDX #imm | Load X Register | 2 | 2 |
| $AE | LDX abs | Load X Register (absolute) | 4 | 3 |
| $A0 | LDY #imm | Load Y Register | 2 | 2 |
| $AC | LDY abs | Load Y Register (absolute) | 4 | 3 |

### Register Transfer

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $AA | TAX | Transfer A to X | 2 |
| $8A | TXA | Transfer X to A | 2 |
| $A8 | TAY | Transfer A to Y | 2 |
| $98 | TYA | Transfer Y to A | 2 |
| $TSX | TSX | Transfer SP to X | 2 |
| $9A | TXS | Transfer X to SP | 2 |

### Stack Operations

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $48 | PHA | Push Accumulator | 3 |
| $68 | PLA | Pull Accumulator | 4 |
| $08 | PHP | Push Status | 3 |
| $28 | PLP | Pull Status | 4 |

### Logical Operations

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $29 | AND #imm | AND with Accumulator | 2 |
| $25 | AND zp | AND (zero page) | 3 |
| $09 | ORA #imm | OR with Accumulator | 2 |
| $05 | ORA zp | OR (zero page) | 3 |
| $49 | EOR #imm | Exclusive OR | 2 |
| $45 | EOR zp | EOR (zero page) | 3 |
| $24 | BIT abs | Bit Test | 4 |

### Arithmetic Operations

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $69 | ADC #imm | Add with Carry | 2 |
| $65 | ADC zp | ADC (zero page) | 3 |
| $E9 | SBC #imm | Subtract with Carry | 2 |
| $E5 | SBC zp | SBC (zero page) | 3 |
| $C9 | CMP #imm | Compare Accumulator | 2 |
| $E0 | CPX #imm | Compare X Register | 2 |
| $C0 | CPY #imm | Compare Y Register | 2 |

### Increment/Decrement

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $E8 | INX | Increment X | 2 |
| $C8 | INY | Increment Y | 2 |
| $CA | DEX | Decrement X | 2 |
| $88 | DEY | Decrement Y | 2 |
| $EE | INC abs | Increment Memory | 6 |
| $E6 | INC zp | Increment (zero page) | 5 |
| $CE | DEC abs | Decrement Memory | 6 |
| $C6 | DEC zp | Decrement (zero page) | 5 |

### Shift/Rotate

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $0A | ASL A | Arithmetic Shift Left | 2 |
| $06 | ASL zp | ASL (zero page) | 5 |
| $4A | LSR A | Logical Shift Right | 2 |
| $46 | LSR zp | LSR (zero page) | 5 |
| $2A | ROL A | Rotate Left | 2 |
| $26 | ROL zp | ROL (zero page) | 5 |
| $6A | ROR A | Rotate Right | 2 |
| $66 | ROR zp | ROR (zero page) | 5 |

### Branch Instructions

| Opcode | Mnemonic | Description | Cycles* |
|--------|----------|-------------|---------|
| $F0 | BEQ | Branch if Equal (Z=1) | 2/3 |
| $D0 | BNE | Branch if Not Equal (Z=0) | 2/3 |
| $B0 | BCS | Branch if Carry Set (C=1) | 2/3 |
| $90 | BCC | Branch if Carry Clear (C=0) | 2/3 |
| $30 | BMI | Branch if Minus (N=1) | 2/3 |
| $10 | BPL | Branch if Plus (N=0) | 2/3 |
| $70 | BVS | Branch if Overflow Set (V=1) | 2/3 |
| $50 | BVC | Branch if Overflow Clear (V=0) | 2/3 |

*Branch takes +2 cycles if taken and crosses page boundary

### Jump/Call

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $4C | JMP abs | Jump | 3 |
| $6C | JMP (ind) | Jump Indirect | 5 |
| $20 | JSR abs | Jump to Subroutine | 6 |
| $60 | RTS | Return from Subroutine | 6 |
| $40 | RTI | Return from Interrupt | 6 |

### Flag Control

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $38 | SEC | Set Carry | 2 |
| $18 | CLC | Clear Carry | 2 |
| $F8 | SED | Set Decimal | 2 |
| $D8 | CLD | Clear Decimal | 2 |
| $78 | SEI | Set Interrupt Disable | 2 |
| $58 | CLI | Clear Interrupt Disable | 2 |
| $B8 | CLV | Clear Overflow | 2 |

### System Instructions

| Opcode | Mnemonic | Description | Cycles |
|--------|----------|-------------|--------|
| $EA | NOP | No Operation | 2 |
| $00 | BRK | Break (software interrupt) | 7 |

## Addressing Modes

### Immediate (#)
```assembly
LDA #$42    ; Load immediate value 0x42 into A
```

### Zero Page (zp)
```assembly
LDA $80     ; Load from address 0x0080 (faster, 2 bytes)
```

### Absolute (abs)
```assembly
LDA $8000   ; Load from address 0x8000
```

### Indexed
```assembly
LDA $1000,X ; Load from 0x1000 + X
LDA $1000,Y ; Load from 0x1000 + Y
```

### Indirect
```assembly
JMP ($FFFC) ; Jump to address stored at 0xFFFC
```

### Indexed Indirect
```assembly
LDA ($80,X) ; Load from address at (0x80 + X)
```

### Indirect Indexed
```assembly
LDA ($80),Y ; Load from address at (0x80) + Y
```

## Example: Mining Loop

```assembly
; Initialize
        LDA #$00        ; A = 0
        STA $0200       ; Store at RAM
        STA $0201       ; Nonce low byte
        STA $0202       ; Nonce high byte

; Mining loop
mining_loop:
        INC $0201       ; Increment nonce low
        BNE check_hash
        INC $0202       ; Increment nonce high

check_hash:
        ; Compute hash (simplified)
        LDA $0201       ; Load nonce
        EOR $0300       ; XOR with wallet byte
        STA $0210       ; Store hash result
        
        ; Check difficulty
        CMP #$80        ; Compare with target
        BCS found_valid ; Branch if valid
        
        JMP mining_loop ; Continue mining

found_valid:
        ; Valid hash found
        JSR submit      ; Call submit routine
        JMP mining_loop ; Continue
```

## Timing Calculations

### Centipede Arcade (1.5 MHz)

```
Clock Period: 1 / 1,500,000 = 667 nanoseconds

Instruction Timing:
- LDA #imm: 2 cycles = 1.33 μs
- STA abs:  4 cycles = 2.67 μs
- JMP abs:  3 cycles = 2.00 μs
- JSR abs:  6 cycles = 4.00 μs

Hash Computation (simplified, ~500 cycles):
- Time per hash: 500 × 667 ns = 333 μs
- Hashes per second: ~3,000 H/s (theoretical)
- Real-world (with I/O): ~1.5 H/s
```

## Memory Map for Centipede Miner

```
$0000-$00FF   Zero Page
  $00-$01     wallet_ptr (pointer to wallet string)
  $02         epoch_num
  $03-$04     nonce (16-bit)
  $05         hash_result
  $06         temp
  $07-$08     checksum

$0100-$01FF   Stack

$0200-$07FF   RAM
  $0200       wallet string
  $0210       hash buffer
  $0220       network buffer

$0800-$0FFF   Hardware Registers
  $0800       submission flag

$8000-$FFFF   ROM (Miner Code)
```

## Resources

- [6502 Datasheet - WDC](https://www.westerndesigncenter.com/wdc/documentation/65c02.pdf)
- [6502 Instruction Set](http://www.6502.org/tutorials/6502opcodes.html)
- [Programming the 6502](https://www.amazon.com/Programming-6502-Christopher-Lampton/dp/0830608818)
- [Visual 6502 Simulator](http://www.visual6502.org/)

## License

MIT License - Part of RustChain Centipede Miner project
