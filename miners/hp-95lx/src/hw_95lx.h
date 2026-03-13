/*
 * hw_95lx.h - HP 95LX hardware detection
 * 
 * Detects HP 95LX-specific hardware and differentiates
 * from emulators and other DOS platforms.
 */

#ifndef HW_95LX_H
#define HW_95LX_H

/* HP 95LX hardware detection */
int hw_95lx_detect(void);

/* Check if running on emulator (returns 1 if emulator, 0 if real hardware) */
int hw_95lx_is_emulator(void);

/* Get hardware information */
const char* hw_95lx_get_cpu_name(void);
int hw_95lx_get_cpu_speed_mhz(void);
int hw_95lx_get_memory_kb(void);

/* Hardware fingerprinting (for attestation) */
int hw_95lx_get_fingerprint(char *buf, int max_len);

/* Timer functions */
unsigned long get_timer_ticks(void);

#endif /* HW_95LX_H */
