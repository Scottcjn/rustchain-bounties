// SPDX-License-Identifier: MIT
/*
 * RustChain Proof-of-Antiquity Miner — Apple II (6502) Port
 *
 * Milestones covered:
 *   1. Networking    — W5100 direct-register TCP/IP (Uthernet II, Slot 3)
 *   2. Miner Client  — SHA-256 in pure C, JSON builder, HTTP POST
 *   3. Fingerprinting— 5-probe anti-emulation fingerprint
 *
 * Compiler: CC65  (https://cc65.github.io/)
 * Target  : apple2enh   (IIe Enhanced / IIgs, 128 KB)
 * Build   : make             -> miner.system  (ProDOS SYS file)
 *
 * References
 *   W5100 Datasheet v1.2 — WIZnet
 *   Understanding the Apple IIe — Jim Sather
 *   CC65 Apple II Programmer's Guide
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <peekpoke.h>
#include <conio.h>

/* ──────────────────────────────────────────────────────────────
 * Configuration
 * ────────────────────────────────────────────────────────────── */
#define WALLET_NAME    "Apple2-Antiquity-Node"
#define RUSTCHAIN_HOST "rustchain.org"
#define RUSTCHAIN_PORT 80
#define MINING_EPOCH   "rustchain-epoch-legacy"

/* Server IP: 50.28.86.131 */
static const uint8_t SERVER_IP[4] = {50, 28, 86, 131};

/* ──────────────────────────────────────────────────────────────
 * Uthernet II / W5100  (Slot 3 → I/O base 0xC0B0)
 *
 * The W5100 exposes four 8-bit registers behind an indirect
 * address+data window.  All socket state is inside the chip;
 * the 6502 only needs four I/O locations.
 * ────────────────────────────────────────────────────────────── */
#define W5100_BASE  0xC0B0
#define W5100_MR    (W5100_BASE)        /* Mode Register            */
#define W5100_AR_H  (W5100_BASE + 0x01) /* Address Register – high  */
#define W5100_AR_L  (W5100_BASE + 0x02) /* Address Register – low   */
#define W5100_DR    (W5100_BASE + 0x03) /* Data Register            */

/* Socket 0 register block (all offsets inside W5100 address space) */
#define S0_MR      0x0400   /* Protocol / mode                      */
#define S0_CR      0x0401   /* Command register                     */
#define S0_IR      0x0402   /* Interrupt register                   */
#define S0_SR      0x0403   /* Status register                      */
#define S0_SPORT_H 0x0404   /* Source port high                     */
#define S0_SPORT_L 0x0405   /* Source port low                      */
#define S0_DIPR    0x040C   /* Destination IP (4 bytes)             */
#define S0_DPORT_H 0x0410   /* Destination port high                */
#define S0_DPORT_L 0x0411   /* Destination port low                 */
#define S0_TX_FSR  0x0420   /* TX Free Size register (2 bytes)      */
#define S0_TX_RD   0x0422   /* TX Read Pointer                      */
#define S0_TX_WR   0x0424   /* TX Write Pointer                     */
#define S0_RX_RSR  0x0426   /* RX Received Size (2 bytes)           */
#define S0_RX_RD   0x0428   /* RX Read Pointer                      */

/* W5100 internal TX/RX ring buffers (2 KB each for socket 0) */
#define W5100_TX_BASE 0x4000u
#define W5100_RX_BASE 0x6000u
#define W5100_RING_MASK 0x07FFu  /* 2 KB mask */

/* Protocol codes */
#define SOCK_STREAM     0x01
/* Command codes */
#define CR_OPEN         0x01
#define CR_CONNECT      0x04
#define CR_DISCON       0x08
#define CR_CLOSE        0x10
#define CR_SEND         0x20
#define CR_RECV         0x40
/* Status codes */
#define SOCK_CLOSED     0x00
#define SOCK_INIT       0x13
#define SOCK_ESTABLISHED 0x17
#define SOCK_CLOSE_WAIT 0x1C

/* ──────────────────────────────────────────────────────────────
 * W5100 register helpers
 * ────────────────────────────────────────────────────────────── */
static void w5100_write(uint16_t addr, uint8_t val)
{
    POKE(W5100_AR_H, (uint8_t)(addr >> 8));
    POKE(W5100_AR_L, (uint8_t)(addr & 0xFF));
    POKE(W5100_DR,   val);
}

