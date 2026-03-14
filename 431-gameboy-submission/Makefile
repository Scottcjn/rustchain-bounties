# RustChain Game Boy Miner - Makefile

# Toolchain
RGBASM ?= rgbasm
RGBLINK ?= rgblink
RGBFIX ?= rgbfix

# Source files
SRCS = src/main.asm
OBJS = $(SRCS:.asm=.o)

# Output
TARGET = rustchain_miner.gb
MAPFILE = rustchain_miner.map

# Flags
ASMFLAGS = -Weverything -Werror
LDFLAGS = -m $(MAPFILE)

# Directories
BUILD_DIR = build

# ═══════════════════════════════════════════════════════════
# Build Rules
# ═══════════════════════════════════════════════════════════

.PHONY: all clean debug test

all: $(TARGET)

# Link object files into ROM
$(TARGET): $(OBJS)
	@echo "Linking $(TARGET)..."
	$(RGBLINK) $(LDFLAGS) -o $@ $^
	@echo "Fixing ROM header..."
	$(RGBFIX) -v -p $FF $@
	@echo "Build complete: $(TARGET)"
	@ls -lh $(TARGET)

# Assemble source files
%.o: %.asm
	@echo "Assembling $<..."
	@mkdir -p $(BUILD_DIR)
	$(RGBASM) $(ASMFLAGS) -o $@ $<

# Debug build with symbols
debug: ASMFLAGS += -g
debug: $(TARGET)
	@echo "Debug build complete"

# Clean build artifacts
clean:
	@echo "Cleaning..."
	rm -rf $(OBJS) $(TARGET) $(MAPFILE) $(BUILD_DIR)
	@echo "Clean complete"

# Test in emulator (requires sameboy or gambatte)
test: $(TARGET)
	@echo "Running tests..."
	@if command -v sameboy &> /dev/null; then \
		sameboy $(TARGET); \
	elif command -v gambatte &> /dev/null; then \
		gambatte $(TARGET); \
	else \
		echo "No emulator found. Install sameboy or gambatte."; \
		exit 1; \
	fi

# Run SHA-256 test vectors
test-sha256:
	@echo "Running SHA-256 test vectors..."
	cd tests && python test_sha256.py

# Run serial protocol tests
test-serial:
	@echo "Running serial protocol tests..."
	cd tests && python test_serial.py

# Generate full SHA-256 constants
generate-constants:
	@echo "Generating SHA-256 constants..."
	cd tools && python generate_sha256_consts.py > include/sha256_consts.asm
	@echo "Constants generated"

# Flash to cartridge (requires gbxcart-rw)
flash: $(TARGET)
	@echo "Flashing to cartridge..."
	python gbxcart_rw.py write $(TARGET)
	@echo "Flash complete"

# Check ROM size
check-size: $(TARGET)
	@echo "ROM size check:"
	@ls -l $(TARGET)
	@SIZE=$$(stat -f%z $(TARGET) 2>/dev/null || stat -c%s $(TARGET)); \
	if [ $$SIZE -gt 32768 ]; then \
		echo "ERROR: ROM exceeds 32 KB limit!"; \
		exit 1; \
	else \
		echo "OK: ROM fits in 32 KB cartridge"; \
	fi

# Show help
help:
	@echo "RustChain Game Boy Miner - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all              - Build ROM (default)"
	@echo "  debug            - Build with debug symbols"
	@echo "  clean            - Remove build artifacts"
	@echo "  test             - Run in emulator"
	@echo "  test-sha256      - Run SHA-256 test vectors"
	@echo "  test-serial      - Run serial protocol tests"
	@echo "  generate-constants - Generate SHA-256 constants"
	@echo "  flash            - Flash to cartridge"
	@echo "  check-size       - Verify ROM size"
	@echo "  help             - Show this help"
	@echo ""
	@echo "Variables:"
	@echo "  RGBASM=$(RGBASM)"
	@echo "  RGBLINK=$(RGBLINK)"
	@echo "  RGBFIX=$(RGBFIX)"
