/*
 * RUSTCHAIN APPLE II MINER
 * Main Program
 * 
 * "1977 meets 2026 - Wozniak's masterpiece mining crypto at 1MHz"
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <conio.h>
#include <apple2.h>
#include "rustchain.h"

/* Global state */
Apple2Entropy g_entropy;
WalletConfig g_wallet;
NetworkStatus g_network;

/* Forward declarations */
extern void network_init_status(void);
extern int network_send_attestation(WalletConfig *w, Apple2Entropy *e);

/**
 * Print startup banner
 */
void print_banner(void) {
    clrscr();
    
    printf("\n");
    printf("========================================\n");
    printf("  RUSTCHAIN APPLE II MINER\n");
    printf("  \"Fossil Edition\"\n");
    printf("========================================\n");
    printf("  MOS 6502 @ 1MHz\n");
    printf("  1977 meets 2026\n");
    printf("========================================\n");
    printf("  Dev Fee: 0.001 RTC/epoch\n");
    printf("  -> founder_dev_fund\n");
    printf("========================================\n\n");
}

/**
 * Print system status
 */
void print_status(void) {
    printf("\n--- MINER STATUS ---\n");
    printf("Wallet:    %s\n", g_wallet.wallet_id);
    printf("Miner ID:  %s\n", g_wallet.miner_id);
    printf("ROM:       %.8s (v%02X)\n", 
           g_entropy.rom_date, g_entropy.rom_version);
    printf("RAM:       %u KB%s\n", 
           g_entropy.ram_size_kb,
           g_entropy.has_language_card ? " (Lang Card)" : "");
    printf("Video:     Mode %u, 80-col: %s\n",
           g_entropy.video_mode,
           g_entropy.has_80col ? "Yes" : "No");
    printf("Float Bus: 0x%02X\n", g_entropy.floating_bus_value);
    printf("Network:   %s\n", g_network.connected ? "Online" : "Offline");
    printf("Node:      %s:%u\n", RUSTCHAIN_NODE_HOST, RUSTCHAIN_NODE_PORT);
    printf("Tier:      VINTAGE (4.0x multiplier!)\n");
    printf("--------------------\n\n");
}

/**
 * Initialize all subsystems
 */
int initialize_all(void) {
    printf("Initializing...\n\n");
    
    /* Step 1: Collect entropy */
    printf("[1/4] Collecting hardware entropy...\n");
    entropy_init(&g_entropy);
    entropy_collect_rom(&g_entropy);
    entropy_collect_memory(&g_entropy);
    entropy_collect_timer(&g_entropy);
    entropy_collect_video(&g_entropy);
    entropy_collect_floating_bus(&g_entropy);
    entropy_collect_keyboard(&g_entropy);
    entropy_generate_hash(&g_entropy);
    
    /* Step 2: Try to load existing wallet */
    printf("[2/4] Loading wallet...\n");
    if (wallet_load(&g_wallet, WALLET_FILE)) {
        printf("  Wallet loaded from %s\n", WALLET_FILE);
    } else {
        printf("  No wallet found, generating new one...\n");
        wallet_generate(&g_wallet, &g_entropy);
        wallet_save(&g_wallet, WALLET_FILE);
        printf("  Wallet saved to %s\n", WALLET_FILE);
        printf("  BACKUP THIS FILE!\n");
    }
    
    /* Step 3: Initialize network */
    printf("[3/4] Initializing network...\n");
    memset(&g_network, 0, sizeof(NetworkStatus));
    /* Network initialization would go here */
    g_network.initialized = 1;
    g_network.connected = 0;  /* Start offline */
    printf("  Network: Offline mode\n");
    
    /* Step 4: Print status */
    printf("[4/4] Ready!\n\n");
    
    return 1;
}

/**
 * Main mining loop
 */
void mining_loop(void) {
    unsigned long next_attest = 0;
    unsigned long now = 0;
    int cycle = 0;
    char key;
    
    printf("Starting mining loop...\n");
    printf("Press 'S' for status, 'Q' to quit\n\n");
    
    while (1) {
        /* Check for keypress */
        if (kbhit()) {
            key = cgetc();
            if (key == 'q' || key == 'Q' || key == 27) {  /* Q or ESC */
                printf("\nExiting miner...\n");
                break;
            }
            if (key == 's' || key == 'S') {
                print_status();
                printf("Press any key to continue...\n");
                cgetc();
            }
        }
        
        /* Simulate time passage (in real implementation, use timer) */
        now++;
        
        /* Check if it's time for attestation */
        if (now >= next_attest) {
            cycle++;
            printf("\n[%lu] Cycle %d: Collecting entropy...\n", now, cycle);
            
            /* Refresh entropy */
            entropy_collect_timer(&g_entropy);
            entropy_collect_keyboard(&g_entropy);
            entropy_generate_hash(&g_entropy);
            
            /* Try to send attestation */
            if (g_network.connected) {
                printf("[%lu] Sending attestation...\n", now);
                if (network_send_attestation(&g_wallet, &g_entropy)) {
                    printf("[%lu] SUCCESS! Attestation accepted.\n", now);
                } else {
                    printf("[%lu] WARN: Attestation failed.\n", now);
                }
            } else {
                printf("[%lu] Offline mode - entropy collected.\n", now);
                printf("  (Network not available)\n");
            }
            
            /* Schedule next attestation */
            next_attest = now + (BLOCK_TIME_SECONDS / 10);  /* Scaled for demo */
            printf("[%lu] Next attestation in %d cycles.\n\n", 
                   now, BLOCK_TIME_SECONDS / 10);
        }
        
        /* Small delay to avoid busy loop */
        delay(100);
    }
}

/**
 * Main entry point
 */
int main(int argc, char *argv[]) {
    print_banner();
    
    /* Initialize all subsystems */
    if (!initialize_all()) {
        printf("ERROR: Initialization failed!\n");
        return 1;
    }
    
    /* Print wallet info */
    wallet_print(&g_wallet);
    
    /* Start mining loop */
    mining_loop();
    
    printf("\nMiner stopped.\n");
    printf("Wallet saved. Run again to continue mining.\n");
    
    return 0;
}
