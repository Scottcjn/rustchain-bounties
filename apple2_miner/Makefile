
CC = sh4-unknown-linux-gnu-gcc
CFLAGS = -O3 -m4a-nofpu
LDFLAGS = -static

miner: miner.c
	$(CC) $(CFLAGS) -o miner miner.c $(LDFLAGS)

clean:
	rm -f miner