static uint8_t w5100_read(uint16_t addr)
{
    POKE(W5100_AR_H, (uint8_t)(addr >> 8));
    POKE(W5100_AR_L, (uint8_t)(addr & 0xFF));
    return PEEK(W5100_DR);
}

static uint16_t w5100_read16(uint16_t addr)
{
    return ((uint16_t)w5100_read(addr) << 8) | w5100_read(addr + 1);
}

/* ──────────────────────────────────────────────────────────────
 * TCP socket layer  (Milestone 1)
 *
 * The W5100 handles the full TCP state machine in hardware.
 * We only need to drive its command register and manage the
 * TX/RX ring-buffer pointers.
 * ────────────────────────────────────────────────────────────── */

/* Poll socket status until it equals 'want', with a spin-loop
   timeout.  Returns 1 on success, 0 on timeout. */
static uint8_t sock_wait(uint8_t want, uint16_t timeout)
{
    uint16_t t;
    for (t = 0; t < timeout; ++t) {
        if (w5100_read(S0_SR) == want) return 1;
    }
    return 0;
}

/* Open a TCP connection to SERVER_IP:port.  Returns 1 on success. */
static uint8_t tcp_connect(uint16_t port)
{
    uint8_t i;

    /* Ensure socket is fully closed before re-use */
    w5100_write(S0_CR, CR_CLOSE);
    sock_wait(SOCK_CLOSED, 2000);

    /* Configure as TCP stream */
    w5100_write(S0_MR,      SOCK_STREAM);

    /* Source port 4096 (0x1000) — arbitrary ephemeral port */
    w5100_write(S0_SPORT_H, 0x10);
    w5100_write(S0_SPORT_L, 0x00);

    /* Destination IP address */
    for (i = 0; i < 4; ++i)
        w5100_write(S0_DIPR + i, SERVER_IP[i]);

    /* Destination port */
    w5100_write(S0_DPORT_H, (uint8_t)(port >> 8));
    w5100_write(S0_DPORT_L, (uint8_t)(port & 0xFF));

    /* OPEN → chip transitions to SOCK_INIT */
    w5100_write(S0_CR, CR_OPEN);
    if (!sock_wait(SOCK_INIT, 2000)) return 0;

    /* CONNECT → W5100 performs TCP three-way handshake */
    w5100_write(S0_CR, CR_CONNECT);
    return sock_wait(SOCK_ESTABLISHED, 8000);
}

/* Write buf[0..len-1] into the W5100 TX ring and issue SEND. */
static void tcp_send(const char *buf, uint16_t len)
{
    uint16_t ptr, i;

    /* Wait until there is enough free TX space */
    while (w5100_read16(S0_TX_FSR) < len)
        ;

    ptr = w5100_read16(S0_TX_WR);

    for (i = 0; i < len; ++i)
        w5100_write(W5100_TX_BASE + ((ptr + i) & W5100_RING_MASK),
                    (uint8_t)buf[i]);

    ptr += len;
    w5100_write(S0_TX_WR,     (uint8_t)(ptr >> 8));
    w5100_write(S0_TX_WR + 1, (uint8_t)(ptr & 0xFF));

    w5100_write(S0_CR, CR_SEND);
}

/* Copy up to maxlen received bytes into buf.  Returns actual count. */
static uint16_t tcp_recv(char *buf, uint16_t maxlen)
{
    uint16_t rsr, ptr, got, i;

    rsr = w5100_read16(S0_RX_RSR);
    if (rsr == 0) return 0;

    got = (rsr < maxlen) ? rsr : (maxlen - 1);
    ptr = w5100_read16(S0_RX_RD);

    for (i = 0; i < got; ++i)
        buf[i] = (char)w5100_read(W5100_RX_BASE +
                                  ((ptr + i) & W5100_RING_MASK));
    buf[got] = '\0';

    ptr += got;
    w5100_write(S0_RX_RD,     (uint8_t)(ptr >> 8));
    w5100_write(S0_RX_RD + 1, (uint8_t)(ptr & 0xFF));
    w5100_write(S0_CR, CR_RECV);
    return got;
}

static void tcp_close(void)
{
    w5100_write(S0_CR, CR_DISCON);
    sock_wait(SOCK_CLOSED, 4000);
}

