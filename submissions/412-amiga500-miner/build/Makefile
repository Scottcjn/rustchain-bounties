# Amiga 500 Miner - Build System
# Bounty: #412 - Port Miner to Amiga 500 (1987)

CC = m68k-amigaos-gcc
AS = m68k-amigaos-as
LD = m68k-amigaos-ld

# Alternative: vbcc (Volker Barthelmann C Compiler)
# CC = vcc
# AS = vasmm68k_mot

CFLAGS = -O2 -m68000 -Wall
ASFLAGS = -m68000 --strip-local-absolute
LDFLAGS = -Wl,--oformat=binary -Wl,-Ttext=0x080000

# Source files
C_SOURCES = src/miner.c
ASM_SOURCES = src/sha256.asm

# Object files
C_OBJECTS = build/miner.o
ASM_OBJECTS = build/sha256.o

# Output
TARGET = build/miner.bin
TARGET_ELF = build/miner.elf

.PHONY: all clean test run

all: $(TARGET)

# Compile C code
$(C_OBJECTS): $(C_SOURCES)
	@mkdir -p build
	$(CC) $(CFLAGS) -c $< -o $@

# Assemble assembly code
$(ASM_OBJECTS): $(ASM_SOURCES)
	@mkdir -p build
	$(AS) $(ASFLAGS) $< -o $@

# Link everything
$(TARGET_ELF): $(C_OBJECTS) $(ASM_OBJECTS)
	$(LD) $(LDFLAGS) -o $@ $^

# Create binary
$(TARGET): $(TARGET_ELF)
	@echo "Creating Amiga 500 binary..."
	@cp $(TARGET_ELF) $(TARGET)
	@echo "Built: $(TARGET)"
	@echo ""
	@echo "To run on Amiga:"
	@echo "  1. Transfer to Amiga (serial/ethernet/floppy)"
	@echo "  2. Execute from Workbench or CLI"
	@echo "  3. Watch it mine (very slowly!)"

# Test with Python simulator
test:
	@echo "Running Python simulator tests..."
	cd simulator && python3 amiga_emulator.py --test

# Run full demo
run:
	@echo "Running Amiga 500 mining simulation..."
	cd simulator && python3 amiga_emulator.py

# Clean build artifacts
clean:
	rm -rf build/*.o build/*.bin build/*.elf

# Generate documentation
docs:
	@echo "Generating documentation..."
	@echo "See README.md and docs/ for details"

# Info about the build
info:
	@echo "Amiga 500 Miner Build System"
	@echo "============================="
	@echo ""
	@echo "Target: Motorola 68000 @ 7.14 MHz"
	@echo "Output: build/miner.bin (raw binary)"
	@echo "Load Address: $$080000 (512 KB)"
	@echo ""
	@echo "Bounty: #412 - LEGENDARY Tier"
	@echo "Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"
