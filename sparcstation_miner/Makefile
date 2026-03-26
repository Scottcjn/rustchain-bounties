# Makefile for RustChain SPARCstation Miner
# 
# Targets: Sun SPARCstation IPX (1991), SPARC V7 @ 40MHz
# Build native on SPARCstation or cross-compile on x86

CC = gcc
CFLAGS = -Wall -O2 -static -no-pie -march=v7
LDFLAGS = -lsocket -lnsl

# Cross-compile toolchain (install via apt)
CROSS_PREFIX = sparc-linux-gnu-
CROSS_CC = $(CROSS_PREFIX)gcc
CROSS_CFLAGS = -Wall -O2 -static -no-pie -march=v7
CROSS_LDFLAGS = -static

TARGET = minersparc
SRC = miner.c

.PHONY: all native cross clean

all: native

# Native build on SPARCstation
native: $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

# Cross-compile from x86 Linux
cross: $(SRC)
	$(CROSS_CC) $(CROSS_CFLAGS) -o $(TARGET) $(SRC) $(CROSS_LDFLAGS)

# Debug build (native)
debug: $(SRC)
	$(CC) -Wall -g -O0 -DDEBUG -o $(TARGET)_debug $(SRC) $(LDFLAGS)

clean:
	rm -f $(TARGET) $(TARGET)_debug
