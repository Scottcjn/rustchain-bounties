/*
 * RustChain Miner for Commodore 64
 * Main miner logic and attestation flow
 * 
 * Target: MOS 6510 @ 1.023 MHz, 64 KB RAM
 * Compiler: cc65
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <cbm.h>
#include <peekpoke.h>

#include "miner.h"
#include "network.h"
#include "fingerprint.h"
#include "ui.h"
#include "json.h"

/* ============================================================================
 * Constants and Configuration
 * ============================================================================ */

#define MINER_VERSION "0.1.0"
#define ATTESTATION_INTERVAL 600  /* 10 minutes in seconds */
#define API_ENDPOINT "rustchain.org"
#define API_PORT 80
#define API_PATH "/api/attest"

/* Memory configuration */
#define SCREEN_RAM 0x0400
#define COLOR_RAM 0xD800
#define ZERO_PAGE_START 0x00FA

/* VIC-II registers */
#define VIC_CTRL1 POKE(0xD011, val)
#define VIC_RASTER PEEK(0xD012)

/* CIA registers */
#define CIA1_LO 0xDC04
#define CIA1_HI 0xDC05

/* ============================================================================
 * Global State
 * ============================================================================ */

typedef struct {
    uint8_t initialized;
    uint8_t network_ready;
    uint8_t wallet_set;
    uint32_t last_attest;
    uint32_t epoch_start;
    float earned_rtc;
    uint16_t attestation_count;
    char wallet[32];
    char miner_id[32];
} MinerState;

static MinerState g_miner;

/* Hardware fingerprint */
static HardwareFingerprint g_hw_fp;

/* Network buffer (shared) */
static uint8_t g_net_buffer[NET_BUFFER_SIZE];

/* ============================================================================
 * Forward Declarations
 * ============================================================================ */

static void init_miner(void);
static void main_loop(void);
static uint8_t perform_attestation(void);
static void build_attestation_payload(char* buffer, size_t size);
static uint8_t parse_response(const char* response, char* error, size_t error_size);
static void update_display(void);
static void handle_input(void);
static uint32_t get_timestamp(void);
static void wait_epoch(void);

/* ============================================================================
 * Initialization
 * ============================================================================ */

static void init_miner(void)
{
    /* Clear state */
    memset(&g_miner, 0, sizeof(g_miner));
    memset(&g_hw_fp, 0, sizeof(g_hw_fp));
    
    /* Initialize display */
    ui_init();
    ui_show_splash(MINER_VERSION);
    
    /* Initialize hardware fingerprinting */
    fingerprint_init(&g_hw_fp);
    
    /* Generate miner ID from hardware fingerprint */
    sprintf(g_miner.miner_id, "c64-%04X%04X", 
            g_hw_fp.cia_jitter & 0xFFFF,
            g_hw_fp.vic_raster & 0xFFFF);
    
    /* Initialize network */
    ui_show_status("INITIALIZING NETWORK...");
    if (network_init() == 0) {
        g_miner.network_ready = 1;
        ui_show_status("NETWORK READY");
    } else {
        ui_show_status("NETWORK FAILED");
        /* Continue in offline mode */
    }
    
    /* Load wallet from storage (or prompt) */
    ui_show_status("LOADING WALLET...");
    /* TODO: Load from EEPROM or prompt user */
    strcpy(g_miner.wallet, "RTC4325af95d26d59c3ef025963656d22af638bb96b");
    g_miner.wallet_set = 1;
    
    g_miner.initialized = 1;
    g_miner.epoch_start = get_timestamp();
    
    /* Clear screen and show main UI */
    ui_clear();
    ui_draw_main_screen();
}

/* ============================================================================
 * Main Loop
 * ============================================================================ */

static void main_loop(void)
{
    uint32_t current_time;
    uint32_t elapsed;
    
    while (1) {
        /* Handle keyboard input */
        handle_input();
        
        /* Check if it's time for attestation */
        current_time = get_timestamp();
        elapsed = (current_time - g_miner.epoch_start) / 100; /* Approximate seconds */
        
        if (elapsed >= ATTESTATION_INTERVAL) {
            ui_show_status("ATTESTING...");
            
            if (perform_attestation()) {
                g_miner.attestation_count++;
                g_miner.earned_rtc += 0.0042f; /* Base reward * 4.0 multiplier */
                g_miner.epoch_start = current_time;
                ui_show_status("ATTESTATION OK");
            } else {
                ui_show_status("ATTEST FAILED");
            }
        }
        
        /* Update display */
        update_display();
        
        /* Small delay to avoid busy-waiting */
        /* Use VIC-II raster wait for cycle-accurate timing */
        while (VIC_RASTER < 50) {
            /* Wait for raster line 50 */
        }
    }
}

/* ============================================================================
 * Attestation Logic
 * ============================================================================ */

static uint8_t perform_attestation(void)
{
    char payload[512];
    char response[256];
    char error[64];
    int16_t status;
    
    /* Refresh hardware fingerprint */
    fingerprint_refresh(&g_hw_fp);
    
    /* Build JSON payload */
    build_attestation_payload(payload, sizeof(payload));
    
    /* Send HTTP POST */
    status = network_post(API_ENDPOINT, API_PORT, API_PATH, 
                         payload, strlen(payload),
                         (char*)g_net_buffer, sizeof(g_net_buffer));
    
    if (status < 0) {
        return 0; /* Network error */
    }
    
    /* Parse response */
    strncpy((char*)g_net_buffer, response, sizeof(response) - 1);
    response[sizeof(response) - 1] = '\0';
    
    if (!parse_response(response, error, sizeof(error))) {
        return 0; /* Parse error */
    }
    
    g_miner.last_attest = get_timestamp();
    return 1;
}