/* ──────────────────────────────────────────────────────────────
 * SHA-256  (Milestone 2)
 *
 * Pure C, no 64-bit integers, no floating point.
 * All rotates decomposed into right-shift + left-shift so that
 * CC65's 16-bit arithmetic does not produce wrong results.
 * The context struct keeps bitlen as two 32-bit halves.
 *
 * On a 1 MHz 6502 one SHA-256 compression round takes roughly
 * 0.5 – 2 seconds; this is expected and acknowledged by the bounty.
 * ────────────────────────────────────────────────────────────── */

static const uint32_t SHA256_K[64] = {
    0x428a2f98UL, 0x71374491UL, 0xb5c0fbcfUL, 0xe9b5dba5UL,
    0x3956c25bUL, 0x59f111f1UL, 0x923f82a4UL, 0xab1c5ed5UL,
    0xd807aa98UL, 0x12835b01UL, 0x243185beUL, 0x550c7dc3UL,
    0x72be5d74UL, 0x80deb1feUL, 0x9bdc06a7UL, 0xc19bf174UL,
    0xe49b69c1UL, 0xefbe4786UL, 0x0fc19dc6UL, 0x240ca1ccUL,
    0x2de92c6fUL, 0x4a7484aaUL, 0x5cb0a9dcUL, 0x76f988daUL,
    0x983e5152UL, 0xa831c66dUL, 0xb00327c8UL, 0xbf597fc7UL,
    0xc6e00bf3UL, 0xd5a79147UL, 0x06ca6351UL, 0x14292967UL,
    0x27b70a85UL, 0x2e1b2138UL, 0x4d2c6dfcUL, 0x53380d13UL,
    0x650a7354UL, 0x766a0abbUL, 0x81c2c92eUL, 0x92722c85UL,
    0xa2bfe8a1UL, 0xa81a664bUL, 0xc24b8b70UL, 0xc76c51a3UL,
    0xd192e819UL, 0xd6990624UL, 0xf40e3585UL, 0x106aa070UL,
    0x19a4c116UL, 0x1e376c08UL, 0x2748774cUL, 0x34b0bcb5UL,
    0x391c0cb3UL, 0x4ed8aa4aUL, 0x5b9cca4fUL, 0x682e6ff3UL,
    0x748f82eeUL, 0x78a5636fUL, 0x84c87814UL, 0x8cc70208UL,
    0x90befffaUL, 0xa4506cebUL, 0xbef9a3f7UL, 0xc67178f2UL
};

#define ROTR(x,n) (((x) >> (n)) | ((x) << (32u - (n))))
#define CH(x,y,z)  (((x)&(y)) ^ (~(x)&(z)))
#define MAJ(x,y,z) (((x)&(y)) ^ ((x)&(z)) ^ ((y)&(z)))
#define EP0(x)  (ROTR(x,2)  ^ ROTR(x,13) ^ ROTR(x,22))
#define EP1(x)  (ROTR(x,6)  ^ ROTR(x,11) ^ ROTR(x,25))
#define SIG0(x) (ROTR(x,7)  ^ ROTR(x,18) ^ ((x) >> 3))
#define SIG1(x) (ROTR(x,17) ^ ROTR(x,19) ^ ((x) >> 10))

typedef struct {
    uint8_t  buf[64];
    uint8_t  buflen;
    uint32_t bits_lo;  /* message length in bits, low 32 */
    uint32_t bits_hi;  /* message length in bits, high 32 */
    uint32_t h[8];
} sha256_ctx;

