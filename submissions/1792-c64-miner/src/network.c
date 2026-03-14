/*
 * RustChain Miner for Commodore 64
 * Network driver - supports RR-Net and Userport+ESP32
 */

#include <stdio.h>
#include <string.h>
#include <cbm.h>
#include <peekpoke.h>

#include "network.h"

/* ============================================================================
 * Configuration
 * ============================================================================ */

/* Uncomment to use Userport+ESP32 instead of RR-Net */
/* #define USE_USERPORT_ESP32 */

#ifdef USE_USERPORT_ESP32
    /* Userport RS-232 configuration */
    #define BAUD_RATE 9600
    #define CIA2_CRB 0xDD03  /* Control register B */
    #define CIA2_DRB 0xDD01  /* Data register B */
    #define CIA2_LO 0xDD04  /* Timer 1 low byte */
    #define CIA2_HI 0xDD05  /* Timer 1 high byte */
#else
    /* RR-Net configuration */
    #define RRNET_BASE 0xDE00  /* Base address for RR-Net */
    #define RRNET_DATA (RRNET_BASE + 0)
    #define RRNET_STATUS (RRNET_BASE + 1)
    #define RRNET_COMMAND (RRNET_BASE + 2)
    #define RRNET_CONTROL (RRNET_BASE + 3)
#endif

/* ============================================================================
 * Global State
 * ============================================================================ */

static uint8_t g_initialized = 0;
static uint8_t g_ip_address[4] = {0, 0, 0, 0};
static uint8_t g_gateway[4] = {0, 0, 0, 0};
static uint8_t g_dns[4] = {0, 0, 0, 0};

/* ============================================================================
 * Forward Declarations
 * ============================================================================ */

#ifdef USE_USERPORT_ESP32
static int16_t userport_init(void);
static int16_t userport_send(const uint8_t* data, size_t len);
static int16_t userport_recv(uint8_t* buffer, size_t max_len);
#else
static int16_t rrnet_init(void);
static int16_t rrnet_connect(const char* host, uint16_t port);
static int16_t rrnet_send(const uint8_t* data, size_t len);
static int16_t rrnet_recv(uint8_t* buffer, size_t max_len);
static void rrnet_close(void);
#endif

/* ============================================================================
 * Public API
 * ============================================================================ */

int16_t network_init(void)
{
    if (g_initialized) {
        return 0; /* Already initialized */
    }
    
#ifdef USE_USERPORT_ESP32
    if (userport_init() != 0) {
        return -1;
    }
#else
    if (rrnet_init() != 0) {
        return -1;
    }
#endif
    
    /* Set default DNS (Google DNS) */
    g_dns[0] = 8;
    g_dns[1] = 8;
    g_dns[2] = 8;
    g_dns[3] = 8;
    
    g_initialized = 1;
    return 0;
}

int16_t network_post(const char* host, uint16_t port, const char* path,
                     const char* payload, size_t payload_len,
                     char* response, size_t response_max)
{
    char header[256];
    size_t header_len;
    int16_t status;
    int16_t recv_len;
    
    if (!g_initialized) {
        return -1;
    }
    
    /* Build HTTP POST header */
    header_len = snprintf(header, sizeof(header),
        "POST %s HTTP/1.1\r\n"
        "Host: %s\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: %u\r\n"
        "Connection: close\r\n"
        "\r\n",
        path, host, (unsigned int)payload_len);
    
    /* Connect to server */
#ifdef USE_USERPORT_ESP32
    /* ESP32 handles connection internally */
    status = 0;
#else
    status = rrnet_connect(host, port);
    if (status != 0) {
        return -1;
    }
#endif
    
    /* Send header */
#ifdef USE_USERPORT_ESP32
    status = userport_send((uint8_t*)header, header_len);
#else
    status = rrnet_send((uint8_t*)header, header_len);
#endif
    
    if (status != 0) {
        return -1;
    }
    
    /* Send payload */
#ifdef USE_USERPORT_ESP32
    status = userport_send((uint8_t*)payload, payload_len);
#else
    status = rrnet_send((uint8_t*)payload, payload_len);
#endif
    
    if (status != 0) {
        return -1;
    }
    
    /* Receive response */
#ifdef USE_USERPORT_ESP32
    recv_len = userport_recv((uint8_t*)response, response_max - 1);
#else
    recv_len = rrnet_recv((uint8_t*)response, response_max - 1);
    rrnet_close();
#endif
    
    if (recv_len < 0) {
        return -1;
    }
    
    response[recv_len] = '\0';
    
    /* Parse HTTP status code */
    if (strstr(response, "200 OK") != NULL) {
        /* Find body (after double CRLF) */
        char* body = strstr(response, "\r\n\r\n");
        if (body) {
            memmove(response, body + 4, strlen(body + 4) + 1);
        }
        return 0;
    }
    
    return -1; /* HTTP error */
}

void network_cleanup(void)
{
#ifndef USE_USERPORT_ESP32
    rrnet_close();
#endif
    g_initialized = 0;
}

/* ============================================================================
 * RR-Net Implementation
 * ============================================================================ */

#ifndef USE_USERPORT_ESP32

