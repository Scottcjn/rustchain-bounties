/*
 * fingerprint.c - Hardware Fingerprinting Implementation
 * 
 * Measures Motorola 68000 instruction timing jitter
 * to create unique hardware fingerprint
 */

#include <stdint.h>
#include <string.h>
#include "fingerprint.h"

/* MFP Timer A register */
#define MFP_TIMER_A (*(volatile uint8_t*)0x00FFFA01)

/*
 * External assembly function to measure jitter
 */
extern uint32_t asm_measure_jitter(void);

/*
 * Read MFP timer value
 */
uint8_t fingerprint_read_timer(void) {
    return MFP_TIMER_A & 0x0F;
}

/*
 * Measure jitter using assembly routine
 */
uint32_t fingerprint_measure_jitter(void) {
    return asm_measure_jitter();
}

/*
 * Simple hash function (FNV-1a variant)
 */
uint32_t fingerprint_hash(const uint8_t *data, int len) {
    uint32_t hash = 2166136261u;
    int i;
    
    for (i = 0; i < len; i++) {
        hash ^= data[i];
        hash *= 16777619u;
    }
    
    return hash;
}

/*
 * Collect hardware fingerprint
 */
int fingerprint_collect(uint8_t *buffer, int size) {
    int i;
    uint32_t jitter;
    
    if (size < 256) {
        return -1;
    }
    
    /* Collect 256 jitter samples */
    for (i = 0; i < 256; i++) {
        jitter = fingerprint_measure_jitter();
        
        /* Store lower 8 bits */
        buffer[i] = (uint8_t)(jitter & 0xFF);
        
        /* Small delay to let timer drift */
        volatile int delay;
        for (delay = 0; delay < 100; delay++);
    }
    
    return 0;
}

/*
 * Generate hardware ID from fingerprint
 */
int fingerprint_generate_id(uint8_t *id) {
    uint8_t buffer[256];
    uint32_t hash1, hash2, hash3, hash4;
    
    /* Collect fresh fingerprint */
    fingerprint_collect(buffer, 256);
    
    /* Hash different sections */
    hash1 = fingerprint_hash(buffer, 64);
    hash2 = fingerprint_hash(buffer + 64, 64);
    hash3 = fingerprint_hash(buffer + 128, 64);
    hash4 = fingerprint_hash(buffer + 192, 64);
    
    /* Create 16-byte ID */
    id[0] = (hash1 >> 24) & 0xFF;
    id[1] = (hash1 >> 16) & 0xFF;
    id[2] = (hash1 >> 8) & 0xFF;
    id[3] = hash1 & 0xFF;
    
    id[4] = (hash2 >> 24) & 0xFF;
    id[5] = (hash2 >> 16) & 0xFF;
    id[6] = (hash2 >> 8) & 0xFF;
    id[7] = hash2 & 0xFF;
    
    id[8] = (hash3 >> 24) & 0xFF;
    id[9] = (hash3 >> 16) & 0xFF;
    id[10] = (hash3 >> 8) & 0xFF;
    id[11] = hash3 & 0xFF;
    
    id[12] = (hash4 >> 24) & 0xFF;
    id[13] = (hash4 >> 16) & 0xFF;
    id[14] = (hash4 >> 8) & 0xFF;
    id[15] = hash4 & 0xFF;
    
    return 0;
}

/*
 * Verify fingerprint against hardware ID
 */
int fingerprint_verify(const uint8_t *fingerprint, const uint8_t *id) {
    uint32_t hash1, hash2, hash3, hash4;
    uint8_t computed_id[16];
    
    /* Hash fingerprint sections */
    hash1 = fingerprint_hash(fingerprint, 64);
    hash2 = fingerprint_hash(fingerprint + 64, 64);
    hash3 = fingerprint_hash(fingerprint + 128, 64);
    hash4 = fingerprint_hash(fingerprint + 192, 64);
    
    /* Reconstruct ID */
    computed_id[0] = (hash1 >> 24) & 0xFF;
    computed_id[1] = (hash1 >> 16) & 0xFF;
    computed_id[2] = (hash1 >> 8) & 0xFF;
    computed_id[3] = hash1 & 0xFF;
    
    computed_id[4] = (hash2 >> 24) & 0xFF;
    computed_id[5] = (hash2 >> 16) & 0xFF;
    computed_id[6] = (hash2 >> 8) & 0xFF;
    computed_id[7] = hash2 & 0xFF;
    
    computed_id[8] = (hash3 >> 24) & 0xFF;
    computed_id[9] = (hash3 >> 16) & 0xFF;
    computed_id[10] = (hash3 >> 8) & 0xFF;
    computed_id[11] = hash3 & 0xFF;
    
    computed_id[12] = (hash4 >> 24) & 0xFF;
    computed_id[13] = (hash4 >> 16) & 0xFF;
    computed_id[14] = (hash4 >> 8) & 0xFF;
    computed_id[15] = hash4 & 0xFF;
    
    /* Compare IDs */
    if (memcmp(computed_id, id, 16) != 0) {
        return -1;  /* Mismatch */
    }
    
    return 0;  /* Match */
}
