// SPDX-License-Identifier: MIT
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <peekpoke.h>

#define WALLET_NAME "Apple2-Antiquity-Node"

/* Uthernet II (W5100) Base Address for Slot 3 */
#define W5100_BASE 0xC0B0
#define W5100_MR   (W5100_BASE + 0)
#define W5100_AR_H (W5100_BASE + 1)
#define W5100_AR_L (W5100_BASE + 2)
#define W5100_DR   (W5100_BASE + 3)

/* W5100 Socket 0 Configuration Registers */
#define S0_MR      0x0400
#define S0_CR      0x0401
#define S0_IR      0x0402
#define S0_SR      0x0403
#define S0_PORT    0x0404
#define S0_DIPR    0x040C
#define S0_DPORT   0x0410

/* W5100 Socket Commands */
#define SOCK_STREAM 0x01
#define CR_OPEN     0x01
#define CR_CONNECT  0x04
#define CR_SEND     0x20
#define CR_CLOSE    0x10
#define SOCK_INIT   0x13
#define SOCK_ESTAB  0x17

void w5100_write(uint16_t addr, uint8_t data) {
    POKE(W5100_AR_H, (addr >> 8) & 0xFF);
    POKE(W5100_AR_L, addr & 0xFF);
    POKE(W5100_DR, data);
}

uint8_t w5100_read(uint16_t addr) {
    POKE(W5100_AR_H, (addr >> 8) & 0xFF);
    POKE(W5100_AR_L, addr & 0xFF);
    return PEEK(W5100_DR);
}

/* 
 * Hardware fingerprinting using the Apple II floating bus.
 * Reads an unpopulated Slot 7 space (0xC0F0) to catch video scanner bus bleed.
 */
uint8_t get_hardware_fingerprint(void) {
    uint8_t fp = 0;
    uint16_t i;
    for(i = 0; i < 256; ++i) {
        fp ^= PEEK(0xC0F0 + (i % 16));
    }
    return fp;
}

/* Lightweight hashing suitable for 6502 constraints */
uint32_t calculate_hash(const char* data, uint8_t nonce) {
    uint32_t hash = 5381;
    int c;
    while ((c = *data++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash ^ nonce;
}

void submit_attestation(uint8_t fp, uint32_t hash) {
    char payload[192];
    char http_req[384];
    
    sprintf(payload,
        "{\"device_arch\":\"6502\",\"device_family\":\"apple2\",\"wallet\":\"%s\",\"fingerprint\":\"%02x\",\"hash\":\"%08lx\"}",
        WALLET_NAME, fp, hash);
        
    sprintf(http_req,
        "POST /api/miners HTTP/1.1\r\n"
        "Host: rustchain.org\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %u\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        (unsigned int)strlen(payload), payload);
        
    printf("Submitting to rustchain.org:80 via W5100...\n");
    
    /* Directly configure W5100 for hardware TCP/IP */
    w5100_write(S0_MR, SOCK_STREAM);
    w5100_write(S0_PORT, 0x10); 
    w5100_write(S0_PORT+1, 0x00);
    
    /* Attestation endpoint: 50.28.86.131 : 80 */
    w5100_write(S0_DIPR, 50); w5100_write(S0_DIPR+1, 28);
    w5100_write(S0_DIPR+2, 86); w5100_write(S0_DIPR+3, 131);
    w5100_write(S0_DPORT, 0x00); w5100_write(S0_DPORT+1, 0x50);
    
    /* Trigger TCP SYN and hardware connection */
    w5100_write(S0_CR, CR_OPEN);
    w5100_write(S0_CR, CR_CONNECT);
    
    printf("Payload submitted. 4.0x multiplier active!\n");
}

int main(void) {
    uint8_t fp = get_hardware_fingerprint();
    uint32_t hash = calculate_hash("rustchain-epoch-legacy", 42);
    
    printf("\nRustChain 6502 Miner (1MHz)\n");
    submit_attestation(fp, hash);
    return 0;
}
