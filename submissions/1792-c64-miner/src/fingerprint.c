/*
 * RustChain Miner for Commodore 64
 * Hardware fingerprinting - collects unique hardware signatures
 */

#include <stdio.h>
#include <string.h>
#include <cbm.h>
#include <peekpoke.h>

#include "fingerprint.h"

/* ============================================================================
 * CIA Timer Constants
 * ============================================================================ */

#define CIA1_LO 0xDC04  /* Timer 1 low byte */
#define CIA1_HI 0xDC05  /* Timer 1 high byte */
#define CIA1_CRB 0xDC0F /* Control register B */

/* ============================================================================
 * VIC-II Constants
 * ============================================================================ */

#define VIC_RASTER 0xD012
#define VIC_CTRL1 0xD011

/* ============================================================================
 * SID Constants
 * ============================================================================ */

#define SID_FREQ_LO 0xD400
#define SID_FREQ_HI 0xD401
#define SID_CTRL 0xD404

/* ============================================================================
 * ROM Constants
 * ============================================================================ */

#define KERNAL_START 0xE000
#define KERNAL_END 0xFFFF
#define KERNAL_SIZE (KERNAL_END - KERNAL_START + 1)

/* ============================================================================
 * Forward Declarations
 * ============================================================================ */

static uint32_t measure_cia_jitter(void);
static uint32_t measure_vic_raster(void);
static uint32_t measure_sid_offset(void);
static uint16_t calculate_rom_checksum(void);

/* ============================================================================
 * Public API
 * ============================================================================ */

void fingerprint_init(HardwareFingerprint* fp)
{
    if (!fp) {
        return;
    }
    
    memset(fp, 0, sizeof(HardwareFingerprint));
    
    /* Initial measurement */
    fingerprint_refresh(fp);
}

void fingerprint_refresh(HardwareFingerprint* fp)
{
    if (!fp) {
        return;
    }
    
    /* Measure CIA timer jitter */
    fp->cia_jitter = measure_cia_jitter();
    
    /* Measure VIC-II raster timing */
    fp->vic_raster = measure_vic_raster();
    
    /* Measure SID frequency offset */
    fp->sid_offset = measure_sid_offset();
    
    /* Calculate Kernal ROM checksum */
    fp->rom_checksum = calculate_rom_checksum();
    
    /* Combined fingerprint */
    fp->combined = fp->cia_jitter ^ fp->vic_raster ^ 
                   fp->sid_offset ^ ((uint32_t)fp->rom_checksum << 16);
}

/* ============================================================================
 * CIA Timer Jitter Measurement
 * ============================================================================ */

static uint32_t measure_cia_jitter(void)
{
    uint8_t lo1, hi1, lo2, hi2;
    uint32_t delta1, delta2, jitter;
    uint8_t i;
    uint32_t total_jitter = 0;
    
    /* Configure CIA timer 1 */
    POKE(CIA1_CRB, 0x01); /* Free run mode */
    
    /* Take multiple measurements to capture jitter */
    for (i = 0; i < 10; i++) {
        /* Read timer twice in quick succession */
        hi1 = PEEK(CIA1_HI);
        lo1 = PEEK(CIA1_LO);
        
        hi2 = PEEK(CIA1_HI);
        lo2 = PEEK(CIA1_LO);
        
        /* Calculate delta */
        delta1 = ((uint32_t)hi1 << 8) | lo1;
        delta2 = ((uint32_t)hi2 << 8) | lo2;
        
        /* Jitter is the variance in timing */
        if (delta2 > delta1) {
            jitter = delta2 - delta1;
        } else {
            jitter = delta1 - delta2;
        }
        
        total_jitter += jitter;
    }
    
    /* Return average jitter */
    return total_jitter / 10;
}

/* ============================================================================
 * VIC-II Raster Timing Measurement
 * ============================================================================ */

