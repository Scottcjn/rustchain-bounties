# ZX Spectrum RustChain Miner - Implementation Plan

## Project Overview

**Goal:** Port RustChain miner to ZX Spectrum (1982)  
**Target Hardware:** Z80 CPU @ 3.5469 MHz, 48 KB RAM  
**Bounty:** 100 RTC (3.5× antiquity multiplier)  
**Wallet:** RTC4325af95d26d59c3ef025963656d22af638bb96b  
**Issue:** #420

---

## Phase 1: Development Environment Setup (Week 1-2)

### 1.1 Install Toolchain

**Option A: z88dk (Recommended - C with Z80 optimization)**

```powershell
# Windows (download installer)
# https://z88dk.org/site/

# Or build from source
git clone https://github.com/z88dk/z88dk.git
cd z88dk
./build.sh
```

**Option B: Pure Assembly (Pasmo)**

```powershell
# Download Pasmo
# http://pasmo.speccy.org/

choco install pasmo  # Or download manually
```

**Option C: SjASMPlus (Modern Z80 assembler)**

```powershell
# Download from GitHub
# https://github.com/z00m128/sjasmplus
```

### 1.2 Emulator Setup

```powershell
# Fuse (Free Unix Spectrum Emulator)
choco install fuse-emulator

# Or download from:
# https://fuse-emulator.sourceforge.io/
```

### 1.3 Project Structure

```
zx-spectrum-miner/
├── src/
│   ├── main.c              # Entry point (if using z88dk)
│   ├── main.asm            # Entry point (if using assembly)
│   ├── miner.c / miner.asm # Core miner logic
│   ├── network.c / network.asm  # Serial communication
│   ├── fingerprint.asm     # Hardware fingerprinting (assembly required)
│   ├── sha256.asm          # SHA-256 implementation
│   ├── ui.c / ui.asm       # User interface
│   └── json.asm            # Minimal JSON builder
├── include/
│   ├── zx.inc              # ZX Spectrum hardware defines
│   └── serial.inc          # Serial protocol constants
├── tools/
│   ├── build.bat           # Build script
│   └── test_serial.py      # PC bridge for testing
├── docs/
│   ├── wiring.md           # Serial interface wiring
│   └── protocol.md         # Communication protocol
├── Makefile
├── README.md
└── miner.tap               # Output (TAP file for cassette)
    miner.pzx               # Or PZX file
```

### 1.4 Hello World Test

**Using z88dk (C):**

```c
// src/main.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <conio.h>

void main(void) {
    // Clear screen
    clrscr();
    
    // Set colors (INK, PAPER, BRIGHT)
    // Spectrum colors: 0=black, 1=blue, 2=red, 3=magenta, 
    //                  4=green, 5=cyan, 6=yellow, 7=white
    
    printf("\n\n");
    printf("  +----------------------------------+\n");
    printf("  |  RUSTCHAIN MINER v0.1 - ZX SPEC  |\n");
    printf("  +----------------------------------+\n");
    printf("  |  Development Test OK             |\n");
    printf("  |  Z80 @ 3.5 MHz                   |\n");
    printf("  |  48 KB RAM                       |\n");
    printf("  |                                  |\n");
    printf("  |  Press any key to exit...        |\n");
    printf("  +----------------------------------+\n");
    
    getchar();  // Wait for keypress
}
```

**Build:**
```bash
zcc +zx -vn -O3 -o miner.tap src/main.c
```

**Load in Fuse:**
- File → Open → Select miner.tap
- Machine → Start

**Pure Assembly Version:**

```assembly
; src/main.asm
    OUTPUT miner.tap
    ORG $8000           ; Load address

start:
    ; Clear screen (call BASIC CLS)
    LD A, $0E           ; PRINT token
    RST $10
    LD A, $0C           ; CLS token
    RST $10
    
    ; Print header
    LD HL, header
    CALL print_string
    
    ; Wait for keypress
    CALL wait_key
    
    ; Exit
    RST $38             ; Restart

print_string:
    LD A, (HL)
    OR A
    RET Z
    RST $10             ; PRINT char
    INC HL
    JR print_string

wait_key:
    ; Simple keyboard wait
    ; Read keyboard matrix via $FE
.wait
    LD A, $FE
    IN A, ($FE)
    ; Check for keypress (simplified)
    JR Z, .wait
    RET

header:
    DEFM "  RUSTCHAIN MINER v0.1 - ZX SPEC", 13
    DEFM "  Development Test OK", 13
    DEFM "  Press any key...", 13
    DEFM 0

    END start
```

