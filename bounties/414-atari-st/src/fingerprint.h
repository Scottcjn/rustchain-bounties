/*
 * fingerprint.h - Hardware Fingerprinting
 * 
 * Motorola 68000 cycle-accurate timing and jitter measurement
 */

#ifndef _FINGERPRINT_H
#define _FINGERPRINT_H

#include <stdint.h>

/*
 * Collect hardware fingerprint
 * 
 * Parameters:
 *   buffer - Output buffer for fingerprint data
 *   size   - Size of buffer (should be 256)
 * 
 * Returns:
 *   0 on success, -1 on error
 */
int fingerprint_collect(uint8_t *buffer, int size);

/*
 * Generate unique hardware ID from fingerprint
 * 
 * Parameters:
 *   id - Output buffer for 16-byte hardware ID
 * 
 * Returns:
 *   0 on success, -1 on error
 */
int fingerprint_generate_id(uint8_t *id);

/*
 * Verify fingerprint matches hardware ID
 * 
 * Parameters:
 *   fingerprint - Current fingerprint data
 *   id          - Hardware ID to verify against
 * 
 * Returns:
 *   0 if match, -1 if mismatch
 */
int fingerprint_verify(const uint8_t *fingerprint, const uint8_t *id);

/*
 * Measure CPU jitter (assembly implementation)
 * 
 * Returns:
 *   Jitter measurement (timing variance)
 */
uint32_t fingerprint_measure_jitter(void);

/*
 * Read MFP timer (68901 chip)
 * 
 * Returns:
 *   Timer value (4 bits)
 */
uint8_t fingerprint_read_timer(void);

/*
 * Simple hash function for fingerprint
 * 
 * Parameters:
 *   data - Input data
 *   len  - Length of data
 * 
 * Returns:
 *   Hash value
 */
uint32_t fingerprint_hash(const uint8_t *data, int len);

#endif /* _FINGERPRINT_H */
