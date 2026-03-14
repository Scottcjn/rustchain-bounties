# Architecture Design - Battlezone Miner

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BATTLEZONE HARDWARE                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   6502 CPU   │  │    8KB RAM   │  │   16KB ROM   │      │
│  │  @ 1.5 MHz   │◄─┤  $0000-$1FFF │  │  $C000-$FFFF │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ Vector Display│  │  I/O Ports   │                        │
│  │ 1024×768     │  │  Joysticks   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

## Memory Map

```
Address Range    Size    Usage
─────────────────────────────────────────────
$0000 - $00FF    256 B   Zero Page (fast access)
$0100 - $01FF    256 B   Stack
$0200 - $07FF    1.5 KB  Miner Variables & Buffers
$0800 - $0FFF    2 KB    Vector Display Buffer
$1000 - $7FFF    28 KB   Available RAM (if 48KB total)
$8000 - $BFFF    16 KB   I/O Registers (vector hardware)
$C000 - $FFFF    16 KB   ROM (game code, now miner code)
```

## Miner Core Components

### 1. Zero Page Variables ($0000-$00FF)

```asm
; Zero Page Variable Assignments
NONCE_LOW       = $00    ; Nonce byte 0
NONCE_HIGH      = $01    ; Nonce byte 1
HASH_RESULT     = $02    ; Current hash result
TARGET          = $03    ; Mining target difficulty
TEMP_A          = $04    ; Temporary storage
TEMP_X          = $05    ; Temporary storage
TEMP_Y          = $06    ; Temporary storage
BLOCK_HEADER    = $07    ; Block header pointer (low)
BLOCK_HEADER_H  = $08    ; Block header pointer (high)
HASH_COUNT      = $09    ; Hashes attempted (low)
HASH_COUNT_H    = $0A    ; Hashes attempted (high)
DISPLAY_FLAG    = $0B    ; Update display flag
```

### 2. Hash Function (Simplified 8-bit)

Given the 6502's limitations, we use a simplified hash function:

```
Hash(nonce, data) = XOR_fold(data) ⊕ LFSR_transform(nonce)

Where:
- XOR_fold: XOR all bytes of block header into single byte
- LFSR_transform: Linear Feedback Shift Register based on nonce
```

**Assembly Implementation:**

```asm
; Simplified 8-bit hash function
; Input: NONCE_LOW, NONCE_HIGH, block header at BLOCK_HEADER
; Output: HASH_RESULT

compute_hash:
    LDA #$00           ; Initialize hash = 0
    STA TEMP_A
    
    ; XOR fold block header (simplified - just first 8 bytes)
    LDX #$00
xor_loop:
    LDA (BLOCK_HEADER),Y
    EOR TEMP_A
    STA TEMP_A
    INY
    INX
    CPX #$08
    BNE xor_loop
    
    ; Mix with nonce using LFSR
    LDA NONCE_LOW
    LSR A
    BCC no_xor
    EOR #$B8           ; LFSR polynomial
no_xor:
    EOR TEMP_A
    STA HASH_RESULT
    RTS
```

### 3. Mining Loop

```asm
; Main mining loop
; Continuously increments nonce and checks hash against target

mining_loop:
    ; Increment nonce
    INC NONCE_LOW
    BNE check_hash
    INC NONCE_HIGH
    
check_hash:
    ; Compute hash of current nonce
    JSR compute_hash
    
    ; Compare against target
    LDA HASH_RESULT
    CMP TARGET
    BCS no_success     ; Hash >= target, continue
    
    ; Success! Hash < target
    JSR found_solution
    JMP mining_loop
    
no_success:
    ; Update hash counter
    INC HASH_COUNT
    BNE skip_high
    INC HASH_COUNT_H
    
skip_high:
    ; Periodically update display
    DEC DISPLAY_FLAG
    BPL mining_loop
    
    JSR update_display
    LDA #$20           ; Reset display counter
    STA DISPLAY_FLAG
    JMP mining_loop
```

### 4. Vector Display Update

The Battlezone vector display requires special handling:

