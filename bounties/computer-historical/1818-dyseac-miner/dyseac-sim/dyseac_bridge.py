#!/usr/bin/env python3
"""
DYSEAC Network Bridge
=====================

Connects DYSEAC (1954) to the modern RustChain network.

Since DYSEAC has no native networking, we use a bridge approach:
1. Paper Tape Bridge - Microcontroller handles TCP/IP + HTTPS
2. DYSEAC punches requests to paper tape
3. Microcontroller reads tape, sends to network
4. Response punched to new tape, DYSEAC reads

Alternative interfaces:
- Teleprinter Interface - Serial communication
- Direct I/O Interface - FPGA/microcontroller memory-mapped I/O

This implementation simulates the bridge for testing.

Author: RustChain Community
License: MIT
"""

import json
import time
import hashlib
import requests
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


# ============================================================================
# Paper Tape Protocol
# ============================================================================

@dataclass
class PaperTapeFrame:
    """Represents a frame of data on paper tape"""
    address: int
    data: int
    checksum: int
    timestamp: float = 0.0


class PaperTapeProtocol:
    """
    Paper tape communication protocol
    
    Format:
    - Start marker (0xFF)
    - Address (2 bytes)
    - Data length (1 byte)
    - Data (N bytes)
    - Checksum (2 bytes)
    - End marker (0xFE)
    """
    
    START_MARKER = 0xFF
    END_MARKER = 0xFE
    
    def encode_request(self, request_type: str, data: Dict) -> bytes:
        """Encode a request to paper tape format"""
        payload = json.dumps({
            "type": request_type,
            "data": data,
            "timestamp": time.time()
        }).encode('utf-8')
        
        # Build frame
        frame = bytes([self.START_MARKER])
        frame += len(payload).to_bytes(2, 'big')
        frame += payload
        checksum = self._calculate_checksum(payload)
        frame += checksum.to_bytes(2, 'big')
        frame += bytes([self.END_MARKER])
        
        return frame
    
    def decode_response(self, tape_data: bytes) -> Optional[Dict]:
        """Decode a response from paper tape format"""
        if len(tape_data) < 6:
            return None
        
        if tape_data[0] != self.START_MARKER:
            return None
        
        if tape_data[-1] != self.END_MARKER:
            return None
        
        # Extract payload length
        payload_len = int.from_bytes(tape_data[1:3], 'big')
        
        # Extract payload
        payload = tape_data[3:3+payload_len]
        
        # Verify checksum
        stored_checksum = int.from_bytes(tape_data[3+payload_len:3+payload_len+2], 'big')
        calculated_checksum = self._calculate_checksum(payload)
        
        if stored_checksum != calculated_checksum:
            print(f"[WARN] Checksum mismatch: stored={stored_checksum}, calc={calculated_checksum}")
            return None
        
        # Parse JSON
        try:
            message = json.loads(payload.decode('utf-8'))
            return message
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            return None
    
    def _calculate_checksum(self, data: bytes) -> int:
        """Calculate simple checksum"""
        return sum(data) & 0xFFFF


# ============================================================================
# Network Bridge (Microcontroller Side)
# ============================================================================

