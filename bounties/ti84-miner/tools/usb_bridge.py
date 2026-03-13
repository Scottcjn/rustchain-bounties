#!/usr/bin/env python3
"""
USB Bridge for TI-84 RustChain Miner

This tool acts as a bridge between the TI-84 calculator and the RustChain network.
It receives attestations from the calculator via USB and forwards them to the node.

Requirements:
    pip install pyusb requests
"""

import usb.core
import usb.util
import json
import time
import hashlib
import requests
from typing import Optional, Dict, Any

# RustChain Node Configuration
NODE_URL = "http://node.rustchain.io:8080"
ATTESTATION_ENDPOINT = "/api/v1/attestation"
WORK_ENDPOINT = "/api/v1/work"

# TI-84 USB Vendor/Product IDs
TI_VENDOR_ID = 0x0451
TI_PRODUCT_ID = 0xC402  # TI-84 Plus

class TI84Bridge:
    """Bridge between TI-84 calculator and RustChain network."""
    
    def __init__(self, node_url: str = NODE_URL):
        self.node_url = node_url
        self.device: Optional[usb.core.Device] = None
        self.endpoint_out = None
        self.endpoint_in = None
        
    def connect(self) -> bool:
        """Connect to TI-84 via USB."""
        print("Searching for TI-84 calculator...")
        
        try:
            self.device = usb.core.find(idVendor=TI_VENDOR_ID, 
                                       idProduct=TI_PRODUCT_ID)
            
            if self.device is None:
                print("❌ TI-84 not found. Please connect via USB cable.")
                return False
            
            # Set configuration
            self.device.set_configuration()
            
            # Find endpoints
            cfg = self.device.get_active_configuration()
            intf = cfg[(0, 0)]
            
            self.endpoint_out = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            
            self.endpoint_in = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
            
            if self.endpoint_out and self.endpoint_in:
                print("✅ Connected to TI-84")
                return True
            else:
                print("❌ Could not find USB endpoints")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def receive_attestation(self) -> Optional[Dict[str, Any]]:
        """Receive attestation data from TI-84."""
        try:
            print("Waiting for attestation data from TI-84...")
            
            # Read data from calculator
            data = self.endpoint_in.read(1024, timeout=30000)
            
            # Parse attestation
            attestation = json.loads(data.tobytes().decode('utf-8'))
            
            print(f"✅ Received attestation (epoch {attestation.get('epoch', '?')})")
            return attestation
            
        except usb.core.USBError as e:
            print(f"❌ USB read error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            return None
    
    def send_work(self, work: Dict[str, Any]) -> bool:
        """Send work unit to TI-84."""
        try:
            print("Sending work unit to TI-84...")
            
            data = json.dumps(work).encode('utf-8')
            self.endpoint_out.write(data)
            
            print("✅ Work unit sent")
            return True
            
        except Exception as e:
            print(f"❌ USB write error: {e}")
            return False
    
    def submit_to_node(self, attestation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Submit attestation to RustChain node."""
        try:
            print(f"Submitting to node: {self.node_url}")
            
            response = requests.post(
                f"{self.node_url}{ATTESTATION_ENDPOINT}",
                json=attestation,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Attestation accepted! Hash: {result.get('hash', 'unknown')}")
                return result
            else:
                print(f"❌ Node rejected attestation: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Node communication error: {e}")
            return None
    
    def get_work_from_node(self) -> Optional[Dict[str, Any]]:
        """Get new work unit from RustChain node."""
        try:
            response = requests.get(
                f"{self.node_url}{WORK_ENDPOINT}",
                timeout=30
            )
            
            if response.status_code == 200:
                work = response.json()
                print(f"✅ Got work unit (epoch {work.get('next_epoch', '?')})")
                return work
            else:
                print(f"❌ Failed to get work: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Node communication error: {e}")
            return None
    
    def run(self):
        """Main bridge loop."""
        print("=" * 60)
        print("TI-84 RustChain USB Bridge")
        print("=" * 60)
        
        if not self.connect():
            return
        
        print("\nBridge active. Press Ctrl+C to exit.\n")
        
        while True:
            try:
                # 1. Receive attestation from TI-84
                attestation = self.receive_attestation()
                if not attestation:
                    time.sleep(1)
                    continue
                
                # 2. Submit to RustChain node
                result = self.submit_to_node(attestation)
                if not result:
                    print("⚠️  Attestation failed, retrying...")
                    time.sleep(2)
                    continue
                
                # 3. Get new work unit
                work = self.get_work_from_node()
                if work:
                    self.send_work(work)
                
                print("-" * 60)
                
            except KeyboardInterrupt:
                print("\n\nBridge stopped by user.")
                break
            except Exception as e:
                print(f"❌ Error in bridge loop: {e}")
                time.sleep(2)


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='TI-84 RustChain USB Bridge')
    parser.add_argument('--node', default=NODE_URL, help='RustChain node URL')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    args = parser.parse_args()
    
    bridge = TI84Bridge(node_url=args.node)
    bridge.run()


if __name__ == '__main__':
    main()
