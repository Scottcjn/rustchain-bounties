# TI-84 RustChain Miner - Build System
# Target: TI-84 Plus (Z80 @ 15 MHz)

# Tools
ASM = spasm
CC = sdcc
EMU = cemu
TI_TOOL = ti84tools

# Directories
SRC_DIR = src
INC_DIR = include
LIB_DIR = lib
BUILD_DIR = build
TOOLS_DIR = tools

# Source files
ASM_SOURCES = $(SRC_DIR)/main.asm \
              $(SRC_DIR)/sha512.asm \
              $(SRC_DIR)/ed25519.asm \
              $(SRC_DIR)/fingerprint.asm \
              $(SRC_DIR)/usb.asm \
              $(SRC_DIR)/math64.asm

# Output
OUTPUT = miner.8xp
OUTPUT_CE = miner.8ce

# Flags
ASM_FLAGS = -v
DEBUG_FLAGS = -DDEBUG

.PHONY: all clean run emu test debug help

# Default target
all: $(BUILD_DIR) $(OUTPUT)
	@echo "Build complete: $(OUTPUT)"
	@echo "Size: $$(wc -c < $(OUTPUT)) bytes"

# Create build directory
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# Assemble main program
$(OUTPUT): $(ASM_SOURCES)
	$(ASM) $(ASM_FLAGS) $(SRC_DIR)/main.asm $(OUTPUT)
	@echo "Assembled: $(OUTPUT)"

# Build for TI-84 CE (eZ80)
ce: $(BUILD_DIR)
	$(ASM) $(ASM_FLAGS) -DEZ80 $(SRC_DIR)/main.asm $(OUTPUT_CE)
	@echo "Build complete: $(OUTPUT_CE) (eZ80 version)"

# Run in emulator
run: $(OUTPUT)
	$(EMU) $(OUTPUT)

# Debug build
debug: ASM_FLAGS += $(DEBUG_FLAGS)
debug: $(OUTPUT)
	@echo "Debug build complete"

# Run tests
test: $(BUILD_DIR)
	@echo "Running unit tests..."
	python $(TOOLS_DIR)/test_vectors.py
	@echo "Tests complete"

# Performance profiling
profile: $(OUTPUT)
	@echo "Running performance profile..."
	$(EMU) --profile $(OUTPUT)

# Transfer to calculator
transfer: $(OUTPUT)
	@echo "Transferring to TI-84..."
	python $(TOOLS_DIR)/transfer_to_ti84.py $(OUTPUT)

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR)
	rm -f $(OUTPUT) $(OUTPUT_CE)
	rm -f *.bin *.o *.lst

# Show help
help:
	@echo "TI-84 RustChain Miner - Build Targets"
	@echo ""
	@echo "  all       - Build miner.8xp (default)"
	@echo "  ce        - Build for TI-84 CE (eZ80)"
	@echo "  run       - Run in CEmu emulator"
	@echo "  test      - Run unit tests"
	@echo "  debug     - Build with debug symbols"
	@echo "  profile   - Run performance profile"
	@echo "  transfer  - Transfer to physical TI-84"
	@echo "  clean     - Remove build artifacts"
	@echo "  help      - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - SPASM assembler (https://github.com/SPASMDev/SPASM)"
	@echo "  - CEmu emulator (https://github.com/CE-Programming/CEmu)"
	@echo "  - Python 3 (for tools)"

# Size analysis
size: $(OUTPUT)
	@echo "Memory usage analysis:"
	@echo "======================"
	@python $(TOOLS_DIR)/analyze_size.py $(OUTPUT)

# Documentation
docs:
	@echo "Generating documentation..."
	@python $(TOOLS_DIR)/generate_docs.py

# Install dependencies (Linux/macOS)
install-deps:
	@echo "Installing dependencies..."
	@echo "Please install manually:"
	@echo "  1. SPASM: git clone https://github.com/SPASMDev/SPASM && cd SPASM && make"
	@echo "  2. CEmu:  git clone https://github.com/CE-Programming/CEmu && cd CEmu && mkdir build && cd build && cmake .. && make"
	@echo "  3. Python deps: pip install -r requirements.txt"

# CI/CD build
ci: clean all test
	@echo "CI build complete"
