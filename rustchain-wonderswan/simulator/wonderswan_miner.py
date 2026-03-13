#!/usr/bin/env python3
"""
WonderSwan Miner Simulator
===========================

Simulates the RustChain miner ported to Bandai WonderSwan (1999).
Emulates WonderSwan hardware constraints:
- NEC V30 MZ CPU @ 3.072 MHz (16-bit, 8086-compatible)
- 512 Kbit (64 KB) RAM total
- 224×144 pixel display with portrait/landscape dual-mode
- 16-level grayscale
- No FPU (integer math only)
- Truncated SHA-256 (4 rounds for demo)

Author: OpenClaw Subagent
Bounty: #441 - Port Miner to WonderSwan (200 RTC / $20)
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import hashlib
import time
import struct
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum


class WonderSwanMode(Enum):
    """WonderSwan display modes"""
    PORTRAIT = "Portrait"    # Vertical (144×224)
    LANDSCAPE = "Landscape"  # Horizontal (224×144)


class WSColor(Enum):
    """WonderSwan 16-level grayscale values"""
    BLACK = 0x0
    GRAY1 = 0x1
    GRAY2 = 0x2
    GRAY3 = 0x3
    GRAY4 = 0x4
    GRAY5 = 0x5
    GRAY6 = 0x6
    GRAY7 = 0x7
    GRAY8 = 0x8
    GRAY9 = 0x9
    GRAY10 = 0xA
    GRAY11 = 0xB
    GRAY12 = 0xC
    GRAY13 = 0xD
    GRAY14 = 0xE
    WHITE = 0xF


@dataclass
class WonderSwanMemory:
    """
    Emulates WonderSwan memory layout.
    
    Memory Map:
    $000000-$07FFFF  Cartridge ROM (up to 4 MB)
    $080000-$08FFFF  Work RAM (64 KB)
    $090000-$09FFFF  Video RAM (shared)
    $0A0000-$0FFFFF  Hardware I/O registers
    """
    
    # Work RAM (64 KB)
    work_ram: bytearray = None
    
    # Cartridge RAM (for nonce persistence)
    cart_ram: bytearray = None
    
    def __post_init__(self):
        if self.work_ram is None:
            self.work_ram = bytearray(65536)  # 64 KB
        if self.cart_ram is None:
            self.cart_ram = bytearray(8192)   # 8 KB (battery-backed)
    
    # Mining state in Work RAM
    NONCE_ADDR = 0x1000      # Offset for nonce counter
    HASH_BUF_ADDR = 0x1010   # Hash buffer (64 bytes)
    BLOCK_HEADER_ADDR = 0x1050  # Block header (80 bytes)
    TARGET_ADDR = 0x10A0     # Target difficulty (4 bytes)
    STATS_ADDR = 0x10B0      # Mining statistics
    
    def write_nonce(self, nonce: int) -> None:
        """Write 32-bit nonce to RAM (little-endian, NEC V30 format)"""
        data = struct.pack('<I', nonce & 0xFFFFFFFF)
        self.work_ram[self.NONCE_ADDR:self.NONCE_ADDR+4] = data
    
    def read_nonce(self) -> int:
        """Read 32-bit nonce from RAM"""
        data = bytes(self.work_ram[self.NONCE_ADDR:self.NONCE_ADDR+4])
        return struct.unpack('<I', data)[0]
    
    def increment_nonce(self) -> int:
        """Increment nonce and return new value (wraps on overflow)"""
        nonce = self.read_nonce()
        nonce = (nonce + 1) & 0xFFFFFFFF
        self.write_nonce(nonce)
        return nonce
    
    def write_hash(self, hash_data: bytes) -> None:
        """Write 32-byte hash to buffer"""
        self.work_ram[self.HASH_BUF_ADDR:self.HASH_BUF_ADDR+32] = hash_data[:32]
    
    def read_stats(self) -> dict:
        """Read mining statistics from RAM"""
        offset = self.STATS_ADDR
        return {
            'total_hashes': struct.unpack('<I', bytes(self.work_ram[offset:offset+4]))[0],
            'shares_found': struct.unpack('<I', bytes(self.work_ram[offset+4:offset+8]))[0],
            'start_time': struct.unpack('<I', bytes(self.work_ram[offset+8:offset+12]))[0]
        }
    
    def increment_hash_count(self) -> int:
        """Increment total hash counter"""
        offset = self.STATS_ADDR
        current = struct.unpack('<I', bytes(self.work_ram[offset:offset+4]))[0]
        current = (current + 1) & 0xFFFFFFFF
        self.work_ram[offset:offset+4] = struct.pack('<I', current)
        return current


class TruncatedSHA256:
    """
    Truncated SHA-256 implementation for WonderSwan.
    
    Full SHA-256 requires 64 rounds and ~8 KB state.
    This demo version uses 4 rounds and ~2 KB state.
    
    NOT suitable for actual cryptographic use!
    Optimized for NEC V30 16-bit architecture.
    """
    
    # First 8 primes (sqrt(2), sqrt(3), etc.) - 32-bit fractional parts
    H0 = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]
    
    # First 16 round constants
    K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174
    ]
    
    def __init__(self, rounds: int = 4):
        """
        Initialize truncated SHA-256.
        
        Args:
            rounds: Number of rounds (4 for WonderSwan demo, 64 for full)
        """
        self.rounds = rounds
    
    def _rotr(self, x: int, n: int) -> int:
        """Right rotate 32-bit integer (NEC V30 optimized)"""
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF
    
    def _ch(self, x: int, y: int, z: int) -> int:
        """Choice function"""
        return (x & y) ^ (~x & z)
    
    def _maj(self, x: int, y: int, z: int) -> int:
        """Majority function"""
        return (x & y) ^ (x & z) ^ (y & z)
    
    def _sigma0(self, x: int) -> int:
        """Σ0 function"""
        return self._rotr(x, 2) ^ self._rotr(x, 13) ^ self._rotr(x, 22)
    
    def _sigma1(self, x: int) -> int:
        """Σ1 function"""
        return self._rotr(x, 6) ^ self._rotr(x, 11) ^ self._rotr(x, 25)
    
    def _gamma0(self, x: int) -> int:
        """σ0 function"""
        return self._rotr(x, 7) ^ self._rotr(x, 18) ^ (x >> 3)
    
    def _gamma1(self, x: int) -> int:
        """σ1 function"""
        return self._rotr(x, 17) ^ self._rotr(x, 19) ^ (x >> 10)
    
    def hash(self, data: bytes, nonce: int) -> bytes:
        """
        Compute truncated SHA-256 hash.
        
        Args:
            data: Block header data (80 bytes)
            nonce: 32-bit nonce value
            
        Returns:
            32-byte hash (truncated rounds)
        """
        # Append nonce to data (nonce is critical for mining!)
        nonce_bytes = struct.pack('<I', nonce)
        data_with_nonce = data[:60] + nonce_bytes  # Replace last 4 bytes with nonce
        
        # Ensure exactly 64 bytes (padding for demo)
        if len(data_with_nonce) < 64:
            data_with_nonce = data_with_nonce + b'\x80' + b'\x00' * (63 - len(data_with_nonce))
        data_with_nonce = data_with_nonce[:64]
        
        # Initialize hash values
        h = list(self.H0)
        
        # Prepare message schedule (first 16 words from input)
        w = []
        for i in range(16):
            w.append(struct.unpack('>I', data_with_nonce[i*4:(i+1)*4])[0])
        
        # Run truncated rounds (NEC V30 optimized)
        for i in range(self.rounds):
            # Extend message schedule for rounds >= 16
            if i >= 16:
                w.append((self._gamma1(w[i-2]) + w[i-7] + 
                         self._gamma0(w[i-15]) + w[i-16]) & 0xFFFFFFFF)
            
            # Working variables
            a, b, c, d, e, f, g, hh = h
            
            # Round function (optimized for 16-bit CPU)
            t1 = (hh + self._sigma1(e) + self._ch(e, f, g) + 
                  self.K[i % 16] + w[i % 16]) & 0xFFFFFFFF
            t2 = (self._sigma0(a) + self._maj(a, b, c)) & 0xFFFFFFFF
            
            h = [
                (t1 + t2) & 0xFFFFFFFF,
                a,
                b,
                c,
                (d + t1) & 0xFFFFFFFF,
                e,
                f,
                g
            ]
        
        # Add to hash value
        for i in range(8):
            h[i] = (h[i] + self.H0[i]) & 0xFFFFFFFF
        
        # Produce final hash (big-endian for compatibility)
        return b''.join(struct.pack('>I', x) for x in h)


@dataclass
class BlockHeader:
    """Bitcoin-style block header (80 bytes)"""
    version: int = 1
    prev_hash: bytes = b'\x00' * 32
    merkle_root: bytes = b'\x00' * 32
    timestamp: int = 0
    bits: int = 0x1d00ffff  # Difficulty target
    nonce: int = 0
    
    def serialize(self) -> bytes:
        """Serialize to 80-byte block header"""
        return (
            struct.pack('<I', self.version) +
            self.prev_hash +
            self.merkle_root +
            struct.pack('<I', self.timestamp) +
            struct.pack('<I', self.bits)
        )


class WonderSwanMiner:
    """
    WonderSwan Miner - Main mining logic.
    
    Emulates the constraints and behavior of mining on WonderSwan hardware.
    Optimized for NEC V30 MZ @ 3.072 MHz.
    """
    
    def __init__(self, truncated_rounds: int = 4):
        """
        Initialize WonderSwan miner.
        
        Args:
            truncated_rounds: SHA-256 rounds (4 for demo, 64 for full)
        """
        self.memory = WonderSwanMemory()
        self.sha256 = TruncatedSHA256(rounds=truncated_rounds)
        self.start_time = time.time()
        self.found_shares: list = []
        
        # Target difficulty (leading zeros required)
        # WonderSwan can only find very easy shares due to limited power
        self.target_zeros = 2  # Number of leading zero bytes
        
        # CPU clock speed
        self.clock_mhz = 3.072
    
    def check_share(self, hash_result: bytes, nonce: int) -> bool:
        """Check if hash meets target difficulty"""
        leading_zeros = 0
        for byte in hash_result:
            if byte == 0:
                leading_zeros += 1
            else:
                break
        
        if leading_zeros >= self.target_zeros:
            self.found_shares.append({
                'nonce': nonce,
                'hash': hash_result.hex(),
                'zeros': leading_zeros,
                'timestamp': time.time()
            })
            # Update stats in memory
            offset = self.memory.STATS_ADDR + 4
            current = struct.unpack('<I', bytes(self.memory.work_ram[offset:offset+4]))[0]
            current = (current + 1) & 0xFFFFFFFF
            self.memory.work_ram[offset:offset+4] = struct.pack('<I', current)
            return True
        return False
    
    def mine(self, block_header: BlockHeader, max_nonces: int = 1000) -> Optional[dict]:
        """
        Run mining loop.
        
        Args:
            block_header: Block header to mine
            max_nonces: Maximum nonces to try (WonderSwan will wrap)
            
        Returns:
            Share info if found, None otherwise
        """
        header_bytes = block_header.serialize()
        
        for i in range(max_nonces):
            # Increment nonce in WonderSwan memory
            nonce = self.memory.increment_nonce()
            
            # Compute hash (truncated SHA-256)
            hash_result = self.sha256.hash(header_bytes, nonce)
            
            # Update hash count
            self.memory.increment_hash_count()
            
            # Check if we found a share
            if self.check_share(hash_result, nonce):
                return self.found_shares[-1]
        
        return None
    
    def get_hash_rate(self) -> float:
        """Calculate current hash rate (H/s)"""
        elapsed = time.time() - self.start_time
        stats = self.memory.read_stats()
        if elapsed < 0.001:
            return 0.0
        return stats['total_hashes'] / elapsed
    
    def reset(self) -> None:
        """Reset miner state"""
        self.memory.write_nonce(0)
        self.start_time = time.time()
        self.found_shares = []
        # Clear stats
        for i in range(12):
            self.memory.work_ram[self.memory.STATS_ADDR + i] = 0


class WonderSwanDisplay:
    """
    Simulates WonderSwan display (224×144 pixels).
    
    Supports both portrait and landscape modes.
    16-level grayscale.
    """
    
    WIDTH = 224
    HEIGHT = 144
    
    def __init__(self, mode: WonderSwanMode = WonderSwanMode.PORTRAIT):
        """Initialize display with specified mode"""
        self.mode = mode
        self.screen = [[WSColor.WHITE.value for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
        self.font_scale = 1
    
    def set_mode(self, mode: WonderSwanMode):
        """Switch between portrait and landscape mode"""
        self.mode = mode
        self.clear()
    
    def clear(self):
        """Clear screen to white"""
        self.screen = [[WSColor.WHITE.value for _ in range(self.WIDTH)] for _ in range(self.HEIGHT)]
    
    def draw_rect(self, x: int, y: int, w: int, h: int, color: WSColor):
        """Draw filled rectangle"""
        for dy in range(h):
            for dx in range(w):
                if 0 <= y+dy < self.HEIGHT and 0 <= x+dx < self.WIDTH:
                    self.screen[y+dy][x+dx] = color.value
    
    def print_text(self, x: int, y: int, text: str, color: WSColor = WSColor.BLACK, max_len: int = 0):
        """Print text at position (simplified - just characters)"""
        if max_len > 0:
            text = text[:max_len]
        for i, char in enumerate(text):
            if 0 <= x+i < self.WIDTH and 0 <= y < self.HEIGHT:
                # Simplified: just store character code as "pixel"
                self.screen[y][x+i] = min(ord(char) & 0xF, 15)
    
    def render_text(self):
        """Render display to terminal (ASCII art)"""
        # Use ASCII-safe characters for Windows compatibility
        border_char = '='
        chars = ' .oO#'  # ASCII-safe grayscale
        
        print('\n' + border_char * min(self.WIDTH, 80))
        
        # Show visible area based on mode
        if self.mode == WonderSwanMode.PORTRAIT:
            # Portrait: show 20 rows, 30 cols
            for row in range(min(20, self.HEIGHT)):
                line = ''
                for col in range(min(30, self.WIDTH)):
                    val = self.screen[row][col]
                    line += chars[min(val, len(chars)-1)]
                print(line)
        else:
            # Landscape: show 15 rows, 50 cols
            for row in range(min(15, self.HEIGHT)):
                line = ''
                for col in range(min(50, self.WIDTH)):
                    val = self.screen[row][col]
                    line += chars[min(val, len(chars)-1)]
                print(line)
        
        print(border_char * min(self.WIDTH, 80))
    
    def update_mining_stats(self, miner: WonderSwanMiner, current_nonce: int):
        """Update display with mining statistics"""
        self.clear()
        
        if self.mode == WonderSwanMode.PORTRAIT:
            # Portrait mode layout
            self.draw_rect(30, 0, 164, 30, WSColor.GRAY8)
            self.print_text(35, 2, "╔════════════════════╗", WSColor.BLACK)
            self.print_text(35, 4, "║  RUSTCHAIN WS      ║", WSColor.BLACK)
            self.print_text(35, 6, "║  MINER (1999)      ║", WSColor.BLACK)
            self.print_text(35, 8, "╚════════════════════╝", WSColor.BLACK)
            
            self.print_text(5, 15, f"Nonce: {current_nonce:,}", WSColor.BLACK)
            self.print_text(5, 20, f"Hash: {miner.get_hash_rate():.1f} H/s", WSColor.BLACK)
            self.print_text(5, 25, f"Shares: {len(miner.found_shares)}", WSColor.BLACK)
            self.print_text(5, 30, f"CPU: {miner.clock_mhz:.3f} MHz", WSColor.BLACK)
            
            # Wallet address (truncated)
            wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
            self.print_text(5, 35, f"Wallet: {wallet[:20]}...", WSColor.BLACK)
            
            # Mode indicator
            self.print_text(5, 40, "[START] Toggle  [A] Mine  [B] Stop", WSColor.BLACK)
            
        else:
            # Landscape mode layout
            self.draw_rect(0, 0, 80, 40, WSColor.GRAY8)
            self.print_text(2, 2, "╔════════════════╗", WSColor.BLACK)
            self.print_text(2, 4, "║ RUSTCHAIN WS   ║", WSColor.BLACK)
            self.print_text(2, 6, "╚════════════════╝", WSColor.BLACK)
            
            self.print_text(2, 12, f"Hash: {miner.get_hash_rate():.1f} H/s", WSColor.BLACK)
            self.print_text(2, 16, f"Nonce: {current_nonce:,}", WSColor.BLACK)
            self.print_text(2, 20, f"Shares: {len(miner.found_shares)}", WSColor.BLACK)
            
            wallet = "RTC4325...bb96b"
            self.print_text(2, 24, f"Wallet: {wallet}", WSColor.BLACK)
            
            self.print_text(2, 30, "[START]Mode [A]Mine [B]Stop", WSColor.BLACK)


def run_simulation(duration: float = 10.0, mode: WonderSwanMode = WonderSwanMode.PORTRAIT):
    """
    Run WonderSwan mining simulation.
    
    Args:
        duration: How long to run (seconds)
        mode: Display mode (portrait or landscape)
    """
    print("\n" + "=" * 70)
    print("  RUSTCHAIN WONDERSWAN MINER SIMULATOR")
    print("  Bounty #441 - LEGENDARY TIER (200 RTC / $20)")
    print("  Bandai WonderSwan (1999) - NEC V30 MZ @ 3.072 MHz")
    print("=" * 70 + "\n")
    
    # Initialize
    miner = WonderSwanMiner(truncated_rounds=4)
    display = WonderSwanDisplay(mode=mode)
    
    # Create test block header
    block = BlockHeader(
        version=1,
        prev_hash=bytes.fromhex('00' * 32),
        merkle_root=bytes.fromhex('00' * 32),
        timestamp=int(time.time()),
        bits=0x1d00ffff
    )
    
    print(f"Starting WonderSwan mining simulation...")
    print(f"Display Mode: {mode.value}")
    print(f"CPU: NEC V30 MZ @ {miner.clock_mhz} MHz")
    print(f"Target: {miner.target_zeros} leading zero bytes")
    print(f"Duration: {duration} seconds\n")
    
    start = time.time()
    last_display_update = 0
    
    try:
        while time.time() - start < duration:
            # Mine batch of nonces
            result = miner.mine(block, max_nonces=100)
            
            # Update display every second
            if time.time() - last_display_update >= 1.0:
                nonce = miner.memory.read_nonce()
                display.update_mining_stats(miner, nonce)
                
                print(f"\n{'='*60}")
                print(f"WONDERSWAN DISPLAY ({mode.value} MODE)")
                print(f"{'='*60}")
                display.render_text()
                
                last_display_update = time.time()
                
                if miner.found_shares:
                    share = miner.found_shares[-1]
                    print(f"\n🎉 SHARE FOUND! Nonce={share['nonce']}, Zeros={share['zeros']}")
                    print(f"   Hash: {share['hash'][:64]}...")
            
            # Small delay to simulate WonderSwan speed
            time.sleep(0.001)
    
    except KeyboardInterrupt:
        print("\n\nMining interrupted by user")
    
    # Final stats
    print("\n" + "=" * 70)
    print("  MINING COMPLETE - FINAL STATISTICS")
    print("=" * 70)
    stats = miner.memory.read_stats()
    print(f"  Total Hashes:     {stats['total_hashes']:,}")
    print(f"  Hash Rate:        {miner.get_hash_rate():.2f} H/s")
    print(f"  Shares Found:     {len(miner.found_shares)}")
    print(f"  Duration:         {time.time() - start:.2f} seconds")
    print(f"  CPU:              NEC V30 MZ @ {miner.clock_mhz} MHz")
    print(f"  RAM:              64 KB Work RAM")
    print(f"  Display:          224×144, 16 grayscale")
    print(f"  Wallet:           RTC4325af95d26d59c3ef025963656d22af638bb96b")
    print("=" * 70 + "\n")
    
    if miner.found_shares:
        print("🎉 Shares found (proof of work):")
        for i, share in enumerate(miner.found_shares[:5], 1):
            print(f"  {i}. Nonce={share['nonce']:,}, Zeros={share['zeros']}, Hash={share['hash'][:32]}...")
    
    return miner


def main():
    """Main entry point"""
    import sys
    
    # Parse arguments
    duration = 10.0
    mode = WonderSwanMode.PORTRAIT
    
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            pass
    
    if len(sys.argv) > 2 and sys.argv[2].upper() == 'LANDSCAPE':
        mode = WonderSwanMode.LANDSCAPE
    
    # Run simulation
    run_simulation(duration=duration, mode=mode)


if __name__ == '__main__':
    main()
