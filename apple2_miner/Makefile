# SPDX-License-Identifier: MIT

CC = cl65
CFLAGS = -t apple2enh -O

SRC = miner.c
OUT = miner.system

all: $(OUT)

$(OUT): $(SRC)
	$(CC) $(CFLAGS) -o $(OUT) $(SRC)

clean:
	rm -f $(OUT) *.o
