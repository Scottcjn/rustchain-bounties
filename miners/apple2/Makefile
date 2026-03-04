# SPDX-License-Identifier: MIT
# Minimal build script for the Apple II RustChain miner (stub)
# Requires: CC65 toolchain installed and in PATH

PROGRAM  = rustchain_apple2_miner
TARGET   = apple2          # cc65 target platform

# Source files
SRC      = main.c
OBJ      = $(SRC:.c=.o)

# CC65 tools
CC       = cl65
CFLAGS   = -t $(TARGET) --static-locals -Oirs -g

all: $(PROGRAM).dsk

$(PROGRAM).o: $(SRC)
	$(CC) $(CFLAGS) -c $< -o $@

$(PROGRAM).bin: $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^

# Create Apple II DOS 3.3 disk image with the program
$(PROGRAM).dsk: $(PROGRAM).bin
	@echo "Creating Apple II disk image $(PROGRAM).dsk …"
	@cp $(PROGRAM).bin $(PROGRAM)
	@ciderpress -f $(PROGRAM).dsk -i $(PROGRAM)
	@rm -f $(PROGRAM)

clean:
	rm -f $(OBJ) $(PROGRAM).bin $(PROGRAM).dsk

.PHONY: all clean
