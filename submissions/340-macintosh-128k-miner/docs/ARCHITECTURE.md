# Macintosh 128K Architecture (1984)

## Overview
The original Macintosh 128K was revolutionary for its graphical user interface, but extremely limited by modern standards.

## Hardware Specifications

### CPU: Motorola 68000
- **Clock Speed**: 7.8336 MHz
- **Architecture**: 16/32-bit hybrid (CISC)
- **Data Bus**: 16-bit external, 32-bit internal
- **Address Bus**: 24-bit (16 MB addressable space)
- **Registers**: 
  - 8 data registers (D0-D7, 32-bit)
  - 8 address registers (A0-A7, 32-bit, A7 is stack pointer)
  - Program Counter (PC, 24-bit)
  - Status Register (SR, 16-bit)

### Memory
- **RAM**: 128 KB (512 KB on Macintosh 512K "Fat Mac")
- **ROM**: 64 KB (Macintosh Toolbox)
- **VRAM**: 54 KB (for 512×342 pixel display, 1-bit)

### Storage
- **Floppy Drive**: 3.5" single-sided, 400 KB
- **No Hard Drive**: Original model had no HDD option

### I/O
- **Serial Ports**: 2× RS-422 (printer, modem)
- **No Ethernet**: Networking required expensive add-on
- **No USB**: Didn't exist until 1998 (iMac)

## Macintosh Toolbox ROM
The 64 KB ROM contained essential system routines:
- QuickDraw (graphics)
- Window Manager
- Menu Manager
- Event Manager
- Memory Manager
- File Manager
- Resource Manager

## Programming Model

### Assembly Language (68000)
```assembly
MOVE.L  D0, D1      ; Copy long word
ADD.L   #4, D0      ; Add immediate
MOVEA.L #\$1000, A0 ; Load address
JSR     \$40000      ; Jump to subroutine (ROM)
```

### High-Level Languages (Historical)
- **MacPascal**: Official Pascal implementation
- **C**: Lightspeed C, Aztec C (later)
- **Assembly**: MPW Assembler

## Constraints for Mining

### Memory Limitations
- **128 KB total**: Must fit code, data, and system
- **System overhead**: ~20-30 KB for OS
- **Available for miner**: ~50-80 KB maximum

### Computational Limitations
- **No FPU**: 68881 FPU was optional add-on
- **Integer math only**: All crypto operations must use integer arithmetic
- **Slow by modern standards**: ~0.5 MIPS

### No Network Stack
- Original Mac had no built-in networking
- Mining would be purely demonstrative/simulated
- Would require serial connection to another computer

## Porting Strategy

Given these constraints, a "real" cryptocurrency miner is **impossible**:

1. **SHA-256 requires significant computation** - would take years per hash
2. **No network** - can't submit shares or receive work
3. **Memory too limited** - can't store blockchain or mining state

### Solution: Educational Simulator

We'll create:
1. **68000 Emulator** in Python (simulates CPU, memory, basic Toolbox)
2. **"Miner" Program** in 68000 assembly that demonstrates the concept
3. **Python Host** that does actual mining work, "fed" to the emulator
4. **Documentation** explaining the historical context

This preserves the spirit of the challenge while acknowledging physical reality.

## References
- [Motorola 68000 Manual](https://www.nxp.com/docs/en/reference-manual/M68000PM.pdf)
- [Inside Macintosh](https://archive.org/details/inside-macintosh)
- [Macintosh ROM Disassembly](http://www.mac512.com/)