**Build:**
```bash
pasmo main.asm miner.tap
```

---

## Phase 2: Serial Communication (Week 3-6)

### 2.1 Interface Selection

**Recommended: ZXpand+**

- Modern SD card + serial interface
- Well-documented SPI interface
- Cost: ~$60-80
- URL: https://www.zxpand.com/

**Budget: Custom Serial via Edge Connector**

```
ZX Spectrum Edge Connector Pinout:
Pin 1: +5V (red)
Pin 2: 0V (black)
Pin 3: +5V
Pin 4: 0V
Pin 5: Reset
Pin 6: IORQ (I/O request)
Pin 7-14: Data bus D0-D7
Pin 15: R/W
Pin 16: A0
Pin 17: A1
Pin 18: A2
Pin 19: A3
Pin 20: A4
Pin 21: A5
Pin 22: A6
Pin 23: A7
Pin 24: A8
Pin 25: A9
Pin 26: A10
Pin 27: A11
Pin 28: A12
Pin 29: A13
Pin 30: A14
Pin 31: A15
Pin 32: MREQ
Pin 33: ROMCS
Pin 34: INT
Pin 35: NMI
Pin 36: WAIT
Pin 37: BUSRQ
Pin 38: BUSAK
Pin 39: A16 (128K only)
Pin 40: A17 (128K only)

Custom Serial (bit-banged via I/O):
- Use any available I/O port
- Bit-bang TX/RX via ULA port ($FE)
- Or use GPIO expander (e.g., 74HC595)
```

**Cheapest: Arduino/ESP32 Bridge**

```
ZX Spectrum ←→ Arduino/ESP32 ←→ USB ←→ PC
   (Serial)       (Serial)      (USB)   (Bridge)
```

### 2.2 ZXpand+ SPI Interface

```assembly
; ZXpand+ uses SPI via I/O ports
; Port $E3: Control register
; Port $E4: Data register

; ZXpand+ Control bits:
; Bit 7: SS (slave select) - active low
; Bit 6: MOSI
; Bit 5: MISO (input)
; Bit 4: SCK (clock)

; Initialize SPI
zxpsnd_init:
    ; Set SS high (deselect)
    LD A, $80
    OUT ($E3), A
    RET

; Send byte via SPI
zxpsnd_send:
    LD B, 8           ; 8 bits
    LD A, (tx_byte)
.send_bit
    RLA               ; Rotate left, bit 7 -> carry
    ; Set MOSI based on carry
    JR C, .mosi_high
    LD C, $40         ; MOSI low
    JR .set_mosi
.mosi_high
    LD C, $C0         ; MOSI high
.set_mosi
    ; Pulse clock
    OUT ($E3), C      ; MOSI set, SCK low
    LD A, $D0         ; SCK high
    OUT ($E3), A
    DJNZ .send_bit
    
    ; Deselect
    LD A, $80
    OUT ($E3), A
    RET

; Receive byte via SPI
zxpsnd_recv:
    LD B, 8
    LD A, 0
.recv_bit
    ; Clock pulse
    LD C, $10         ; SCK low
    OUT ($E3), C
    LD C, $50         ; SCK high
    OUT ($E3), C
    
    ; Read MISO
    IN A, ($E4)       ; Read data register
    RLA               ; Shift into A
    DJNZ .recv_bit
    RET
```

### 2.3 Bit-Banged Serial (ULA Port)