static void build_attestation_payload(char* buffer, size_t size)
{
    char fingerprint_hex[65];
    uint32_t timestamp;
    
    timestamp = get_timestamp();
    
    /* Calculate fingerprint hash (simplified - use raw values) */
    sprintf(fingerprint_hex, "%08X%08X%08X%08X",
            g_hw_fp.cia_jitter,
            g_hw_fp.vic_raster,
            g_hw_fp.sid_offset,
            g_hw_fp.rom_checksum);
    
    /* Build JSON manually (no library to save space) */
    snprintf(buffer, size,
        "{"
        "\"miner_id\":\"%s\","
        "\"device\":{"
            "\"arch\":\"6510\","
            "\"family\":\"commodore_64\","
            "\"cpu_speed\":1023000,"
            "\"total_ram_kb\":64,"
            "\"rom_checksum\":%u"
        "},"
        "\"signals\":{"
            "\"cia_jitter\":%u,"
            "\"vic_raster\":%u,"
            "\"sid_offset\":%u"
        "},"
        "\"fingerprint\":\"%s\","
        "\"report\":{"
            "\"epoch\":%u,"
            "\"timestamp\":%lu"
        "}"
        "}",
        g_miner.miner_id,
        g_hw_fp.rom_checksum,
        g_hw_fp.cia_jitter,
        g_hw_fp.vic_raster,
        g_hw_fp.sid_offset,
        fingerprint_hex,
        g_miner.attestation_count,
        (unsigned long)timestamp
    );
}

static uint8_t parse_response(const char* response, char* error, size_t error_size)
{
    /* Simple JSON parser - look for "status":"ok" */
    const char* status_pos = strstr(response, "\"status\"");
    
    if (!status_pos) {
        strncpy(error, "No status field", error_size - 1);
        return 0;
    }
    
    /* Check if status is "ok" */
    if (strstr(status_pos, "\"ok\"") != NULL) {
        /* Parse reward amount (simplified) */
        const char* reward_pos = strstr(response, "\"reward\"");
        if (reward_pos) {
            /* Extract numeric value */
            char* endptr;
            float reward = strtod(reward_pos + 8, &endptr);
            g_miner.earned_rtc += reward;
        }
        return 1;
    }
    
    strncpy(error, "Status not ok", error_size - 1);
    return 0;
}

/* ============================================================================
 * Display Update
 * ============================================================================ */

static void update_display(void)
{
    uint32_t current_time;
    uint32_t elapsed;
    uint32_t remaining;
    uint8_t minutes, seconds;
    
    current_time = get_timestamp();
    elapsed = (current_time - g_miner.epoch_start) / 100;
    
    if (elapsed < ATTESTATION_INTERVAL) {
        remaining = ATTESTATION_INTERVAL - elapsed;
        minutes = remaining / 60;
        seconds = remaining % 60;
        
        ui_update_timer(minutes, seconds);
    }
    
    ui_update_earned(g_miner.earned_rtc);
    ui_update_count(g_miner.attestation_count);
}

/* ============================================================================
 * Input Handling
 * ============================================================================ */

static void handle_input(void)
{
    uint8_t key;
    
    /* Check keyboard (simplified - uses CIA) */
    key = PEEK(0xDC00); /* CIA1 Port A - keyboard matrix */
    
    if (key != 0xFF) {
        /* Key pressed - decode */
        /* F1 = Pause, F3 = Menu, F5 = Quit */
        /* TODO: Implement full keyboard scanning */
    }
}

/* ============================================================================
 * Time Functions
 * ============================================================================ */

static uint32_t get_timestamp(void)
{
    /* Use CIA timer for approximate timestamp */
    /* In real implementation, would sync with NTP or RTC cartridge */
    uint8_t lo = PEEK(CIA1_LO);
    uint8_t hi = PEEK(CIA1_HI);
    
    return ((uint32_t)hi << 8) | lo;
}

static void wait_epoch(void)
{
    /* Wait for next epoch (10 minutes) */
    /* Use raster interrupt for accurate timing */
    uint32_t start = get_timestamp();
    uint32_t elapsed;
    
    do {
        handle_input();
        elapsed = (get_timestamp() - start) / 100;
        update_display();
    } while (elapsed < ATTESTATION_INTERVAL);
}

/* ============================================================================
 * Main Entry Point
 * ============================================================================ */

void main(void)
{
    /* Disable interrupts during init */
    asm("sei");
    
    /* Initialize miner */
    init_miner();
    
    /* Re-enable interrupts */
    asm("cli");
    
    /* Enter main loop */
    main_loop();
}

/* ============================================================================
 * Interrupt Handlers
 * ============================================================================ */

/* Raster interrupt handler for precise timing */
void __interrupt__ raster_irq(void)
{
    /* Acknowledge interrupt */
    PEEK(0xD019);
    
    /* TODO: Implement precise timing logic */
}
