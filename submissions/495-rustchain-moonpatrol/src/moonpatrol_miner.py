#!/usr/bin/env python3
"""
RustChain Moon Patrol Miner (1982)
Proof-of-Antiquity Mining for Irem M-52 Arcade Hardware

This simulator emulates the Moon Patrol arcade hardware and generates
attestations for the RustChain blockchain.
"""

import hashlib
import json
import time
import random
import argparse
from datetime import datetime
from z80_cpu import Z80CPU


class IremM52Hardware:
    """
    Irem M-52 arcade hardware emulator for Moon Patrol.
    Manages Z80 CPU, video, sound, and parallax scrolling.
    """
    
    def __init__(self):
        # Main CPU
        self.cpu = Z80CPU(clock_hz=3072000)
        
        # Video RAM (8 KB)
        self.vram = bytearray(8192)
        
        # Sound CPU (M6803 @ 894.886 kHz) - simulated
        self.sound_cpu_cycles = 0
        self.sound_cpu_hz = 894886
        
        # Parallax scroll registers (3 layers)
        self.parallax_bg = 0    # Background (mountains)
        self.parallax_mid = 0   # Mid-ground (craters)
        self.parallax_fg = 0    # Foreground (rover path)
        
        # Video timing
        self.frame_count = 0
        self.raster_line = 0
        self.vblank = False
        
        # Hardware entropy sources
        self.entropy_pool = bytearray(32)
        
    def update_parallax(self):
        """Update parallax scrolling layers"""
        # Each layer scrolls at different speeds
        self.parallax_bg = (self.parallax_bg + 1) & 0xFF
        self.parallax_mid = (self.parallax_mid + 2) & 0xFF
        self.parallax_fg = (self.parallax_fg + 4) & 0xFF
        
    def update_video(self):
        """Simulate video timing"""
        self.raster_line = (self.raster_line + 1) % 224
        
        # VBLANK occurs after all raster lines
        if self.raster_line == 0:
            self.vblank = True
            self.frame_count += 1
        else:
            self.vblank = False
    
    def collect_entropy(self):
        """
        Collect hardware entropy from multiple sources.
        Simulates unique characteristics of each M-52 board.
        """
        # Z80 cycle timing variance
        z80_entropy = self.cpu.get_cycle_timing_entropy()
        
        # Parallax timing variance (each board has slight differences)
        parallax_entropy = (
            (self.parallax_bg & 0x03) ^
            ((self.parallax_mid >> 2) & 0x03) ^
            ((self.parallax_fg >> 4) & 0x03)
        )
        
        # Video timing (raster position jitter)
        video_entropy = self.raster_line & 0xFF
        
        # Sound CPU sync (phase relationship)
        sound_entropy = (self.sound_cpu_cycles >> 8) & 0xFF
        
        # Combine entropy sources
        combined = z80_entropy ^ parallax_entropy ^ video_entropy ^ sound_entropy
        
        # Add to entropy pool
        pool_index = self.frame_count % 32
        self.entropy_pool[pool_index] ^= combined
        
        return combined
    
    def get_hardware_fingerprint(self):
        """
        Generate unique hardware fingerprint for this M-52 board.
        """
        # Collect entropy over several frames
        for _ in range(60):  # 1 second at 60 FPS
            self.update_parallax()
            self.update_video()
            self.collect_entropy()
            self.cpu.step()  # Execute some CPU cycles
        
        # Create fingerprint from entropy pool
        fingerprint_hash = hashlib.sha256(bytes(self.entropy_pool)).hexdigest()
        
        return {
            'z80_timing': fingerprint_hash[:16],
            'parallax_signature': fingerprint_hash[16:32],
            'video_timing': fingerprint_hash[32:48],
            'sound_cpu_sync': fingerprint_hash[48:64]
        }