```assembly
; Bit-banged serial via ULA port ($FE)
; Uses EAR/MIC bits for TX/RX

; Baud rate: 9600 (104μs per bit)
; At 3.5469 MHz: ~369 T-states per bit

BAUD_DELAY equ 369

; Transmit byte
serial_tx:
    LD B, 8
    LD A, (tx_data)
    
    ; Start bit (low)
    LD A, 0
    OUT ($FE), A
    CALL delay_baud
    
    ; Data bits
.tx_loop
    RRA               ; Bit 0 -> carry
    JR C, .tx_one
    LD A, 0           ; Send 0
    OUT ($FE), A
    JR .tx_delay
.tx_one
    LD A, 1           ; Send 1
    OUT ($FE), A
.tx_delay
    CALL delay_baud
    DJNZ .tx_loop
    
    ; Stop bit (high)
    LD A, 1
    OUT ($FE), A
    CALL delay_baud
    
    RET

; Receive byte
serial_rx:
    ; Wait for start bit
.wait_start
    IN A, ($FE)
    AND $08           ; EAR bit
    JR NZ, .wait_start
    
    ; Wait half baud (sample in middle)
    CALL delay_half_baud
    
    ; Sample 8 bits
    LD B, 8
    LD C, 0           ; Result byte
.rx_loop
    CALL delay_baud
    IN A, ($FE)
    AND $08
    RR C              ; Shift into C
    DJNZ .rx_loop
    
    ; Wait for stop bit
    CALL delay_baud
    
    LD A, C
    RET

; Delay routines (timing-critical!)
delay_baud:
    ; ~369 T-states
    ; Calibrate for exact baud rate
    PUSH BC
    LD BC, BAUD_DELAY
.delay_loop
    DEC BC
    LD A, B
    OR C
    JR NZ, .delay_loop
    POP BC
    RET

delay_half_baud:
    ; ~184 T-states
    PUSH BC
    LD BC, BAUD_DELAY / 2
    ; ... same as above
    POP BC
    RET
```

### 2.4 PC Bridge (Python)

```python
# tools/pc_bridge.py
import serial
import json
import requests
import time

SERIAL_PORT = 'COM3'
BAUD_RATE = 9600
RUSTCHAIN_API = 'https://rustchain.org/api'

class ZXBridge:
    def __init__(self, port=SERIAL_PORT, baud=BAUD_RATE):
        self.ser = serial.Serial(port, baud, timeout=1)
        print(f"Connected to {port} at {baud} baud")
    
    def read_line(self):
        """Read line from ZX Spectrum"""
        line = self.ser.readline().decode('ascii', errors='ignore').strip()
        return line
    
    def write_line(self, line):
        """Write line to ZX Spectrum"""
        self.ser.write(f"{line}\n".encode('ascii'))
    
    def forward_attestation(self, data):
        """Forward attestation to RustChain"""
        try:
            response = requests.post(
                f"{RUSTCHAIN_API}/attest",
                json=data,
                timeout=30
            )
            return response.json()
        except Exception as e:
            print(f"API Error: {e}")
            return {"success": False, "error": str(e)}
    
    def run(self):
        """Main bridge loop"""
        print("ZX Spectrum Bridge running...")
        print("Waiting for attestations...")
        
        while True:
            try:
                line = self.read_line()
                
                if line.startswith('ATTEST:'):
                    print(f"Received attestation from ZX Spectrum")
                    data = json.loads(line[7:])
                    
                    # Forward to RustChain
                    result = self.forward_attestation(data)
                    
                    # Send response back
                    if result.get('success'):
                        self.write_line(f"ACK:OK:{result.get('reward', 0)}")
                        print(f"Success! Reward: {result.get('reward')} RTC")
                    else:
                        self.write_line(f"ACK:FAIL:{result.get('error', 'Unknown')}")
                        print(f"Failed: {result.get('error')}")
                
                elif line.startswith('STATUS:'):
                    print(f"ZX Status: {line[7:]}")
                
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                time.sleep(1)
            except json.JSONDecodeError as e:
                print(f"JSON error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(1)

if __name__ == '__main__':
    bridge = ZXBridge()
    bridge.run()
```

---

## Phase 3: Hardware Fingerprinting (Week 7-10)

### 3.1 ROM Checksum

