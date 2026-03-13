/*
 * miner.c - Miner Core Implementation
 * 
 * RustChain Miner for Atari ST
 * Bounty #414 - 150 RTC
 */

#include <stdint.h>
#include <string.h>
#include "miner.h"
#include "fingerprint.h"
#include "network.h"

/* Global miner context */
miner_context_t g_miner;

/* Default configuration */
static miner_config_t g_config = {
    .wallet_address = "RTC4325af95d26d59c3ef025963656d22af638bb96b",
    .device_name = "Atari ST 68000",
    .epoch_duration = 600,          /* 10 minutes */
    .attestation_interval = 60,     /* 1 minute */
    .network_enabled = 1
};

/* State names for display */
static const char* state_names[] = {
    "Idle",
    "Mining",
    "Attesting",
    "Submitting",
    "Error"
};

/*
 * Initialize the miner
 */
void miner_init(void) {
    /* Clear context */
    memset(&g_miner, 0, sizeof(g_miner));
    
    /* Set initial state */
    g_miner.state = MINER_STATE_IDLE;
    g_miner.epoch = 0;
    g_miner.reward_lo = 0;
    g_miner.reward_hi = 0;
    
    /* Collect hardware fingerprint */
    fingerprint_collect(g_miner.fingerprint, 256);
    fingerprint_generate_id(g_miner.hardware_id);
    
    /* Set status message */
    strcpy(g_miner.status_message, "Initialized");
    
    /* Initialize network */
    if (g_config.network_enabled) {
        network_init();
    }
}

/*
 * Shutdown the miner
 */
void miner_shutdown(void) {
    miner_stop();
    network_shutdown();
    g_miner.state = MINER_STATE_IDLE;
    strcpy(g_miner.status_message, "Shutdown");
}

/*
 * Main miner tick - called periodically
 */
void miner_tick(void) {
    g_miner.uptime++;
    
    switch (g_miner.state) {
        case MINER_STATE_IDLE:
            /* Wait for user input */
            break;
            
        case MINER_STATE_MINING:
            /* Simulate mining work */
            /* In real implementation, this would do actual work */
            if ((g_miner.uptime % g_config.attestation_interval) == 0) {
                miner_set_state(MINER_STATE_ATTESTING);
            }
            break;
            
        case MINER_STATE_ATTESTING:
            /* Perform attestation */
            if (miner_attest() == 0) {
                miner_set_state(MINER_STATE_SUBMITTING);
            } else {
                miner_set_state(MINER_STATE_ERROR);
                strcpy(g_miner.status_message, "Attestation failed");
            }
            break;
            
        case MINER_STATE_SUBMITTING:
            /* Submit attestation */
            if (miner_submit_attestation() == 0) {
                g_miner.epoch++;
                g_miner.attestations++;
                miner_set_state(MINER_STATE_MINING);
                strcpy(g_miner.status_message, "Attestation submitted");
            } else {
                miner_set_state(MINER_STATE_ERROR);
                strcpy(g_miner.status_message, "Submit failed");
            }
            break;
            
        case MINER_STATE_ERROR:
            /* Error state - wait for recovery */
            break;
    }
}

/*
 * Set miner state
 */
void miner_set_state(miner_state_t state) {
    g_miner.state = state;
}

/*
 * Get current miner state
 */
miner_state_t miner_get_state(void) {
    return g_miner.state;
}

/*
 * Start mining
 */
void miner_start(void) {
    if (g_miner.state == MINER_STATE_IDLE) {
        g_miner.state = MINER_STATE_MINING;
        strcpy(g_miner.status_message, "Mining started");
    }
}

/*
 * Stop mining
 */
void miner_stop(void) {
    if (g_miner.state != MINER_STATE_IDLE) {
        g_miner.state = MINER_STATE_IDLE;
        strcpy(g_miner.status_message, "Mining stopped");
    }
}

/*
 * Pause mining
 */
void miner_pause(void) {
    /* For now, same as stop */
    miner_stop();
}

