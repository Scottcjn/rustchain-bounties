# SPDX-License-Identifier: MIT
CROSS = sh4-linux-gnu-
CC = $(CROSS)gcc
CFLAGS = -Wall -Wextra -O2 -static -no-pie
SRC = miner.c
TARGET = minerdc

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET) *.o

.PHONY: all clean