```asm
; Update vector display with mining statistics
; Shows: nonce value, hash rate, found solutions

update_display:
    ; Clear screen (vector home)
    JSR vector_home
    
    ; Draw "MINING" title
    LDA #$4D           ; 'M'
    JSR vector_char
    ; ... (continue for each character)
    
    ; Draw nonce value (hex)
    LDA NONCE_HIGH
    JSR draw_hex_byte
    LDA NONCE_LOW
    JSR draw_hex_byte
    
    ; Draw hash counter
    LDA HASH_COUNT
    JSR draw_decimal
    
    ; Draw vector "tank" or indicator
    JSR draw_tank_indicator
    
    RTS
```

## Python Simulator Architecture

### Class Structure

```python
class CPU6502:
    """Cycle-accurate 6502 emulator"""
    - registers: A, X, Y, SP, PC, status flags
    - memory: 64 KB addressable space
    - clock: cycle counter
    - methods: execute(), load_rom(), read(), write()

class BattlezoneMiner:
    """Mining logic and state"""
    - nonce: 16-bit counter
    - target: difficulty target
    - hash_count: total hashes computed
    - solutions: list of found solutions
    - methods: compute_hash(), check_solution(), get_stats()

class VectorDisplay:
    """Vector graphics simulation"""
    - vectors: list of (x1, y1, x2, y2) lines
    - methods: draw_line(), clear(), render()

class Simulator:
    """Main simulation coordinator"""
    - cpu: CPU6502 instance
    - miner: BattlezoneMiner instance
    - display: VectorDisplay instance
    - methods: run(), step(), render_stats()
```

### Simulation Loop

```python
def run_simulation():
    cpu = CPU6502()
    miner = BattlezoneMiner()
    display = VectorDisplay()
    
    # Load miner ROM
    cpu.load_rom('src/miner_6502.bin')
    
    # Set initial state
    miner.set_target(0x10)  # Difficulty
    cpu.write_word(0x07, miner.get_block_header_addr())
    
    clock = 0
    while True:
        # Execute CPU cycles
        cycles = cpu.execute_instruction()
        clock += cycles
        
        # Check for display updates
        if cpu.read(0x0B) == 0:
            update_display(cpu, display)
            cpu.write(0x0B, 0x20)
        
        # Update mining stats
        if clock % 10000 == 0:
            print_stats(miner, clock)
        
        # Render (60 FPS target)
        if clock % 25000 == 0:  # ~1.5 MHz / 60
            display.render()
```

## Performance Estimates

### Hash Rate Calculation

```
6502 @ 1.5 MHz = 1,500,000 cycles/second

Hash computation:
- XOR fold (8 bytes):  8 × 4 cycles = 32 cycles
- LFSR transform:      ~20 cycles
- Compare & branch:    ~8 cycles
- Nonce increment:     ~4 cycles
- Overhead:            ~36 cycles
─────────────────────────────────
Total per hash:        ~100 cycles

Theoretical hash rate:
1,500,000 / 100 = 15,000 hashes/second

With display updates (~10% overhead):
~13,500 hashes/second
```

### Memory Usage

```
Code (ROM):     ~2 KB
Variables:      ~256 bytes (zero page + stack)
Display buffer: ~2 KB
Total:          ~4.5 KB (fits in 8 KB minimum config)
```

## Security Considerations

⚠️ **This is a conceptual demonstration only:**

1. **Simplified Hash**: The 8-bit hash is not cryptographically secure
2. **Tiny Nonce Space**: 16-bit nonce (65,536) is trivially searchable
3. **No Network**: No actual blockchain connectivity
4. **Educational Purpose**: Demonstrates constraints, not practical mining

## Extensions (Future Work)

1. **32-bit Nonce**: Use multiple passes for larger nonce space
2. **Better Hash**: Implement simplified SHA-1 or MD5 rounds
3. **Network Interface**: Simulated block submission via serial
4. **Multi-unit Mining**: Link multiple Battlezone cabinets

---

*Document Version: 1.0*
*Last Updated: 2026-03-14*
