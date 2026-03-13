# [BOUNTY] Port RustChain Miner to ZX Spectrum — 100 RTC

**Issue**: #420  
**Difficulty**: Extreme  
**Estimated Effort**: 2-4 months for experienced Z80 developer  
**Reward**: 100 RTC ($10 USD)  
**Multiplier**: 3.5× antiquity multiplier  
**Status**: Open

---

## Overview

Port the RustChain miner to the ZX Spectrum (1982), powered by the Z80 CPU at 3.5 MHz with 16-48 KB RAM. This is an iconic Proof-of-Antiquity mining platform from the golden age of home computing.

The ZX Spectrum was Sir Clive Sinclair's revolutionary home computer that brought computing to the masses in the UK and Europe. Successfully mining on this hardware demonstrates that authentic 8-bit machines can participate in the RustChain network.

---

## Why ZX Spectrum?

| Feature | Specification | Significance |
|---------|--------------|--------------|
| **Year** | 1982 | 44 years old (2026) |
| **CPU** | Z80 @ 3.5469 MHz | Classic 8-bit processor |
| **RAM** | 16 KB / 48 KB / 128 KB | Extremely constrained |
| **OS** | Sinclair BASIC (in ROM) | No OS, direct hardware access |
| **Network** | None (requires expansion) | Must add serial/ethernet interface |
| **Power** | 5V DC, ~5W | Low power consumption |

### The Challenge

- **RAM constraint**: 48 KB must hold everything (OS, network, miner, data)
- **No networking**: Requires custom interface (serial, ethernet, or WiFi)
- **Z80 architecture**: Requires assembly or cross-compiled C
- **Timing constraints**: Precise timing for any I/O
- **Video interference**: ULA contention slows CPU during display

---

## Network Architecture

### Option 1: Serial Interface (Recommended)

```
┌─────────────────┐     Serial      ┌──────────────┐     HTTP      ┌─────────────┐
│ ZX Spectrum     │ ◄─────────────► │ PC Bridge    │ ◄───────────► │ RustChain   │
│ (Miner ROM)     │   (9600-19200)  │ (Python)     │   (TCP/IP)    │ Network     │
└─────────────────┘                 └──────────────┘               └─────────────┘
     1982                                2026                         Cloud
```

**Interface Options:**
- **ZX Serial Interface** (original Sinclair) - rare, expensive
- **ZXpand+** - modern SD/serial interface
- **Custom GPIO** - Raspberry Pi Pico via edge connector
- **DivMMC Future** - SD card + serial interface

### Option 2: Ethernet Interface

```
┌─────────────────┐     SPI         ┌──────────────┐     HTTP      ┌─────────────┐
│ ZX Spectrum     │ ◄─────────────► │ ZXpand+ /    │ ◄───────────► │ RustChain   │
│ (Miner ROM)     │   (1-2 MHz)     │ DivMMC       │   (Ethernet)  │ Network     │
└─────────────────┘                 └──────────────┘               └─────────────┘
```

**The ZX Spectrum is the miner** — it collects hardware fingerprints and builds attestations. The bridge is just a network proxy.

---

## Hardware Requirements

| Component | Source | Cost |
|-----------|--------|------|
| ZX Spectrum 48K | eBay / Retro stores | $50-150 |
| Interface (ZXpand+ / DivMMC) | eBay / SpecNext | $40-80 |
| SD Card (for storage) | Any | $10 |
| Power Supply | Included / eBay | $10-20 |
| **Total** | | **~$110-260** |

### Budget Alternative

- **ZX Spectrum Clone** (Timex Sinclair, Didaktik) - $30-80
- **Custom Serial Interface** (Arduino/ESP32) - $15-25
- **Total**: ~$50-110

---

## Technical Implementation

### 1. Development Environment

**Toolchain:**

```bash
# Z80 Assembler (z88dk - recommended)
# Download: https://z88dk.org/site/

# Or Pasmo (simple Z80 assembler)
# Download: http://pasmo.speccy.org/

# Emulator: Fuse
# Download: https://fuse-emulator.sourceforge.io/
```

**Build:**

```bash
# Using z88dk
zcc +zx -vn -O3 -o miner.tap miner.c
zcc +zx -vn -O3 -o miner.pzx miner.c

# Or pure assembly
pasmo miner.asm miner.tap
```