static uint32_t measure_vic_raster(void)
{
    uint8_t raster1, raster2;
    uint32_t cycles;
    uint32_t total_cycles = 0;
    uint8_t i;
    
    /* Measure cycles between raster lines */
    for (i = 0; i < 10; i++) {
        /* Wait for raster line 100 */
        while (PEEK(VIC_RASTER) != 100) {
            /* Wait */
        }
        
        /* Count cycles until line 101 */
        cycles = 0;
        while (PEEK(VIC_RASTER) != 101) {
            cycles++;
            /* Prevent overflow */
            if (cycles > 1000) break;
        }
        
        total_cycles += cycles;
    }
    
    /* Average cycles per raster line */
    /* Real hardware has slight variance due to analog components */
    return total_cycles / 10;
}

/* ============================================================================
 * SID Frequency Offset Measurement
 * ============================================================================ */

static uint32_t measure_sid_offset(void)
{
    uint16_t freq_actual;
    uint16_t freq_expected = 0x0000;
    uint32_t offset;
    
    /* Read SID frequency registers */
    /* Note: Some SID registers return different values on read vs write */
    /* This is chip-specific behavior */
    
    POKE(SID_FREQ_LO, 0x00);
    POKE(SID_FREQ_HI, 0x00);
    
    /* Read back - some chips return different values */
    freq_actual = (PEEK(SID_FREQ_HI) << 8) | PEEK(SID_FREQ_LO);
    
    /* Calculate offset from expected */
    if (freq_actual > freq_expected) {
        offset = freq_actual - freq_expected;
    } else {
        offset = freq_expected - freq_actual;
    }
    
    /* Also test SID control register behavior */
    POKE(SID_CTRL, 0x00);
    offset += PEEK(SID_CTRL);
    
    return offset;
}

/* ============================================================================
 * Kernal ROM Checksum
 * ============================================================================ */

static uint16_t calculate_rom_checksum(void)
{
    uint16_t checksum = 0;
    uint16_t addr;
    
    /* Sum all bytes in Kernal ROM */
    for (addr = KERNAL_START; addr <= KERNAL_END; addr++) {
        checksum += PEEK(addr);
    }
    
    return checksum;
}

/* ============================================================================
 * Anti-Emulation Checks
 * ============================================================================ */

uint8_t fingerprint_is_emulated(const HardwareFingerprint* fp)
{
    uint8_t emulated = 0;
    
    if (!fp) {
        return 1; /* Assume emulated if no fingerprint */
    }
    
    /* Check 1: CIA jitter should have some variance */
    /* Emulators often have perfect timing */
    if (fp->cia_jitter < 10) {
        emulated = 1;
    }
    
    /* Check 2: VIC-II raster timing should be ~63-65 cycles */
    /* Emulators may have exact values */
    if (fp->vic_raster == 64) {
        /* Could be real or very good emulation */
        /* Check for analog variance */
    } else if (fp->vic_raster < 60 || fp->vic_raster > 70) {
        emulated = 1;
    }
    
    /* Check 3: SID readback should show chip-specific behavior */
    /* Most emulators don't emulate this perfectly */
    if (fp->sid_offset == 0) {
        emulated = 1;
    }
    
    /* Check 4: ROM checksum should match known Kernal versions */
    /* Invalid checksums indicate modification or emulation */
    if (fp->rom_checksum == 0 || fp->rom_checksum == 0xFFFF) {
        emulated = 1;
    }
    
    return emulated;
}

/* ============================================================================
 * Hardware ID Generation
 * ============================================================================ */

void fingerprint_generate_id(const HardwareFingerprint* fp, char* buffer, size_t size)
{
    if (!fp || !buffer || size < 17) {
        return;
    }
    
    /* Generate hex ID from combined fingerprint */
    snprintf(buffer, size, "%08X%08X",
             (unsigned int)(fp->combined >> 16),
             (unsigned int)(fp->combined & 0xFFFF));
}
