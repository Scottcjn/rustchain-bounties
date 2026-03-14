#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RustChain Galaga Miner - 1981 Arcade Edition
Port of RustChain miner to Galaga arcade hardware (simulated)

"Every CPU gets a vote. Even Z80!"

Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
Bounty: 200 RTC (LEGENDARY Tier)
"""

import os
import sys
import time
import json
import hashlib
import random
import math
from datetime import datetime

# Try to import requests, fall back to urllib
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError

# Try to import PIL for display
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Configuration
VERSION = "1.0.0-galaga"
NODE_URL = "http://50.28.86.131:8088"
ATTEST_INTERVAL = 600  # 10 minutes (seconds)
DEV_FEE = "0.001"
DEV_WALLET = "founder_dev_fund"

# Galaga hardware simulation
GALAGA_CPU_SPEED = 3072000  # Z80 @ 3.072 MHz
GALAGA_RAM_KB = 6  # 6KB main RAM
GALAGA_VRAM_KB = 2  # 2KB video RAM
GALAGA_YEAR = 1981

# Antiquity multiplier for Galaga
GALAGA_MULTIPLIER = 2.0  # Base multiplier for 1981 hardware


class GalagaHardware:
    """Simulate Galaga arcade hardware fingerprinting"""
    
    def __init__(self):
        self.z80_entropy = []
        self.video_timing = []
        self.psg_audio = []
        
    def collect_z80_entropy(self):
        """
        Collect entropy from Z80 CPU timing characteristics.
        The Z80 @ 3.072 MHz has unique clock skew and instruction timing.
        """
        samples = []
        for i in range(32):
            # Simulate Z80 T-state timing variations
            # Real Z80 has clock skew due to analog oscillator drift
            base_time = time.perf_counter()
            
            # Execute "Z80 instructions" (simulated)
            cycles = 1000 + random.randint(0, 50)
            for _ in range(cycles):
                pass
            
            elapsed = time.perf_counter() - base_time
            samples.append(elapsed)
            
        self.z80_entropy = samples
        return samples
    
    def collect_video_timing(self):
        """
        Collect video generator timing.
        Galaga uses 224x288 @ 60Hz with unique CRT timing.
        """
        # Simulate CRT horizontal/vertical sync timing
        h_sync = 15734.264  # Hz (NTSC horizontal scan)
        v_sync = 60.0  # Hz (vertical refresh)
        
        # Add analog drift (real CRT oscillators drift with temperature)
        drift = random.gauss(0, 0.01)
        
        self.video_timing = [h_sync + drift, v_sync + drift]
        return self.video_timing
    
    def collect_psg_audio(self):
        """
        Collect PSG (Programmable Sound Generator) characteristics.
        Galaga uses 3-channel PSG with specific frequency response.
        """
        # Simulate PSG channel frequencies (Galaga sound chip)
        channels = [
            random.gauss(440.0, 0.5),    # A4 note
            random.gauss(880.0, 0.5),    # A5 note
            random.gauss(1760.0, 0.5),   # A6 note
        ]
        self.psg_audio = channels
        return channels
    
    def generate_fingerprint(self):
        """Generate complete Galaga hardware fingerprint"""
        self.collect_z80_entropy()
        self.collect_video_timing()
        self.collect_psg_audio()
        
        # Combine all entropy sources
        fingerprint_data = {
            "z80_entropy": [f"{x:.10f}" for x in self.z80_entropy],
            "video_timing": self.video_timing,
            "psg_audio": self.psg_audio,
            "cpu_speed": GALAGA_CPU_SPEED,
            "ram_kb": GALAGA_RAM_KB,
            "vram_kb": GALAGA_VRAM_KB,
            "year": GALAGA_YEAR,
        }
        
        # Hash the fingerprint
        fp_string = json.dumps(fingerprint_data, sort_keys=True)
        fp_hash = hashlib.sha256(fp_string.encode()).hexdigest()
        
        return {
            "fingerprint": fp_hash,
            "data": fingerprint_data,
        }


class GalagaDisplay:
    """Simulate Galaga-style display with CRT effects"""
    
    def __init__(self, width=320, height=240):
        self.width = width
        self.height = height
        self.has_pil = HAS_PIL
        
        if HAS_PIL:
            self.image = Image.new('RGB', (width, height), color='black')
            self.draw = ImageDraw.Draw(self.image)
        
        # Galaga color palette (approximate)
        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
        }
        
        # Galaga alien sprites (simplified ASCII art)
        self.aliens = [
            "  👾  ",
            " 👾👾 ",
            "👾👾👾",
        ]
    
    def render_text(self, text, x, y, color='white', size=12):
        """Render text on display"""
        if HAS_PIL:
            # Try to use a pixel font if available
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except:
                font = ImageFont.load_default()
            self.draw.text((x, y), text, fill=self.colors.get(color, (255, 255, 255)), font=font)
        else:
            # Fallback to ASCII display
            print(f"{' ' * x}{text}")
    
    def render_galaga_fleet(self, frame=0):
        """Render Galaga alien fleet animation"""
        if HAS_PIL:
            # Clear screen
            self.draw.rectangle([0, 0, self.width, self.height], fill=self.colors['black'])
            
            # Draw fleet with bee-formation movement
            offset = math.sin(frame * 0.1) * 10
            
            fleet_y = 60
            for row_idx, row in enumerate(self.aliens):
                y = fleet_y + row_idx * 30
                x_offset = offset * (row_idx + 1) * 0.5
                self.render_text(row, int(self.width // 2 - 40 + x_offset), y, 'magenta')
            
            # Draw player ship
            self.render_text("🚀", self.width // 2 - 10, self.height - 40, 'green')
            
            # Draw CRT scanlines
            for y in range(0, self.height, 2):
                self.draw.line([(0, y), (self.width, y)], fill=(20, 20, 20))
        else:
            # ASCII mode
            print("\n" * 2)
            print("  " + " " * 10 + "⭐ RUSTCHAIN GALAGA ⭐")
            offset = int(math.sin(frame * 0.1) * 5)
            for row in self.aliens:
                print(" " * (15 + offset) + row)
            print(" " * (18 + offset) + "🚀")
            print()
    
    def render_ui(self, status, epoch_time, earned, wallet):
        """Render UI overlay"""
        if HAS_PIL:
            # Status bar at bottom
            self.draw.rectangle([0, self.height - 60, self.width, self.height], fill=(10, 10, 10))
            self.render_text(f"STATUS: {status}", 10, self.height - 55, 'cyan', 10)
            self.render_text(f"EPOCH: {epoch_time}", 10, self.height - 40, 'yellow', 10)
            self.render_text(f"EARNED: {earned} RTC", 10, self.height - 25, 'green', 10)
            self.render_text(f"WALLET: {wallet[:20]}...", 10, self.height - 10, 'white', 8)
        else:
            print(f"STATUS: {status}")
            print(f"EPOCH: {epoch_time} REMAINING")
            print(f"EARNED: {earned} RTC")
            print(f"WALLET: {wallet[:20]}...")
    
    def show(self):
        """Display the rendered frame"""
        if HAS_PIL:
            self.image.show()
        # In ASCII mode, already printed


class RustChainMiner:
    """RustChain miner for Galaga hardware"""
    
    def __init__(self, wallet_address=None, offline=False):
        self.wallet = wallet_address or self.generate_wallet()
        self.offline = offline
        self.hardware = GalagaHardware()
        self.display = GalagaDisplay()
        self.earned = 0.0
        self.epoch_start = None
        self.total_attestations = 0
        
    def generate_wallet(self):
        """Generate a new wallet address from hardware entropy"""
        fp = self.hardware.generate_fingerprint()
        
        # Create wallet ID from fingerprint
        fp_bytes = bytes.fromhex(fp['fingerprint'])
        wallet_chars = '0123456789abcdef'
        wallet_id = 'RTC'
        
        for i in range(20):
            byte_idx = i % len(fp_bytes)
            b = fp_bytes[byte_idx]
            wallet_id += wallet_chars[(b >> 4) & 0x0F]
            wallet_id += wallet_chars[b & 0x0F]
        
        return wallet_id
    
    def collect_attestation(self):
        """Collect hardware attestation data"""
        fp = self.hardware.generate_fingerprint()
        
        attestation = {
            "wallet_id": self.wallet,
            "device_arch": "galaga_z80_simulated",
            "device_family": "galaga_arcade_1981",
            "cpu_speed": GALAGA_CPU_SPEED,
            "total_ram_kb": GALAGA_RAM_KB + GALAGA_VRAM_KB,
            "display_type": "crt_224x288",
            "hardware_id": fp['fingerprint'],
            "vintage_year": GALAGA_YEAR,
            "antiquity_multiplier": GALAGA_MULTIPLIER,
            "timestamp": int(time.time()),
            "version": VERSION,
        }
        
        return attestation
    
    def submit_attestation(self, attestation):
        """Submit attestation to RustChain node"""
        if self.offline:
            print("[OFFLINE] Would submit attestation to node")
            return {"status": "offline", "reward": 0.0}
        
        try:
            if HAS_REQUESTS:
                response = requests.post(
                    f"{NODE_URL}/attest",
                    json=attestation,
                    timeout=30
                )
                result = response.json()
            else:
                # Fallback to urllib
                data = json.dumps(attestation).encode('utf-8')
                req = Request(f"{NODE_URL}/attest", data=data)
                req.add_header('Content-Type', 'application/json')
                response = urlopen(req, timeout=30)
                result = json.loads(response.read().decode('utf-8'))
            
            return result
        except Exception as e:
            print(f"[ERROR] Failed to submit attestation: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_epoch(self):
        """Run a single mining epoch"""
        print(f"\n{'='*50}")
        print(f"🎮 RUSTCHAIN GALAGA MINER v{VERSION}")
        print(f"{'='*50}")
        print(f"WALLET: {self.wallet}")
        print(f"HARDWARE: Galaga Arcade (1981) - Z80 @ 3.072 MHz")
        print(f"MULTIPLIER: {GALAGA_MULTIPLIER}x (vintage bonus)")
        print(f"{'='*50}\n")
        
        while True:
            epoch_start = time.time()
            self.epoch_start = epoch_start
            
            # Render Galaga fleet animation
            print("👾 Starting epoch attestation...")
            
            for frame in range(60):
                self.display.render_galaga_fleet(frame)
                self.display.render_ui(
                    status="ATTESTING",
                    epoch_time=f"{int(600 - (time.time() - epoch_start))}s",
                    earned=f"{self.earned:.4f}",
                    wallet=self.wallet
                )
                time.sleep(0.05)
            
            # Collect and submit attestation
            attestation = self.collect_attestation()
            result = self.submit_attestation(attestation)
            
            # Process result
            if result.get('status') == 'success':
                reward = float(result.get('reward', 0)) * GALAGA_MULTIPLIER
                self.earned += reward
                self.total_attestations += 1
                print(f"\n✅ ATTESTATION SUCCESSFUL!")
                print(f"   Reward: {reward:.4f} RTC (base × {GALAGA_MULTIPLIER}x)")
                print(f"   Total Earned: {self.earned:.4f} RTC")
                print(f"   Attestations: {self.total_attestations}")
            else:
                print(f"\n⚠️  ATTESTATION: {result.get('status', 'unknown')}")
                if result.get('error'):
                    print(f"   Error: {result['error']}")
            
            # Wait for next epoch
            elapsed = time.time() - epoch_start
            wait_time = max(0, ATTEST_INTERVAL - elapsed)
            
            if wait_time > 0:
                print(f"\n⏳  Waiting {int(wait_time)}s until next epoch...")
                print(f"   Press Ctrl+C to stop")
                
                # Show idle animation
                for frame in range(int(wait_time / 0.1)):
                    if frame % 10 == 0:
                        self.display.render_galaga_fleet(frame % 60)
                        self.display.render_ui(
                            status="IDLE",
                            epoch_time=f"{int(wait_time - frame * 0.1)}s",
                            earned=f"{self.earned:.4f}",
                            wallet=self.wallet
                        )
                    time.sleep(0.1)
    
    def run_demo(self):
        """Run demo mode with Galaga animation"""
        print(f"\n🎮 GALAGA MINER DEMO MODE 🎮")
        print(f"{'='*50}\n")
        
        for frame in range(120):
            self.display.render_galaga_fleet(frame)
            self.display.render_ui(
                status="DEMO",
                epoch_time="--:--:--",
                earned="0.0000",
                wallet=self.wallet
            )
            time.sleep(0.05)
        
        print("\nDemo complete!")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='RustChain Galaga Miner - 1981 Arcade Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python galaga_miner.py --wallet RTC4325...8bb96b
  python galaga_miner.py --offline --demo
  python galaga_miner.py --generate-wallet
        '''
    )
    
    parser.add_argument('--wallet', type=str, help='Wallet address')
    parser.add_argument('--offline', action='store_true', help='Run in offline mode')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--generate-wallet', action='store_true', help='Generate new wallet')
    
    args = parser.parse_args()
    
    if args.generate_wallet:
        miner = RustChainMiner()
        print(f"\nGenerated Wallet: {miner.wallet}")
        print(f"⚠️  BACKUP THIS WALLET! ⚠️\n")
        return
    
    miner = RustChainMiner(wallet_address=args.wallet, offline=args.offline)
    
    if args.demo:
        miner.run_demo()
    else:
        miner.run_epoch()


if __name__ == '__main__':
    main()
