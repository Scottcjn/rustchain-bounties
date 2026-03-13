# Atari ST RustChain Miner - Makefile

# Compiler and assembler
CC = vbcc
AS = vasm
LD = vlink

# Flags
CFLAGS = -c -O -Iinclude
ASFLAGS = -o
LDFLAGS = -t tos -o

# Target
TARGET = miner.tos

# Source files
SRCS_C = src/main.c src/miner.c src/network.c src/fingerprint.c src/ui_gem.c
SRCS_ASM = asm/startup.s asm/fingerprint.s

# Object files
OBJS_C = $(SRCS_C:.c=.o)
OBJS_ASM = $(SRCS_ASM:.s=.o)
OBJS = $(OBJS_C) $(OBJS_ASM)

# Default target
all: $(TARGET)
	@echo "Build complete: $(TARGET)"
	@ls -l $(TARGET)

# Link
$(TARGET): $(OBJS)
	$(LD) $(LDFLAGS) $@ $(OBJS)

# Compile C files
%.o: %.c
	$(CC) $(CFLAGS) $< -o $@

# Assemble 68000 files
%.o: %.s
	$(AS) $(ASFLAGS) $@ $<

# Clean
clean:
	del *.o 2>nul
	del src\*.o 2>nul
	del asm\*.o 2>nul
	del $(TARGET) 2>nul
	@echo "Clean complete"

# Run in Hatari emulator
run: $(TARGET)
	hatari --compatible $(TARGET)

# Run in STE mode
ste: $(TARGET)
	hatari --ste --memory 4096 $(TARGET)

# Debug mode
debug: CFLAGS += -g
debug: $(TARGET)
	hatari --debug --log-file=debug.log $(TARGET)

# Create HAT package
hat: $(TARGET)
	@echo "Creating HAT package..."
	mkdir -p dist
	cp $(TARGET) dist/MINER.TOS
	cp resources/miner.inf dist/
	cd dist && zip -r ../miner.hat *
	@echo "Created: miner.hat"

# Create floppy disk image
disk: $(TARGET)
	@echo "Creating floppy disk image..."
	# Requires hms or similar tool
	@echo "Install 'hms' (Hatari Makefile System) for disk creation"

# Install dependencies (Windows)
install:
	@echo "Download vbcc from: https://github.com/serpent/vbcc/releases"
	@echo "Download vasm from: http://sun.hasenbraten.de/vasm/"
	@echo "Download Hatari from: https://hatari.tuxfamily.org/"
	@echo ""
	@echo "Add vbcc and vasm to your PATH"

# Show help
help:
	@echo "Atari ST Miner - Build Targets"
	@echo ""
	@echo "  make          - Build for standard ST (512 KB)"
	@echo "  make ste      - Build for STE (1-4 MB)"
	@echo "  make clean    - Remove build artifacts"
	@echo "  make run      - Run in Hatari emulator"
	@echo "  make debug    - Run in debug mode"
	@echo "  make hat      - Create HAT package"
	@echo "  make disk     - Create floppy image"
	@echo "  make install  - Show installation instructions"
	@echo "  make help     - Show this help"

.PHONY: all clean run ste debug hat disk install help
