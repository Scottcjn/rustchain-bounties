# TRS-80 Miner - Technical Design Document

## 1. System Constraints

### 1.1 Hardware Limitations

```
CPU:        Z80 @ 1.77 MHz (≈ 585 K instructions/sec theoretical)
RAM:        4 KB total (we use 2 KB for code + data)
Video:      64×16 text, memory-mapped at 0x4000
Storage:    Cassette tape (load/save via KCS standard)
I/O:        Memory-mapped, no interrupts for mining
```

### 1.2 Design Goals

1. **Fit in 1 KB code** - Leave 3 KB for data/stack
2. **No external dependencies** - Pure Z80 assembly
3. **Visible progress** - Update display every 100 hashes
4. **Pause/Resume** - Support cassette save/load state

## 2. Memory Layout

```
┌─────────────────────────────────────────┐
│ 0x0000 - 0x3FFF  (16 KB)  ROM (BASIC)   │
├─────────────────────────────────────────┤
│ 0x4000 - 0x43FF  (1 KB)   Video RAM     │ ← Display output
├─────────────────────────────────────────┤
│ 0x4400 - 0x44FF  (256 B)  Miner Code    │ ← Our program
├─────────────────────────────────────────┤
│ 0x4500 - 0x45FF  (256 B)  Block Data    │ ← Current work
├─────────────────────────────────────────┤
│ 0x4600 - 0x46FF  (256 B)  Hash State    │ ← Intermediate values
├─────────────────────────────────────────┤
│ 0x4700 - 0x47FF  (256 B)  Stack         │ ← Call stack
└─────────────────────────────────────────┘
```

## 3. Mining Algorithm

### 3.1 Simplified Hash Function

Full SHA-256 is too large for 4 KB RAM. We implement **MiniHash-8**:

```
Input:  32-byte block header
Output: 4-byte hash

Algorithm:
  state[0..3] = IV constants
  for each byte b in block:
    state[0] = (state[0] + b) mod 256
    state[1] = state[1] XOR state[0]
    state[2] = ROTL(state[2], 3) XOR b
    state[3] = (state[3] * 7) mod 256
    // Mix states
    temp = state[0]
    state[0] = state[1]
    state[1] = state[2]
    state[2] = state[3]
    state[3] = temp
  return concatenate(state[0..3])
```

### 3.2 Proof of Work

```
target = 0x00FFFFFF  // Difficulty: top byte must be 0x00
nonce = 0 to 65535

for nonce in 0..65535:
  block[28..29] = nonce (little-endian)
  hash = MiniHash(block)
  if hash < target:
    return (nonce, hash)  // FOUND!
```

Expected iterations: ~256 (1 in 256 chance per nonce)
Expected time: 256 × 1000 cycles / 1.77 MHz ≈ 0.14 seconds

## 4. Z80 Register Allocation

```
During mining loop:
  HL     - Points to current block byte
  DE     - Nonce counter (0-65535)
  BC     - Hash state (B=state0, C=state1)
  A      - Working accumulator
  IX     - Points to video RAM for display
  IY     - Points to block data
```

## 5. Display Routine

### 5.1 Video RAM Layout

```
0x4000: Row 0, cols 0-63
0x4040: Row 1, cols 0-63
...
0x43C0: Row 15, cols 0-63
```

### 5.2 Display Update

```assembly
; Update nonce display at row 1, col 35
; Nonce value in DE
display_nonce:
  push de
  ld a, d          ; High byte
  call print_hex_byte
  ld a, e          ; Low byte
  call print_hex_byte
  pop de
  ret
```

## 6. Code Sections

### 6.1 Entry Point (0x4400)

```assembly
ORG 0x4400

START:
  ; Initialize stack
  LD SP, 0x47FF
  
  ; Clear screen
  CALL cls
  
  ; Print header
  LD HL, header_text
  CALL print_string
  
  ; Initialize block
  CALL init_block
  
  ; Start mining
  JP mine_loop
```

### 6.2 Mining Loop (0x4420)

```assembly
mine_loop:
  ; Increment nonce
  INC DE
  
  ; Update block with nonce
  LD (block_nonce), de
  
  ; Calculate hash
  CALL minihash
  
  ; Check against target
  CALL check_target
  JR Z, found_block
  
  ; Update display every 100 hashes
  INC hash_count
  LD A, hash_count
  AND 0x0F        ; Every 16 hashes
  JR NZ, mine_loop
  CALL update_display
  
  JP mine_loop
```

### 6.3 Found Block (0x4480)

```assembly
found_block:
  ; Display success message
  LD HL, success_text
  CALL print_string
  
  ; Show nonce and hash
  CALL display_result
  
  ; Wait for keypress
  CALL wait_key
  
  ; Reset for next block
  CALL init_block
  JP mine_loop
```

## 7. Python Simulator

The simulator (`simulator.py`) provides:

1. **Z80 CPU emulation** - Accurate instruction timing
2. **Memory mapping** - Video RAM, I/O ports
3. **Display rendering** - Terminal-based UI
4. **Performance metrics** - Hash rate, uptime
5. **State save/load** - Snapshot miner state

### 7.1 Simulator Architecture

```python
class Z80CPU:
    # Registers: A, B, C, D, E, H, L, IX, IY, SP, PC
    # Flags: S, Z, H, P/V, N, C
    
class TRS80Memory:
    # 64 KB address space
    # ROM, Video RAM, I/O mapping
    
class Miner:
    # Block management
    # Hash calculation
    # Display updates
```

## 8. Testing Strategy

### 8.1 Unit Tests

- Hash function correctness
- Display routine output
- Nonce increment logic

### 8.2 Integration Tests

- Full mining cycle (find valid block)
- Display update frequency
- Memory boundary checks

### 8.3 Hardware Testing

- Run on actual TRS-80 emulator (TRS80GP)
- Verify cassette save/load
- Measure real hash rate

## 9. Optimization Techniques

### 9.1 Cycle Counting

```
Instruction          Cycles    Usage
------------------------------------
INC DE               4         Nonce increment
LD (addr), DE        20        Store nonce
CALL minihash        ~1000     Hash calculation
XOR A                4         Clear accumulator
ADD A, B             4         Hash mixing
```

Total per hash: ~1100 cycles
Hashes per second: 1.77 MHz / 1100 ≈ 1600 H/s (theoretical)
Real-world: ~100-200 H/s (with display updates)

### 9.2 Memory Optimization

- Use registers over memory where possible
- Reuse memory regions for different purposes
- Avoid recursion (limited stack)

### 9.3 Display Optimization

- Only update changed characters
- Use direct video RAM writes
- Minimize display updates during mining

## 10. Future Enhancements

1. **Network mode** - Connect via 300 baud modem (if available)
2. **Multi-block** - Queue multiple blocks
3. **Statistics** - Track blocks found, uptime
4. **Overclock mode** - Push Z80 beyond 1.77 MHz (emulator only)

## 11. References

- Z80 Instruction Set: https://z80.info/
- TRS-80 Technical Manual: https://www.trs-80.com/
- MiniHash design: Original for this project

---

*Designed for the TRS-80 Model I, 1977*
*Recreated with love in 2026*
