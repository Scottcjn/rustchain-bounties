# 📖 Frogger Miner Porting Guide

## How to Actually Port RustChain to Frogger Hardware

This guide walks through the theoretical process of implementing a RustChain miner on the actual Frogger arcade PCB.

---

## ⚠️ Disclaimer

**This is primarily educational.** The Z80 @ 3 MHz with 8 KB RAM cannot perform meaningful cryptocurrency mining. This guide is for:
- Understanding embedded constraints
- Learning Z80 assembly
- Appreciating modern computing power
- Winning a legendary bounty 🏆

---

## 🛠️ Prerequisites

### Hardware Needed

1. **Frogger Arcade PCB** (Konami, 1981)
   - Original or MAME-compatible reproduction
   - Cost: $200-2000 (depending on condition)

2. **EPROM Programmer**
   - For burning modified ROM
   - Must support 27256 (32 KB) or 27512 (64 KB) EPROMs

3. **Logic Analyzer / Oscilloscope**
   - For debugging timing issues
   - Optional but recommended

4. **Modern Development PC**
   - For assembling code
   - Cross-compiler toolchain

### Software Needed

```bash
# Z80 Assembler
sudo apt install z80asm

# Or use modern alternative
pip install z80-macroasm

# Emulator for testing
sudo apt install mame

# Python simulator (included)
python3 simulator/frogger_miner.py
```

---

## 📋 Step-by-Step Porting Process

### Step 1: ROM Dump & Analysis

```bash
# Dump original Frogger ROM
dd if=/dev/rom0 of=frogger_original.bin bs=1024 count=48

# Analyze ROM structure
z80dasm frogger_original.bin > frogger_disassembly.asm

# Identify hook points
grep -n "GameLoop\|VBlank\|PlayerInput" frogger_disassembly.asm
```

**Expected Output:**
- Main game loop: ~$2000
- VBlank interrupt: ~$0066
- Input handler: ~$2100

### Step 2: Design Memory Layout

```
Original Layout:
$0000-$0FFF  RAM (variables)
$1000-$1FFF  Video
$2000-$BFFF  ROM (game code)
$C000-$FFFF  RAM (stack)

Modified Layout:
$0000-$00FF  MINING VARIABLES ← New!
$0100-$0FFF  GAME VARIABLES (shifted)
$1000-$1FFF  Video
$2000-$27FF  MINING CODE ← New!
$2800-$BFFF  GAME CODE (original)
$C000-$FFFF  Stack
```

### Step 3: Implement Mining Core

**File: `mining_core.asm`**

```z80
; Initialize mining state
InitMining:
    LD HL, $0000        ; Hash counter
    LD (HL), 0
    INC HL
    LD (HL), 0
    
    LD HL, NONCE
    LD (HL), 0          ; Start nonce at 0
    INC HL
    LD (HL), 0
    INC HL
    LD (HL), 0
    INC HL
    LD (HL), 0
    
    RET
```

### Step 4: Hook Into Game Loop

**Original game loop** (simplified):
```z80
GameLoop:
    CALL ReadInput
    CALL UpdateFrog
    CALL CheckCollision
    CALL UpdateDisplay
    CALL PlaySound
    JP GameLoop
```

**Modified game loop:**
```z80
GameLoop:
    CALL ReadInput
    CALL UpdateFrog
    CALL IncrementHashCounter    ; ← New!
    CALL CheckCollision
    CALL CheckBlockFound         ; ← New!
    CALL UpdateDisplay
    CALL PlaySound
    JP GameLoop
```

### Step 5: Implement Block Detection

```z80
CheckBlockFound:
    ; Check if frog reached home
    LD A, (FrogY)
    CP $00
    RET NZ                  ; Not at home yet
    
    ; Simplified difficulty check
    LD A, (Nonce)
    AND $0F                 ; Check lower 4 bits
    JR NZ, NoBlock          ; Non-zero = no block
    
    ; BLOCK FOUND!
    CALL CelebrateBlock
    INC (BlockHeight)
    
NoBlock:
    CALL ResetFrog
    RET
```