### 2. Serial Communication

**ZX Spectrum ULA Port (for custom serial):**

```assembly
; ZX Spectrum edge connector pinout
; Pin 3: +5V
; Pin 4: 0V (GND)
; Pin 6: IORQ (I/O request)
; Custom serial via bit-banging

; Bit-banged serial transmit
serial_tx:
    ld b, 8           ; 8 bits
    ld a, (data_byte)
.tx_bit
    rra               ; Rotate right, bit 0 -> carry
    jr c, .tx_high
    ; Send low bit
    ld a, 0
    out (0xFE), a     ; EAR = 0
    jr .tx_delay
.tx_high
    ld a, 1
    out (0xFE), a     ; EAR = 1
.tx_delay
    ; Delay for baud rate (e.g., 9600 = 104μs per bit)
    ; At 3.5 MHz, ~366 T-states per bit
    call delay_366
    djnz .tx_bit
    ret
```

**Using ZXpand+ (SPI):**

```assembly
; ZXpand+ uses SPI via I/O ports
; Port $E3: Control
; Port $E4: Data

zxpsnd_send:
    ld a, (data_byte)
    out ($E4), a      ; Send byte via SPI
    ret
```

### 3. Hardware Fingerprinting

```c
typedef struct {
    char device_arch[16];      // "zx_z80"
    char device_family[16];    // "zx_spectrum"
    uint32_t cpu_speed;        // 3546900 (3.5469 MHz)
    uint16_t total_ram_kb;     // 16, 48, or 128
    uint32_t rom_checksum;     // ROM checksum
    uint32_t ula_fingerprint;  // ULA timing variance
    uint32_t drampattern_fp;   // DRAM refresh timing
} ZXSpectrumFingerprint;
```

**Fingerprint Sources:**

1. **ROM Checksum**: Different ROM versions (16K/48K/128K) have different checksums
2. **ULA Timing**: ULA contention causes CPU slowdowns during display - varies per hardware
3. **DRAM Refresh**: Z80 DRAM refresh timing has analog variance
4. **Crystal Variance**: Actual CPU clock varies slightly (3.5469 MHz ± tolerance)

### 4. ROM Checksum Implementation

```assembly
; Calculate 48K ROM checksum (0x0000-0xBFFF)
rom_checksum:
    ld hl, $0000      ; Start of ROM
    ld de, $C000      ; End of ROM (48K)
    ld bc, $0000      ; Accumulator
    
.calc_loop
    ld a, (hl)
    add c
    ld c, a
    jr nc, .no_carry
    inc b
.no_carry
    inc hl
    ld a, h
    cp d
    jr nz, .calc_loop
    ld a, l
    cp e
    jr nz, .calc_loop
    
    ; BC now contains checksum
    ld (checksum_hi), b
    ld (checksum_lo), c
    ret
```

### 5. ULA Timing Fingerprint

```assembly
; Measure ULA contention timing
; CPU slows during display period (lines 0-191)
ula_fingerprint:
    ; Disable interrupts for precise timing
    di
    
    ; Wait for specific raster line
.wait_raster
    in a, ($FE)       ; Read keyboard/ULA
    ; Timing varies based on ULA state
    
    ; Measure time to execute fixed code during vs outside display
    ; Real hardware: varies due to ULA contention
    ; Emulators: often perfect timing
    
    ei
    ret
```

### 6. Anti-Emulation

Detect Fuse/ZEsarUx emulators:

```assembly
detect_emulator:
    ; Emulators often have:
    ; 1. Perfect timing (no ULA contention variance)
    ; 2. Fixed values for undocumented Z80 registers
    ; 3. No DRAM refresh timing jitter
    
    ; Test undocumented Z80 flags
    ld a, $FF
    inc a             ; Should set flags in specific way
    ; Emulators may get flags wrong
    
    ; Test timing jitter
    call measure_timing_variance
    ; Real hardware: variance > 0
    ; Emulators: variance = 0 (or very low)
    
    ret
```

### 7. PC Bridge (Python)

