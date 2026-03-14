/*
 * Amiga 500 SHA-256 Miner - C Implementation
 * Target: vbcc or m68k-amigaos-gcc
 * 
 * Bounty: #412 - Port Miner to Amiga 500 (1987)
 * Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
 */

#include <stdint.h>
#include <string.h>
#include <stdio.h>

/* SHA-256 constants */
static const uint32_t K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
    0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
    0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
    0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
    0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

/* Initial hash values */
static const uint32_t H0[8] = {
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
};

/* Rotate right */
#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))

/* SHA-256 functions */
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22))
#define EP1(x) (ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25))
#define SIG0(x) (ROTR(x, 7) ^ ROTR(x, 18) ^ ((x) >> 3))
#define SIG1(x) (ROTR(x, 17) ^ ROTR(x, 19) ^ ((x) >> 10))

/* SHA-256 context */
typedef struct {
    uint32_t h[8];
    uint8_t data[64];
    uint32_t datalen;
    uint64_t bitlen;
} SHA256_CTX;

/* Transform a single 512-bit block */
static void sha256_transform(SHA256_CTX *ctx, const uint8_t *block) {
    uint32_t w[64];
    uint32_t a, b, c, d, e, f, g, h;
    uint32_t t1, t2;
    int i;
    
    /* Convert big-endian input to host format */
    for (i = 0; i < 16; i++) {
        w[i] = ((uint32_t)block[i*4] << 24) |
               ((uint32_t)block[i*4+1] << 16) |
               ((uint32_t)block[i*4+2] << 8) |
               ((uint32_t)block[i*4+3]);
    }
    
    /* Extend the sixteen 32-bit words into sixty-four 32-bit words */
    for (i = 16; i < 64; i++) {
        w[i] = SIG1(w[i-2]) + w[i-7] + SIG0(w[i-15]) + w[i-16];
    }
    
    /* Initialize working variables */
    a = ctx->h[0];
    b = ctx->h[1];
    c = ctx->h[2];
    d = ctx->h[3];
    e = ctx->h[4];
    f = ctx->h[5];
    g = ctx->h[6];
    h = ctx->h[7];
    
    /* Main loop - 64 rounds */
    for (i = 0; i < 64; i++) {
        t1 = h + EP1(e) + CH(e, f, g) + K[i] + w[i];
        t2 = EP0(a) + MAJ(a, b, c);
        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }
    
    /* Add working variables to hash state */
    ctx->h[0] += a;
    ctx->h[1] += b;
    ctx->h[2] += c;
    ctx->h[3] += d;
    ctx->h[4] += e;
    ctx->h[5] += f;
    ctx->h[6] += g;
    ctx->h[7] += h;
}

/* Initialize SHA-256 context */
static void sha256_init(SHA256_CTX *ctx) {
    memcpy(ctx->h, H0, sizeof(H0));
    ctx->datalen = 0;
    ctx->bitlen = 0;
}

/* Process input data */
static void sha256_update(SHA256_CTX *ctx, const uint8_t *data, size_t len) {
    size_t i;
    
    for (i = 0; i < len; i++) {
        ctx->data[ctx->datalen] = data[i];
        ctx->datalen++;
        
        if (ctx->datalen == 64) {
            sha256_transform(ctx, ctx->data);
            ctx->bitlen += 512;
            ctx->datalen = 0;
        }
    }
}

/* Finalize and produce hash */
static void sha256_final(SHA256_CTX *ctx, uint8_t *hash) {
    uint32_t i = ctx->datalen;
    int j;
    
    /* Pad the data */
    ctx->data[i++] = 0x80;
    
    if (i > 56) {
        while (i < 64) {
            ctx->data[i++] = 0x00;
        }
        sha256_transform(ctx, ctx->data);
        i = 0;
    }
    
    while (i < 56) {
        ctx->data[i++] = 0x00;
    }
    
    /* Append bit length (big-endian) */
    ctx->bitlen += ctx->datalen * 8;
    ctx->data[56] = (ctx->bitlen >> 56) & 0xff;
    ctx->data[57] = (ctx->bitlen >> 48) & 0xff;
    ctx->data[58] = (ctx->bitlen >> 40) & 0xff;
    ctx->data[59] = (ctx->bitlen >> 32) & 0xff;
    ctx->data[60] = (ctx->bitlen >> 24) & 0xff;
    ctx->data[61] = (ctx->bitlen >> 16) & 0xff;
    ctx->data[62] = (ctx->bitlen >> 8) & 0xff;
    ctx->data[63] = ctx->bitlen & 0xff;
    
    sha256_transform(ctx, ctx->data);
    
    /* Output hash (big-endian) */
    for (i = 0; i < 8; i++) {
        hash[i*4] = (ctx->h[i] >> 24) & 0xff;
        hash[i*4+1] = (ctx->h[i] >> 16) & 0xff;
        hash[i*4+2] = (ctx->h[i] >> 8) & 0xff;
        hash[i*4+3] = ctx->h[i] & 0xff;
    }
}

