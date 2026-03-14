#!/usr/bin/env python3
"""
RustChain C64 Miner Simulator

This simulator mimics the Commodore 64 hardware behavior for testing
the miner logic without real hardware. It simulates:
- CIA timer jitter
- VIC-II raster timing
- SID register behavior
- Network communication
- Attestation flow
"""

import time
import random
import hashlib
import json
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Optional, Dict, Any

# ============================================================================
# Configuration
# ============================================================================

API_ENDPOINT = "http://rustchain.org/api/attest"
ATTESTATION_INTERVAL = 600  # 10 minutes in seconds
SIMULATION_SPEED = 1.0  # 1.0 = real-time, 10.0 = 10x faster

# ============================================================================
# C64 Hardware Simulation
# ============================================================================

@dataclass
class C64HardwareFingerprint:
    """Simulates C64 hardware fingerprint"""
    cia_jitter: int
    vic_raster: int
    sid_offset: int
    rom_checksum: int
    combined: int
    
    @classmethod
    def generate(cls) -> 'C64HardwareFingerprint':
        """Generate a realistic C64 hardware fingerprint"""
        # CIA jitter: real hardware has variance (10-100 cycles)
        cia_jitter = random.randint(15, 85)
        
        # VIC-II raster: typically 63-65 cycles per line
        vic_raster = random.randint(62, 66)
        
        # SID offset: chip-specific behavior (non-zero on real hardware)
        sid_offset = random.randint(1, 255)
        
        # ROM checksum: known Kernal ROM values
        # Common Kernal ROM checksums: 0x6361, 0x77EA, etc.
        rom_checksums = [0x6361, 0x77EA, 0x9B6E, 0x286F]
        rom_checksum = random.choice(rom_checksums)
        
        # Combined fingerprint
        combined = cia_jitter ^ vic_raster ^ sid_offset ^ (rom_checksum << 16)
        
        return cls(
            cia_jitter=cia_jitter,
            vic_raster=vic_raster,
            sid_offset=sid_offset,
            rom_checksum=rom_checksum,
            combined=combined
        )
    
    def is_emulated(self) -> bool:
        """Check if fingerprint looks emulated"""
        # Emulators often have perfect/zero values
        if self.cia_jitter < 10:
            return True
        if self.sid_offset == 0:
            return True
        if self.rom_checksum == 0 or self.rom_checksum == 0xFFFF:
            return True
        return False
    
    def to_miner_id(self) -> str:
        """Generate miner ID from fingerprint"""
        return f"c64-{self.combined:08X}"

# ============================================================================
# Miner State
# ============================================================================

class MinerState:
    """Simulates miner state"""
    
    def __init__(self, wallet: str):
        self.wallet = wallet
        self.hardware = C64HardwareFingerprint.generate()
        self.miner_id = self.hardware.to_miner_id()
        self.earned_rtc = 0.0
        self.attestation_count = 0
        self.last_attest = 0.0
        self.epoch_start = time.time()
        self.network_ready = True
        
    def refresh_fingerprint(self):
        """Refresh hardware fingerprint (with slight variance)"""
        self.hardware = C64HardwareFingerprint.generate()
        self.miner_id = self.hardware.to_miner_id()

# ============================================================================
# Network Simulation
# ============================================================================

