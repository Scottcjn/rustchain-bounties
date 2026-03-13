#!/usr/bin/env python3
"""
RustChain Sigma 7 Gateway Proxy

This gateway translates between the Sigma 7's binary serial protocol
and the RustChain HTTP/HTTPS API. It enables the 1967 computer to
participate in the modern blockchain network.

Features:
- Serial communication @ 9600 baud (COC-compatible)
- Binary protocol encoding/decoding
- HTTP/HTTPS translation to rustchain.org
- Wallet management
- Logging and debugging

Requirements:
- Python 3.8+
- pyserial
- requests

Usage:
    python gateway_proxy.py --port /dev/ttyUSB0 --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import argparse
import serial
import requests
import struct
import hashlib
import time
import json
import logging
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sigma7_gateway.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

SIGMA7_NODE = "https://rustchain.org"
DEFAULT_SERIAL_PORT = "/dev/ttyUSB0"
DEFAULT_BAUD_RATE = 9600
DEFAULT_TIMEOUT = 30

# Protocol Constants
CMD_EPOCH = 0x01
CMD_ATTEST = 0x02
CMD_BALANCE = 0x03
CMD_HEARTBEAT = 0x04

STATUS_SUCCESS = 0x00
STATUS_ERROR = 0x01
STATUS_RETRY = 0x02

# Frame Format:
# [CMD:1][LEN:1][DATA:LEN][CHECKSUM:2]

# ============================================================================
# CRC-16 Implementation (Modbus)
# ============================================================================

def calc_crc16(data: bytes) -> bytes:
    """Calculate CRC-16 checksum (Modbus polynomial)"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def verify_crc16(data: bytes, expected_crc: bytes) -> bool:
    """Verify CRC-16 checksum"""
    return calc_crc16(data) == expected_crc

# ============================================================================
# Protocol Encoding/Decoding
# ============================================================================

def encode_frame(cmd: int, data: bytes) -> bytes:
    """Encode a protocol frame"""
    frame = struct.pack('BB', cmd, len(data)) + data
    checksum = calc_crc16(data)
    return frame + checksum

def decode_frame(raw: bytes) -> Tuple[Optional[int], Optional[bytes]]:
    """
    Decode a protocol frame.
    Returns (cmd, data) or (None, None) if invalid.
    """
    if len(raw) < 4:
        return None, None
    
    cmd = raw[0]
    length = raw[1]
    
    if len(raw) < 4 + length:
        return None, None
    
    data = raw[2:2+length]
    received_crc = raw[2+length:2+length+2]
    
    if not verify_crc16(data, received_crc):
        logger.warning("CRC mismatch in received frame")
        return None, None
    
    return cmd, data

# ============================================================================
# Sigma 7 Communication Handler
# ============================================================================

