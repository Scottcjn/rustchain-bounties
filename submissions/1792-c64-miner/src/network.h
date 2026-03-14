/*
 * RustChain Miner for Commodore 64
 * Network driver header
 */

#ifndef NETWORK_H
#define NETWORK_H

#include <stdint.h>
#include <stddef.h>

/* Buffer size */
#define NET_BUFFER_SIZE 512

/* Error codes */
#define NET_OK 0
#define NET_ERR_INIT -1
#define NET_ERR_CONNECT -2
#define NET_ERR_SEND -3
#define NET_ERR_RECV -4
#define NET_ERR_TIMEOUT -5

/* Function prototypes */
int16_t network_init(void);
int16_t network_post(const char* host, uint16_t port, const char* path,
                     const char* payload, size_t payload_len,
                     char* response, size_t response_max);
void network_cleanup(void);

#endif /* NETWORK_H */