/* Convenience function for hashing a single buffer */
static void sha256(const uint8_t *data, size_t len, uint8_t *hash) {
    SHA256_CTX ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, data, len);
    sha256_final(&ctx, hash);
}

/* Simplified block header for Amiga demo */
typedef struct {
    uint32_t version;
    uint8_t prev_hash[16];  /* Truncated for demo */
    uint32_t timestamp;
    uint32_t difficulty;
    uint32_t nonce;
} BlockHeader;

/* Mine a block - find nonce that produces hash with leading zeros */
static uint32_t mine_block(const BlockHeader *header, uint32_t difficulty, 
                           uint8_t *out_hash) {
    BlockHeader block;
    uint8_t hash[32];
    uint32_t nonce = 0;
    int leading_zeros;
    int i;
    
    memcpy(&block, header, sizeof(BlockHeader));
    
    while (1) {
        block.nonce = nonce;
        
        /* Hash the block */
        sha256((uint8_t*)&block, sizeof(BlockHeader) - 4, hash);
        
        /* Count leading zero hex digits */
        leading_zeros = 0;
        for (i = 0; i < 32 && leading_zeros < difficulty; i++) {
            if ((hash[i] >> 4) == 0) leading_zeros++;
            else break;
            if ((hash[i] & 0x0f) == 0) leading_zeros++;
            else break;
        }
        
        if (leading_zeros >= difficulty) {
            memcpy(out_hash, hash, 32);
            return nonce;
        }
        
        nonce++;
        
        /* Progress indicator every 10000 hashes */
        if (nonce % 10000 == 0) {
            printf("\rMining... Nonce: %lu", nonce);
            fflush(stdout);
        }
    }
}

/* Print hash as hex string */
static void print_hash(const uint8_t *hash) {
    int i;
    for (i = 0; i < 32; i++) {
        printf("%02x", hash[i]);
    }
}

/* Main entry point */
int main(int argc, char *argv[]) {
    BlockHeader header;
    uint8_t hash[32];
    uint32_t nonce;
    int difficulty = 3;
    
    printf("==============================================================\n");
    printf("  Amiga 500 SHA-256 Miner - RustChain Port\n");
    printf("  Bounty #412 - LEGENDARY Tier (200 RTC / $20)\n");
    printf("==============================================================\n\n");
    
    printf("Target: Motorola 68000 @ 7.14 MHz\n");
    printf("Architecture: 16/32-bit hybrid (big-endian)\n");
    printf("RAM: 512 KB Chip RAM\n");
    printf("Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b\n\n");
    
    /* Create genesis block header */
    header.version = 1;
    memset(header.prev_hash, 0, sizeof(header.prev_hash));
    header.prev_hash[0] = 0x41;  /* "Amiga500Genesis" */
    header.prev_hash[1] = 0x6d;
    header.timestamp = 0;  /* Genesis timestamp */
    header.difficulty = 0x0000FFFF;
    
    printf("Mining with difficulty %d (leading zero hex digits)...\n\n", difficulty);
    
    /* Mine the block */
    nonce = mine_block(&header, difficulty, hash);
    
    printf("\n\n*** NONCE FOUND! ***\n");
    printf("Nonce: %lu (0x%08lX)\n", nonce, nonce);
    printf("Hash:  ");
    print_hash(hash);
    printf("\n\n");
    
    printf("==============================================================\n");
    printf("  BOUNTY CLAIM READY\n");
    printf("  Issue: #412 - Port Miner to Amiga 500 (1987)\n");
    printf("  Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b\n");
    printf("==============================================================\n");
    
    return 0;
}
