/*
 * serial.c - Serial port communication for HP 95LX
 * 
 * HP 95LX has RS-232 serial port via standard UART (8250/16450/16550)
 * COM1: 0x3F8, COM2: 0x2F8 (if available)
 * 
 * Used for SLIP/PPP networking or direct connection to gateway PC
 */

#include <stdio.h>
#include <dos.h>
#include <i86.h>

#include "serial.h"

/* Serial port state */
static struct {
    int initialized;
    int port;
    int baud;
    int data_bits;
    int stop_bits;
    int parity;
} g_serial_state;

/* UART register offsets */
#define UART_RBR 0  /* Receiver Buffer Register (read) */
#define UART_THR 0  /* Transmitter Holding Register (write) */
#define UART_IER 1  /* Interrupt Enable Register */
#define UART_IIR 2  /* Interrupt Identification Register */
#define UART_FCR 2  /* FIFO Control Register (16450/16550) */
#define UART_LCR 3  /* Line Control Register */
#define UART_MCR 4  /* Modem Control Register */
#define UART_LSR 5  /* Line Status Register */
#define UART_MSR 6  /* Modem Status Register */
#define UART_DLL 0  /* Divisor Latch Low (when LCR[7]=1) */
#define UART_DLM 1  /* Divisor Latch High (when LCR[7]=1) */

/* Line Status Register bits */
#define LSR_DR  0x01  /* Data Ready */
#define LSR_OE  0x02  /* Overrun Error */
#define LSR_PE  0x04  /* Parity Error */
#define LSR_FE  0x08  /* Framing Error */
#define LSR_BI  0x10  /* Break Interrupt */
#define LSR_THRE 0x20 /* Transmitter Holding Register Empty */
#define LSR_TEMT 0x40 /* Transmitter Empty */
#define LSR_ERR 0x80  /* Error in received FIFO */

/*
 * Initialize serial port
 * 
 * port: Base port address (COM1=0x3F8, COM2=0x2F8)
 * baud: Baud rate (9600, 19200, 38400, etc.)
 * 
 * Returns: 0 on success, -1 on failure
 */
int serial_init(int port, int baud)
{
    unsigned int divisor;
    unsigned char lcr;
    
    /* Validate port */
    if (port != COM1 && port != COM2) {
        fprintf(stderr, "Invalid COM port: 0x%04X\n", port);
        return -1;
    }
    
    /* Calculate divisor for baud rate */
    /* UART base clock is typically 1.8432 MHz */
    /* Divisor = 1843200 / (16 * baud) */
    divisor = 1843200L / (16L * baud);
    
    /* Store state */
    g_serial_state.port = port;
    g_serial_state.baud = baud;
    g_serial_state.data_bits = 8;
    g_serial_state.stop_bits = 1;
    g_serial_state.parity = 0;  /* No parity */
    
    /* Disable interrupts */
    outp(port + UART_IER, 0x00);
    
    /* Enable divisor latch access (set DLAB bit) */
    lcr = inp(port + UART_LCR);
    outp(port + UART_LCR, lcr | 0x80);
    
    /* Set divisor (baud rate) */
    outp(port + UART_DLL, divisor & 0xFF);        /* Low byte */
    outp(port + UART_DLM, (divisor >> 8) & 0xFF); /* High byte */
    
    /* Set line control (8N1) */
    /* 8 data bits, no parity, 1 stop bit */
    outp(port + UART_LCR, 0x03);
    
    /* Set modem control */
    /* DTR and RTS high */
    outp(port + UART_MCR, 0x03);
    
    /* Clear FIFO (if 16450/16550) */
    outp(port + UART_FCR, 0x07);
    
    /* Clear any pending data */
    while (inp(port + UART_LSR) & LSR_DR) {
        inp(port + UART_RBR);  /* Read and discard */
    }
    
    g_serial_state.initialized = 1;
    
    return 0;
}

/*
 * Close serial port
 */
void serial_close(void)
{
    if (!g_serial_state.initialized) return;
    
    /* Disable interrupts */
    outp(g_serial_state.port + UART_IER, 0x00);
    
    /* Reset modem control */
    outp(g_serial_state.port + UART_MCR, 0x00);
    
    g_serial_state.initialized = 0;
}

/*
 * Set baud rate
 * 
 * baud: New baud rate
 */
void serial_set_baud(int baud)
{
    unsigned int divisor;
    unsigned char lcr;
    
    if (!g_serial_state.initialized) return;
    
    /* Calculate new divisor */
    divisor = 1843200L / (16L * baud);
    
    /* Enable divisor latch access */
    lcr = inp(g_serial_state.port + UART_LCR);
    outp(g_serial_state.port + UART_LCR, lcr | 0x80);
    
    /* Set new divisor */
    outp(g_serial_state.port + UART_DLL, divisor & 0xFF);
    outp(g_serial_state.port + UART_DLM, (divisor >> 8) & 0xFF);
    
    /* Restore line control */
    outp(g_serial_state.port + UART_LCR, 0x03);
    
    g_serial_state.baud = baud;
}

/*
 * Send data
 * 
 * data: Data buffer
 * len: Number of bytes to send
 */
void serial_send(const char *data, int len)
{
    int i;
    unsigned char lsr;
    
    if (!g_serial_state.initialized || !data || len <= 0) return;
    
    for (i = 0; i < len; i++) {
        /* Wait for transmitter to be ready */
        do {
            lsr = inp(g_serial_state.port + UART_LSR);
        } while (!(lsr & LSR_THRE));
        
        /* Send byte */
        outp(g_serial_state.port + UART_THR, data[i]);
    }
    
    /* Wait for transmitter to empty */
    do {
        lsr = inp(g_serial_state.port + UART_LSR);
    } while (!(lsr & LSR_TEMT));
}

/*
 * Receive data
 * 
 * buf: Buffer to store received data
 * max_len: Maximum bytes to receive
 * 
 * Returns: Number of bytes received, or -1 on error
 */
int serial_recv(char *buf, int max_len)
{
    int count = 0;
    unsigned char lsr;
    
    if (!g_serial_state.initialized || !buf || max_len <= 0) {
        return -1;
    }
    
    /* Read available data */
    while (count < max_len) {
        lsr = inp(g_serial_state.port + UART_LSR);
        
        /* Check if data available */
        if (lsr & LSR_DR) {
            buf[count++] = inp(g_serial_state.port + UART_RBR);
        } else {
            break;  /* No more data */
        }
    }
    
    return count;
}

/*
 * Check if data available
 * 
 * Returns: 1 if data available, 0 otherwise
 */
int serial_data_available(void)
{
    if (!g_serial_state.initialized) return 0;
    
    return inp(g_serial_state.port + UART_LSR) & LSR_DR;
}

/*
 * Send a single byte
 * 
 * byte: Byte to send
 */
void serial_send_byte(unsigned char byte)
{
    unsigned char lsr;
    
    if (!g_serial_state.initialized) return;
    
    /* Wait for transmitter ready */
    do {
        lsr = inp(g_serial_state.port + UART_LSR);
    } while (!(lsr & LSR_THRE));
    
    /* Send byte */
    outp(g_serial_state.port + UART_THR, byte);
}

/*
 * Receive a single byte (blocking)
 * 
 * Returns: Received byte
 */
unsigned char serial_recv_byte(void)
{
    unsigned char lsr;
    
    if (!g_serial_state.initialized) return 0;
    
    /* Wait for data available */
    do {
        lsr = inp(g_serial_state.port + UART_LSR);
    } while (!(lsr & LSR_DR));
    
    /* Read byte */
    return inp(g_serial_state.port + UART_RBR);
}