class NetworkBridge:
    """
    Network bridge between DYSEAC and RustChain network
    
    Runs on microcontroller (Arduino Due, Raspberry Pi, etc.)
    Handles:
    - TCP/IP stack
    - HTTPS client
    - Paper tape I/O
    - Protocol conversion
    """
    
    def __init__(self, node_url: str = "https://rustchain.org"):
        self.node_url = node_url
        self.protocol = PaperTapeProtocol()
        self.wallet = None
        self.session = requests.Session()
        self.session.verify = False  # Self-signed certs
        
        print("=" * 70)
        print("DYSEAC Network Bridge")
        print("=" * 70)
        print(f"Node URL: {node_url}")
        print("Interface: Paper Tape Bridge (simulated)")
        print("=" * 70)
    
    def connect_to_dyseac(self):
        """Initialize connection to DYSEAC (via paper tape reader/punch)"""
        print("\n[BRIDGE] Connecting to DYSEAC...")
        # In real implementation, this would initialize GPIO pins
        # for paper tape reader and punch
        print("[BRIDGE] Paper tape interface ready")
        return True
    
    def send_request(self, request_type: str, data: Dict) -> bytes:
        """Send request to DYSEAC via paper tape"""
        print(f"\n[BRIDGE] Sending {request_type} to DYSEAC...")
        
        # Encode request
        tape_frame = self.protocol.encode_request(request_type, data)
        
        # Simulate punching to paper tape
        print(f"[BRIDGE] Punching {len(tape_frame)} bytes to paper tape...")
        time.sleep(0.1)  # Simulate punch time
        
        return tape_frame
    
    def read_response(self, tape_data: bytes) -> Optional[Dict]:
        """Read response from DYSEAC via paper tape"""
        print(f"\n[BRIDGE] Reading response from paper tape...")
        
        # Simulate reading from paper tape
        time.sleep(0.1)  # Simulate read time
        
        # Decode response
        response = self.protocol.decode_response(tape_data)
        
        if response:
            print(f"[BRIDGE] Response received: {response.get('type', 'unknown')}")
        
        return response
    
    # ========================================================================
    # RustChain Network Operations
    # ========================================================================
    
    def get_epoch_info(self) -> Optional[Dict]:
        """Get current epoch information from RustChain network"""
        try:
            response = self.session.get(f"{self.node_url}/epoch", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[ERROR] Epoch request failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Network error: {e}")
        return None
    
    def get_work(self, miner_id: str) -> Optional[Dict]:
        """Get mining work from network"""
        try:
            response = self.session.post(
                f"{self.node_url}/mine/get_work",
                json={"miner_id": miner_id},
                timeout=10
            )
            if response.status_code == 200:
                work = response.json()
                print(f"[BRIDGE] Got work: difficulty={work.get('difficulty', 'N/A')}")
                return work
            else:
                print(f"[ERROR] Get work failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Network error: {e}")
        return None
    
    def submit_proof(self, miner_id: str, hash_result: str, nonce: int, 
                     fingerprint: Dict) -> Optional[Dict]:
        """Submit mining proof to network"""
        try:
            proof = {
                "miner_id": miner_id,
                "hash": hash_result,
                "nonce": nonce,
                "timestamp": time.time(),
                "fingerprint": fingerprint
            }
            
            response = self.session.post(
                f"{self.node_url}/mine/submit",
                json=proof,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"[BRIDGE] Proof submitted: {result.get('status', 'N/A')}")
                return result
            else:
                print(f"[ERROR] Submit proof failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Network error: {e}")
        return None
    
    def attest_hardware(self, fingerprint: Dict) -> Optional[Dict]:
        """Submit hardware attestation to network"""
        try:
            response = self.session.post(
                f"{self.node_url}/attest/submit",
                json=fingerprint,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"[BRIDGE] Attestation submitted: {result.get('status', 'N/A')}")
                return result
            else:
                print(f"[ERROR] Attestation failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Network error: {e}")
        return None
    
    def check_balance(self, wallet: str) -> Optional[float]:
        """Check wallet balance"""
        try:
            response = self.session.get(
                f"{self.node_url}/wallet/balance",
                params={"miner_id": wallet},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                balance = result.get('balance_rtc', 0)
                print(f"[BRIDGE] Balance: {balance} RTC")
                return balance
            else:
                print(f"[ERROR] Balance check failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Network error: {e}")
        return None


# ============================================================================
# DYSEAC Hardware Fingerprinting
# ============================================================================

class DYSEACFingerprinter:
    """
    Generates unique hardware fingerprint for DYSEAC
    
    Fingerprint components:
    1. Mercury delay-line timing signature
    2. Temperature-dependent drift patterns
    3. Vacuum tube characteristics (simulated)
    4. Diode logic timing profile
    """
    
    def __init__(self, dyseac_system):
        self.dyseac = dyseac_system
        self.baseline_timing = None
        self.drift_profile = None
    
    def measure_delay_line_timing(self) -> Dict:
        """Measure mercury delay-line access times"""
        print("\n[FINGERPRINT] Measuring delay-line timing...")
        
        timing_profile = self.dyseac.memory.get_timing_profile()
        
        # Extract key metrics
        channel_times = []
        for channel in timing_profile['channels']:
            channel_times.append(channel['avg_access_time'])
        
        self.baseline_timing = {
            "channel_avg_times": channel_times,
            "global_avg": sum(channel_times) / len(channel_times),
            "variance": self._calculate_variance(channel_times),
            "fingerprint": timing_profile['channels'][0]['fingerprint'][:16]
        }
        
        print(f"[FINGERPRINT] Baseline timing captured")
        print(f"  Global avg: {self.baseline_timing['global_avg']:.2f} μs")
        print(f"  Variance: {self.baseline_timing['variance']:.4f}")
        
        return self.baseline_timing
    
    def measure_temperature_drift(self, temp_range: Tuple[float, float] = (35.0, 45.0)) -> Dict:
        """Measure temperature-dependent drift patterns"""
        print(f"\n[FINGERPRINT] Measuring temperature drift ({temp_range[0]}-{temp_range[1]}°C)...")
        
        drift_data = []
        temp_step = 1.0
        
        for temp in range(int(temp_range[0]), int(temp_range[1]) + 1, int(temp_step)):
            self.dyseac.set_temperature(float(temp))
            time.sleep(0.01)  # Let temperature stabilize (simulated)
            
            timing = self.dyseac.memory.get_timing_profile()
            avg_time = sum(
                ch['avg_access_time'] for ch in timing['channels']
            ) / len(timing['channels'])
            
            drift_data.append({
                "temperature": temp,
                "avg_access_time": avg_time
            })
        
        # Calculate drift coefficient
        if len(drift_data) >= 2:
            delta_time = drift_data[-1]['avg_access_time'] - drift_data[0]['avg_access_time']
            delta_temp = drift_data[-1]['temperature'] - drift_data[0]['temperature']
            drift_coefficient = delta_time / delta_temp if delta_temp != 0 else 0
        else:
            drift_coefficient = 0
        
        self.drift_profile = {
            "measurements": drift_data,
            "drift_coefficient": drift_coefficient,
            "unit": "μs/°C"
        }
        
        print(f"[FINGERPRINT] Drift coefficient: {drift_coefficient:.4f} μs/°C")
        
        return self.drift_profile
    
    def _calculate_variance(self, values: list) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
    
    def generate_fingerprint(self) -> Dict:
        """Generate complete hardware fingerprint"""
        print("\n" + "=" * 70)
        print("DYSEAC Hardware Fingerprint Generation")
        print("=" * 70)
        
        # Measure timing
        timing = self.measure_delay_line_timing()
        
        # Measure temperature drift
        drift = self.measure_temperature_drift()
        
        # Get memory fingerprint
        memory_fp = self.dyseac.memory.get_fingerprint()
        
        # Compile complete fingerprint
        fingerprint = {
            "system": "DYSEAC",
            "year": 1954,
            "manufacturer": "National Bureau of Standards",
            "type": "First portable computer (truck-mounted)",
            "timestamp": time.time(),
            
            "mercury_delay_line": {
                "channels": 64,
                "words_per_channel": 8,
                "total_words": 512,
                "timing_profile": timing,
                "drift_profile": drift,
                "fingerprint": memory_fp
            },
            
            "vacuum_tubes": {
                "count": 900,
                "type": "Amplification/inversion/flip-flops",
                "warmup_drift": "simulated"  # Would be measured on real hardware
            },
            
            "crystal_diodes": {
                "count": 24500,
                "type": "All logic functions",
                "timing_signature": "simulated"  # Would be measured on real hardware
            },
            
            "serial_architecture": {
                "word_bits": 45,
                "clock_mhz": 1.0,
                "cycles_per_word": 45
            },
            
            "mobile_design": {
                "enclosure": "Truck-mounted",
                "weight_tons": 20,
                "shock_mounted": True,
                "temperature_controlled": True
            }
        }
        
        # Generate overall fingerprint hash
        fp_string = json.dumps(fingerprint, sort_keys=True)
        fingerprint["overall_hash"] = hashlib.sha256(fp_string.encode()).hexdigest()
        
        print(f"\n[FINGERPRINT] Complete fingerprint generated")
        print(f"  Hash: {fingerprint['overall_hash'][:32]}...")
        
        return fingerprint


# ============================================================================
# DYSEAC Mining Loop
# ============================================================================

class DYSEAC_MiningLoop:
    """
    Complete mining loop for DYSEAC
    
    Orchestrates:
    1. Hardware attestation
    2. Get work from network
    3. Mine on DYSEAC
    4. Submit proof
    5. Receive rewards
    """
    
    def __init__(self, wallet: str, dyseac_system, bridge: NetworkBridge):
        self.wallet = wallet
        self.dyseac = dyseac_system
        self.bridge = bridge
        self.fingerprinter = DYSEACFingerprinter(dyseac_system)
        
        # Import SHA256 miner
        from dyseac_sha256 import DYSEAC_Miner
        self.miner = DYSEAC_Miner(wallet, dyseac_system)
        
        self.running = False
        self.epoch_count = 0
        self.total_rewards = 0.0
    
    def attest(self) -> bool:
        """Attest hardware to RustChain network"""
        print("\n" + "=" * 70)
        print("DYSEAC Hardware Attestation")
        print("=" * 70)
        
        # Generate fingerprint
        fingerprint = self.fingerprinter.generate_fingerprint()
        
        # Submit to network
        result = self.bridge.attest_hardware(fingerprint)
        
        if result and result.get('ok'):
            print("\n[SUCCESS] Hardware attested!")
            return True
        else:
            print("\n[FAILED] Attestation failed")
            return False
    
    def mine_epoch(self) -> bool:
        """Mine for one epoch (10 minutes)"""
        print(f"\n{'='*70}")
        print(f"Epoch #{self.epoch_count + 1}")
        print(f"{'='*70}")
        
        # Get work from network
        work = self.bridge.get_work(self.wallet)
        if not work:
            print("[ERROR] Failed to get work")
            return False
        
        # Extract work data
        data = work.get('data', b'RustChain DYSEAC Test').encode() if isinstance(work.get('data'), str) else b'RustChain DYSEAC Test'
        difficulty = work.get('difficulty', 2)
        
        print(f"Mining difficulty: {difficulty}")
        print(f"Starting mining loop...")
        
        # Mine on DYSEAC
        start_time = time.time()
        hash_result, nonce = self.miner.mine(data, difficulty)
        mining_time = time.time() - start_time
        
        print(f"\n[SUCCESS] Solution found in {mining_time:.2f}s")
        print(f"  Hash: {hash_result.hex()}")
        print(f"  Nonce: {nonce}")
        
        # Get fingerprint for proof
        fingerprint = self.fingerprinter.generate_fingerprint()
        
        # Submit proof
        proof_result = self.bridge.submit_proof(
            miner_id=self.wallet,
            hash_result=hash_result.hex(),
            nonce=nonce,
            fingerprint=fingerprint
        )
        
        if proof_result and proof_result.get('ok'):
            reward = proof_result.get('reward', 0)
            self.total_rewards += reward
            print(f"\n[REWARD] +{reward} RTC")
            print(f"  Total rewards: {self.total_rewards} RTC")
            return True
        else:
            print(f"\n[ERROR] Proof submission failed")
            return False
    
    def run(self, epochs: int = 1):
        """Run mining loop for specified number of epochs"""
        print("\n" + "=" * 70)
        print("DYSEAC Mining Loop Starting")
        print("=" * 70)
        print(f"Wallet: {self.wallet}")
        print(f"Epochs: {epochs}")
        print("=" * 70)
        
        self.running = True
        
        # Attest hardware first
        if not self.attest():
            print("[ERROR] Attestation failed - cannot start mining")
            return
        
        # Mine epochs
        for i in range(epochs):
            self.epoch_count = i
            if not self.mine_epoch():
                print(f"[WARN] Epoch {i+1} failed, continuing...")
            
            if i < epochs - 1:
                print(f"\n[INFO] Waiting for next epoch...")
                time.sleep(1)  # Short wait for demo
        
        self.running = False
        
        # Final summary
        print("\n" + "=" * 70)
        print("Mining Session Complete")
        print("=" * 70)
        print(f"Epochs completed: {self.epoch_count + 1}")
        print(f"Total rewards: {self.total_rewards} RTC")
        print(f"Total hashes: {self.miner.hashes_computed}")
        print("=" * 70)


# ============================================================================
# Main Entry Point (Demo Mode)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("DYSEAC Network Bridge - RustChain Miner")
    print("First Portable Computer Mining Demo")
    print("=" * 70)
    
    # Import DYSEAC simulator
    from dyseac_simulator import DYSEAC_System
    
    # Create DYSEAC system
    dyseac = DYSEAC_System(seed=42)
    
    # Create network bridge (simulated)
    bridge = NetworkBridge(node_url="https://rustchain.org")
    
    # Create mining loop
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    mining_loop = DYSEAC_MiningLoop(wallet, dyseac, bridge)
    
    # Run demo (1 epoch)
    print("\n[DEMO MODE] Running 1 epoch for demonstration...")
    mining_loop.run(epochs=1)
    
    print("\n" + "=" * 70)
    print("DYSEAC Network Bridge Demo Complete!")
    print("=" * 70)
