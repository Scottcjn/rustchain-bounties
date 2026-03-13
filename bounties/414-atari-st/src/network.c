/*
 * network.c - Network Interface Implementation
 * 
 * Stub implementation for offline/symbolic mode
 * Real implementation requires ST-Link or Serial hardware
 */

#include <stdint.h>
#include <string.h>
#include "network.h"

/* Global network driver */
network_driver_t *g_network = NULL;

/* Connection status */
static int g_connected = 0;

/*
 * ST-Link driver stub
 */
static int stlink_init_stub(void) {
    /* Real implementation would initialize RTL8019AS */
    g_connected = 0;  /* No hardware available */
    return 0;
}

static int stlink_send_stub(const uint8_t *data, int len) {
    (void)data;
    (void)len;
    return g_connected ? len : -1;
}

static int stlink_recv_stub(uint8_t *buffer, int max_len) {
    (void)buffer;
    (void)max_len;
    return 0;
}

static void stlink_shutdown_stub(void) {
    g_connected = 0;
}

static int stlink_connected_stub(void) {
    return g_connected;
}

network_driver_t stlink_driver = {
    .init = stlink_init_stub,
    .send = stlink_send_stub,
    .recv = stlink_recv_stub,
    .shutdown = stlink_shutdown_stub,
    .is_connected = stlink_connected_stub
};

/*
 * Serial driver stub
 */
static int serial_init_stub(void) {
    /* Real implementation would configure MFP for serial */
    g_connected = 0;  /* No hardware available */
    return 0;
}

static int serial_send_stub(const uint8_t *data, int len) {
    (void)data;
    (void)len;
    return g_connected ? len : -1;
}

static int serial_recv_stub(uint8_t *buffer, int max_len) {
    (void)buffer;
    (void)max_len;
    return 0;
}

static void serial_shutdown_stub(void) {
    g_connected = 0;
}

static int serial_connected_stub(void) {
    return g_connected;
}

network_driver_t serial_driver = {
    .init = serial_init_stub,
    .send = serial_send_stub,
    .recv = serial_recv_stub,
    .shutdown = serial_shutdown_stub,
    .is_connected = serial_connected_stub
};

/*
 * Initialize network
 */
int network_init(void) {
    /* Try ST-Link first */
    g_network = &stlink_driver;
    if (g_network->init() == 0) {
        return 0;
    }
    
    /* Fall back to serial */
    g_network = &serial_driver;
    return g_network->init();
}

/*
 * Shutdown network
 */
void network_shutdown(void) {
    if (g_network) {
        g_network->shutdown();
        g_network = NULL;
    }
    g_connected = 0;
}

/*
 * Send data
 */
int network_send(const uint8_t *data, int len) {
    if (!g_network) {
        return -1;
    }
    return g_network->send(data, len);
}

/*
 * Receive data
 */
int network_recv(uint8_t *buffer, int max_len) {
    if (!g_network) {
        return 0;
    }
    return g_network->recv(buffer, max_len);
}

/*
 * Check connection status
 */
int network_is_connected(void) {
    if (!g_network) {
        return 0;
    }
    return g_network->is_connected();
}

/*
 * Register miner with network (stub)
 */
int network_register(const char *wallet, const uint8_t *hw_id, const uint8_t *fingerprint) {
    (void)wallet;
    (void)hw_id;
    (void)fingerprint;
    
    /* In offline mode, always succeed */
    return 0;
}

/*
 * Submit attestation (stub)
 */
int network_submit_attestation(uint32_t epoch, const uint8_t *fingerprint, const uint8_t *hw_id) {
    (void)epoch;
    (void)fingerprint;
    (void)hw_id;
    
    /* In offline mode, simulate success */
    return 0;
}

/*
 * Send heartbeat (stub)
 */
int network_heartbeat(uint32_t epoch, uint32_t attestations) {
    (void)epoch;
    (void)attestations;
    
    /* In offline mode, no-op */
    return 0;
}

/*
 * HTTP GET (stub)
 */
int http_get(const char *url, uint8_t *response, int max_len) {
    (void)url;
    (void)response;
    (void)max_len;
    
    return -1;  /* Not implemented */
}

/*
 * HTTP POST (stub)
 */
int http_post(const char *url, const uint8_t *data, int data_len,
              uint8_t *response, int max_len) {
    (void)url;
    (void)data;
    (void)data_len;
    (void)response;
    (void)max_len;
    
    return -1;  /* Not implemented */
}