```assembly
; Calculate ROM checksum for fingerprint
; Different ROM versions = different checksums

rom_checksum:
    ; 48K Spectrum: ROM at 0x0000-0xBFFF (48 KB)
    ; 16K Spectrum: ROM at 0x0000-0x3FFF (16 KB)
    
    LD HL, $0000      ; Start address
    LD DE, $C000      ; End address (48K)
    LD BC, $0000      ; Checksum accumulator
    
.calc_loop
    LD A, (HL)
    ADD C
    LD C, A
    JR NC, .no_carry
    INC B
.no_carry
    INC HL
    
    ; Check if done
    LD A, H
    CP D
    JR NZ, .calc_loop
    LD A, L
    CP E
    JR NZ, .calc_loop
    
    ; BC = checksum
    LD (rom_checksum_lo), C
    LD (rom_checksum_hi), B
    RET
```

### 3.2 ULA Contention Timing

```assembly
; Measure ULA contention variance
; Real hardware: CPU slows during display period
; Emulators: often perfect timing

ula_timing_fingerprint:
    DI              ; Disable interrupts
    
    ; Wait for display period (lines 0-191)
    ; This is approximate - ULA timing is complex
    
    ; Measure time to execute fixed code
    LD HL, $0000
    LD BC, 1000
    
.measure1
    INC HL
    DEC BC
    LD A, B
    OR C
    JR NZ, .measure1
    
    LD (timing1_lo), L
    LD (timing1_hi), H
    
    ; Small delay
    CALL delay_short
    
    ; Measure again
    LD HL, $0000
    LD BC, 1000
    
.measure2
    INC HL
    DEC BC
    LD A, B
    OR C
    JR NZ, .measure2
    
    LD (timing2_lo), L
    LD (timing2_hi), H
    
    EI
    
    ; Calculate variance (timing2 - timing1)
    ; Variance indicates real hardware (ULA contention)
    RET
```

### 3.3 DRAM Refresh Timing

```assembly
; Z80 performs DRAM refresh every instruction
; Real hardware has analog variance in refresh timing

dram_refresh_fingerprint:
    DI
    
    ; Execute NOPs and measure time
    ; Refresh happens during each instruction
    ; Variance in timing = real hardware
    
    LD BC, 500
    
.refresh_loop
    NOP
    NOP
    NOP
    DEC BC
    LD A, B
    OR C
    JR NZ, .refresh_loop
    
    ; Measure total time (via external counter or cycle count)
    ; Variance from expected = fingerprint
    
    EI
    RET
```

### 3.4 Combined Fingerprint Structure

```assembly
; Fingerprint structure (stored in RAM)
; Offset  Size  Field
; 0       16    device_arch ("zx_z80\0...")
; 16      16    device_family ("zx_spectrum\0...")
; 32      4     cpu_speed (3546900)
; 36      2     total_ram_kb (48)
; 38      4     rom_checksum
; 42      4     ula_fingerprint
; 46      4     dram_fingerprint
; 50      32    wallet_address
; Total: 82 bytes

fingerprint_buffer: DEFS 82

build_fingerprint:
    LD HL, fingerprint_buffer
    
    ; device_arch = "zx_z80"
    LD DE, arch_str
    CALL copy_string
    
    ; device_family = "zx_spectrum"
    LD DE, family_str
    CALL copy_string
    
    ; cpu_speed = 3546900
    LD DE, 3546900
    ; Store as 4-byte little-endian
    
    ; total_ram_kb = 48
    LD (HL), 48
    INC HL
    
    ; Calculate ROM checksum
    CALL rom_checksum
    ; Store checksum
    
    ; Measure ULA timing
    CALL ula_timing_fingerprint
    ; Store result
    
    ; Measure DRAM timing
    CALL dram_refresh_fingerprint
    ; Store result
    
    RET

arch_str: DEFM "zx_z80", 0
family_str: DEFM "zx_spectrum", 0
```

---

## Phase 4: SHA-256 Implementation (Week 11-14)

### 4.1 Z80 SHA-256 Overview

**Challenges:**
- SHA-256 requires 64 rounds × 64 operations = 4096 operations
- Z80 @ 3.5 MHz ≈ 1 MIPS effective
- Estimated time: 5-10 seconds per hash
- RAM constraint: ~300 bytes working memory