```python
import serial
import requests
import time

ser = serial.Serial('COM3', 9600, timeout=1)

def forward_attestation(data):
    """Forward ZX Spectrum attestation to RustChain"""
    response = requests.post(
        'https://rustchain.org/api/attest',
        json=data,
        timeout=30
    )
    return response.json()

while True:
    try:
        # Read attestation from ZX Spectrum
        line = ser.readline().decode('ascii').strip()
        
        if line.startswith('ATTEST:'):
            data = json.loads(line[7:])
            result = forward_attestation(data)
            
            # Send response back
            ser.write(f"ACK:{result['success']}\n".encode())
            
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(600)  # 10-minute epochs
```

---

## Memory Budget (48K Model)

| Component | Allocation | Address Range |
|-----------|------------|---------------|
| ROM (BASIC + OS) | 16 KB | 0x0000-0x3FFF |
| Display File | 6.5 KB | 0x4000-0x57FF |
| Attributes | 768 B | 0x5800-0x5AFF |
| System Variables | 256 B | 0x5B00-0x5BFF |
| **Available RAM** | **~30 KB** | 0x5C00-0xFFFF |
| - Network stack | ~8 KB | 0x5C00-0x7BFF |
| - Miner runtime | ~10 KB | 0x7C00-0xA3FF |
| - Attestation data | ~2 KB | 0xA400-0xABFF |
| - Stack | ~1 KB | 0xAC00-0xAFFF |
| - **Free** | **~9 KB** | 0xB000-0xFFFF |

### 128K Model

Additional banks via paging:
- Bank 0-7: Additional 48 KB each
- Much more room for network stack and buffers

---

## Power Consumption

| State | Current Draw | Duration |
|-------|-------------|----------|
| Active mining | ~800 mA @ 5V | 1-2 min |
| Display on | ~800 mA | User interaction |
| Display off | ~600 mA | Mining (10 min epoch) |

**Power**: ~4W during operation  
**Note**: Original power supply recommended for stability

---

## User Interface

### Text Mode (32×24)

```
┌────────────────────────────────┐
│ RUSTCHAIN v0.1 - ZX SPECTRUM │
├────────────────────────────────┤
│ STATUS: ATTESTING...           │
│ EPOCH: 00:07:23 REMAINING      │
│ EARNED: 0.0042 RTC             │
│                                │
│ HARDWARE:                      │
│ CPU: Z80 @ 3.5 MHZ             │
│ RAM: 48 KB                     │
│ NET: SERIAL (9600)             │
│ ROM: ISSUE 2 (48K)             │
│                                │
│ [1] START  [2] STOP  [3] QUIT │
└────────────────────────────────┘
```

### Graphics Mode (256×192, attribute colors)

- Retro spectrum colors (bright green on black)
- Simple animated border during mining
- Flashing "ATTESTING" indicator

---

## Implementation Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Dev Setup | Week 1-2 | Toolchain, emulator, test ROM |
| 2. Serial Comm | Week 3-6 | Serial driver + PC bridge |
| 3. Fingerprint | Week 7-10 | Hardware ID, anti-emulation |
| 4. SHA-256 | Week 11-14 | Z80-optimized SHA-256 |
| 5. Miner | Week 15-18 | Attestation protocol |
| 6. UI Polish | Week 19-20 | Display, input handling |
| 7. Testing | Week 21-22 | Real hardware, video proof |

**Total**: 22 weeks (~5-6 months)

---

## Acceptance Criteria

- ✅ Real ZX Spectrum hardware (not emulation)
- ✅ Successful attestation on RustChain network
- ✅ Photo of ZX Spectrum running miner (with timestamp)
- ✅ Video showing full attestation cycle (30+ seconds)
- ✅ Screenshot in `https://rustchain.org/api/miners`
- ✅ All source code on GitHub (MIT license)
- ✅ Build instructions (z88dk setup, TAP/PZX loading)
- ✅ TAP/PZX file for others to test

---

## Claim Instructions

1. Complete the implementation
2. Test on real ZX Spectrum hardware
3. Record photo/video proof
4. Open a PR to `rustchain-bounties` with:
   - Link to your miner repository
   - Photo of hardware running the miner
   - Video of attestation cycle
   - Attestation ID from the network
5. Comment on this issue with:
   - Link to your PR
   - Your RTC wallet address
   - Brief description of your approach

**Bounty Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## Resources

### Development

