# Network Setup Guide - RustChain C64 Miner

The Commodore 64 has no built-in networking. This guide covers all viable options.

## Overview

| Option | Cost | Speed | Complexity | Recommended |
|--------|------|-------|------------|-------------|
| RR-Net | $80-150 | Fast | Low | ✓ Best |
| Userport+ESP32 | $20 | Slow | Medium | ✓ Cheapest |
| SD2IEC | $100-200 | Medium | Low | Good |
| 1541 Ultimate | $200+ | Medium | Low | Expensive |

## Option A: RR-Net (Recommended)

### Hardware Required

- RR-Net cartridge (~$80-150 from retro stores)
- Ethernet cable
- Router with DHCP

### Installation

1. Insert RR-Net into C64 cartridge port
2. Connect Ethernet cable
3. Power on C64

### Driver Configuration

The miner uses the tcpip.lib library for RR-Net:

```c
#include <tcpip.h>

/* Initialize network */
if (network_init() == 0) {
    /* Network ready */
}
```

### DHCP Configuration

RR-Net auto-configures via DHCP. For static IP:

```c
/* In network.c */
static uint8_t g_ip_address[4] = {192, 168, 1, 100};
static uint8_t g_gateway[4] = {192, 168, 1, 1};
static uint8_t g_netmask[4] = {255, 255, 255, 0};
static uint8_t g_dns[4] = {8, 8, 8, 8};
```

### Testing

```c
/* Test connection */
int16_t status = network_post(
    "rustchain.org", 80, "/health",
    "", 0,
    buffer, sizeof(buffer)
);

if (status == 0) {
    /* Connection successful */
}
```

### Troubleshooting

**No link light:**
- Check Ethernet cable
- Try different router port

**DHCP fails:**
- Check router DHCP settings
- Try static IP

**Connection timeout:**
- Check firewall settings
- Verify rustchain.org is reachable

## Option B: Userport + ESP32 Bridge

### Hardware Required

- ESP32 development board (~$10-20)
- Userport connector or breadboard
- Jumper wires
- 5V power for ESP32

### Wiring Diagram

```
C64 Userport          ESP32
-----------           -------
PA0 (PB)   ---------> GPIO 17 (RX)
PA1 (PA)   ---------> GPIO 16 (TX)
FLAG2      ---------> GND
GND        ---------> GND
5V         ---------> 5V (or use USB)
```

**Pinout Reference:**

```
C64 Userport (bottom view):
  C B A 9 8 7 6 5 4 3 2 1
  O O O O O O O O O O O O
  1 1 1 1 1 1 1 1 1 1 1 1
  
A = PA0 (output)
B = PA1 (output)
FLAG2 = Ground sense
```

### ESP32 Firmware

Flash this code to ESP32 using Arduino IDE:

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

HardwareSerial Serial2(2);

void setup() {
  Serial2.begin(9600, SERIAL_8N1, 16, 17);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void loop() {
  if (Serial2.available()) {
    String cmd = Serial2.readStringUntil('\n');
    
    if (cmd.startsWith("CONNECT")) {
      // Parse host and port
      // Make HTTP request
      // Return response
    }
  }
}
```

### C64 Driver

Enable Userport mode in build:

```bash
make userport
```

Or define in code:

```c
#define USE_USERPORT_ESP32
```

### Communication Protocol

Simple serial protocol:

```
C64 -> ESP32:
CONNECT rustchain.org 80
POST /api/attest
{"miner_id": ...}
END

ESP32 -> C64:
HTTP/1.1 200 OK
{"status": "ok", ...}
```

### Baud Rate

Default: 9600 baud

For faster speeds (unreliable):
- 19200: Some C64 units support
- 2400: More reliable on old hardware

Configure in `network.c`:

```c
#define BAUD_RATE 9600
```

### Troubleshooting

**No response from ESP32:**
- Check wiring
- Verify ESP32 is powered
- Check baud rate match

**Garbage characters:**
- Baud rate mismatch
- Wiring issue (swap TX/RX)

**Connection fails:**
- Check WiFi credentials
- Verify ESP32 connects to router

## Option C: SD2IEC

### Hardware Required

- SD2IEC device (~$100-200)
- SD card
- IEC cable (included with C64)

### Installation

1. Insert SD card into SD2IEC
2. Connect IEC cable to C64
3. Power on SD2IEC, then C64

### Networking

SD2IEC has limited networking via firmware:

```c
/* SD2IEC uses IEC protocol */
/* Requires custom driver */
```

### Limitations

- Slower than RR-Net
- Limited HTTP support
- Requires firmware configuration

## Option D: 1541 Ultimate-II+

### Hardware Required

- 1541 Ultimate-II+ (~$200)
- SD card
- IEC cable

### Features

- Full C64 emulation
- Ethernet support
- Easy file transfer

### Limitations

- Expensive
- Overkill for just mining

## Network Security

### Firewall Configuration

Allow outbound connections:
- Port 80 (HTTP) to rustchain.org
- Port 443 (HTTPS) for future use

### IP Whitelist

If behind restrictive firewall:
- rustchain.org: 50.28.86.131 (verify current IP)

### No TLS Support

Current implementation uses plain HTTP:
- No certificate validation
- No encryption
- Acceptable for attestation (public data)

## Performance Comparison

| Option | Connect Time | POST Time | Total |
|--------|--------------|-----------|-------|
| RR-Net | ~2s | ~1s | ~3s |
| Userport | ~5s | ~10s | ~15s |
| SD2IEC | ~3s | ~5s | ~8s |

## Power Consumption

| Option | Power Draw |
|--------|------------|
| RR-Net | ~500mA (from C64) |
| ESP32 | ~250mA (separate USB) |
| SD2IEC | ~200mA (from IEC) |

## Recommendation

**For most users:** RR-Net
- Easiest setup
- Best performance
- Well-documented

**For budget users:** Userport + ESP32
- Cheapest option
- Good learning project
- Acceptable performance

**For collectors:** SD2IEC or 1541 Ultimate
- Multi-purpose device
- Already owned by many

## Resources

- [RR-Net Documentation](https://www.c64-wiki.com/wiki/RR-Net)
- [ESP32 Arduino Core](https://github.com/espressif/arduino-esp32)
- [SD2IEC Firmware](https://www.sd2iec.com)
- [C64 Networking Wiki](https://www.c64-wiki.com/wiki/Networking)

## Next Steps

After network setup:
1. Test connection in VICE or real hardware
2. Run first attestation
3. Verify in https://rustchain.org/api/miners
4. Submit bounty claim

For build instructions, see BUILD.md.
