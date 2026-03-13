/*
 * network.h - Network Interface
 * 
 * ST-Link Ethernet and Serial-to-Ethernet bridge support
 */

#ifndef _NETWORK_H
#define _NETWORK_H

#include <stdint.h>

/* Network driver interface */
typedef struct {
    int (*init)(void);
    int (*send)(const uint8_t *data, int len);
    int (*recv)(uint8_t *buffer, int max_len);
    void (*shutdown)(void);
    int (*is_connected)(void);
} network_driver_t;

/* Network drivers */
extern network_driver_t stlink_driver;
extern network_driver_t serial_driver;

/* Current driver */
extern network_driver_t *g_network;

/* Function prototypes */

/* Initialize network */
int network_init(void);

/* Shutdown network */
void network_shutdown(void);

/* Send data */
int network_send(const uint8_t *data, int len);

/* Receive data */
int network_recv(uint8_t *buffer, int max_len);

/* Check connection status */
int network_is_connected(void);

/* Register miner with network */
int network_register(const char *wallet, const uint8_t *hw_id, const uint8_t *fingerprint);

/* Submit attestation */
int network_submit_attestation(uint32_t epoch, const uint8_t *fingerprint, const uint8_t *hw_id);

/* Send heartbeat */
int network_heartbeat(uint32_t epoch, uint32_t attestations);

/* HTTP client */
int http_get(const char *url, uint8_t *response, int max_len);
int http_post(const char *url, const uint8_t *data, int data_len,
              uint8_t *response, int max_len);

#endif /* _NETWORK_H */