class Sigma7Handler:
    """Handles communication with the Sigma 7 via serial"""
    
    def __init__(self, port: str, baud: int = DEFAULT_BAUD_RATE):
        self.port = port
        self.baud = baud
        self.ser: Optional[serial.Serial] = None
        self.connected = False
    
    def connect(self) -> bool:
        """Open serial connection"""
        try:
            self.ser = serial.Serial(
                self.port, 
                self.baud, 
                timeout=DEFAULT_TIMEOUT,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.connected = True
            logger.info(f"Connected to Sigma 7 on {self.port} @ {self.baud} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.connected = False
            logger.info("Disconnected from Sigma 7")
    
    def receive_message(self) -> Tuple[Optional[int], Optional[bytes]]:
        """Receive a message from Sigma 7"""
        if not self.connected:
            return None, None
        
        try:
            # Read header (CMD + LEN)
            header = self.ser.read(2)
            if len(header) < 2:
                return None, None
            
            cmd, length = struct.unpack('BB', header)
            
            # Read data
            data = self.ser.read(length)
            if len(data) < length:
                logger.warning(f"Incomplete data: expected {length}, got {len(data)}")
                return None, None
            
            # Read checksum
            checksum = self.ser.read(2)
            if len(checksum) < 2:
                return None, None
            
            # Verify CRC
            if not verify_crc16(data, checksum):
                logger.warning("CRC verification failed")
                return None, None
            
            logger.debug(f"Received CMD={cmd:02X}, LEN={length}")
            return cmd, data
            
        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            return None, None
    
    def send_response(self, status: int, data: bytes) -> bool:
        """Send a response to Sigma 7"""
        if not self.connected:
            return False
        
        try:
            frame = struct.pack('BB', status, len(data)) + data
            checksum = calc_crc16(data)
            self.ser.write(frame + checksum)
            self.ser.flush()
            logger.debug(f"Sent STATUS={status:02X}, LEN={len(data)}")
            return True
        except serial.SerialException as e:
            logger.error(f"Send error: {e}")
            return False

# ============================================================================
# RustChain API Client
# ============================================================================

class RustChainClient:
    """Client for RustChain HTTP/HTTPS API"""
    
    def __init__(self, node_url: str = SIGMA7_NODE):
        self.node_url = node_url
        self.session = requests.Session()
        self.session.verify = False  # Self-signed certs
        logger.warning("SSL verification disabled for self-signed certificates")
    
    def get_epoch(self) -> Optional[dict]:
        """Get current epoch information"""
        try:
            resp = self.session.get(f"{self.node_url}/epoch", timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.error(f"Epoch request failed: {e}")
            return None
    
    def submit_attestation(self, wallet: str, fingerprint: str) -> bool:
        """Submit hardware attestation"""
        try:
            resp = self.session.post(
                f"{self.node_url}/api/attest",
                json={
                    "wallet": wallet,
                    "fingerprint": fingerprint,
                    "platform": "sigma7",
                    "era": "1967"
                },
                timeout=30
            )
            resp.raise_for_status()
            logger.info(f"Attestation submitted for wallet {wallet[:10]}...")
            return True
        except requests.RequestException as e:
            logger.error(f"Attestation failed: {e}")
            return False
    
    def check_balance(self, wallet: str) -> Optional[float]:
        """Check wallet balance"""
        try:
            resp = self.session.get(
                f"{self.node_url}/wallet/balance?miner_id={wallet}",
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get('balance', 0.0)
        except requests.RequestException as e:
            logger.error(f"Balance check failed: {e}")
            return None
    
    def heartbeat(self) -> bool:
        """Send heartbeat to node"""
        try:
            resp = self.session.get(f"{self.node_url}/health", timeout=5)
            return resp.status_code == 200
        except requests.RequestException:
            return False

# ============================================================================
# Gateway Proxy Server
# ============================================================================

class Sigma7Gateway:
    """Main gateway proxy server"""
    
    def __init__(self, serial_port: str, wallet: str, baud: int = DEFAULT_BAUD_RATE):
        self.serial_handler = Sigma7Handler(serial_port, baud)
        self.rustchain_client = RustChainClient()
        self.wallet = wallet
        self.running = False
        self.stats = {
            'epochs_processed': 0,
            'attestations_sent': 0,
            'errors': 0,
            'start_time': None
        }
    
    def start(self):
        """Start the gateway server"""
        logger.info("=" * 60)
        logger.info("RustChain Sigma 7 Gateway Proxy")
        logger.info("=" * 60)
        logger.info(f"Serial Port: {self.serial_handler.port}")
        logger.info(f"Baud Rate: {self.serial_handler.baud}")
        logger.info(f"Wallet: {self.wallet}")
        logger.info(f"Node: {SIGMA7_NODE}")
        logger.info("=" * 60)
        
        if not self.serial_handler.connect():
            logger.error("Failed to connect to Sigma 7. Exiting.")
            return
        
        self.stats['start_time'] = datetime.now()
        self.running = True
        
        try:
            while self.running:
                self.process_message()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the gateway server"""
        self.running = False
        self.serial_handler.disconnect()
        self.print_stats()
    
    def print_stats(self):
        """Print statistics"""
        if self.stats['start_time']:
            uptime = datetime.now() - self.stats['start_time']
            logger.info("=" * 60)
            logger.info("Gateway Statistics")
            logger.info("=" * 60)
            logger.info(f"Uptime: {uptime}")
            logger.info(f"Epochs Processed: {self.stats['epochs_processed']}")
            logger.info(f"Attestations Sent: {self.stats['attestations_sent']}")
            logger.info(f"Errors: {self.stats['errors']}")
            logger.info("=" * 60)
    
    def process_message(self):
        """Process a single message from Sigma 7"""
        cmd, data = self.serial_handler.receive_message()
        
        if cmd is None:
            time.sleep(0.1)
            return
        
        logger.info(f"Processing command: {cmd:02X}")
        
        try:
            if cmd == CMD_EPOCH:
                self.handle_epoch_request()
            elif cmd == CMD_ATTEST:
                self.handle_attestation(data)
            elif cmd == CMD_BALANCE:
                self.handle_balance_request(data)
            elif cmd == CMD_HEARTBEAT:
                self.handle_heartbeat()
            else:
                logger.warning(f"Unknown command: {cmd:02X}")
                self.serial_handler.send_response(STATUS_ERROR, b'Unknown command')
                self.stats['errors'] += 1
        except Exception as e:
            logger.error(f"Error processing command {cmd:02X}: {e}")
            self.serial_handler.send_response(STATUS_ERROR, str(e).encode()[:50])
            self.stats['errors'] += 1
    
    def handle_epoch_request(self):
        """Handle epoch info request"""
        epoch_info = self.rustchain_client.get_epoch()
        
        if epoch_info:
            # Pack epoch number as 64-bit integer
            epoch_num = epoch_info.get('epoch', 0)
            data = struct.pack('<Q', epoch_num)
            self.serial_handler.send_response(STATUS_SUCCESS, data)
            logger.info(f"Sent epoch {epoch_num} to Sigma 7")
        else:
            self.serial_handler.send_response(STATUS_ERROR, b'Failed to get epoch')
            self.stats['errors'] += 1
    
    def handle_attestation(self, data: bytes):
        """Handle attestation submission"""
        if len(data) < 104:
            self.serial_handler.send_response(STATUS_ERROR, b'Invalid attestation length')
            return
        
        # Parse attestation
        wallet = data[:40].decode('utf-8', errors='ignore').strip('\x00')
        fingerprint = data[40:104].hex()
        
        logger.info(f"Received attestation from wallet {wallet[:10]}...")
        
        # Submit to RustChain
        success = self.rustchain_client.submit_attestation(wallet, fingerprint)
        
        if success:
            self.serial_handler.send_response(STATUS_SUCCESS, b'OK')
            self.stats['attestations_sent'] += 1
            self.stats['epochs_processed'] += 1
        else:
            self.serial_handler.send_response(STATUS_ERROR, b'Attestation failed')
            self.stats['errors'] += 1
    
    def handle_balance_request(self, data: bytes):
        """Handle balance query"""
        wallet = data[:40].decode('utf-8', errors='ignore').strip('\x00')
        balance = self.rustchain_client.check_balance(wallet)
        
        if balance is not None:
            balance_bytes = struct.pack('<d', balance)
            self.serial_handler.send_response(STATUS_SUCCESS, balance_bytes)
            logger.info(f"Sent balance {balance} RTC to Sigma 7")
        else:
            self.serial_handler.send_response(STATUS_ERROR, b'Balance query failed')
            self.stats['errors'] += 1
    
    def handle_heartbeat(self):
        """Handle heartbeat ping"""
        alive = self.rustchain_client.heartbeat()
        
        if alive:
            self.serial_handler.send_response(STATUS_SUCCESS, b'ALIVE')
        else:
            self.serial_handler.send_response(STATUS_RETRY, b'Node unavailable')

# ============================================================================
# Command Line Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='RustChain Sigma 7 Gateway Proxy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --port /dev/ttyUSB0 --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
  %(prog)s --port COM3 --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b --baud 9600
  %(prog)s --port /dev/ttyUSB0 --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b --node https://rustchain.org
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        default=DEFAULT_SERIAL_PORT,
        help=f'Serial port (default: {DEFAULT_SERIAL_PORT})'
    )
    
    parser.add_argument(
        '--baud', '-b',
        type=int,
        default=DEFAULT_BAUD_RATE,
        help=f'Baud rate (default: {DEFAULT_BAUD_RATE})'
    )
    
    parser.add_argument(
        '--wallet', '-w',
        required=True,
        help='RustChain wallet address'
    )
    
    parser.add_argument(
        '--node', '-n',
        default=SIGMA7_NODE,
        help=f'RustChain node URL (default: {SIGMA7_NODE})'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Update node URL if specified
    global SIGMA7_NODE
    SIGMA7_NODE = args.node
    
    # Create and start gateway
    gateway = Sigma7Gateway(
        serial_port=args.port,
        wallet=args.wallet,
        baud=args.baud
    )
    
    gateway.start()

if __name__ == "__main__":
    main()
