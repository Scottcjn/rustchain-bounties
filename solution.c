/*
 * vintage-x86 miner: non-RDTSC timing-variance fallback for 486/386
 * C89 single-file implementation using RTC (CMOS) or PIT (8253/8254)
 * to produce clock-drift fingerprint without RDTSC.
 */

#include <stdint.h>
#include <string.h>
#include <time.h>

/* Port I/O for CMOS RTC (port 0x70/0x71) and PIT (0x40-0x43) */
#if defined(__linux__) || defined(__unix__)
#include <sys/io.h>
#define INB(x) inb(x)
#define OUTB(x,y) outb(y,x)
#elif defined(_WIN32)
#include <windows.h>
/* Windows does not allow user-mode port I/O; use QueryPerformanceCounter fallback */
#else
/* Assume GCC inline assembly for DOS/FreeDOS */
static inline uint8_t INB(uint16_t port) {
    uint8_t ret;
    __asm__ volatile("inb %1, %0" : "=a"(ret) : "dN"(port));
    return ret;
}
static inline void OUTB(uint16_t port, uint8_t val) {
    __asm__ volatile("outb %0, %1" : : "a"(val), "dN"(port));
}
#endif

/* Use RTC (CMOS) if available (most 486/386 have it) */
static uint8_t cmos_read(uint8_t reg) {
    OUTB(0x70, reg);
    return INB(0x71);
}

/* Wait for RTC update to ensure consistent reads */
static void rtc_wait_update(void) {
    while (cmos_read(0x0A) & 0x80);  /* UIP bit */
}

/* Read current RTC second (0-59) and fractional ticks from register 0x0B? */
/* Use PIT counter 2 for high-resolution timing */
static uint16_t pit_read_count(void) {
    OUTB(0x43, 0x82);  /* Latch counter 2 */
    uint8_t lo = INB(0x42);
    uint8_t hi = INB(0x42);
    return (uint16_t)(hi << 8) | lo;
}

/*
 * Timing variance measurement: measure PIT count over a short interval
 * by polling RTC second changes. This gives a clock-drift signature
 * based on CPU speed and interrupt latency.
 */
int measure_timing_variance(uint32_t *samples, int nsamples) {
    int i;
    uint8_t last_sec = 0;
    uint16_t tick_start, tick_end;
    uint32_t delta;

    /* Wait for RTC second boundary */
    rtc_wait_update();
    last_sec = cmos_read(0x00);  /* seconds */
    while (cmos_read(0x00) == last_sec) {
        /* busy wait */
    }

    for (i = 0; i < nsamples; i++) {
        tick_start = pit_read_count();
        /* Wait for next second change */
        rtc_wait_update();
        last_sec = cmos_read(0x00);
        while (cmos_read(0x00) == last_sec) {
            /* busy wait */
        }
        tick_end = pit_read_count();
        delta = (uint32_t)(tick_start - tick_end);  /* PIT counts down */
        samples[i] = delta;
    }
    return 0;
}

/* Fallback: if no port I/O, use clock() or time() */
int measure_timing_variance_fallback(uint32_t *samples, int nsamples) {
    int i;
    clock_t start, end;
    for (i = 0; i < nsamples; i++) {
        start = clock();
        /* Busy wait for a measurable delay */
        while ((clock() - start) < CLOCKS_PER_SEC / 50) {
            /* spin */
        }
        end = clock();
        samples[i] = (uint32_t)(end - start);
    }
    return 0;
}

/* Entry point: detect RDTSC availability (via CPUID or try/catch) */
int get_timing_samples(uint32_t *samples, int nsamples) {
    /* Try RDTSC first (if available) - omitted for brevity */
    /* If RDTSC fails, use RTC/PIT or clock fallback */
#if defined(__linux__) || defined(__unix__) || defined(__DOS__)
    if (ioperm(0x70, 2, 1) == 0 && ioperm(0x40, 4, 1) == 0) {
        return measure_timing_variance(samples, nsamples);
    }
#endif
    return measure_timing_variance_fallback(samples, nsamples);
}