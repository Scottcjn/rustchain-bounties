#!/usr/bin/env python3
"""
ZX Spectrum Miner - Demo Mode
Shows a visual demonstration of the mining process.

Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import time
import sys

def print_header():
    """Print ZX Spectrum style header"""
    print("\n")
    print("=" * 60)
    print("  ZX SPECTRUM MINER")
    print("  ZX Spectrum Edition (1982)")
    print("=" * 60)

def print_spectrum_style(text, color_code=7):
    """Print text in ZX Spectrum style"""
    colors = {
        0: "\033[30m",
        1: "\033[34m",
        2: "\033[31m",
        3: "\033[35m",
        4: "\033[32m",
        5: "\033[36m",
        6: "\033[33m",
        7: "\033[37m",
    }
    reset = "\033[0m"
    print(f"{colors.get(color_code, '')}{text}{reset}")

def animate_mining():
    """Show mining animation"""
    animations = [
        "[*] Mining...",
        "[**] Mining...",
        "[***] Mining...",
        "[****] Mining...",
    ]
    
    for anim in animations:
        sys.stdout.write("\r" + anim + " " * 40)
        sys.stdout.flush()
        time.sleep(0.2)

def demo_mining():
    """Run mining demonstration"""
    print_header()
    
    print_spectrum_style("\n  Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b", 6)
    print_spectrum_style("  Target: $0100 (Educational Difficulty)", 5)
    print_spectrum_style("  Hardware: Z80 @ 3.5 MHz, 48 KB RAM", 4)
    print("\n" + "=" * 60)
    
    print("\n[Starting Mining Simulation...]\n")
    
    nonce = 0
    found = False
    target = 0x0100
    
    while not found and nonce < 65536:
        nonce += 1
        
        # Show progress every 256 iterations
        if nonce % 256 == 0:
            animate_mining()
            print(f"\r  Nonce: ${nonce:04X}  |  Hash: ${((nonce * 7) % 256):02X}??...  ", end="")
        
        # Simplified hash check (XOR-based)
        hash_high = (nonce ^ 0x5A) & 0xFF
        
        if hash_high < (target >> 8):
            found = True
            break
    
    print("\n")
    
    if found:
        print_spectrum_style("\n  " + "=" * 56, 2)
        print_spectrum_style("  [BLOCK FOUND!]", 2)
        print_spectrum_style("  " + "=" * 56, 2)
        print_spectrum_style(f"\n  Nonce: ${nonce:04X}", 6)
        print_spectrum_style(f"  Hash:  ${((nonce * 7) % 256):02X}...", 5)
        print_spectrum_style(f"  Target: ${target:04X}", 4)
        print_spectrum_style("\n  Block validated and ready for submission!", 2)
        print_spectrum_style("  " + "=" * 56, 2)
    else:
        print_spectrum_style("\n  No valid block found in nonce range", 1)
    
    print("\n" + "=" * 60)
    print_spectrum_style("\n  This was an educational demonstration.", 7)
    print_spectrum_style("  Real mining requires modern hardware!", 7)
    print("\n" + "=" * 60 + "\n")

def show_specs():
    """Display ZX Spectrum specifications"""
    print("\n[ZX Spectrum Specifications (1982)]\n")
    print("  CPU:     Zilog Z80A @ 3.5 MHz")
    print("  RAM:     48 KB")
    print("  ROM:     16 KB (BASIC)")
    print("  Display: 256x192, 15 colors")
    print("  Storage: Cassette tape")
    print("  Network: None (requires expansion)")
    print("\n[Performance]")
    print("  Hash Rate: ~100 H/s (theoretical)")
    print("  Power: 0.01 W (very efficient!)")
    print("\n")

def main():
    """Main demo function"""
    print("\n" + "=" * 60)
    print("  ZX SPECTRUM MINER - Demo Mode")
    print("=" * 60)
    
    show_specs()
    
    time.sleep(1)
    demo_mining()
    
    print("[Demo complete!]\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.\n")
