# Game Boy Link Cable Wiring Guide

## Overview

This guide explains how to wire a Game Boy to a Raspberry Pi Pico for RustChain mining (RIP-304).

## Game Boy Link Port Pinout

The Game Boy link port uses a 3.5mm stereo jack (TRS):

```
        ┌─────────────┐
        │   Tip       │  → VCC (3.3V)
        ├─────────────┤
        │   Ring      │  → Data (bidirectional)
        ├─────────────┤
        │   Sleeve    │  → GND
        └─────────────┘
```

### Electrical Specifications

| Pin | Signal | Voltage | Notes |
|-----|--------|---------|-------|
| Tip | VCC | 3.3V DC | Power output (limited current) |
| Ring | Data | 0-3.3V | Serial data (bidirectional) |
| Sleeve | GND | 0V | Ground |

### Serial Specifications

- **Protocol**: Synchronous serial
- **Speed**: 8192 Hz (8 Kbit/s) standard
- **Speed**: 262144 Hz (262 Kbit/s) CGB high speed
- **Logic**: 3.3V CMOS
- **Mode**: Master/Slave selectable

## Raspberry Pi Pico Pinout

Use these GPIO pins on the Pico:

```
        ┌──────────────────┐
        │  Raspberry Pi    │
        │     Pico         │
        │                  │
   GND ─┤  Pin 3   (GND)   │
   GPIO0┤  Pin 1   (GPIO0) │
   VBUS─┤  Pin 40  (VSYS)  │
        └──────────────────┘
```

### Recommended Pins

| Pico Pin | GPIO | Function | Notes |
|----------|------|----------|-------|
| Pin 40 | VSYS | VCC | 3.3V-5V input |
| Pin 1 | GPIO0 | Data | 3.3V tolerant |
| Pin 3 | GND | Ground | Common ground |

## Wiring Diagram

### Direct Connection (3.3V Pico)

```
Game Boy Link Port          Raspberry Pi Pico
     (3.5mm TRS)                
        │                        
        ├──── Tip (VCC) ────────┼── Pin 40 (VSYS)
        │                        │
        ├──── Ring (Data) ──────┼── Pin 1 (GPIO0)
        │                        │
        └──── Sleeve (GND) ─────┼── Pin 3 (GND)
                                 │
```

**Note**: This works because both Game Boy and Pico use 3.3V logic.

### With Level Shifter (5V Pico)

If your Pico setup uses 5V logic, add a level shifter:

```
Game Boy Link Port    Level Shifter    Raspberry Pi Pico
     (3.5mm TRS)       (3.3V↔5V)           
        │                 │                  │
        ├──── VCC ────────┼──────────────────┼── 5V (optional)
        │                 │                  │
        ├──── Data ───────┼── LV ─── HV ─────┼── GPIO0
        │                 │   TX    TX       │
        │                 │                  │
        └──── GND ────────┼── GND ───────────┼── GND
                          │                  │
                     VCC: 3.3V          VCC: 5V
```

**Recommended Level Shifter**: TXB0108, TXS0108E, or MOSFET-based bidirectional shifter.

## Cable Construction

### Option 1: Modify Existing Link Cable

1. Get a Game Boy link cable (original or aftermarket)
2. Cut off the second Game Boy connector
3. Strip wires:
   - Red/White → VCC
   - Green/Yellow → Data
   - Blue/Black → GND
4. Solder to Pico pins or connector

### Option 2: Build from Scratch

**Materials:**
- 3.5mm stereo jack (TRS)
- 3-conductor cable (audio cable works)
- Raspberry Pi Pico
- Soldering iron, solder, heat shrink

**Steps:**

1. **Prepare cable:**
   - Cut cable to desired length (30-50cm recommended)
   - Strip outer jacket
   - Strip individual conductors

2. **Connect to 3.5mm jack:**
   ```
   Tip    → Red wire   (VCC)
   Ring   → Green wire (Data)
   Sleeve → Blue wire  (GND)
   ```

3. **Connect to Pico:**
   ```
   Red wire   → Pin 40 (VSYS) or 3.3V pin
   Green wire → Pin 1 (GPIO0)
   Blue wire  → Pin 3 (GND)
   ```

4. **Insulate connections:**
   - Use heat shrink tubing
   - Ensure no shorts between wires

### Option 3: Use Breadboard Jumper Wires

For prototyping:

```
Game Boy Link Port → 3.5mm to Dupont adapter → Jumper wires → Pico
```

**Note**: This is fragile and not recommended for long-term use.

## Testing Connection

### Continuity Test

Before connecting to Game Boy:

1. Set multimeter to continuity mode
2. Test each connection:
   - Tip ↔ VSYS: Should beep
   - Ring ↔ GPIO0: Should beep
   - Sleeve ↔ GND: Should beep
3. Check for shorts:
   - Tip ↔ Ring: No beep
   - Tip ↔ Sleeve: No beep
   - Ring ↔ Sleeve: No beep

### Voltage Test

After connecting to Pico (powered off):

1. Set multimeter to DC voltage
2. Measure between Tip and Sleeve
3. Should read 3.3V (or 5V if using VSYS)

### Serial Test

With Pico firmware running:

```bash
# On PC, monitor serial output
screen /dev/ttyACM0 115200

# Or use Python
python -m serial.tools.miniterm /dev/ttyACM0 115200
```

## Troubleshooting

### No Communication

**Possible causes:**
- Wrong GPIO pin
- Bad connection
- Level shifter issue
- Pico firmware not running

**Solutions:**
1. Verify wiring with multimeter
2. Check Pico firmware is uploaded
3. Try different GPIO pin
4. Ensure common ground

### Intermittent Connection

**Possible causes:**
- Loose solder joints
- Damaged cable
- Poor contact in jack

**Solutions:**
1. Re-solder connections
2. Replace cable
3. Use strain relief

### Data Corruption

**Possible causes:**
- Cable too long (>1m)
- Electrical interference
- Wrong baud rate

**Solutions:**
1. Shorten cable
2. Add shielding
3. Verify baud rate (115200 for Pico-PC, 8192 for GB-Pico)

## Safety Notes

⚠️ **Important:**

1. **Never hot-plug**: Disconnect power before modifying wiring
2. **Check polarity**: Reverse VCC/GND can damage Game Boy
3. **Current limit**: Game Boy link port provides limited current (<50mA)
4. **ESD protection**: Use wrist strap when handling cartridges

## Alternative: Game Boy Color Link Port

Game Boy Color uses the same 3.5mm jack but supports high-speed mode:

| Mode | Speed | Compatibility |
|------|-------|---------------|
| Normal | 8 Kbit/s | All Game Boys |
| High | 262 Kbit/s | GBC only |

**Recommendation**: Use normal speed for maximum compatibility.

## Parts List

| Part | Quantity | Source | Approx. Cost |
|------|----------|--------|--------------|
| 3.5mm stereo jack | 1 | Electronics store | $1 |
| Audio cable (3-conductor) | 1 | Electronics store | $2 |
| Raspberry Pi Pico | 1 | Pi Shop, Amazon | $4 |
| Heat shrink tubing | 1 pack | Electronics store | $3 |
| **Total** | | | **~$10** |

## References

- [Pan Docs - Serial Data Transfer](https://gbdev.io/pandocs/Serial_Data_Transfer_(Link_Cable).html)
- [Game Boy Link Cable Pinout](https://www.retroreversing.com/gameboy-link-cable)
- [Raspberry Pi Pico Datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf)

---

*Last Updated: 2026-03-13*  
*RustChain Game Boy Miner Project*