**Optimization Strategies:**
1. Unroll critical loops
2. Use registers efficiently (Z80 has limited registers)
3. Precompute constants in ROM
4. Minimize memory access (slow on Spectrum)

### 4.2 SHA-256 Constants (ROM)

```assembly
; SHA-256 round constants (first 16 of 64)
; Store in ROM bank or high memory

sha256_k:
    DEFM $428A2F98, $71374491, $B5C0FBCF, $E9B5DBA5
    DEFM $3956C25B, $59F111F1, $923F82A4, $AB1C5ED5
    DEFM $D807AA98, $12835B01, $243185BE, $550C7DC3
    DEFM $72BE5D74, $80DEB1FE, $9BDC06A7, $C19BF174
    ; ... (64 total)
```

### 4.3 SHA-256 Core (Simplified)

```assembly
; SHA-256 implementation for Z80
; This is a simplified version - full implementation is ~2-3 KB

sha256_init:
    ; Initialize hash values (first 32 bits of fractional parts of sqrt of first 8 primes)
    LD (h0), $6A09E667
    LD (h1), $BB67AE85
    LD (h2), $3C6EF372
    LD (h3), $A54FF53A
    LD (h4), $510E527F
    LD (h5), $9B05688C
    LD (h6), $1F83D9AB
    LD (h7), $5BE0CD19
    RET

sha256_update:
    ; Process message block
    ; Input: HL points to 64-byte message block
    
    ; 1. Prepare message schedule (16 words → 64 words)
    ; 2. Initialize working variables
    ; 3. 64 rounds of mixing
    ; 4. Add to hash state
    
    ; This is the performance-critical section
    ; Expect ~5-10 seconds on real hardware
    
    CALL prepare_schedule
    CALL sha256_rounds
    CALL update_state
    
    RET

sha256_final:
    ; Pad message and process final block
    ; Output 32-byte hash
    
    RET
```

### 4.4 Performance Optimization

```assembly
; Optimized rotation macros for Z80

; ROTR(x, n) for 32-bit value
; Z80 is 8-bit, so this requires multiple operations

macro ROTR32_2
    ; Rotate right 2 bits (32-bit)
    ; Input: DEHL = 32-bit value
    ; Output: DEHL = rotated value
    
    ; This is slow on Z80 - consider lookup tables
    ; Or precompute in C and embed constants
endm

; Consider assembly optimization:
; - Use IX/IY registers for pointers
; - Minimize memory access
; - Unroll loops where possible
; - Use shadow registers (EXX) for context switching
```

---

## Phase 5: Miner Integration (Week 15-18)

### 5.1 Attestation Protocol

```assembly
; Attestation state machine

STATE_IDLE      EQU 0
STATE_CHALLENGE EQU 1
STATE_COMPUTE   EQU 2
STATE_SEND      EQU 3
STATE_WAIT      EQU 4

attestation_loop:
    LD A, STATE_IDLE
    LD (attestation_state), A
    
.main_loop
    LD A, (attestation_state)
    
    CP STATE_IDLE
    JR Z, .idle
    
    CP STATE_CHALLENGE
    JR Z, .challenge
    
    CP STATE_COMPUTE
    JR Z, .compute
    
    CP STATE_SEND
    JR Z, .send
    
    CP STATE_WAIT
    JR Z, .wait
    
.idle
    ; Wait for challenge from PC bridge
    CALL serial_rx
    ; Parse "CHALLENGE:<nonce>"
    JR .main_loop
    
.challenge
    ; Received challenge, compute response
    CALL sha256_update
    LD A, STATE_COMPUTE
    LD (attestation_state), A
    JR .main_loop
    
.compute
    ; SHA-256 computation in progress
    ; This takes 5-10 seconds
    CALL sha256_final
    LD A, STATE_SEND
    LD (attestation_state), A
    JR .main_loop
    
.send
    ; Send "ATTEST:<hash>" to PC bridge
    CALL build_attestation_json
    CALL serial_tx_string
    LD A, STATE_WAIT
    LD (attestation_state), A
    JR .main_loop
    
.wait
    ; Wait for ACK (10-minute epoch)
    ; Display countdown
    CALL update_display
    CALL check_epoch_complete
    JR Z, .idle  ; Start new epoch
    JR .main_loop
```