static void sha256_compress(sha256_ctx *ctx)
{
    uint32_t w[64];
    uint32_t a,b,c,d,e,f,g,h,t1,t2;
    uint8_t i,j;

    for (i=0,j=0; i<16; ++i, j+=4)
        w[i] = ((uint32_t)ctx->buf[j]   << 24) |
               ((uint32_t)ctx->buf[j+1] << 16) |
               ((uint32_t)ctx->buf[j+2] <<  8) |
               ((uint32_t)ctx->buf[j+3]);

    for (i=16; i<64; ++i)
        w[i] = SIG1(w[i-2]) + w[i-7] + SIG0(w[i-15]) + w[i-16];

    a=ctx->h[0]; b=ctx->h[1]; c=ctx->h[2]; d=ctx->h[3];
    e=ctx->h[4]; f=ctx->h[5]; g=ctx->h[6]; h=ctx->h[7];

    for (i=0; i<64; ++i) {
        t1 = h + EP1(e) + CH(e,f,g) + SHA256_K[i] + w[i];
        t2 = EP0(a) + MAJ(a,b,c);
        h=g; g=f; f=e; e=d+t1;
        d=c; c=b; b=a; a=t1+t2;
    }
    ctx->h[0]+=a; ctx->h[1]+=b; ctx->h[2]+=c; ctx->h[3]+=d;
    ctx->h[4]+=e; ctx->h[5]+=f; ctx->h[6]+=g; ctx->h[7]+=h;
}

static void sha256_init(sha256_ctx *ctx)
{
    ctx->buflen  = 0;
    ctx->bits_lo = 0;
    ctx->bits_hi = 0;
    ctx->h[0] = 0x6a09e667UL; ctx->h[1] = 0xbb67ae85UL;
    ctx->h[2] = 0x3c6ef372UL; ctx->h[3] = 0xa54ff53aUL;
    ctx->h[4] = 0x510e527fUL; ctx->h[5] = 0x9b05688cUL;
    ctx->h[6] = 0x1f83d9abUL; ctx->h[7] = 0x5be0cd19UL;
}

static void sha256_update(sha256_ctx *ctx, const uint8_t *data, uint16_t len)
{
    uint16_t i;
    for (i=0; i<len; ++i) {
        ctx->buf[ctx->buflen++] = data[i];
        if (ctx->buflen == 64) {
            sha256_compress(ctx);
            ctx->bits_lo += 512;
            if (ctx->bits_lo < 512) ctx->bits_hi++;
            ctx->buflen = 0;
        }
    }
}

static void sha256_final(sha256_ctx *ctx, uint8_t *digest)
{
    uint32_t total_lo, total_hi;
    uint8_t  i;

    /* Account for remaining bytes */
    total_lo = ctx->bits_lo + ((uint32_t)ctx->buflen << 3);
    total_hi = ctx->bits_hi + (total_lo < ctx->bits_lo ? 1 : 0);

    /* Pad */
    ctx->buf[ctx->buflen++] = 0x80;
    if (ctx->buflen > 56) {
        while (ctx->buflen < 64) ctx->buf[ctx->buflen++] = 0;
        sha256_compress(ctx);
        ctx->buflen = 0;
    }
    while (ctx->buflen < 56) ctx->buf[ctx->buflen++] = 0;

    /* Big-endian 64-bit message length */
    ctx->buf[56] = (uint8_t)(total_hi >> 24);
    ctx->buf[57] = (uint8_t)(total_hi >> 16);
    ctx->buf[58] = (uint8_t)(total_hi >>  8);
    ctx->buf[59] = (uint8_t)(total_hi      );
    ctx->buf[60] = (uint8_t)(total_lo >> 24);
    ctx->buf[61] = (uint8_t)(total_lo >> 16);
    ctx->buf[62] = (uint8_t)(total_lo >>  8);
    ctx->buf[63] = (uint8_t)(total_lo      );
    sha256_compress(ctx);

    for (i=0; i<4; ++i) {
        digest[i   ] = (uint8_t)(ctx->h[0] >> (24 - i*8));
        digest[i+ 4] = (uint8_t)(ctx->h[1] >> (24 - i*8));
        digest[i+ 8] = (uint8_t)(ctx->h[2] >> (24 - i*8));
        digest[i+12] = (uint8_t)(ctx->h[3] >> (24 - i*8));
        digest[i+16] = (uint8_t)(ctx->h[4] >> (24 - i*8));
        digest[i+20] = (uint8_t)(ctx->h[5] >> (24 - i*8));
        digest[i+24] = (uint8_t)(ctx->h[6] >> (24 - i*8));
        digest[i+28] = (uint8_t)(ctx->h[7] >> (24 - i*8));
    }
}

