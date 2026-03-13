/*
 * RUSTCHAIN APPLE II MINER
 * Entropy Collection Module
 * 
 * Collects hardware entropy from unique Apple II characteristics
 */

#include <stdio.h>
#include <string.h>
#include <apple2.h>
#include "rustchain.h"

/* External references to assembly routines */
extern unsigned char read_floating_bus(void);
extern void delay_cycles(unsigned int cycles);

/**
 * Initialize entropy structure
 */
void entropy_init(Apple2Entropy *e) {
    memset(e, 0, sizeof(Apple2Entropy));
}

/**
 * Collect ROM information
 * Apple II ROM is at 0xD000-0xFFFF
 */
void entropy_collect_rom(Apple2Entropy *e) {
    unsigned char far *rom = (unsigned char far *)0xD000;
    int i;
    
    /* Read ROM date (typically at 0xD000-0xD007) */
    for (i = 0; i < 8 && i < 8; i++) {
        e->rom_date[i] = rom[i];
    }
    
    /* ROM version indicator */
    e->rom_version = rom[0xFF];  /* Last byte of ROM page */
}

/**
 * Collect memory configuration
 */
void entropy_collect_memory(Apple2Entropy *e) {
    /* Detect RAM size by testing memory */
    unsigned char far *test_mem;
    unsigned char original, test_val;
    
    /* Test for language card (extends RAM to 64KB+) */
    test_mem = (unsigned char far *)0xC000;
    original = *test_mem;
    
    /* Try to write and read back */
    *test_mem = 0xAA;
    test_val = *test_mem;
    *test_mem = original;  /* Restore */
    
    if (test_val == 0xAA) {
        e->has_language_card = 1;
        e->ram_size_kb = 64;
    } else {
        e->has_language_card = 0;
        e->ram_size_kb = 48;  /* Standard IIe */
    }
}

/**
 * Collect timer entropy
 * Uses Apple II's unique timer behavior
 */
void entropy_collect_timer(Apple2Entropy *e) {
    int i, j;
    unsigned char dummy;
    
    for (i = 0; i < TIMER_SAMPLE_COUNT; i++) {
        /* Read keyboard strobe for timing variance */
        dummy = *((unsigned char *)KBD);
        
        /* Small delay using busy loop */
        for (j = 0; j < 100; j++) {
            __asm__("nop");
        }
        
        /* Capture timer value (simulated via loop count) */
        e->timer_samples[i] = (unsigned int)dummy << 8 | (unsigned int)j;
    }
}

/**
 * Collect video information
 */
void entropy_collect_video(Apple2Entropy *e) {
    /* Detect video mode via soft switches */
    unsigned char *video_mem = (unsigned char *)TEXT_BASE;
    
    /* Check current text mode */
    e->video_mode = 0;  /* Default text mode */
    
    /* Test for 80-column card */
    /* 80-column firmware at 0xC300 */
    e->has_80col = (*((unsigned char *)0xC300) != 0xFF) ? 1 : 0;
}

/**
 * Collect floating bus signature
 * This is UNIQUE to each Apple II motherboard
 * The floating bus behavior differs due to analog characteristics
 */
void entropy_collect_floating_bus(Apple2Entropy *e) {
    e->floating_bus_value = read_floating_bus();
}

/**
 * Collect keyboard timing entropy
 * Keyboard read timing has analog variance
 */
void entropy_collect_keyboard(Apple2Entropy *e) {
    int i;
    unsigned char dummy;
    
    /* Clear keyboard strobe */
    dummy = *((unsigned char *)KBD_STROBE);
    
    /* Sample keyboard timing */
    for (i = 0; i < 8; i++) {
        /* Read keyboard register multiple times */
        e->keyboard_strobe[i] = *((unsigned char *)KBD);
        
        /* Small delay */
        delay_cycles(100);
    }
}

/**
 * Generate entropy hash
 * Simplified hash suitable for 6502
 */
void entropy_generate_hash(Apple2Entropy *e) {
    uint32_t h[4] = {0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476};
    int i, j;
    unsigned char *ptr;
    
    /* Mix ROM data */
    for (i = 0; i < 8; i++) {
        h[0] ^= (uint32_t)e->rom_date[i] << ((i % 4) * 8);
        h[0] = (h[0] << 5) | (h[0] >> 27);
    }
    
    h[1] ^= e->rom_version;
    h[1] ^= e->ram_size_kb;
    h[1] = (h[1] << 7) | (h[1] >> 25);
    
    /* Mix timer samples */
    for (i = 0; i < TIMER_SAMPLE_COUNT; i++) {
        h[2] ^= e->timer_samples[i];
        h[2] = (h[2] << 3) | (h[2] >> 29);
    }
    
    /* Mix floating bus and keyboard */
    h[3] ^= e->floating_bus_value;
    for (i = 0; i < 8; i++) {
        h[3] ^= ((uint32_t)e->keyboard_strobe[i]) << ((i % 4) * 8);
    }
    
    /* Mix rounds */
    for (j = 0; j < 8; j++) {
        h[0] += h[1];
        h[1] = (h[1] << 13) | (h[1] >> 19);
        h[2] += h[3];
        h[3] = (h[3] << 17) | (h[3] >> 15);
        h[0] ^= h[3];
        h[2] ^= h[1];
    }
    
    /* Store 32-byte hash */
    for (i = 0; i < 4; i++) {
        ptr = (unsigned char *)&h[i];
        e->hash[i*4 + 0] = ptr[0];
        e->hash[i*4 + 1] = ptr[1];
        e->hash[i*4 + 2] = ptr[2];
        e->hash[i*4 + 3] = ptr[3];
        
        /* Duplicate with XOR for 32 bytes */
        e->hash[16 + i*4 + 0] = ptr[0] ^ 0xAA;
        e->hash[16 + i*4 + 1] = ptr[1] ^ 0x55;
        e->hash[16 + i*4 + 2] = ptr[2] ^ 0xAA;
        e->hash[16 + i*4 + 3] = ptr[3] ^ 0x55;
    }
}

/**
 * Complete entropy collection
 */
void entropy_init(Apple2Entropy *e) {
    entropy_init(e);
    entropy_collect_rom(e);
    entropy_collect_memory(e);
    entropy_collect_timer(e);
    entropy_collect_video(e);
    entropy_collect_floating_bus(e);
    entropy_collect_keyboard(e);
    entropy_generate_hash(e);
}
