/*
 * serial.h - Serial port communication for HP 95LX
 * 
 * HP 95LX has RS-232 serial port (DB25 connector via cable)
 * Used for SLIP/PPP networking or direct connection to gateway PC
 */

#ifndef SERIAL_H
#define SERIAL_H

/* Serial port definitions */
#define COM1 0x3F8
#define COM2 0x2F8

/* Common baud rates */
#define BAUD_9600   9600
#define BAUD_19200  19200
#define BAUD_38400  38400
#define BAUD_57600  57600
#define BAUD_115200 115200

/* Initialize serial port */
int serial_init(int port, int baud);

/* Close serial port */
void serial_close(void);

/* Set baud rate */
void serial_set_baud(int baud);

/* Send data */
void serial_send(const char *data, int len);

/* Receive data (returns bytes read, or -1 on error) */
int serial_recv(char *buf, int max_len);

/* Check if data available */
int serial_data_available(void);

/* Send byte */
void serial_send_byte(unsigned char byte);

/* Receive byte (blocking) */
unsigned char serial_recv_byte(void);

#endif /* SERIAL_H */