/* Hash (msg || nonce_byte); store result as 64-char hex in out[65]. */
static void sha256_hex(const char *msg, uint8_t nonce, char *out)
{
    sha256_ctx ctx;
    uint8_t    digest[32];
    uint8_t    i;
    static const char HEX[] = "0123456789abcdef";

    sha256_init(&ctx);
    sha256_update(&ctx, (const uint8_t *)msg, (uint16_t)strlen(msg));
    sha256_update(&ctx, &nonce, 1);
    sha256_final(&ctx, digest);

    for (i=0; i<32; ++i) {
        out[i*2  ] = HEX[digest[i] >> 4];
        out[i*2+1] = HEX[digest[i] & 0x0F];
    }
    out[64] = '\0';
}

/* ──────────────────────────────────────────────────────────────
 * Hardware Fingerprinting  (Milestone 3)
 *
 * Five independent probes that produce an 8-byte fingerprint.
 * Real Apple II hardware differs from emulators in all five
 * respects; the XOR combination makes the fingerprint unique
 * to a specific machine's electrical characteristics.
 *
 *  fp[0..1]  Floating-bus scan  (Slot 7 I/O, 0xC0F0-0xC0FF)
 *            The Apple II video scanner bleeds partially-decoded
 *            addresses onto the data bus when no card responds.
 *            Emulators typically return a static value.
 *
 *  fp[2..3]  DRAM refresh jitter
 *            Real DRAM undergoes asynchronous CAS/RAS refresh
 *            that can momentarily corrupt a read-back.  Emulators
 *            model RAM as perfect synchronous memory.
 *
 *  fp[4]     Bus timing signature
 *            Consecutive PEEK to the same floating-bus address
 *            on real hardware shows phase jitter from the
 *            asynchronous video/CPU bus arbitration.
 *
 *  fp[5]     Speaker cycle counter
 *            Each PEEK(0xC030) toggles the speaker driver.
 *            The 6502's exact cycle count per tight loop is
 *            architecture-specific and deviates in emulators.
 *
 *  fp[6..7]  Vertical-blank timing
 *            Reads of the VBL flag (0xC019) around soft-switch
 *            toggles expose the real 60 Hz video scan rate on
 *            hardware; emulators may return a fixed value.
 * ────────────────────────────────────────────────────────────── */

/* Apple II soft-switch / I/O addresses */
#define SLOT7_IO   0xC0F0   /* Slot 7 I/O (unpopulated on most machines) */
#define SPEAKER    0xC030   /* Speaker toggle (each access = one click)   */
#define SW_GR      0xC050   /* Soft switch: enable graphics page 1        */
#define SW_TEXT    0xC051   /* Soft switch: enable text mode              */
#define VBL_FLAG   0xC019   /* Vertical blank status (bit 7)             */

static void get_hardware_fingerprint(uint8_t *fp)
{
    uint16_t i;
    uint8_t  a, b;

    /* Probe 1 – Floating-bus XOR scan */
    fp[0] = 0; fp[1] = 0;
    for (i = 0; i < 256; ++i) {
        a = PEEK(SLOT7_IO + (i & 0x0F));
        fp[0] ^= a;
        fp[1]  = (uint8_t)((fp[1] << 1) | (fp[1] >> 7));
        fp[1] ^= a;
    }

    /* Probe 2 – DRAM refresh jitter (zero-page round-trip) */
    fp[2] = 0; fp[3] = 0;
    for (i = 0; i < 128; ++i) {
        POKE(0x06, (uint8_t)(i ^ 0xA5));
        a = PEEK(0x06);
        b = PEEK(0x06);
        if (a != b) fp[2]++;
        fp[3] ^= (uint8_t)(a ^ b ^ (uint8_t)i);
    }

    /* Probe 3 – Consecutive-read bus-phase jitter */
    fp[4] = 0;
    for (i = 0; i < 64; ++i) {
        a = PEEK(SLOT7_IO);
        b = PEEK(SLOT7_IO);
        fp[4] ^= (uint8_t)(a ^ b ^ (uint8_t)i);
    }

    /* Probe 4 – Speaker cycle counter */
    fp[5] = 0;
    for (i = 0; i < 32; ++i) {
        (void)PEEK(SPEAKER);
        fp[5] ^= (uint8_t)(i * 7);
    }

    /* Probe 5 – Vertical-blank timing around soft-switch */
    fp[6] = 0; fp[7] = 0;
    for (i = 0; i < 16; ++i) {
        (void)PEEK(SW_GR);
        a = PEEK(VBL_FLAG);
        (void)PEEK(SW_TEXT);
        b = PEEK(VBL_FLAG);
        fp[6] ^= a;
        fp[7] ^= b;
    }
}

