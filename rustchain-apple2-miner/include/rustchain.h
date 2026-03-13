/*
 * RUSTCHAIN APPLE II MINER
 * Header file
 * 
 * Target: Apple II (MOS 6502 @ 1MHz)
 * Compiler: CC65
 */

#ifndef RUSTCHAIN_H
#define RUSTCHAIN_H

#include <stddef.h>
#include <stdint.h>

/* ============================================
   CONFIGURATION
   ============================================ */

#define RUSTCHAIN_NODE_HOST "50.28.86.131"
#define RUSTCHAIN_NODE_PORT 8088
#define RUSTCHAIN_ATTEST_PATH "/attest/submit"
#define BLOCK_TIME_SECONDS 600  /* 10 minutes */
#define DEV_FEE_AMOUNT "0.001"
#define DEV_FEE_WALLET "founder_dev_fund"

/* Memory constraints */
#define MAX_BUFFER_SIZE 512      /* HTTP buffer */
#define WALLET_FILE "MINER.WLT"
#define CONFIG_FILE "MINER.CFG"

/* Timer samples for entropy */
#define TIMER_SAMPLE_COUNT 16

/* ============================================
   ENTROPY STRUCTURES
   ============================================ */

/**
 * Apple II hardware entropy
 * Collected from unique hardware characteristics
 */
typedef struct {
    /* BIOS/ROM information */
    char rom_date[8];           /* Apple II ROM date */
    uint8_t rom_version;        /* ROM version byte */
    
    /* CPU information */
    uint8_t cpu_speed_flag;     /* 6502 speed indicator */
    
    /* Memory configuration */
    uint8_t ram_size_kb;        /* RAM size in KB */
    uint8_t has_language_card;  /* Language card present */
    
    /* Timer entropy */
    uint16_t timer_samples[TIMER_SAMPLE_COUNT];
    
    /* Video timing */
    uint8_t video_mode;         /* Current video mode */
    uint8_t has_80col;          /* 80-column card present */
    
    /* Floating bus signature */
    uint8_t floating_bus_value; /* Unique per machine */
    
    /* Keyboard timing */
    uint8_t keyboard_strobe[8]; /* Keyboard read timing */
    
    /* Final hash */
    uint8_t hash[32];           /* Entropy hash */
} Apple2Entropy;

/**
 * Wallet configuration
 */
typedef struct {
    char wallet_id[48];         /* RTC + 40 hex chars */
    char miner_id[16];          /* APPLE2-XXXX format */
    uint32_t created_timestamp;
    uint8_t initialized;
} WalletConfig;

/* ============================================
   NETWORK STRUCTURES
   ============================================ */

/**
 * HTTP request buffer
 */
typedef struct {
    char buffer[MAX_BUFFER_SIZE];
    uint16_t length;
    uint8_t ready;
} HttpRequest;

/**
 * Network status
 */
typedef struct {
    uint8_t initialized;
    uint8_t connected;
    uint8_t has_ip;
    char ip_address[16];
} NetworkStatus;

/* ============================================
   GLOBAL STATE
   ============================================ */

extern Apple2Entropy g_entropy;
extern WalletConfig g_wallet;
extern NetworkStatus g_network;

/* ============================================
   FUNCTION PROTOTYPES
   ============================================ */

/* entropy.c */
void entropy_init(Apple2Entropy *e);
void entropy_collect_rom(Apple2Entropy *e);
void entropy_collect_memory(Apple2Entropy *e);
void entropy_collect_timer(Apple2Entropy *e);
void entropy_collect_video(Apple2Entropy *e);
void entropy_collect_floating_bus(Apple2Entropy *e);
void entropy_collect_keyboard(Apple2Entropy *e);
void entropy_generate_hash(Apple2Entropy *e);

/* wallet.c */
int wallet_load(WalletConfig *w, const char *filename);
int wallet_save(WalletConfig *w, const char *filename);
void wallet_generate(WalletConfig *w, Apple2Entropy *e);
void wallet_init(WalletConfig *w);

/* network.c */
int network_init(void);
int network_send_attestation(WalletConfig *w, Apple2Entropy *e);
void network_status(NetworkStatus *s);

/* http.c */
int http_build_post(HttpRequest *req, WalletConfig *w, Apple2Entropy *e);
int http_send(HttpRequest *req);

/* json.c */
int json_build_attestation(char *buf, size_t len, WalletConfig *w, Apple2Entropy *e);

/* fingerprint.c */
int fingerprint_detect_emulation(void);
uint8_t fingerprint_floating_bus(void);

/* ui.c */
void ui_init(void);
void ui_clear(void);
void ui_print_banner(void);
void ui_print_status(WalletConfig *w, Apple2Entropy *e);
void ui_print_message(const char *msg);
char ui_get_key(void);
int ui_key_pressed(void);

/* main.c */
void main_loop(void);

/* ============================================
   APPLE II MEMORY MAP
   ============================================ */

/* Apple II zero page usage */
#define ZP_TEMP         0x00    /* Temporary storage */
#define ZP_PTR          0x02    /* Pointer */
#define ZP_COUNTER      0x04    /* Counter */

/* Apple II soft switches */
#define KBD             0xC000  /* Keyboard input */
#define KBD_STROBE      0xC010  /* Keyboard strobe */
#define RDMAINRAM       0xC005  /* Read main RAM */
#define WRMAINRAM       0xC003  /* Write main RAM */

/* Video */
#define TEXT_BASE       0x0400  /* Text page 1 */
#define TEXT_SIZE       0x0400  /* 1024 bytes */

#endif /* RUSTCHAIN_H */