### 5.2 JSON Builder

```assembly
; Minimal JSON builder for attestation
; Output: {"device_arch":"zx_z80",...,"wallet":"RTC..."}

build_attestation_json:
    LD HL, json_buffer
    
    ; Start object
    LD (HL), '{'
    INC HL
    
    ; device_arch
    LD DE, arch_json
    CALL copy_string_hl
    
    ; ... add all fields ...
    
    ; End object
    LD (HL), '}'
    INC HL
    LD (HL), 0  ; Null terminator
    
    RET

arch_json: DEFM '"device_arch":"zx_z80",'
```

---

## Phase 6: User Interface (Week 19-20)

### 6.1 Text Display

```assembly
; Simple text UI using Spectrum BASIC printer

ui_init:
    ; Clear screen
    LD A, $0E       ; PRINT token
    RST $10
    LD A, $0C       ; CLS token
    RST $10
    
    ; Set colors (optional)
    ; INK 7 (white), PAPER 0 (black)
    
    RET

ui_show_status:
    ; Print status at fixed position
    ; Use PRINT AT y,x
    LD A, $10       ; PRINT AT token
    RST $10
    LD A, 5         ; Row
    RST $10
    LD A, 2         ; Column
    RST $10
    
    ; Print status string
    LD HL, (status_string)
    CALL print_string
    
    RET

ui_show_countdown:
    ; Display epoch countdown timer
    ; Format: MM:SS remaining
    
    ; Calculate minutes and seconds
    ; Print at fixed position
    
    RET
```

### 6.2 Keyboard Input

```assembly
; Read Spectrum keyboard matrix
; Keyboard is scanned via ULA port ($FE)

; Keyboard matrix layout:
; 8 rows × 5 columns
; Read row by setting port bits, read column from data

read_keyboard:
    ; Scan keyboard matrix
    ; Return key code in A (0 = no key)
    
    ; Simplified version - check specific keys
    ; 1=START, 2=STOP, 3=QUIT
    
    LD A, $FE       ; Select row 0 (keys 1-5: 1,2,3,4,5)
    OUT ($FE), A
    IN A, ($FE)
    
    ; Check bits for pressed keys
    ; Bit 0 = key 1, Bit 1 = key 2, etc.
    
    RET
```

---

## Phase 7: Testing & Documentation (Week 21-22)

### 7.1 Testing Checklist

- [ ] Build succeeds with z88dk or Pasmo
- [ ] Runs in Fuse emulator
- [ ] Serial communication works (loopback test)
- [ ] PC bridge connects and forwards data
- [ ] Fingerprint collection works
- [ ] SHA-256 produces correct hashes (test vectors)
- [ ] Full attestation cycle completes
- [ ] **Test on real ZX Spectrum hardware** (CRITICAL)
- [ ] Anti-emulation detects Fuse
- [ ] Photo/video proof captured
- [ ] Attestation visible on rustchain.org

### 7.2 Documentation

Create README.md with:
- Build instructions (z88dk setup)
- Hardware requirements (ZXpand+ or custom serial)
- Wiring diagram
- Usage instructions (LOAD "", RUN)
- Troubleshooting

### 7.3 Proof Collection

1. **Photo:** ZX Spectrum running miner with timestamp
2. **Video:** 30+ second attestation cycle
3. **Screenshot:** rustchain.org/api/miners showing ZX Spectrum
4. **Hardware info:** ROM checksum, ULA fingerprint values
5. **Wallet address:** RTC4325af95d26d59c3ef025963656d22af638bb96b

---

## Memory Optimization

### RAM Layout (48K Model)

```
$5C00-$7FFF: Network stack, buffers (~8 KB)
$8000-$9FFF: Miner runtime (~8 KB)
$A000-$AFFF: Attestation data, JSON (~4 KB)
$B000-$BFFF: Stack, variables (~4 KB)
$C000-$FFFF: Free / SHA-256 workspace (~16 KB)
```