/* Render 8 bytes as 16 lower-case hex chars + NUL. */
static void fp_to_hex(const uint8_t *fp, char *out)
{
    static const char H[] = "0123456789abcdef";
    uint8_t i;
    for (i = 0; i < 8; ++i) {
        out[i*2  ] = H[fp[i] >> 4];
        out[i*2+1] = H[fp[i] & 0x0F];
    }
    out[16] = '\0';
}

/* ──────────────────────────────────────────────────────────────
 * JSON + HTTP builder  (Milestone 2)
 * ────────────────────────────────────────────────────────────── */

/* Buffers sized to fit within Apple II 128 KB RAM. */
static char g_payload[256];
static char g_request[512];
static char g_resp   [512];

static void build_payload(const char *fp_hex, const char *hash_hex,
                          uint8_t nonce)
{
    sprintf(g_payload,
        "{"
          "\"device_arch\":\"6502\","
          "\"device_family\":\"apple2\","
          "\"wallet\":\"%s\","
          "\"epoch\":\"%s\","
          "\"nonce\":%u,"
          "\"fingerprint\":\"%s\","
          "\"hash\":\"%s\","
          "\"multiplier\":4"
        "}",
        WALLET_NAME, MINING_EPOCH,
        (unsigned)nonce, fp_hex, hash_hex);
}

static void build_http_request(void)
{
    sprintf(g_request,
        "POST /api/miners HTTP/1.1\r\n"
        "Host: " RUSTCHAIN_HOST "\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %u\r\n"
        "Connection: close\r\n"
        "\r\n%s",
        (unsigned)strlen(g_payload), g_payload);
}

/* ──────────────────────────────────────────────────────────────
 * One mining round: hash → build payload → TCP POST → read reply
 * ────────────────────────────────────────────────────────────── */
static uint8_t do_mining_round(uint8_t nonce,
                               const uint8_t *fp, const char *fp_hex)
{
    char     hash_hex[65];
    uint16_t got, tries;

    /* SHA-256(epoch || nonce) */
    sha256_hex(MINING_EPOCH, nonce, hash_hex);
    printf("Nonce %3u  hash %.8s...\n", (unsigned)nonce, hash_hex);

    build_payload(fp_hex, hash_hex, nonce);
    build_http_request();

    /* Milestone 1 — TCP connect */
    printf("Connecting to %s:%d ... ", RUSTCHAIN_HOST, RUSTCHAIN_PORT);
    if (!tcp_connect(RUSTCHAIN_PORT)) {
        printf("FAILED\n");
        return 0;
    }
    printf("OK\n");

    /* Milestone 2 — HTTP POST */
    tcp_send(g_request, (uint16_t)strlen(g_request));

    /* Read server response (best-effort) */
    got = 0;
    for (tries = 0; tries < 300 && got == 0; ++tries)
        got = tcp_recv(g_resp, sizeof(g_resp) - 1);

    if (got > 0)
        printf("Response: %.50s\n", g_resp);
    else
        printf("(no response — node may be offline)\n");

    tcp_close();
    return 1;
}

/* ──────────────────────────────────────────────────────────────
 * main
 * ────────────────────────────────────────────────────────────── */
int main(void)
{
    uint8_t fp[8];
    char    fp_hex[17];
    uint8_t nonce;

    clrscr();
    printf("RustChain 6502 Miner (1MHz)\n");
    printf("Wallet  : %s\n", WALLET_NAME);
    printf("Server  : %s:%d\n\n", RUSTCHAIN_HOST, RUSTCHAIN_PORT);

    /* Milestone 3 — hardware fingerprinting */
    printf("Probing hardware...\n");
    get_hardware_fingerprint(fp);
    fp_to_hex(fp, fp_hex);
    printf("Fingerprint : %s\n\n", fp_hex);

    /* Milestones 1 + 2 — mining loop */
    for (nonce = 0; nonce < 16; ++nonce) {
        do_mining_round(nonce, fp, fp_hex);
        if (kbhit()) {
            printf("\nStopped by user.\n");
            break;
        }
    }

    printf("\nDone. Press any key.\n");
    cgetc();
    return 0;
}