### Step 6: Build & Test

```bash
# Assemble
z80asm -i frogger_miner.asm -o frogger_miner.bin

# Check size (must fit in available space!)
ls -l frogger_miner.bin
# Should be < 8 KB for mining code

# Test in MAME
mame frogger -rompath . -window
```

### Step 7: Burn EPROM

```bash
# Verify checksum
md5sum frogger_miner.bin

# Burn to EPROM (example with minipro)
minipro -p AT28C256 -w frogger_miner.bin

# Install in PCB
# - Power off arcade cabinet
# - Replace original ROM chip
# - Power on and test
```

---

## 🐛 Debugging Tips

### Common Issues

1. **Game Crashes on Boot**
   - Check memory map overlaps
   - Verify interrupt vectors
   - Ensure stack space available

2. **Mining Too Slow**
   - Profile hash function
   - Reduce difficulty for testing
   - Optimize hot paths

3. **Graphics Corruption**
   - Video buffer collision
   - Check timing with VBlank
   - Verify sprite attribute memory

### Debug Output

Add debug display to score area:

```z80
DebugPrint:
    ; Print hash counter to score display
    LD A, (HashCounter)
    CALL ConvertToBCD
    CALL DisplayScore
    RET
```

---

## 📊 Performance Optimization

### Cycle Counting

```z80
; Count cycles for critical section
; Example: Hash increment

IncrementHash:          ; 4 T-states
    INC HL              ; 4 T-states
    LD (HL), 0          ; 7 T-states
    JR NZ, SkipHigh     ; 7/12 T-states
SkipHigh:
                        ; Total: 15-20 T-states per hash
```

### Optimization Techniques

1. **Use Register Pairs**
   ```z80
   ; Slow
   LD A, (Counter)
   INC A
   LD (Counter), A
   
   ; Fast
   LD HL, Counter
   INC (HL)
   ```

2. **Unroll Loops**
   ```z80
   ; Instead of loop, repeat instructions
   CALL HashRound
   CALL HashRound
   CALL HashRound
   ; ... (64 times for SHA-256)
   ```

3. **Lookup Tables**
   ```z80
   ; Pre-compute constants
   SHA256_K:
       .DB $42, $8A, $56, $78  ; etc.
   ```

---

## 🎓 Learning Resources

### Z80 Assembly

- [Z80 Instruction Set Reference](http://www.z80.info/)
- [Programming the Z80](https://archive.org/details/programming-the-z80)
- [Z80 Assembly for Beginners](https://wikibooks.org/wiki/Z80_Assembly/)

### Frogger Specific

- [Frogger ROM Map](https://www.arcade-museum.com/)
- [Konami Hardware Docs](https://github.com/mamedev/mame/blob/master/src/mame/drivers/konami.cpp)
- [MAME Frogger Source](https://github.com/mamedev/mame/blob/master/src/mame/drivers/frogger.cpp)

### SHA-256 Implementation

- [FIPS 180-4 Specification](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- [SHA-256 on 8-bit AVR](https://github.com/wrboyce/avr-sha256) (similar constraints)

---

## 🏆 Bounty Submission Checklist

- [ ] ROM code assembled and tested
- [ ] MAME emulation working
- [ ] Documentation complete
- [ ] Performance analysis included
- [ ] Wallet address added: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
- [ ] PR submitted to RustChain repo
- [ ] Demo video recorded (optional but cool!)

---

## 🎉 Conclusion

You now have everything needed to port RustChain miner to Frogger!

**Remember:**
- It won't mine real blocks (physics forbids it)
- It WILL be legendary
- The journey is the reward
- The frog is your spirit animal now 🐸

**Good luck, and happy mining!**

---

*Bounty Wallet: `RTC4325af95d26d59c3ef025963656d22af638bb96b`*