### Use VRAM for Computation

```assembly
; When display is off, VRAM ($4000-$5AFF) can be used for computation
; Saves WRAM for other purposes

; Disable display:
; Set bit 5 of $FE (border color doesn't matter if display off)
```

---

## Anti-Emulation Techniques

```assembly
detect_emulator:
    ; 1. Timing variance test
    CALL measure_timing_variance
    LD A, (timing_variance)
    OR A
    JR Z, .emulator_detected  ; Perfect timing = emulator
    
    ; 2. Undocumented Z80 flags test
    ; Emulators often get these wrong
    LD A, $FF
    INC A
    ; Check flags register (push AF, pop IX, etc.)
    
    ; 3. ULA contention test
    ; Emulators often don't simulate this accurately
    
    ; 4. DRAM refresh timing
    ; Real hardware has analog variance
    
    XOR A  ; Real hardware
    RET
    
.emulator_detected
    LD A, 1  ; Emulator
    RET
```

---

## Build System

### Makefile (or build.bat for Windows)

```makefile
# Makefile for ZX Spectrum Miner

CC = zcc
AS = pasmo

CFLAGS = +zx -vn -O3
ASFLAGS = 

TARGET = miner.tap

all: $(TARGET)

$(TARGET): src/main.c src/miner.c src/network.c
	$(CC) $(CFLAGS) -o $@ $^

# Or for pure assembly:
miner_asm.tap: src/main.asm src/miner.asm
	$(AS) $< $@

clean:
	del *.tap
	del *.pxz
	del *.o

.PHONY: all clean
```

### Windows Build Script (build.bat)

```batch
@echo off
echo Building ZX Spectrum Miner...

REM Using z88dk
zcc +zx -vn -O3 -o miner.tap src/main.c src/miner.c src/network.c

if exist miner.tap (
    echo Build successful!
    echo Load in Fuse: File > Open > miner.tap
) else (
    echo Build failed!
)
```

---

## Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| 1. Dev Environment | Week 1-2 | Toolchain, emulator, hello world |
| 2. Serial Comm | Week 3-6 | Serial driver + PC bridge |
| 3. Fingerprinting | Week 7-10 | Hardware ID, anti-emulation |
| 4. SHA-256 | Week 11-14 | Z80-optimized implementation |
| 5. Miner Integration | Week 15-18 | Attestation protocol |
| 6. UI | Week 19-20 | Display, keyboard input |
| 7. Testing/Docs | Week 21-22 | Real hardware, proof |
| **Total** | **22 weeks** | **~5-6 months** |

---

## Budget

| Item | Cost (USD) |
|------|------------|
| ZX Spectrum 48K | $50-150 |
| ZXpand+ Interface | $60-80 |
| SD Card | $10 |
| **Total** | **$120-240** |

**Budget Alternative:**
| Item | Cost (USD) |
|------|------------|
| ZX Spectrum Clone | $30-80 |
| Arduino/ESP32 Bridge | $15-25 |
| Custom cable | $5-10 |
| **Total** | **$50-115** |

---

## Risk Mitigation

1. **SHA-256 too slow:** Optimize with assembly, use lookup tables, or simplify hash for fingerprinting
2. **No serial interface:** Build custom bit-banged serial via edge connector
3. **Memory too constrained:** Use 128K model, or bank switching
4. **Timing issues:** Use cycle-exact code, disable interrupts during critical sections
5. **Hardware unavailable:** Borrow from retro computing groups, or use clone

---

## Success Criteria

- [ ] Real ZX Spectrum hardware successfully attests to RustChain
- [ ] Attestation visible on rustchain.org/api/miners
- [ ] Source code published on GitHub (MIT license)
- [ ] Build instructions documented
- [ ] Video proof submitted
- [ ] Bounty claimed to wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b

---

*The machine that launched the UK home computer revolution, now mining cryptocurrency. If you can make a ZX Spectrum attest to RustChain, you've earned every satoshi of that 3.5× multiplier.*

**Good luck, and happy coding!**
