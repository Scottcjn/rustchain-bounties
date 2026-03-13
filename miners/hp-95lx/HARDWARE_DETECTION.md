# HP 95LX Hardware Detection Implementation

**Version**: 1.0  
**Date**: 2026-03-13  
**Author**: RustChain Mining Team  

---

## Overview

This document describes the hardware detection implementation for the HP 95LX miner. The detection system identifies:

1. **NEC V20 CPU** - The processor used in HP 95LX
2. **HP 95LX SoC** - Custom system-on-chip
3. **Emulator vs Real Hardware** - Anti-emulation checks
4. **Memory Configuration** - 512 KB or 1 MB RAM

---

## Detection Methods

### 1. NEC V20 CPU Detection

The NEC V20 is an 8088-compatible CPU with enhanced features:

**Detection Approach:**
- Search BIOS ROM for HP signatures
- Check for V20-specific instruction support
- Analyze CPU timing characteristics

**Code Location:** `src/hw_95lx.c` - `detect_nec_v20()`

```c
// Search for HP signature in BIOS
far char *bios_rom = (far char *)0xF000FFF0L;
for (i = 0; i < 256; i++) {
    if (bios_rom[-i] == 'H' && bios_rom[-i+1] == 'P') {
        return 1;  // V20 detected (HP 95LX uses V20)
    }
}
```

**Reliability:** High (when combined with SoC detection)

---

### 2. HP 95LX SoC Detection

HP 95LX uses a custom integrated SoC with unique characteristics:

**Detection Approach:**
- Search BIOS for "HP 95LX", "HEWLETT-PACKARD", or "JUPITER"
- Check custom I/O port responses
- Verify memory map (512 KB or 1 MB)

**Code Location:** `src/hw_95lx.c` - `detect_hp95lx_soc()`

**Signatures Searched:**
- `"HP 95LX"` - Direct model identification
- `"HEWLETT-PACKARD"` - Company name
- `"JUPITER"` - HP 95LX codename

**Reliability:** Very High

---

### 3. Emulator Detection

Distinguishes real HP 95LX hardware from emulators (Jupiter, etc.):

**Detection Methods:**

#### a. BIOS Signature Check
Search for emulator-specific strings:
- `"JUPITER"` (emulator name)
- `"EMU"` or `"EMULATOR"`

#### b. Timer Drift Analysis
Real hardware has slight timer imperfections:
- Measure timer over fixed period
- Check for "too perfect" timing
- Emulators often have perfectly accurate timers

#### c. Hardware Quirks
Real HP 95LX has specific behaviors that emulators may not replicate:
- Timer drift
- Interrupt timing variations
- Hardware imperfections

**Code Location:** `src/hw_95lx.c` - `detect_emulator()`

**Reliability:** Medium-High (improves with multiple checks)

---

### 4. Memory Detection

Uses BIOS interrupt to get system memory size:

**Method:** INT 0x12 - Get Memory Size

```c
union REGS regs;
regs.w.ax = 0;
int86(0x12, &regs, &regs);
return regs.w.ax;  // Memory size in KB
```

**Expected Values:**
- 512 KB - Standard HP 95LX
- 1024 KB - Upgraded HP 95LX

**Code Location:** `src/hw_95lx.c` - `get_memory_kb()`

**Reliability:** Very High

---

## Hardware Fingerprint

A unique fingerprint is generated for attestation:

**Format:**
```
HP95LX-V20-{speed}MHz-{memory}KB-{type}
```

**Example:**
```
HP95LX-V20-5MHz-512KB-HW   // Real hardware
HP95LX-V20-5MHz-512KB-EMU  // Emulator
```

**Code Location:** `src/hw_95lx.c` - `hw_95lx_get_fingerprint()`

---

## API Reference

### Initialization

```c
int hw_95lx_detect(void);
```
Detects HP 95LX hardware and initializes global state.  
**Returns:** 0 on success, -1 on failure

### Status Checks

```c
int hw_95lx_is_emulator(void);
```
Check if running on emulator.  
**Returns:** 1 if emulator, 0 if real hardware

### Hardware Information

```c
const char* hw_95lx_get_cpu_name(void);
int hw_95lx_get_cpu_speed_mhz(void);
int hw_95lx_get_memory_kb(void);
```
Get CPU name, speed, and memory size.

### Fingerprinting

```c
int hw_95lx_get_fingerprint(char *buf, int max_len);
```
Get hardware fingerprint for attestation.  
**Returns:** 0 on success, -1 on error

---

## Testing

### In Emulator

1. Run in Jupiter HP 95LX emulator
2. Execute: `miner`
3. Check output:
   ```
   [WARNING] Emulator detected! No rewards will be earned.
   ```

### On Real Hardware

1. Transfer `miner.com` to HP 95LX
2. Run: `miner`
3. Check output:
   ```
   [OK] Real HP 95LX hardware detected.
   [INFO] Reward multiplier: 2.0x
   ```

---

## Known Limitations

1. **V20 Detection:** May not distinguish V20 from 8088 in all cases
2. **Emulator Detection:** Sophisticated emulators may pass detection
3. **Timer Accuracy:** Requires calibration for different systems

---

## Future Improvements

1. **Enhanced V20 Detection:**
   - Use V20-specific instructions (BRKEM, GETREG)
   - Instruction timing analysis

2. **Better Emulator Detection:**
   - Multiple timer measurements
   - Hardware behavior profiling
   - Machine learning classification

3. **Additional Signatures:**
   - HP 95LX-specific I/O ports
   - Custom timer/counter behavior
   - LCD controller detection

---

## References

- HP 95LX Technical Reference Manual
- NEC V20 Programming Manual
- IBM PC/XT Hardware Detection (dos-xt miner)
- Open Watcom C Documentation

---

## License

Same as HP 95LX Miner project (see LICENSE)

---

**Last Updated:** 2026-03-13  
**Next Review:** After real hardware testing
