# Build Instructions - RustChain C64 Miner

## Prerequisites

### 1. cc65 Compiler Suite

The cc65 cross-compiler is required to build the miner.

#### Windows

```powershell
# Using Chocolatey
choco install cc65

# Or download manually from:
# https://github.com/cc65/cc65/releases
```

#### Linux

```bash
# Debian/Ubuntu
sudo apt install cc65

# Fedora
sudo dnf install cc65

# Arch Linux
sudo pacman -S cc65
```

#### macOS

```bash
# Using Homebrew
brew install cc65
```

### 2. VICE Emulator (Optional, for testing)

VICE is required for testing without real hardware.

#### Windows
Download from: https://vice-emu.sourceforge.io/

#### Linux
```bash
sudo apt install vice
```

#### macOS
```bash
brew install vice
```

### 3. Real Hardware (Required for Attestation)

To actually submit attestations and earn RTC, you need:

- **Commodore 64/64C** - Any model works
- **Network Solution** - One of:
  - RR-Net cartridge (~$80-150)
  - Userport + ESP32 bridge (~$20)
  - SD2IEC with networking (~$100)
- **Storage** - One of:
  - SD2IEC (easiest)
  - 1541 floppy drive
  - Datasette (tape)

## Building

### Standard Build

```bash
# Navigate to project directory
cd rustchain-c64

# Build the miner
make

# Output: miner.prg
```

### Build Options

```bash
# Clean build artifacts
make clean

# Build with debug symbols
make debug

# Build for Userport+ESP32 (instead of RR-Net)
make userport

# Build and run in VICE
make run
```

### Manual Build

If you prefer manual compilation:

```bash
# Compile each source file
cl65 -t c64 -O2 -c src/miner.c
cl65 -t c64 -O2 -c src/network.c
cl65 -t c64 -O2 -c src/fingerprint.c
cl65 -t c64 -O2 -c src/ui.c
cl65 -t c64 -O2 -c src/json.c

# Link
cl65 -t c64 -o miner.prg miner.o network.o fingerprint.o ui.o json.o
```

## Testing in VICE

### Load PRG File

1. Start VICE (x64)
2. File → Attach disk image → Select `miner.prg`
3. In C64: `LOAD "MINER.PRG",8,1`
4. `RUN`

### Or Direct Load

```bash
x64 miner.prg
```

### Debugging

```bash
# Build with debug symbols
make debug

# Run with VICE monitor
x64 -monitor miner.prg
```

## Deploying to Real Hardware

### Method 1: SD2IEC (Recommended)

1. Copy `miner.prg` to SD card
2. Insert SD card into SD2IEC
3. On C64:
   ```
   LOAD "MINER.PRG",8,1
   RUN
   ```

### Method 2: 1541 Floppy

1. Transfer PRG to floppy using StarDOS or similar
2. On C64:
   ```
   LOAD "MINER.PRG",8,1
   RUN
   ```

### Method 3: Datasette (Tape)

1. Convert PRG to tape format:
   ```bash
   tapconv miner.prg miner.tap
   ```
2. Play tape on Datasette
3. On C64:
   ```
   LOAD
   RUN
   ```

### Method 4: Transfer Cable

Use a null-modem cable and terminal program:

```bash
# On PC (using minicom)
minicom -b 2400 -D /dev/ttyUSB0

# On C64, run terminal program
# Receive file
```

## Memory Configuration

The miner uses the following memory layout:

```
$0000-$00FF: Zero Page (critical variables)
$0100-$01FF: Stack
$0200-$03FF: OS vectors/buffers
$0400-$07FF: Screen memory
$0801-$9FFF: Program code (~38 KB)
$A000-$BFFF: BASIC ROM (swapped out for RAM)
$C000-$CFFF: I/O area (VIC-II, CIA, SID)
$D000-$DFFF: Character ROM / RAM
$E000-$FFFF: Kernal ROM (swapped out for RAM)
```

### ROM Banking

To access extra RAM, the miner swaps out ROMs:

```c
/* Enable RAM at $A000-$BFFF */
POKE(1, PEEK(1) & ~0x02);

/* Enable RAM at $E000-$FFFF */
POKE(1, PEEK(1) & ~0x01);

/* Restore ROM */
POKE(1, PEEK(1) | 0x03);
```

## Network Configuration

### RR-Net Setup

1. Insert RR-Net cartridge
2. Connect Ethernet cable
3. Miner auto-configures via DHCP

### Static IP (if needed)

Edit `src/network.c`:

```c
static uint8_t g_ip_address[4] = {192, 168, 1, 100};
static uint8_t g_gateway[4] = {192, 168, 1, 1};
static uint8_t g_dns[4] = {8, 8, 8, 8};
```

### Userport + ESP32 Setup

1. Build ESP32 bridge firmware (see NETWORK.md)
2. Connect ESP32 to C64 Userport
3. Build with: `make userport`
4. Configure baud rate: 9600

## Troubleshooting

### Build Errors

**Problem**: `cl65: command not found`
- **Solution**: Install cc65 and ensure it's in PATH

**Problem**: `undefined reference to 'cbm_clrscr'`
- **Solution**: Link with cbm library: `-lcbm`

**Problem**: `out of memory`
- **Solution**: Reduce code size or enable ROM banking

### Runtime Errors

**Problem**: Miner crashes on startup
- **Solution**: Check memory configuration, ensure no conflicts

**Problem**: Network initialization fails
- **Solution**: Verify hardware connection, check RR-Net presence

**Problem**: Attestation rejected
- **Solution**: Check API endpoint, verify JSON format

### Emulation Detection

**Problem**: Miner detects emulation on real hardware
- **Solution**: Calibrate fingerprint thresholds in `fingerprint.c`

**Problem**: Miner runs in VICE but shouldn't
- **Solution**: Anti-emulation checks need tuning

## Performance Optimization

### Code Size

```bash
# Check code size
cl65 -t c64 -O2 -m miner.map src/miner.c

# Target: < 12 KB runtime
```

### Speed Optimization

```c
/* Use zero page for critical variables */
#pragma bss-name (push,"ZEROPAGE")
static uint8_t critical_var;
#pragma bss-name (pop)

/* Use assembly for hot paths */
asm("lda #$00");
asm("sta $d020");
```

### Memory Optimization

```c
/* Use overlays for rarely-used code */
/* Reuse buffers */
static uint8_t shared_buffer[256];
```

## Verification

### Build Verification

```bash
# Verify PRG file
file miner.prg
# Should show: data

# Check file size
ls -l miner.prg
# Should be: ~8-12 KB
```

### Emulator Verification

1. Load in VICE
2. Check memory map: `MONITOR`
3. Verify no conflicts with OS

### Hardware Verification

1. Photo of C64 running miner
2. Video of full attestation cycle
3. Screenshot in https://rustchain.org/api/miners

## Next Steps

After successful build:

1. Test in VICE
2. Deploy to real hardware
3. Run first attestation
4. Verify in network
5. Submit PR for bounty

For network setup details, see NETWORK.md.
For fingerprinting details, see FINGERPRINT.md.