class NetworkClient:
    """HTTP client for attestation"""
    
    def __init__(self, simulate: bool = True):
        self.simulate = simulate
        self.request_count = 0
        
    def post_attestation(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send attestation to server"""
        
        if self.simulate:
            # Simulate server response
            return self._simulate_response(payload)
        
        try:
            # Real HTTP POST
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                API_ENDPOINT,
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
                
        except urllib.error.URLError as e:
            print(f"Network error: {e}")
            return None
    
    def _simulate_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate server response"""
        self.request_count += 1
        
        # Simulate reward calculation
        base_reward = 0.00105  # Base reward per epoch
        multiplier = 4.0  # C64 multiplier
        
        return {
            "status": "ok",
            "reward": base_reward * multiplier,
            "multiplier": multiplier,
            "epoch": self.request_count,
            "next_epoch": time.time() + ATTESTATION_INTERVAL
        }

# ============================================================================
# Attestation Builder
# ============================================================================

def build_attestation_payload(state: MinerState) -> Dict[str, Any]:
    """Build attestation JSON payload"""
    
    import time as time_module
    
    return {
        "miner_id": state.miner_id,
        "device": {
            "arch": "6510",
            "family": "commodore_64",
            "cpu_speed": 1023000,
            "total_ram_kb": 64,
            "rom_checksum": state.hardware.rom_checksum
        },
        "signals": {
            "cia_jitter": state.hardware.cia_jitter,
            "vic_raster": state.hardware.vic_raster,
            "sid_offset": state.hardware.sid_offset
        },
        "fingerprint": f"{state.hardware.combined:016X}",
        "report": {
            "epoch": state.attestation_count,
            "timestamp": int(time_module.time())
        }
    }

# ============================================================================
# UI Display
# ============================================================================

class TextUI:
    """Simple text-based UI"""
    
    def __init__(self):
        self.width = 60
        
    def clear(self):
        """Clear screen"""
        print("\n" * 2)
        
    def draw_line(self, char: str = "="):
        """Draw horizontal line"""
        print(char * self.width)
        
    def show_header(self, version: str):
        """Show header"""
        self.draw_line("#")
        print(f"# RUSTCHAIN MINER {version} - C64".center(self.width - 2) + "#")
        print(f"# Proof-of-Antiquity - 4.0x Multiplier".center(self.width - 2) + "#")
        self.draw_line("#")
        
    def show_status(self, status: str):
        """Show status message"""
        print(f"STATUS: {status}")
        
    def show_epoch(self, minutes: int, seconds: int):
        """Show epoch timer"""
        print(f"EPOCH:  {minutes:02d}:{seconds:02d} REMAINING")
        
    def show_earned(self, earned: float):
        """Show earned RTC"""
        print(f"EARNED: {earned:.4f} RTC")
        
    def show_count(self, count: int):
        """Show attestation count"""
        print(f"ATTESTS: {count}")
        
    def show_hardware(self, state: MinerState):
        """Show hardware info"""
        print(f"HW: MOS 6510 @ 1.023 MHz, 64 KB RAM")
        print(f"ID: {state.miner_id}")
        print(f"CIA: {state.hardware.cia_jitter}, VIC: {state.hardware.vic_raster}, SID: {state.hardware.sid_offset}")
        
    def show_menu(self):
        """Show menu"""
        print("\n[F1] PAUSE  [F3] MENU  [F5] QUIT")

# ============================================================================
# Main Simulator
# ============================================================================

class MinerSimulator:
    """Main simulator class"""
    
    def __init__(self, wallet: str = "RTC4325af95d26d59c3ef025963656d22af638bb96b"):
        self.state = MinerState(wallet)
        self.network = NetworkClient(simulate=True)
        self.ui = TextUI()
        self.running = False
        
    def run(self, duration: Optional[float] = None):
        """Run the simulator"""
        self.running = True
        start_time = time.time()
        
        self.ui.clear()
        self.ui.show_header("v0.1.0 (SIMULATOR)")
        print()
        self.ui.show_status("INITIALIZING...")
        print()
        self.ui.show_hardware(self.state)
        print()
        self.ui.show_menu()
        print()
        self.ui.draw_line()
        print()
        
        try:
            while self.running:
                current_time = time.time()
                elapsed = current_time - self.state.epoch_start
                
                # Check for attestation
                if elapsed >= ATTESTATION_INTERVAL / SIMULATION_SPEED:
                    self.ui.show_status("ATTESTING...")
                    
                    # Refresh fingerprint
                    self.state.refresh_fingerprint()
                    
                    # Build payload
                    payload = build_attestation_payload(self.state)
                    
                    # Send attestation
                    response = self.network.post_attestation(payload)
                    
                    if response and response.get("status") == "ok":
                        reward = response.get("reward", 0.0)
                        self.state.earned_rtc += reward
                        self.state.attestation_count += 1
                        self.state.epoch_start = current_time
                        self.ui.show_status("ATTESTATION OK ✓")
                        print(f"  Reward: {reward:.4f} RTC")
                    else:
                        self.ui.show_status("ATTESTATION FAILED ✗")
                    
                    # Update display
                    self._update_display()
                    
                # Check duration limit
                if duration and (current_time - start_time) >= duration:
                    break
                
                # Small delay
                time.sleep(0.5 / SIMULATION_SPEED)
                
        except KeyboardInterrupt:
            print("\n\nStopped by user")
        
        # Final summary
        self._show_summary()
    
    def _update_display(self):
        """Update display"""
        elapsed = time.time() - self.state.epoch_start
        remaining = max(0, ATTESTATION_INTERVAL / SIMULATION_SPEED - elapsed)
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        print(f"\r", end="")
        self.ui.show_epoch(minutes, seconds)
        self.ui.show_earned(self.state.earned_rtc)
        self.ui.show_count(self.state.attestation_count)
    
    def _show_summary(self):
        """Show final summary"""
        print()
        self.ui.draw_line()
        print("MINING SUMMARY")
        self.ui.draw_line()
        print(f"Wallet:       {self.state.wallet}")
        print(f"Miner ID:     {self.state.miner_id}")
        print(f"Attestations: {self.state.attestation_count}")
        print(f"Total Earned: {self.state.earned_rtc:.4f} RTC")
        print(f"Multiplier:   4.0x (Commodore 64)")
        print(f"Network Req:  {self.network.request_count}")
        self.ui.draw_line()
        print()

# ============================================================================
# Entry Point
# ============================================================================

def main():
    """Main entry point"""
    import sys
    
    print("=" * 60)
    print("RustChain C64 Miner Simulator")
    print("=" * 60)
    print()
    print("This simulator mimics C64 hardware behavior for testing.")
    print("Real hardware required for actual attestation!")
    print()
    
    # Check for command line argument
    if len(sys.argv) > 1:
        wallet = sys.argv[1]
        duration = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    else:
        # Interactive mode
        try:
            wallet = input("Enter wallet address (or press Enter for default): ").strip()
            if not wallet:
                wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
            
            print()
            print(f"Using wallet: {wallet}")
            print()
            
            duration = input("Run duration in seconds (or press Enter for continuous): ").strip()
            duration = float(duration) if duration else None
        except EOFError:
            # Non-interactive mode (piped input)
            wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
            duration = 30
    
    print()
    print("Starting miner... (Ctrl+C to stop)")
    print()
    
    simulator = MinerSimulator(wallet)
    simulator.run(duration)

if __name__ == "__main__":
    main()
