# RUSTCHAIN APPLE II MINER
# Makefile for CC65 toolchain
#
# Target: Apple II (MOS 6502)
#

# CC65 tools
CC65 = cl65
CA65 = ca65
LD65 = ld65

# Directories
SRCDIR = src
ASMDIR = asm
INCDIR = include
OBJDIR = obj
DISKDIR = disk

# Target
TARGET = miner
OUTPUT = $(DISKDIR)/$(TARGET).dsk

# Source files
C_SOURCES = $(wildcard $(SRCDIR)/*.c)
ASM_SOURCES = $(wildcard $(ASMDIR)/*.s)

# Object files
C_OBJECTS = $(C_SOURCES:$(SRCDIR)/%.c=$(OBJDIR)/%.o)
ASM_OBJECTS = $(ASM_SOURCES:$(ASMDIR)/%.s=$(OBJDIR)/%.o)
OBJECTS = $(C_OBJECTS) $(ASM_OBJECTS)

# Compiler flags
CFLAGS = -t apple2 -Oi -I$(INCDIR)
ASFLAGS = -t apple2
LDFLAGS = -t apple2 -m $(OBJDIR)/$(TARGET).map

# Default target
all: $(OUTPUT)

# Create directories
$(OBJDIR):
	mkdir -p $(OBJDIR)

$(DISKDIR):
	mkdir -p $(DISKDIR)

# Compile C files
$(OBJDIR)/%.o: $(SRCDIR)/%.c | $(OBJDIR)
	$(CC65) $(CFLAGS) -c $< -o $@

# Assemble assembly files
$(OBJDIR)/%.o: $(ASMDIR)/%.s | $(OBJDIR)
	$(CA65) $(ASFLAGS) $< -o $@

# Link
$(DISKDIR)/$(TARGET): $(OBJECTS) | $(DISKDIR)
	$(LD65) $(LDFLAGS) -o $@ $(OBJECTS)

# Create disk image
$(OUTPUT): $(DISKDIR)/$(TARGET)
	@echo "Creating disk image..."
	@# For now, just copy the binary
	@# In production, would create proper .dsk or .po image
	cp $(DISKDIR)/$(TARGET) $(OUTPUT).bin
	@echo "Build complete: $(OUTPUT).bin"
	@echo "Note: Disk image creation requires additional tools (c2d, etc.)"

# Clean
clean:
	rm -rf $(OBJDIR)
	rm -f $(DISKDIR)/$(TARGET)*
	rm -f $(DISKDIR)/*.bin

# Run in emulator (if available)
run: $(OUTPUT)
	@echo "Starting emulator..."
	@# Windows: AppleWin
	@# macOS: KeG II
	@# Linux: MAME
	@echo "Manual step: Load $(OUTPUT).bin in your Apple II emulator"

# Install cc65 (Linux/macOS)
install-cc65:
	git clone https://github.com/cc65/cc65.git
	cd cc65 && make
	sudo make install

# Help
help:
	@echo "RustChain Apple II Miner - Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all          - Build the miner (default)"
	@echo "  clean        - Remove build artifacts"
	@echo "  run          - Run in emulator (manual step)"
	@echo "  install-cc65 - Install CC65 toolchain"
	@echo "  help         - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - CC65 compiler (cl65, ca65, ld65)"
	@echo "  - Apple II emulator (for testing)"
	@echo ""
	@echo "Usage:"
	@echo "  make          - Build the project"
	@echo "  make clean    - Clean build files"
	@echo "  make run      - Run in emulator"

.PHONY: all clean run help install-cc65
