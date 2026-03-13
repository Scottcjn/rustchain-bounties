/*
 * RUSTCHAIN APPLE II MINER
 * Wallet Module
 * 
 * Generates and manages wallet from hardware entropy
 */

#include <stdio.h>
#include <string.h>
#include <apple2.h>
#include "rustchain.h"

/* Hex characters for wallet ID */
static const char hex_chars[] = "0123456789abcdef";

/**
 * Initialize wallet structure
 */
void wallet_init(WalletConfig *w) {
    memset(w, 0, sizeof(WalletConfig));
    w->initialized = 0;
}

/**
 * Generate wallet from entropy
 * Format: RTC + 40 hex characters (20 bytes from hash)
 */
void wallet_generate(WalletConfig *w, Apple2Entropy *e) {
    int i;
    
    /* Wallet ID: "RTC" + 40 hex chars = 43 chars + null */
    strcpy(w->wallet_id, "RTC");
    
    /* Generate 40 hex characters from first 20 bytes of hash */
    for (i = 0; i < 20; i++) {
        w->wallet_id[3 + i*2] = hex_chars[(e->hash[i] >> 4) & 0x0F];
        w->wallet_id[3 + i*2 + 1] = hex_chars[e->hash[i] & 0x0F];
    }
    w->wallet_id[43] = '\0';
    
    /* Miner ID: "APPLE2-" + 8 hex chars */
    sprintf(w->miner_id, "APPLE2-%02X%02X%02X%02X",
            e->hash[0], e->hash[1], e->hash[2], e->hash[3]);
    
    /* Timestamp (simplified - use timer value) */
    w->created_timestamp = (uint32_t)e->timer_samples[0] << 16 | 
                           e->timer_samples[1];
    
    w->initialized = 1;
}

/**
 * Save wallet to file
 * ProDOS file format
 */
int wallet_save(WalletConfig *w, const char *filename) {
    FILE *fp;
    
    fp = fopen(filename, "w");
    if (!fp) {
        return 0;  /* Failed */
    }
    
    /* Write wallet data */
    fprintf(fp, "RUSTCHAIN APPLE II WALLET\n");
    fprintf(fp, "ID=%s\n", w->wallet_id);
    fprintf(fp, "MINER=%s\n", w->miner_id);
    fprintf(fp, "CREATED=%lu\n", w->created_timestamp);
    fprintf(fp, "# DO NOT DELETE - BACKUP TO FLOPPY!\n");
    
    fclose(fp);
    return 1;  /* Success */
}

/**
 * Load wallet from file
 */
int wallet_load(WalletConfig *w, const char *filename) {
    FILE *fp;
    char line[64];
    char key[16];
    char value[48];
    int i;
    
    fp = fopen(filename, "r");
    if (!fp) {
        return 0;  /* File not found */
    }
    
    wallet_init(w);
    
    /* Parse file line by line */
    while (fgets(line, sizeof(line), fp)) {
        /* Skip comments and empty lines */
        if (line[0] == '#' || line[0] == '\n') {
            continue;
        }
        
        /* Parse KEY=VALUE format */
        for (i = 0; line[i] && line[i] != '='; i++) {
            key[i] = line[i];
        }
        key[i] = '\0';
        
        if (line[i] == '=') {
            /* Extract value */
            char *val = &line[i+1];
            int j;
            for (j = 0; val[j] && val[j] != '\n'; j++) {
                value[j] = val[j];
            }
            value[j] = '\0';
            
            if (strcmp(key, "ID") == 0) {
                strncpy(w->wallet_id, value, 47);
                w->wallet_id[47] = '\0';
            } else if (strcmp(key, "MINER") == 0) {
                strncpy(w->miner_id, value, 15);
                w->miner_id[15] = '\0';
            } else if (strcmp(key, "CREATED") == 0) {
                w->created_timestamp = strtoul(value, NULL, 10);
            }
        }
    }
    
    fclose(fp);
    
    /* Mark as initialized if we got a wallet ID */
    if (w->wallet_id[0] != '\0') {
        w->initialized = 1;
        return 1;
    }
    
    return 0;
}

/**
 * Print wallet information
 */
void wallet_print(WalletConfig *w) {
    printf("\n=== WALLET INFORMATION ===\n");
    printf("Wallet ID: %s\n", w->wallet_id);
    printf("Miner ID:  %s\n", w->miner_id);
    printf("Created:   %lu\n", w->created_timestamp);
    printf("===========================\n\n");
}
