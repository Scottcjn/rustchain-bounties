/*
 * miner.h - Miner Core Definitions
 * 
 * RustChain Miner for Atari ST
 * Bounty #414 - 150 RTC
 */

#ifndef _MINER_H
#define _MINER_H

#include <stdint.h>

/* Miner states */
typedef enum {
    MINER_STATE_IDLE = 0,
    MINER_STATE_MINING = 1,
    MINER_STATE_ATTESTING = 2,
    MINER_STATE_SUBMITTING = 3,
    MINER_STATE_ERROR = 4
} miner_state_t;

/* Miner configuration */
typedef struct {
    char wallet_address[64];      /* RTC wallet address */
    char device_name[32];         /* Device identifier */
    uint32_t epoch_duration;      /* Epoch duration in seconds */
    uint32_t attestation_interval; /* Attestation interval */
    uint8_t network_enabled;      /* Network enabled flag */
} miner_config_t;

/* Miner context */
typedef struct {
    miner_state_t state;          /* Current state */
    uint32_t epoch;               /* Current epoch number */
    uint32_t reward_lo;           /* Reward (low 32 bits) */
    uint32_t reward_hi;           /* Reward (high 32 bits) */
    uint8_t hardware_id[16];      /* Hardware fingerprint */
    uint8_t fingerprint[256];     /* CPU jitter fingerprint */
    uint32_t uptime;              /* Uptime in seconds */
    uint32_t attestations;        /* Total attestations */
    uint8_t network_connected;    /* Network status */
    char status_message[64];      /* Status message */
} miner_context_t;

/* Global miner context */
extern miner_context_t g_miner;

/* Function prototypes */

/* Initialization */
void miner_init(void);
void miner_shutdown(void);

/* State machine */
void miner_tick(void);
void miner_set_state(miner_state_t state);
miner_state_t miner_get_state(void);

/* Mining operations */
void miner_start(void);
void miner_stop(void);
void miner_pause(void);

/* Attestation */
int miner_attest(void);
int miner_submit_attestation(void);

/* Rewards */
uint64_t miner_get_reward(void);
void miner_update_reward(uint32_t lo, uint32_t hi);

/* Status */
const char* miner_get_status_string(void);
void miner_get_status_text(char *buffer, int max_len);

/* Configuration */
void miner_set_config(const miner_config_t *config);
const miner_config_t* miner_get_config(void);

/* Hardware fingerprint */
void miner_collect_fingerprint(void);
int miner_verify_fingerprint(void);

/* Network */
int miner_register(void);
int miner_heartbeat(void);

#endif /* _MINER_H */
