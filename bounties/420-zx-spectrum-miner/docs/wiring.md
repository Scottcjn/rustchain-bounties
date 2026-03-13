# ZX Spectrum Serial Interface Wiring

This document describes how to build a serial interface for the ZX Spectrum to connect it to a PC for RustChain mining.

## Option 1: Arduino/ESP32 Bridge (Recommended for Beginners)

### Components

- Arduino Nano or ESP32 dev board (~$10-15)
- Jumper wires (female-to-female)
- ZX Spectrum edge connector (optional, or use paperclip method)

### Wiring Diagram

```
ZX Spectrum Edge Connector          Arduino Nano
─────────────────────────          ────────────
Pin 1 (+5V)        ───────────────► VCC
Pin 2 (GND)        ───────────────► GND
Pin 4 (GND)        ───────────────► GND (common ground)

Bit-banged TX (via ULA)           D2 (RX)
Bit-banged RX (via ULA)           D3 (TX)
```

### ULA Port Bit-Banging

The ZX Spectrum doesn't have a hardware UART, so we bit-bang serial via the ULA port ($FE):

```
ULA Port ($FE) Bits:
Bit 0-2: Border color
Bit 3: EAR output (microphone input)
Bit 4: EAR input (speaker output)
Bit 5: MIC output
Bit 6: MIC input
Bit 7: Not used

We use:
- MIC output (bit 5) for TX
- EAR input (bit 6) for RX
```

### Arduino Firmware

```cpp
// Arduino Serial Bridge for ZX Spectrum
// Upload this to Arduino Nano

#include <SoftwareSerial.h>

// ZX Spectrum serial (bit-banged via ULA)
SoftwareSerial zxSerial(2, 3);  // RX, TX

// PC serial (hardware UART)
HardwareSerial& pcSerial = Serial;

void setup() {
  // ZX Spectrum: 9600 baud
  zxSerial.begin(9600);
  
  // PC: 115200 baud (for debugging)
  pcSerial.begin(115200);
  
  pcSerial.println("ZX Spectrum Bridge Ready");
}

void loop() {
  // Forward from ZX to PC
  if (zxSerial.available()) {
    char c = zxSerial.read();
    pcSerial.write(c);
  }
  
  // Forward from PC to ZX
  if (pcSerial.available()) {
    char c = pcSerial.read();
    zxSerial.write(c);
  }
}
```

### Connection Method

**Option A: Edge Connector**

Buy a ZX Spectrum edge connector breakout board (~$20) or make one with a PCB.

**Option B: Paperclip Method (Temporary)**

1. Straighten a paperclip
2. Insert into edge connector slot at correct pin
3. Connect jumper wire to paperclip
4. **Be careful not to short adjacent pins!**

## Option 2: ZXpand+ (Recommended for Serious Use)

### Overview

ZXpand+ is a modern SD card + I/O interface for the ZX Spectrum.

- **Cost:** ~$60-80
- **URL:** https://www.zxpand.com/
- **Features:** SD card, SPI, RTC, EEPROM

### Wiring

ZXpand+ connects directly to the edge connector. No additional wiring needed.

### SPI Interface

ZXpand+ uses SPI via I/O ports:

```assembly
; ZXpand+ I/O ports
PORT_CONTROL  EQU $E3
PORT_DATA     EQU $E4

; Send byte via SPI
zxpsnd_send:
    LD A, (data)
    OUT (PORT_DATA), A
    RET
```

## Option 3: DivMMC Future

### Overview

DivMMC Future is another modern interface with SD card and serial.

- **Cost:** ~$50-70
- **URL:** https://www.zxdivmmc.com/

## Testing the Connection

### Loopback Test

1. Connect TX to RX on the Arduino
2. Run terminal program (e.g., PuTTY)
3. Type characters - should echo back

### ZX Spectrum Test

```assembly
; Test program - send "Hello" to serial

    ORG $8000

start:
    LD HL, message
    CALL serial_tx_string
    RET

message:
    DEFM "Hello from ZX Spectrum!", 13, 10, 0

serial_tx_string:
    LD A, (HL)
    OR A
    RET Z
    CALL serial_tx
    INC HL
    JR serial_tx_string

serial_tx:
    ; Bit-bang serial (see main.asm)
    ; ...
    RET

    END start
```

Build and run:
```bash
pasmo test_serial.asm test.tap
fuse test.tap
```

Monitor with PC bridge:
```bash
python tools/pc_bridge.py
```

## Troubleshooting

### No Communication

1. **Check power** - Ensure ZX Spectrum is powered on
2. **Check ground** - Common ground is essential
3. **Check wiring** - TX↔RX crossover (TX to RX, RX to TX)
4. **Check baud rate** - Must match (9600)

### Corrupted Data

1. **Timing issues** - Adjust baud delay constants
2. **Noise** - Use shorter wires, add decoupling capacitor
3. **Voltage levels** - ZX Spectrum uses 5V TTL, Arduino is 5V tolerant

### ZX Spectrum Doesn't Load

1. **Check TAP file** - Verify with emulator first
2. **Check LOAD command** - Use `LOAD ""` for first file
3. **Check memory** - Ensure no conflicts with other software

## Safety Notes

⚠️ **Warning:** The ZX Spectrum edge connector carries live voltage. Be careful not to:

- Short adjacent pins (can damage ULA)
- Apply external voltage to data pins
- Insert/remove connector while powered

**Always power off before connecting/disconnecting!**

## Parts List

### Minimal Setup (~$25)

| Item | Source | Cost |
|------|--------|------|
| Arduino Nano | Amazon/AliExpress | $10 |
| Jumper wires | Amazon | $5 |
| Edge connector | eBay | $10 |
| **Total** | | **~$25** |

### Recommended Setup (~$85)

| Item | Source | Cost |
|------|--------|------|
| ZXpand+ | ZXpand.com | $65 |
| Micro SD card | Any | $10 |
| Jumper wires | Amazon | $5 |
| **Total** | | **~$80** |

## Resources

- [ZX Spectrum Pinout](https://spectrumcomputing.co.uk/entry/0000234)
- [ULA Technical Details](https://worldofspectrum.org/tech/)
- [ZXpand+ Documentation](https://www.zxpand.com/docs/)
- [Arduino SoftwareSerial](https://www.arduino.cc/reference/en/libraries/softwareserial/)

---

*Good luck with your ZX Spectrum serial interface!*
