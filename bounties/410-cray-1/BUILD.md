# Building RustChain Miner for Cray-1

This document provides detailed build instructions for the RustChain miner on Cray-1 supercomputer hardware.

## Prerequisites

### Hardware Requirements

- **Cray-1 Supercomputer** (1976 or later)
  - Vector Processor @ 80 MHz (Cray-1) or 100 MHz (Cray-1S)
  - Minimum 1 MW (8 MB) memory, recommended 16 MW (128 MB)
  - COS (Cray Operating System) or CTSS

### Software Requirements

1. **Cray Fortran Translator (CFT)**
   - Version 2.0 or later
   - Included with COS software distribution
   - Verify installation: `cft --version`

2. **Cray Assembly Language (CAL) Assembler**
   - Version 1.0 or later
   - Included with COS software distribution
   - Verify installation: `cal --version`

3. **COS Linker (ld)**
   - Standard COS development tools
   - Verify installation: `ld --version`

4. **Load Module Creator (mkload)**
   - For creating loadable modules
   - Verify installation: `mkload --help`

### Environment Setup

Before building, ensure your environment is properly configured:

```bash
# Set up COS development environment
. /cos/dev/init_env.sh

# Verify tools are available
which cft
which cal
which ld
which mkload

# Set compiler flags
export CFT_OPTS="-C -O"
export CAL_OPTS="-O"
```

## Build Process

### Quick Build

The simplest way to build is using the provided build script:

```bash
cd miners/cray-1
./build.sh
```

This will:
1. Clean previous build artifacts
2. Compile all Fortran sources
3. Assemble all Cray assembly sources
4. Link all object files
5. Create loadable module

### Manual Build

For more control, you can build manually:

#### Step 1: Compile Fortran Sources

```bash
# Create output directory
mkdir -p obj bin

# Compile main program
cft -C -O -o obj/miner_main.o src/miner_main.f

# Compile mining logic
cft -C -O -o obj/mining.o src/mining.f

# Compile network stack
cft -C -O -o obj/network.o src/network.f

# Compile utilities
cft -C -O -o obj/utils.o src/utils.f
```

#### Step 2: Assemble Cray Sources

```bash
# Assemble hardware detection
cal -O -o obj/hw_cray.o src/hw_cray.s

# Assemble attestation module
cal -O -o obj/attest.o src/attest.s

# Assemble vector operations
cal -O -o obj/vector_ops.o src/vector_ops.s

# Assemble timing measurements
cal -O -o obj/pit_cray.o src/pit_cray.s
```

#### Step 3: Link

```bash
ld -lcos -lmath -o bin/miner.com \
    obj/miner_main.o \
    obj/mining.o \
    obj/network.o \
    obj/utils.o \
    obj/hw_cray.o \
    obj/attest.o \
    obj/vector_ops.o \
    obj/pit_cray.o
```

#### Step 4: Create Load Module

```bash
mkload -n RUSTCHAIN_MINER bin/miner.com
```

## Compiler Flags

### CFT (Cray Fortran Translator)

| Flag | Description |
|------|-------------|
| `-C` | Enable comments in output |
| `-O` | Optimize code |
| `-O2` | Aggressive optimization |
| `-g` | Include debugging information |
| `-u` | Enable vectorization |
| `-Z` | Enable bounds checking |

Recommended: `cft -C -O -u`

### CAL (Cray Assembly Language)

| Flag | Description |
|------|-------------|
| `-O` | Optimize assembly |
| `-l` | Generate listing file |
| `-s` | Generate symbol table |

Recommended: `cal -O -l`

## Output Files

After successful build:

```
miners/cray-1/
├── obj/                    # Object files
│   ├── miner_main.o
│   ├── mining.o
│   ├── network.o
│   ├── utils.o
│   ├── hw_cray.o
│   ├── attest.o
│   ├── vector_ops.o
│   └── pit_cray.o
├── bin/                    # Binary outputs
│   ├── miner.com          # Executable
│   └── RUSTCHAIN_MINER    # Load module
└── build.sh               # Build script
```

## Testing

### Basic Test

```bash
# Load the miner
LOAD RUSTCHAIN_MINER

# Run with test wallet
RUSTCHAIN_MINER -w RTC4325af95d26d59c3ef025963656d22af638bb96b
```

### Expected Output

