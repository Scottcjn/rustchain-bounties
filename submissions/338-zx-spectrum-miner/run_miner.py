#!/usr/bin/env python3
"""
ZX Spectrum Miner - Quick Launcher
Run the miner simulator with one command.

Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from z80_simulator import main

if __name__ == "__main__":
    main()
