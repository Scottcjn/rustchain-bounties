/*
 * RustChain Miner for Commodore 64
 * Hardware fingerprinting header
 */

#ifndef FINGERPRINT_H
#define FINGERPRINT_H

#include <stdint.h>
#include <stddef.h>

/* Hardware fingerprint structure */
typedef struct {
    uint32_t cia_jitter;      /* CIA timer variance */
    uint32_t vic_raster;      /* VIC-II raster timing */
    uint32_t sid_offset;      /* SID frequency offset */
    uint16_t rom_checksum;    /* Kernal ROM checksum */
    uint32_t combined;        /* Combined fingerprint hash */
} HardwareFingerprint;

/* Function prototypes */
void fingerprint_init(HardwareFingerprint* fp);
void fingerprint_refresh(HardwareFingerprint* fp);
uint8_t fingerprint_is_emulated(const HardwareFingerprint* fp);
void fingerprint_generate_id(const HardwareFingerprint* fp, char* buffer, size_t size);

#endif /* FINGERPRINT_H */
