/*
 * miner.h - Core miner definitions for HP 95LX
 * 
 * This file contains the core data structures and function
 * declarations for the HP 95LX miner.
 */

#ifndef MINER_H
#define MINER_H

/* Miner state structure */
struct miner_state {
    unsigned long total_iterations;
    unsigned long total_hashes;
    double total_earned;
    double reward_multiplier;
    unsigned long start_time;
    int exit_requested;
    int serial_connected;
    int is_emulator;
    char node_url[128];
    char wallet_address[64];
};

/* Mining iteration function */
void mining_iteration(struct miner_state *state);

/* Get timer ticks (for timing) */
unsigned long get_timer_ticks(void);

/* Update status display */
void update_status_display(struct miner_state *state, 
                           unsigned long iterations, 
                           unsigned long elapsed);

#endif /* MINER_H */
