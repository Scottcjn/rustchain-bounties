/*
 * main.c - RustChain Miner for Atari ST
 * 
 * Main entry point and GEM desktop interface
 * Bounty #414 - 150 RTC
 * Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
 */

#include <stdint.h>
#include <string.h>
#include "tos.h"
#include "gem.h"
#include "miner.h"
#include "network.h"

/* Global variables */
static int g_app_id = -1;
static int g_running = 1;
static char g_status_text[512];

/*
 * Initialize GEM AES
 */
static int init_gem(void) {
    g_app_id = appl_init();
    
    if (g_app_id < 0) {
        /* GEM not available - fall back to text mode */
        Cconws("GEM not available, running in text mode\r\n");
        return -1;
    }
    
    return 0;
}

/*
 * Cleanup GEM
 */
static void cleanup_gem(void) {
    if (g_app_id >= 0) {
        appl_exit();
        g_app_id = -1;
    }
}

/*
 * Display status in text mode
 */
static void display_status_text(void) {
    /* Clear screen */
    Cconws("\033E");  /* ANSI clear screen */
    
    /* Get status */
    miner_get_status_text(g_status_text, sizeof(g_status_text));
    
    /* Display */
    Cconws("\r\n");
    Cconws(g_status_text);
    Cconws("\r\n");
    Cconws("\r\nPress any key to quit...\r\n");
}

/*
 * Handle GEM events
 */
static void handle_events(void) {
    int event;
    int mx, my, mb, ks;
    
    /* Wait for event */
    event = evnt_multi(
        MU_MESAG | MU_TIMER,  /* Event mask */
        0, 0, 0,              /* Button click */
        0, 0, 0,              /* Button mask */
        0, 0,                 /* Mouse click */
        100, 0,               /* Timer (1/60 sec) */
        msg_buf,              /* Message buffer */
        &mx, &my              /* Mouse position */
    );
    
    if (event & MU_MESAG) {
        /* Handle GEM message */
        switch (msg_buf[0]) {
            case MN_SELECTED:
                /* Menu item selected */
                /* msg_buf[3] = menu, msg_buf[4] = item */
                break;
                
            case WM_CLOSED:
                /* Window closed */
                g_running = 0;
                break;
        }
    }
    
    if (event & MU_TIMER) {
        /* Timer event - update miner */
        miner_tick();
    }
}

/*
 * Main entry point
 */
int main(void) {
    int gem_available;
    
    /* Display startup message */
    Cconws("\r\nRustChain Miner for Atari ST v1.0\r\n");
    Cconws("Bounty #414 - 150 RTC\r\n");
    Cconws("Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b\r\n");
    Cconws("\r\nInitializing...\r\n");
    
    /* Initialize GEM */
    gem_available = init_gem();
    
    /* Initialize miner */
    miner_init();
    
    Cconws("Miner initialized.\r\n");
    
    /* Display hardware info */
    Cconws("Hardware: Motorola 68000 @ 8 MHz\r\n");
    Cconws("Fingerprint: Collecting...\r\n");
    
    /* Show status */
    if (gem_available < 0) {
        /* Text mode */
        display_status_text();
        
        /* Wait for key */
        Cconin();
    } else {
        /* GEM mode */
        Cconws("GEM interface active.\r\n");
        
        /* Main event loop */
        while (g_running) {
            handle_events();
            
            /* Check for quit condition */
            if (miner_get_state() == MINER_STATE_ERROR) {
                /* Handle error */
            }
        }
        
        /* Cleanup GEM */
        cleanup_gem();
    }
    
    /* Shutdown miner */
    miner_shutdown();
    
    Cconws("Miner shutdown complete.\r\n");
    
    /* Exit to TOS */
    Pterm0();
    
    return 0;
}
