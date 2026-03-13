#!/usr/bin/env python3
"""
ZX Spectrum RustChain Miner - PC Bridge

This script acts as a network bridge between the ZX Spectrum miner
(running on real 1982 hardware) and the RustChain network.

The ZX Spectrum sends attestations via serial, this bridge forwards
them to the RustChain API and returns responses.

Usage:
    python pc_bridge.py [--port COM3] [--baud 9600]
"""

import serial
import json
import requests
import time
import argparse
from datetime import datetime

# Configuration
DEFAULT_PORT = 'COM3'
DEFAULT_BAUD = 9600
RUSTCHAIN_API = 'https://rustchain.org/api'

class ZXBridge:
    """Bridge between ZX Spectrum serial and RustChain network."""
    
    def __init__(self, port=DEFAULT_PORT, baud=DEFAULT_BAUD):
        """Initialize serial connection."""
        try:
            self.ser = serial.Serial(port, baud, timeout=1)
            print(f"✓ Connected to {port} at {baud} baud")
            print(f"  Waiting for ZX Spectrum attestations...")
            print(f"  Press Ctrl+C to exit\n")
        except serial.SerialException as e:
            print(f"✗ Failed to open {port}: {e}")
            print(f"  Make sure the ZX Spectrum is connected and powered on.")
            print(f"  Check the port name (COM3 on Windows, /dev/ttyUSB0 on Linux)")
            raise SystemExit(1)
        
        self.attestation_count = 0
        self.total_reward = 0.0
        self.start_time = datetime.now()
    
    def read_line(self):
        """Read a line from ZX Spectrum."""
        try:
            line = self.ser.readline().decode('ascii', errors='ignore').strip()
            return line
        except Exception as e:
            print(f"  Read error: {e}")
            return None
    
    def write_line(self, line):
        """Write a line to ZX Spectrum."""
        try:
            self.ser.write(f"{line}\n".encode('ascii'))
        except Exception as e:
            print(f"  Write error: {e}")
    
    def forward_attestation(self, data):
        """Forward attestation to RustChain network."""
        try:
            print(f"  → Forwarding to RustChain API...")
            
            response = requests.post(
                f"{RUSTCHAIN_API}/attest",
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"  ✗ API Error: {e}")
            return {"success": False, "error": str(e)}
        except json.JSONDecodeError as e:
            print(f"  ✗ JSON Error: {e}")
            return {"success": False, "error": "Invalid response"}
    
    def handle_attestation(self, json_str):
        """Handle ATTEST message from ZX Spectrum."""
        print(f"⚡ Received attestation from ZX Spectrum")
        print(f"  Payload: {json_str[:100]}...")
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"  ✗ Invalid JSON: {e}")
            self.write_line("ACK:FAIL:Invalid JSON")
            return
        
        # Validate required fields
        required = ['device_arch', 'wallet']
        for field in required:
            if field not in data:
                print(f"  ✗ Missing field: {field}")
                self.write_line(f"ACK:FAIL:Missing {field}")
                return
        
        # Forward to RustChain
        result = self.forward_attestation(data)
        
        if result.get('success'):
            reward = result.get('reward', 0)
            self.attestation_count += 1
            self.total_reward += reward
            
            print(f"  ✓ Success! Reward: {reward} RTC")
            print(f"  Total: {self.attestation_count} attestations, {self.total_reward:.4f} RTC")
            
            self.write_line(f"ACK:OK:{reward}")
            
            # Log to file
            self.log_attestation(data, result)
        else:
            error = result.get('error', 'Unknown error')
            print(f"  ✗ Failed: {error}")
            self.write_line(f"ACK:FAIL:{error}")
    
    def handle_status(self, status):
        """Handle STATUS message from ZX Spectrum."""
        print(f"📊 ZX Spectrum Status: {status}")
    
    def log_attestation(self, data, result):
        """Log attestation to file."""
        try:
            with open('attestations.log', 'a') as f:
                timestamp = datetime.now().isoformat()
                log_entry = {
                    'timestamp': timestamp,
                    'data': data,
                    'result': result
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"  Warning: Could not log attestation: {e}")
    
    def print_stats(self):
        """Print bridge statistics."""
        elapsed = datetime.now() - self.start_time
        print(f"\n{'='*60}")
        print(f"Bridge Statistics")
        print(f"{'='*60}")
        print(f"  Runtime: {elapsed}")
        print(f"  Attestations: {self.attestation_count}")
        print(f"  Total Reward: {self.total_reward:.4f} RTC")
        print(f"  Average: {self.total_reward / max(self.attestation_count, 1):.6f} RTC per attestation")
        print(f"{'='*60}\n")
    
    def run(self):
        """Main bridge loop."""
        try:
            while True:
                line = self.read_line()
                
                if not line:
                    time.sleep(0.1)
                    continue
                
                if line.startswith('ATTEST:'):
                    self.handle_attestation(line[7:])
                
                elif line.startswith('STATUS:'):
                    self.handle_status(line[7:])
                
                else:
                    print(f"  ? Unknown message: {line}")
                
        except KeyboardInterrupt:
            print(f"\n\n⚠ Interrupted by user")
            self.print_stats()
            print(f"Closing serial connection...")
            self.ser.close()
            print(f"Goodbye!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='ZX Spectrum RustChain Miner - PC Bridge'
    )
    parser.add_argument(
        '--port', '-p',
        default=DEFAULT_PORT,
        help=f'Serial port (default: {DEFAULT_PORT})'
    )
    parser.add_argument(
        '--baud', '-b',
        type=int,
        default=DEFAULT_BAUD,
        help=f'Baud rate (default: {DEFAULT_BAUD})'
    )
    
    args = parser.parse_args()
    
    print(f"{'='*60}")
    print(f"ZX Spectrum RustChain Miner - PC Bridge")
    print(f"{'='*60}")
    print(f"  Serial Port: {args.port}")
    print(f"  Baud Rate: {args.baud}")
    print(f"  RustChain API: {RUSTCHAIN_API}")
    print(f"{'='*60}\n")
    
    bridge = ZXBridge(port=args.port, baud=args.baud)
    bridge.run()

if __name__ == '__main__':
    main()
