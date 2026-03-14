/*
 * RustChain Miner for Commodore 64
 * Main header file
 */

#ifndef MINER_H
#define MINER_H

#include <stdint.h>
#include <stddef.h>

/* Version */
#define MINER_VERSION_MAJOR 0
#define MINER_VERSION_MINOR 1
#define MINER_VERSION_PATCH 0

/* Configuration */
#define ATTESTATION_INTERVAL_SEC 600
#define NETWORK_TIMEOUT_SEC 30
#define MAX_RETRY_COUNT 3

/* Error codes */
#define ERR_OK 0
#define ERR_NETWORK -1
#define ERR_PARSE -2
#define ERR_FINGERPRINT -3
#define ERR_STORAGE -4

/* Miner state flags */
#define FLAG_INITIALIZED 0x01
#define FLAG_NETWORK_READY 0x02
#define FLAG_WALLET_SET 0x04
#define FLAG_ATTESTING 0x08

/* Function prototypes */
int miner_init(void);
int miner_attest(void);
void miner_run(void);
void miner_stop(void);

/* State accessors */
uint8_t miner_is_initialized(void);
uint8_t miner_is_network_ready(void);
float miner_get_earned_rtc(void);
uint16_t miner_get_attestation_count(void);

#endif /* MINER_H */