static int16_t rrnet_init(void)
{
    uint8_t status;
    
    /* Check if RR-Net is present */
    status = PEEK(RRNET_STATUS);
    
    if (status == 0xFF) {
        /* No device found */
        return -1;
    }
    
    /* Initialize W5100 chip */
    POKE(RRNET_COMMAND, 0x01); /* Reset */
    
    /* Wait for reset complete */
    while (PEEK(RRNET_STATUS) & 0x01) {
        /* Wait */
    }
    
    /* Configure for TCP/IP */
    POKE(RRNET_CONTROL, 0x04); /* Enable DHCP */
    
    /* Wait for DHCP */
    /* TODO: Implement timeout */
    while (!(PEEK(RRNET_STATUS) & 0x02)) {
        /* Wait for DHCP complete */
    }
    
    /* Read IP address */
    g_ip_address[0] = PEEK(RRNET_BASE + 0x10);
    g_ip_address[1] = PEEK(RRNET_BASE + 0x11);
    g_ip_address[2] = PEEK(RRNET_BASE + 0x12);
    g_ip_address[3] = PEEK(RRNET_BASE + 0x13);
    
    /* Read gateway */
    g_gateway[0] = PEEK(RRNET_BASE + 0x14);
    g_gateway[1] = PEEK(RRNET_BASE + 0x15);
    g_gateway[2] = PEEK(RRNET_BASE + 0x16);
    g_gateway[3] = PEEK(RRNET_BASE + 0x17);
    
    return 0;
}

static int16_t rrnet_connect(const char* host, uint16_t port)
{
    /* TODO: DNS resolution */
    /* For now, use hardcoded IP for rustchain.org */
    uint8_t ip[4] = {50, 28, 86, 131}; /* Example IP */
    
    /* Open socket */
    POKE(RRNET_COMMAND, 0x04); /* OPEN command */
    
    /* Set destination IP */
    POKE(RRNET_BASE + 0x20, ip[0]);
    POKE(RRNET_BASE + 0x21, ip[1]);
    POKE(RRNET_BASE + 0x22, ip[2]);
    POKE(RRNET_BASE + 0x23, ip[3]);
    
    /* Set destination port */
    POKE(RRNET_BASE + 0x24, (port >> 8) & 0xFF);
    POKE(RRNET_BASE + 0x25, port & 0xFF);
    
    /* Execute connect */
    POKE(RRNET_COMMAND, 0x08); /* CONNECT command */
    
    /* Wait for connection */
    while (!(PEEK(RRNET_STATUS) & 0x04)) {
        /* Wait */
    }
    
    /* Check if connected */
    if (PEEK(RRNET_STATUS) & 0x08) {
        return 0; /* Connected */
    }
    
    return -1; /* Failed */
}

static int16_t rrnet_send(const uint8_t* data, size_t len)
{
    size_t i;
    
    for (i = 0; i < len; i++) {
        /* Wait for transmit buffer ready */
        while (PEEK(RRNET_STATUS) & 0x20) {
            /* Wait */
        }
        
        /* Write data */
        POKE(RRNET_DATA, data[i]);
        
        /* Trigger send */
        POKE(RRNET_COMMAND, 0x10); /* SEND command */
    }
    
    return 0;
}

static int16_t rrnet_recv(uint8_t* buffer, size_t max_len)
{
    size_t count = 0;
    uint8_t status;
    
    while (count < max_len) {
        status = PEEK(RRNET_STATUS);
        
        /* Check if data available */
        if (status & 0x10) {
            buffer[count++] = PEEK(RRNET_DATA);
            
            /* Acknowledge receive */
            POKE(RRNET_COMMAND, 0x20);
        } else if (status & 0x40) {
            /* Connection closed */
            break;
        }
    }
    
    return (int16_t)count;
}

static void rrnet_close(void)
{
    POKE(RRNET_COMMAND, 0x40); /* DISCONNECT command */
}

#endif /* USE_USERPORT_ESP32 */

/* ============================================================================
 * Userport + ESP32 Implementation
 * ============================================================================ */

#ifdef USE_USERPORT_ESP32

static int16_t userport_init(void)
{
    /* Configure CIA2 for RS-232 */
    POKE(CIA2_CRB, 0x1B); /* Set baud rate */
    
    /* Test communication */
    POKE(CIA2_DRB, 0x55); /* Send test byte */
    
    /* Wait for response */
    /* ESP32 should echo back */
    
    return 0;
}

static int16_t userport_send(const uint8_t* data, size_t len)
{
    size_t i;
    
    for (i = 0; i < len; i++) {
        /* Wait for transmit buffer empty */
        while (!(PEEK(CIA2_CRB) & 0x40)) {
            /* Wait */
        }
        
        /* Send byte */
        POKE(CIA2_DRB, data[i]);
    }
    
    return 0;
}

static int16_t userport_recv(uint8_t* buffer, size_t max_len)
{
    size_t count = 0;
    
    while (count < max_len) {
        /* Check if data available */
        if (PEEK(CIA2_CRB) & 0x80) {
            buffer[count++] = PEEK(CIA2_DRB);
        } else {
            /* No more data */
            break;
        }
    }
    
    return (int16_t)count;
}

#endif /* USE_USERPORT_ESP32 */
