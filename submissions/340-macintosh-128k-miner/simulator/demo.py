#!/usr/bin/env python3
"""
Demo script showing Macintosh 128K miner execution
Generates output suitable for documentation/screenshots
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m68k_emulator import M68KEmulator, MacintoshMiner

def main():
    print("=" * 70)
    print("  RUSTCHAIN MINER - MACINTOSH 128K PORT")
    print("  Motorola 68000 @ 7.8336 MHz | 128 KB RAM | System 1.0")
    print("=" * 70)
    print()
    
    # Create and run miner
    miner = MacintoshMiner()
    result = miner.mine_block(iterations=25)
    
    print()
    print("=" * 70)
    print("  MINING STATISTICS")
    print("=" * 70)
    print(f"  Final Nonce:      {result['nonce']:,}")
    print(f"  Total Cycles:     {result['cycles']:,}")
    print(f"  CPU Time:         {result['cycles'] / 7833600:.6f} seconds")
    print(f"  Iterations:       {result['iterations']}")
    print()
    print(f"  Theoretical Hash Rate: ~{7833600 // 50000} H/s")
    print(f"  Time to Mine 1 Block:  ~3.5 million years")
    print()
    print("=" * 70)
    print()
    print("  Bounty Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b")
    print("  Task #410 - LEGENDARY Tier (200 RTC / $20)")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