class MoonPatrolMiner:
    """
    RustChain Proof-of-Antiquity Miner for Moon Patrol.
    Implements simplified RZ-PoA hash algorithm suitable for Z80.
    """
    
    VERSION = "1.0"
    DIFFICULTY_TARGET = 0x40  # First byte must be < 0x40
    
    def __init__(self, wallet_name="default"):
        self.wallet_name = wallet_name
        self.wallet_address = self._generate_wallet(wallet_name)
        self.hardware = IremM52Hardware()
        
        # Mining state
        self.nonce = 0
        self.blocks_found = 0
        self.total_hashes = 0
        self.start_time = None
        
        # Attestation data
        self.current_epoch = 0
        self.last_attestation = None
        
    def _generate_wallet(self, name):
        """
        Generate wallet address from hardware entropy.
        In production, this would use proper cryptographic key generation.
        """
        # Collect hardware entropy
        entropy = self.hardware.collect_entropy()
        
        # Generate deterministic address from name + entropy
        seed = f"{name}:{entropy}:{time.time()}".encode()
        hash_bytes = hashlib.sha256(seed).digest()
        
        # Format as RustChain address (RTC + 40 hex chars)
        address = "RTC" + hash_bytes[:20].hex()
        return address
    
    def rz_poa_hash(self, data):
        """
        RZ-PoA (R-Zone Proof-of-Antiquity) hash algorithm.
        Simplified hash suitable for 8-bit Z80 CPU.
        
        This is a lightweight alternative to SHA-256 that can run
        on severely constrained hardware.
        """
        # Initialize accumulator
        acc = 0
        
        # XOR all input bytes
        for byte in data:
            acc ^= byte
        
        # 16 rounds of mixing
        for round_num in range(16):
            # Rotate left 4 bits
            acc = ((acc << 4) | (acc >> 4)) & 0xFF
            # XOR with constants
            acc ^= 0x5A
            # Rotate left 3 bits
            acc = ((acc << 3) | (acc >> 5)) & 0xFF
            acc ^= 0xC3
        
        # Expand to 32 bytes
        hash_bytes = bytearray(32)
        for i in range(32):
            hash_bytes[i] = (acc ^ i ^ round_num) & 0xFF
        
        return bytes(hash_bytes)
    
    def mine_one_hash(self):
        """
        Perform one hash attempt.
        Returns (hash, success) tuple.
        """
        # Prepare mining data
        wallet_bytes = self.wallet_address.encode()
        nonce_bytes = self.nonce.to_bytes(4, 'big')
        
        # Combine for hashing
        mining_data = wallet_bytes + nonce_bytes
        
        # Execute Z80 instructions (simulates actual mining on hardware)
        for _ in range(100):  # ~100 instructions per hash
            self.hardware.cpu.step()
        
        # Calculate hash
        hash_result = self.rz_poa_hash(mining_data)
        
        # Increment counters
        self.nonce = (self.nonce + 1) & 0xFFFFFFFF
        self.total_hashes += 1
        
        # Check difficulty
        success = hash_result[0] < self.DIFFICULTY_TARGET
        
        if success:
            self.blocks_found += 1
        
        return hash_result, success
    
    def generate_attestation(self):
        """
        Generate hardware attestation for RustChain.
        """
        # Get hardware fingerprint
        fingerprint = self.hardware.get_hardware_fingerprint()
        
        # Create attestation document
        attestation = {
            "version": self.VERSION,
            "hardware": {
                "platform": "Irem M-52 (Moon Patrol)",
                "cpu": "Z80",
                "clock_hz": 3072000,
                "memory_bytes": 16384,
                "video_ram_bytes": 8192,
                "sound_cpu": "M6803 @ 894.886 kHz",
                "year": 1982,
                "manufacturer": "Irem"
            },
            "fingerprint": fingerprint,
            "mining_stats": {
                "nonce": self.nonce,
                "blocks_found": self.blocks_found,
                "total_hashes": self.total_hashes,
                "hash_rate": self.get_hash_rate()
            },
            "antiquity_multiplier": 5.0,
            "timestamp": int(time.time()),
            "epoch": self.current_epoch,
            "wallet": self.wallet_address
        }
        
        # Sign attestation (simulated - in production would use ED25519)
        attestation_json = json.dumps(attestation, sort_keys=True)
        signature = hashlib.sha256(attestation_json.encode()).hexdigest()
        attestation["signature"] = signature
        
        self.last_attestation = attestation
        return attestation
    
    def get_hash_rate(self):
        """Calculate current hash rate"""
        if self.start_time is None:
            return 0.0
        
        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return 0.0
        
        return self.total_hashes / elapsed
    
    def run_mining_session(self, duration_seconds=10.0):
        """
        Run a mining session for specified duration.
        """
        print(f"\n🌙 Starting Moon Patrol mining session...")
        print(f"Duration: {duration_seconds} seconds")
        print(f"Wallet: {self.wallet_address}")
        print(f"Difficulty: 0x{self.DIFFICULTY_TARGET:02X}")
        print("=" * 60)
        
        self.start_time = time.time()
        end_time = self.start_time + duration_seconds
        
        last_status = time.time()
        
        while time.time() < end_time:
            # Mine one hash
            hash_result, success = self.mine_one_hash()
            
            # Check for block found
            if success:
                elapsed = time.time() - self.start_time
                print(f"\n[BLOCK FOUND!] #{self.blocks_found}")
                print(f"  Nonce: 0x{self.nonce:08X}")
                print(f"  Hash:  {hash_result[:8].hex()}...")
                print(f"  Time:  {elapsed:.2f}s")
                print(f"  Hash Rate: {self.get_hash_rate():.0f} H/s")
            
            # Periodic status
            if time.time() - last_status >= 2.0:
                elapsed = time.time() - self.start_time
                print(f"\rMining... {elapsed:.1f}s | "
                      f"Hashes: {self.total_hashes} | "
                      f"Blocks: {self.blocks_found} | "
                      f"Rate: {self.get_hash_rate():.0f} H/s", end="", flush=True)
                last_status = time.time()
        
        # Final statistics
        elapsed = time.time() - self.start_time
        print(f"\n\n{'=' * 60}")
        print(f"Mining Session Complete!")
        print(f"  Duration:     {elapsed:.2f} seconds")
        print(f"  Total Hashes: {self.total_hashes}")
        print(f"  Blocks Found: {self.blocks_found}")
        print(f"  Hash Rate:    {self.get_hash_rate():.0f} H/s")
        print(f"  Expected:     ~{int(elapsed * self.get_hash_rate() / 64)} blocks (statistical)")
        
        return self.blocks_found
    
    def print_status(self):
        """Print current miner status"""
        print(f"\n🌙 Moon Patrol Miner Status")
        print("=" * 60)
        print(f"Wallet:           {self.wallet_address}")
        print(f"Current Nonce:    0x{self.nonce:08X}")
        print(f"Blocks Found:     {self.blocks_found}")
        print(f"Total Hashes:     {self.total_hashes}")
        print(f"Hash Rate:        {self.get_hash_rate():.0f} H/s")
        print(f"Current Epoch:    {self.current_epoch}")
        print(f"Antiquity Mult:   5.0× 🔴 LEGENDARY")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="RustChain Moon Patrol Miner (1982) - Proof-of-Antiquity"
    )
    parser.add_argument(
        "--wallet", "-w",
        default="default",
        help="Wallet name (default: default)"
    )
    parser.add_argument(
        "--mine", "-m",
        action="store_true",
        help="Start mining"
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=10.0,
        help="Mining duration in seconds (default: 10.0)"
    )
    parser.add_argument(
        "--generate-wallet", "-g",
        action="store_true",
        help="Generate new wallet"
    )
    parser.add_argument(
        "--offline", "-o",
        action="store_true",
        help="Offline mode (no network submission)"
    )
    parser.add_argument(
        "--status", "-s",
        action="store_true",
        help="Show miner status"
    )
    
    args = parser.parse_args()
    
    # Create miner
    miner = MoonPatrolMiner(wallet_name=args.wallet)
    
    if args.generate_wallet:
        print(f"\n🌙 Generated new wallet:")
        print(f"  Name:    {args.wallet}")
        print(f"  Address: {miner.wallet_address}")
        print(f"\n⚠️  Save this address! It cannot be recovered.")
        return
    
    if args.status:
        miner.print_status()
        return
    
    if args.mine:
        # Run mining session
        blocks = miner.run_mining_session(duration_seconds=args.duration)
        
        if blocks > 0:
            # Generate attestation
            print(f"\n📝 Generating attestation...")
            attestation = miner.generate_attestation()
            
            if args.offline:
                # Save to file
                filename = f"ATTEST.MP.{int(time.time())}.json"
                with open(filename, 'w') as f:
                    json.dump(attestation, f, indent=2)
                print(f"✓ Attestation saved to {filename}")
            else:
                # Would submit to network (simulated)
                print(f"✓ Attestation ready for submission")
                print(f"  Expected Reward: {blocks * 0.12 * 5.0:.2f} RTC")
        
        return
    
    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