```
  ____  _ _       ____  _                       _   
 | __ )(_) |_    |  _ \(_)_ __ ___   __ _ _ __| |_ 
 |  _ \| | __|   | |_) | | '_ ` _ \ / _` | '__| __|
 | |_) | | |_    |  __/| | | | | | | (_| | |  | |_ 
 |____/|_|\__|   |_|   |_|_| |_| |_|\__,_|_|   \__|
                                                   
           Cray-1 Supercomputer Miner v0.1.0

=== System Information ===
CPU: Cray-1 @ 80 MHz
Memory: 8 MW (Million Words)
System Date: 1976-01-01
========================

[INIT] Initializing hardware detection...
[INIT] Generating miner ID...
[INIT] Miner ID: CRAY1-xxxxxxxx
[CHECK] Running emulator detection...
[OK] Real Cray-1 hardware detected.
[INIT] Initializing network...
[OK] Network initialized.
[ATTEST] Starting hardware attestation...
[OK] Attestation successful!

[MINER] Starting mining loop...
[MINER] Block time: 600 seconds
[MINER] Press any key to stop.

[MINER] Block:       1 | Hashrate:     50000 H/s | Shares:      1/1 (100.00%)
```

### Emulator Test

To test emulator detection (should earn 0 RTC):

```bash
# Run in Cray simulator
sim_cray1 RUSTCHAIN_MINER -w RTC...
```

Expected: `[WARNING] Emulator detected!`

## Troubleshooting

### "cft: command not found"

Ensure COS development tools are installed and in your PATH:

```bash
export PATH=/cos/bin:$PATH
```

### "cal: cannot open source file"

Check that source files are in the correct location:

```bash
ls -la src/*.s
```

### "ld: cannot find -lcos"

Ensure COS libraries are installed:

```bash
ls -la /cos/lib/libcos.a
```

### "mkload: command not found"

Install COS development tools:

```bash
pkg_add cos-dev-tools
```

### Linking Errors

If you get undefined symbol errors, ensure all object files are included:

```bash
ld -o miner.com *.o -lcos -lmath
```

### Runtime Errors

#### "Network initialization failed"

Check network configuration:

```bash
cat NETWORK.CFG
```

Ensure COS network stack is running:

```bash
$NETSTATUS
```

#### "Attestation failed"

Verify network connectivity:

```bash
$PING 50.28.86.131
```

Check node URL is correct.

## Performance Tuning

### Vector Optimization

Enable aggressive vectorization:

```bash
cft -O2 -u -o obj/mining.o src/mining.f
```

### Memory Alignment

Ensure data is aligned for optimal memory access:

```fortran
      REAL*8 DATA(64)
      EQUIVALENCE (DATA(1), ALIGN(8))
```

### Loop Unrolling

For critical loops, consider manual unrolling:

```fortran
      DO 100 I = 1, 64, 4
         V(I) = OP1(I)
         V(I+1) = OP1(I+1)
         V(I+2) = OP1(I+2)
         V(I+3) = OP1(I+3)
  100 CONTINUE
```

## Debugging

### Enable Debug Symbols

```bash
cft -g -o obj/miner_main.o src/miner_main.f
cal -s -o obj/hw_cray.o src/hw_cray.s
```

### Use COS Debugger

```bash
$DEBUG RUSTCHAIN_MINER
```

### Enable Verbose Output

```bash
RUSTCHAIN_MINER -w RTC... -v
```

## Distribution

To create a distribution package:

```bash
# Create release directory
mkdir -p release

# Copy binaries
cp bin/miner.com release/
cp bin/RUSTCHAIN_MINER release/

# Copy documentation
cp README.md release/
cp BUILD.md release/

# Copy configuration examples
cp NETWORK.CFG.example release/

# Create archive
tar -czf rustchain_cray1_v0.1.0.tar.gz release/
```

## References

- [Cray Fortran Reference Manual](https://archive.org/details/Cray_Fortran_Manual)
- [Cray Assembly Language Manual](https://archive.org/details/CAL_Manual)
- [COS Operating System Guide](https://archive.org/details/COS_OS_Guide)
- [Cray-1 Hardware Reference](https://archive.org/details/Cray-1_Hardware_Reference)

---

**Version**: 0.1.0  
**Last Updated**: 2026-03-13  
**Bounty Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`
