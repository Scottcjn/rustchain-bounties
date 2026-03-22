# SPDX-License-Identifier: MIT
# Makefile for RustChain Intel 386 Miner

CC = gcc
CFLAGS = -Wall -Wextra -O2 -march=i386 -std=c99
LDFLAGS = -static

# DOS / DJGPP target
TARGET_DOS = miner386.exe
SRC = miner.c

all: linux

linux: $(SRC)
	$(CC) $(CFLAGS) -o miner386 $(SRC) $(LDFLAGS)

dos: $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET_DOS) $(SRC) -lsocket

clean:
	rm -f miner386 miner386.exe *.o

.PHONY: all linux dos clean
