#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xevious Miner - Main Entry Point
Run the Z80 CPU simulator and mine blocks on Xevious arcade hardware (simulated)

RustChain Bounty Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import sys
import os

# Add simulator directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from z80_cpu import XeviousMiner


def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("Xevious Miner - RustChain on Arcade Hardware")
    print("=" * 60)
    print("\nProject: Port RustChain miner to Xevious arcade (1982)")
    print("Hardware: Namco Galaga system, Z80 @ 3.072 MHz, 16 KB RAM")
    print("Status: Proof of Concept / Educational Demo")
    print("=" * 60)
    print()
    
    # Create miner instance
    miner = XeviousMiner()
    
    # Run mining session (default 10 seconds)
    duration = 10.0
    if len(sys.argv) > 1:
        try:
            duration = float(sys.argv[1])
        except ValueError:
            print(f"Usage: python main.py [duration_seconds]")
            print(f"Example: python main.py 10")
            sys.exit(1)
    
    print(f"Starting mining session ({duration} seconds)...\n")
    miner.run_mining_session(duration_seconds=duration)
    
    print("\nDemo complete!")
    print("For more information, see README.md and ARCHITECTURE.md")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
