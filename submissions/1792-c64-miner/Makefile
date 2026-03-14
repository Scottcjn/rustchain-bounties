# RustChain Miner for Commodore 64
# Makefile for cc65 toolchain

# Target
TARGET = miner
PRG = $(TARGET).prg

# Compiler and tools
CC = cl65
AS = ca65
LD = ld65

# Target system
TARGET_SYS = c64

# Source files
SRCS = src/miner.c \
       src/network.c \
       src/fingerprint.c \
       src/ui.c \
       src/json.c

# Object files
OBJS = $(SRCS:.c=.o)

# Compiler flags
CFLAGS = -t $(TARGET_SYS) \
         -O2 \
         --cpu 6510 \
         -Wall \
         -Wextra

# Linker flags
LDFLAGS = -t $(TARGET_SYS) \
          -m $(TARGET).map \
          -C c64.cfg

# Default target
all: $(PRG)

# Link program
$(PRG): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

# Compile source files
%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $<

# Assembly files (if any)
%.o: %.s
	$(AS) -t $(TARGET_SYS) -o $@ $<

# Clean
clean:
	rm -f $(OBJS) $(PRG) $(TARGET).map

# Install to VICE emulator directory
install: $(PRG)
	cp $(PRG) ~/vice-c64/

# Run in VICE
run: $(PRG)
	x64 $(PRG)

# Build with debug symbols
debug: CFLAGS += -g
debug: $(PRG)

# Build with Userport+ESP32 network driver
userport: CFLAGS += -DUSE_USERPORT_ESP32
userport: $(PRG)

# Help
help:
	@echo "RustChain C64 Miner Build Targets:"
	@echo "  all      - Build miner.prg (default)"
	@echo "  clean    - Remove build artifacts"
	@echo "  install  - Copy to VICE directory"
	@echo "  run      - Build and run in VICE"
	@echo "  debug    - Build with debug symbols"
	@echo "  userport - Build with Userport+ESP32 driver"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - cc65 compiler suite"
	@echo "  - VICE emulator (optional, for testing)"

.PHONY: all clean install run debug userport help
