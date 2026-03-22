# SPDX-License-Identifier: MIT
# RustChain Apple II (6502) Miner — Build System
#
# Requirements:
#   CC65 compiler suite  https://cc65.github.io/
#   (cl65, ca65, ld65 must be on PATH)
#
# Targets:
#   make            Build miner.system (ProDOS SYS executable)
#   make dsk        Wrap miner.system in a bootable 140 KB ProDOS DSK image
#   make clean      Remove build artefacts

CC     = cl65
CFLAGS = -t apple2enh -O --cpu 65c02

SRC  = miner.c
OBJ  = miner.o
OUT  = miner.system
DSK  = rustchain_miner.dsk

all: $(OUT)

$(OUT): $(SRC)
	$(CC) $(CFLAGS) -o $@ $<

# Optional: wrap the .system file into a ProDOS floppy image
# Requires `applecommander` (https://applecommander.github.io/)
dsk: $(OUT)
	java -jar AppleCommander.jar -pro140 $(DSK) RUSTCHAIN
	java -jar AppleCommander.jar -p      $(DSK) MINER.SYSTEM sys < $(OUT)

clean:
	rm -f $(OUT) $(OBJ) $(DSK)
