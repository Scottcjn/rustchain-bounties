/*
 * miner.c - Core mining logic for HP 95LX
 * 
 * Implements the mining iteration and status display updates.
 * This is a simplified PoW miner for the HP 95LX platform.
 */

#include <stdio.h>
#include <string.h>
#include <dos.h>

#include "miner.h"
#include "display.h"
#include "hw_95lx.h"

/*
 * Mining iteration
 * 
 * Performs one mining iteration (hash computation attempt).
 * This is a placeholder for the actual PoW algorithm.
 */
void mining_iteration(struct miner_state *state)
{
    static unsigned long nonce = 0;
    unsigned long i;
    
    /* Increment counters */
    state->total_iterations++;
    nonce++;
    
    /* Simple hash computation (placeholder) */
    /* In real implementation, this would be the actual PoW algorithm */
    for (i = 0; i < 1000; i++) {
        /* Simulate computation */
        nonce = (nonce * 1103515245 + 12345) & 0x7FFFFFFF;
    }
    
    state->total_hashes++;
    
    /* Check for "solution" (placeholder - always finds one eventually) */
    if ((nonce & 0xFFFF) == 0) {
        /* Found a valid hash (simplified) */
        state->total_earned += 0.0001 * state->reward_multiplier;
    }
}

/*
 * Update status display
 * 
 * Updates the mining status on the LCD screen.
 * Called periodically during mining loop.
 */
void update_status_display(struct miner_state *state,
                           unsigned long iterations,
                           unsigned long elapsed)
{
    char buffer[41];  /* 40 chars + null */
    unsigned long seconds;
    unsigned long minutes;
    unsigned long hours;
    
    /* Calculate uptime */
    seconds = elapsed / 18;  /* BIOS timer runs at ~18.2 Hz */
    minutes = seconds / 60;
    hours = minutes / 60;
    seconds %= 60;
    minutes %= 60;
    
    /* Update status line (line 4) */
    if (state->is_emulator) {
        snprintf(buffer, sizeof(buffer), "| STATUS: EMULATOR MODE                |");
    } else {
        snprintf(buffer, sizeof(buffer), "| STATUS: MINING...                      |");
    }
    display_print_line(4, buffer);
    
    /* Update earned amount (line 5) */
    snprintf(buffer, sizeof(buffer), "| EARNED: %.4f RTC                         |", 
             state->total_earned);
    display_print_line(5, buffer);
    
    /* Update uptime (line 6) */
    snprintf(buffer, sizeof(buffer), "| UPTIME: %02lu:%02lu:%02lu                       |",
             hours, minutes, seconds);
    display_print_line(6, buffer);
    
    /* Update hardware info (lines 9-11) */
    snprintf(buffer, sizeof(buffer), "| HW: %-36s |", hw_95lx_get_cpu_name());
    display_print_line(9, buffer);
    
    snprintf(buffer, sizeof(buffer), "| MEM: %d KB                          |", 
             hw_95lx_get_memory_kb());
    display_print_line(10, buffer);
    
    if (state->serial_connected) {
        snprintf(buffer, sizeof(buffer), "| SERIAL: CONNECTED (COM1)               |");
    } else {
        snprintf(buffer, sizeof(buffer), "| SERIAL: NOT CONNECTED                  |");
    }
    display_print_line(11, buffer);
}