/*
 * Perform attestation
 * Returns 0 on success, -1 on error
 */
int miner_attest(void) {
    /* Refresh fingerprint */
    fingerprint_collect(g_miner.fingerprint, 256);
    
    /* Verify fingerprint matches hardware */
    if (fingerprint_verify(g_miner.fingerprint, g_miner.hardware_id) != 0) {
        return -1;
    }
    
    /* In real implementation, generate proof here */
    
    return 0;
}

/*
 * Submit attestation to network
 * Returns 0 on success, -1 on error
 */
int miner_submit_attestation(void) {
    if (!g_config.network_enabled || !g_miner.network_connected) {
        /* Offline mode - simulate success */
        g_miner.reward_lo += 42;  /* Symbolic reward */
        return 0;
    }
    
    /* Submit to network */
    return network_submit_attestation(
        g_miner.epoch,
        g_miner.fingerprint,
        g_miner.hardware_id
    );
}

/*
 * Get current reward
 */
uint64_t miner_get_reward(void) {
    return ((uint64_t)g_miner.reward_hi << 32) | g_miner.reward_lo;
}

/*
 * Update reward
 */
void miner_update_reward(uint32_t lo, uint32_t hi) {
    g_miner.reward_lo = lo;
    g_miner.reward_hi = hi;
}

/*
 * Get status string for current state
 */
const char* miner_get_status_string(void) {
    if (g_miner.state >= 0 && g_miner.state <= MINER_STATE_ERROR) {
        return state_names[g_miner.state];
    }
    return "Unknown";
}

/*
 * Get full status text
 */
void miner_get_status_text(char *buffer, int max_len) {
    char temp[128];
    
    strcpy(buffer, "RustChain Miner v1.0\n");
    strcat(buffer, "Status: ");
    strcat(buffer, miner_get_status_string());
    strcat(buffer, "\n");
    
    /* Epoch */
    sprintf(temp, "Epoch: %lu\n", g_miner.epoch);
    strncat(buffer, temp, max_len - strlen(buffer) - 1);
    
    /* Reward */
    sprintf(temp, "Reward: %lu.%04lu RTC\n", 
            g_miner.reward_hi, g_miner.reward_lo / 10000);
    strncat(buffer, temp, max_len - strlen(buffer) - 1);
    
    /* Hardware */
    strcat(buffer, "Hardware: Motorola 68000 @ 8 MHz\n");
    
    /* Network */
    strcat(buffer, "Network: ");
    strcat(buffer, g_miner.network_connected ? "Connected" : "Offline");
    strcat(buffer, "\n");
    
    /* Uptime */
    sprintf(temp, "Uptime: %lu seconds\n", g_miner.uptime);
    strncat(buffer, temp, max_len - strlen(buffer) - 1);
}

/*
 * Set miner configuration
 */
void miner_set_config(const miner_config_t *config) {
    memcpy(&g_config, config, sizeof(miner_config_t));
}

/*
 * Get miner configuration
 */
const miner_config_t* miner_get_config(void) {
    return &g_config;
}

/*
 * Collect hardware fingerprint
 */
void miner_collect_fingerprint(void) {
    fingerprint_collect(g_miner.fingerprint, 256);
}

/*
 * Verify fingerprint
 */
int miner_verify_fingerprint(void) {
    return fingerprint_verify(g_miner.fingerprint, g_miner.hardware_id);
}

/*
 * Register miner with network
 */
int miner_register(void) {
    if (!g_config.network_enabled) {
        return 0;  /* Offline mode */
    }
    
    return network_register(
        g_config.wallet_address,
        g_miner.hardware_id,
        g_miner.fingerprint
    );
}

/*
 * Send heartbeat to network
 */
int miner_heartbeat(void) {
    if (!g_config.network_enabled || !g_miner.network_connected) {
        return 0;
    }
    
    return network_heartbeat(g_miner.epoch, g_miner.attestations);
}