- [z88dk Z80 Development Kit](https://z88dk.org/site/)
- [Fuse Emulator](https://fuse-emulator.sourceforge.io/)
- [World of Spectrum](https://worldofspectrum.org/)
- [SpeccyWiki](https://spectrumcomputing.co.uk/)
- [ZXpand+ Documentation](https://www.zxpand.com/)

### Hardware Reference

- [Z80 CPU Manual](http://www.z80.info/z80code.htm)
- [ZX Spectrum Hardware Manual](https://spectrumcomputing.co.uk/entry/0000234)
- [ULA Plus Documentation](https://github.com/edmund-ronald/ulaplus)

### Community

- [World of Spectrum Forums](https://worldofspectrum.org/forum/)
- [SpeccyWiki Community](https://spectrumcomputing.co.uk/)
- [Reddit r/zxspectrum](https://reddit.com/r/zxspectrum)

---

## FAQ

**Q: Can I use a ZX Spectrum clone (Timex, Didaktik)?**

A: Yes! Clones with Z80 CPU and compatible architecture qualify for the same multiplier.

**Q: Do I need to implement SHA-256 on the Spectrum?**

A: Yes, but it can be heavily optimized. Z80 is slower than 6502 but has more registers. Expect ~3-8 seconds per hash.

**Q: Can I use assembly?**

A: Highly recommended! Z80 assembly will be much faster and smaller than C. z88dk supports inline assembly.

**Q: Does the PC bridge count as cheating?**

A: No! The Spectrum does the fingerprinting and attestation. The bridge is just a network proxy, like a modem.

**Q: How do I prove it's real hardware?**

A: Photo/video of the Spectrum running the miner. The attestation includes anti-emulation checks that fail on Fuse/ZEsarUx.

**Q: What interface should I use?**

A: ZXpand+ is recommended (modern, well-documented). Custom serial via edge connector is cheaper but requires more work.

---

## Comparison with Other Vintage Bounties

| Hardware | Year | RAM | CPU | Multiplier | Bounty |
|----------|------|-----|-----|------------|--------|
| Apple II (6502) | 1977 | 48 KB | 1 MHz | 4.0× | 150 RTC |
| **ZX Spectrum** | **1982** | **48 KB** | **3.5 MHz** | **3.5×** | **100 RTC** |
| Commodore 64 | 1982 | 64 KB | 1 MHz | 4.0× | 150 RTC |
| Sega Genesis | 1988 | 64 KB | 7.6 MHz | 3.5× | 150 RTC |
| Palm Pilot | 1997 | 512 KB | 16 MHz | 3.0× | 100 RTC |
| Modern x86 | 2026 | 16+ GB | 3+ GHz | 1.0× | 0 RTC |

---

*The machine that defined British home computing, now mining cryptocurrency. If you can make a ZX Spectrum attest to RustChain, you've earned every satoshi of that 3.5× multiplier.*

**Questions?** Comment on this issue or join the [RustChain Discord](https://discord.gg/jMAmHBpXcn).

---

## Appendix: Z80 Assembly Quick Reference

### Essential Instructions

```assembly
; Load
LD A, B        ; A = B
LD A, (HL)     ; A = memory[HL]
LD (HL), A     ; memory[HL] = A

; Arithmetic
ADD A, B       ; A = A + B
ADC A, B       ; A = A + B + carry
SUB B          ; A = A - B
SBC A, B       ; A = A - B - carry

; Logic
AND B          ; A = A & B
OR B           ; A = A | B
XOR B          ; A = A ^ B

; Shift/Rotate
RLA            ; Rotate left through carry
RRA            ; Rotate right through carry
SLA A          ; Shift left arithmetic

; Control
CALL label     ; Call subroutine
RET            ; Return
JP label       ; Jump
JR label       ; Jump relative
DJNZ label     ; Decrement B, jump if not zero

; I/O
IN A, (port)   ; Read from port
OUT (port), A  ; Write to port
```

### ZX Spectrum Memory Map

```
0000-3FFF: ROM (16K)
4000-57FF: Display file (6912 bytes)
5800-5AFF: Color attributes (768 bytes)
5B00-5BFF: System variables
5C00-FFFF: User RAM (42240 bytes in 48K model)
```

### ULA Port ($FE)

```
Bit 0-2: Border color
Bit 3: EAR output (microphone)
Bit 4: EAR input (speaker)
Bit 5: MIC output
Bit 6: MIC input
Bit 7: Not used
```

---

*Good luck, and may your Z80 cycles be ever in your favor!*
