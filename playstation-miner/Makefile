# PlayStation (1994) Miner - Makefile
# ====================================
# Build SHA-256 miner for Sony PlayStation MIPS R3000A CPU

# Compiler selection
CC_NATIVE = gcc
CC_CROSS_MIPSEL = mipsel-linux-gnu-gcc
CC_CROSS_MIPS = mips-linux-gnu-gcc

# Target specifications
TARGET_ARCH = mips1
TARGET_ABI = 32

# Optimization flags for R3000A
# -O2: Good balance of speed vs code size
# -march=mips1: Target MIPS I ISA (R3000A)
# -mabi=32: 32-bit ABI
# -fomit-frame-pointer: Save register (we're memory-constrained!)
CFLAGS = -O2 -march=$(TARGET_ARCH) -mabi=$(TARGET_ABI) -fomit-frame-pointer

# Warning flags
CFLAGS += -Wall -Wextra -Wpedantic

# Debug build (optional)
# CFLAGS += -g -DDEBUG

# Source files
SRC = src/miner_psx.c

# Output binaries
OUT_NATIVE = miner_psx_native
OUT_MIPSEL = miner_psx_ps1
OUT_MIPS_BE = miner_psx_be

# Default target: build native version for testing
all: native

# Native build (for testing on modern systems)
native:
	@echo "Building native version (for testing)..."
	$(CC_NATIVE) $(CFLAGS) -o $(OUT_NATIVE) $(SRC)
	@echo "Built: $(OUT_NATIVE)"
	@echo "Run: ./$(OUT_NATIVE)"

# Cross-compile for PlayStation (little-endian, PS1 Linux)
ps1:
	@echo "Cross-compiling for PlayStation 1 (little-endian)..."
	@which $(CC_CROSS_MIPSEL) > /dev/null || (echo "Error: $(CC_CROSS_MIPSEL) not found"; exit 1)
	$(CC_CROSS_MIPSEL) $(CFLAGS) -o $(OUT_MIPSEL) $(SRC)
	@echo "Built: $(OUT_MIPSEL)"
	@echo "Upload to PS1 Linux environment and run: ./$(OUT_MIPSEL)"

# Cross-compile for big-endian MIPS (true R3000A)
mips-be:
	@echo "Cross-compiling for big-endian MIPS R3000A..."
	@which $(CC_CROSS_MIPS) > /dev/null || (echo "Error: $(CC_CROSS_MIPS) not found"; exit 1)
	$(CC_CROSS_MIPS) $(CFLAGS) -o $(OUT_MIPS_BE) $(SRC)
	@echo "Built: $(OUT_MIPS_BE)"
	@echo "For use with MIPS emulators or hardware"

# Build all versions
all-versions: native ps1 mips-be

# Run simulator instead (Python)
simulate:
	@echo "Running PlayStation mining simulator..."
	python3 simulator/playstation_simulator.py

# Clean build artifacts
clean:
	rm -f $(OUT_NATIVE) $(OUT_MIPSEL) $(OUT_MIPS_BE)
	rm -f src/*.o

# Show help
help:
	@echo "PlayStation (1994) Miner - Build System"
	@echo "========================================"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build native version (default)"
	@echo "  native     - Build for host system (testing)"
	@echo "  ps1        - Cross-compile for PS1 Linux (mipsel)"
	@echo "  mips-be    - Cross-compile for big-endian MIPS"
	@echo "  all-versions - Build all versions"
	@echo "  simulate   - Run Python simulator"
	@echo "  clean      - Remove build artifacts"
	@echo "  help       - Show this help"
	@echo ""
	@echo "PlayStation Specs:"
	@echo "  CPU: MIPS R3000A @ 33.87 MHz"
	@echo "  RAM: 2 MB main + 1 MB VRAM"
	@echo "  Cache: None!"
	@echo ""
	@echo "Bounty: #428 - LEGENDARY Tier (200 RTC / $$20)"
	@echo "Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"

.PHONY: all native ps1 mips-be all-versions simulate clean help
