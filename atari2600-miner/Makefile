# RustChain Atari 2600 Miner - Makefile
# Bounty #426 - LEGENDARY Tier (200 RTC)

# Toolchain
AS = ca65
LD = ld65

# Source files
ASM_SRC = src/rustchain_miner.asm

# Output
OUTPUT = build/rustchain_miner.bin
ROM_SIZE = 4096

# Flags
ASFLAGS = -t none -v
LDFLAGS = -t none -C linker.cfg -m build/rustchain_miner.map

# Default target
all: dirs $(OUTPUT)
	@echo "✓ Build complete: $(OUTPUT)"
	@echo "  ROM size: $(ROM_SIZE) bytes (4 KB)"
	@echo "  Bounty wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"

# Create build directory
dirs:
	@mkdir -p build

# Assemble
build/rustchain_miner.o: $(ASM_SRC)
	@echo "⚙  Assembling $(ASM_SRC)..."
	$(AS) $(ASFLAGS) -o $@ $(ASM_SRC)

# Link
$(OUTPUT): build/rustchain_miner.o
	@echo "🔗 Linking..."
	$(LD) $(LDFLAGS) -o $@ build/rustchain_miner.o

# Clean
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/

# Test in Stella (if installed)
test: $(OUTPUT)
	@echo "🎮 Launching Stella emulator..."
	@if command -v stella >/dev/null 2>&1; then \
		stella $(OUTPUT); \
	else \
		echo "❌ Stella emulator not found. Install from: https://stella-emu.github.io/"; \
		exit 1; \
	fi

# Generate Intel HEX format
hex: $(OUTPUT)
	@echo "📄 Generating Intel HEX..."
	$(LD) $(LDFLAGS) -o build/rustchain_miner.hex --hex build/rustchain_miner.o

# Show ROM info
info: $(OUTPUT)
	@echo "📊 ROM Information:"
	@echo "  File: $(OUTPUT)"
	@echo "  Size: $$(stat -f%z $(OUTPUT) 2>/dev/null || stat -c%s $(OUTPUT)) bytes"
	@echo "  SHA256: $$(shasum -a 256 $(OUTPUT) 2>/dev/null || sha256sum $(OUTPUT) | cut -d' ' -f1)"
	@echo "  Bounty: #426 (LEGENDARY - 200 RTC)"
	@echo "  Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"

# Verify ROM structure
verify: $(OUTPUT)
	@echo "✅ Verifying ROM structure..."
	@python3 -c " \
data = open('$(OUTPUT)', 'rb').read(); \
print(f'  ROM size: {len(data)} bytes'); \
assert len(data) == 4096, 'ROM must be exactly 4 KB'; \
print(f'  Reset vector: 0x{data[-6]:02X}{data[-5]:02X}'); \
print(f'  ✓ ROM structure valid'); \
"

# Help
help:
	@echo "RustChain Atari 2600 Miner - Build Targets"
	@echo ""
	@echo "  make        - Build ROM (default)"
	@echo "  make clean  - Remove build artifacts"
	@echo "  make test   - Run in Stella emulator"
	@echo "  make hex    - Generate Intel HEX format"
	@echo "  make info   - Show ROM information"
	@echo "  make verify - Verify ROM structure"
	@echo "  make help   - Show this help"
	@echo ""
	@echo "Bounty: #426 (LEGENDARY - 200 RTC)"
	@echo "Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"

.PHONY: all dirs clean test hex info verify help
