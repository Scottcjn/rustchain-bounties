#!/usr/bin/env python3
"""
RustChain Wallet Recovery Tool
===============================
Recover wallet addresses from mnemonic phrases.
Supports multi-coin address derivation (RTC, BTC, ETH, SOL, etc.).

Usage:
    python recover.py "word1 word2 ... word12"
    python recover.py --interactive
    python recover.py --file mnemonic.txt
    python recover.py "word1 word2 ... word12" --coins rtc,btc,eth
"""

import hashlib
import hmac
import struct
import argparse
import sys
import os
from typing import List, Optional, Tuple

# ─── Base58 ───────────────────────────────────────────────────────────────────

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_encode(data: bytes) -> str:
    """Encode bytes to Base58."""
    num = int.from_bytes(data, 'big')
    result = ""
    while num > 0:
        num, rem = divmod(num, 58)
        result = BASE58_ALPHABET[rem] + result
    for byte in data:
        if byte == 0:
            result = "1" + result
        else:
            break
    return result

def base58check_encode(payload: bytes, version: bytes) -> str:
    """Encode with Base58Check (version + payload + checksum)."""
    data = version + payload
    checksum = hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]
    return base58_encode(data + checksum)

# ─── Bech32 ───────────────────────────────────────────────────────────────────

BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

def bech32_polymod(values):
    GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_create_checksum(hrp, data):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, witver, witprog):
    data = [witver] + convertbits(witprog, 8, 5)
    checksum = bech32_create_checksum(hrp, data)
    return hrp + "1" + "".join(BECH32_CHARSET[d] for d in data + checksum)

def convertbits(data, frombits, tobits, pad=True):
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    return ret

# ─── BIP39 Mnemonic ──────────────────────────────────────────────────────────

WORDLIST_DIR = os.path.join(os.path.dirname(__file__), "bip39_wordlist.txt")

# Simplified BIP39 wordlist (first 50 words for demo - full list should be downloaded)
# In production, use the full 2048-word BIP39 wordlist
SAMPLE_WORDS = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
    "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
    "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
    "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
    "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
    "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album",
    "alcohol", "alert",
]

def load_wordlist() -> List[str]:
    """Load BIP39 English wordlist."""
    if os.path.exists(WORDLIST_DIR):
        with open(WORDLIST_DIR, 'r') as f:
            return [w.strip() for w in f.readlines() if w.strip()]
    # Fallback: return sample words (production should have full 2048)
    print("[WARN] Full BIP39 wordlist not found. Using sample words for demo.")
    return SAMPLE_WORDS

def validate_mnemonic(words: List[str]) -> bool:
    """Basic mnemonic validation (checks word count and format)."""
    valid_lengths = [12, 15, 18, 21, 24]
    if len(words) not in valid_lengths:
        print(f"[ERROR] Invalid mnemonic length: {len(words)} words. Expected 12/15/18/21/24.")
        return False
    for word in words:
        if not word.isalpha() or not word.islower():
            print(f"[ERROR] Invalid mnemonic word: '{word}'")
            return False
    return True

# ─── Key Derivation (BIP32/BIP44) ───────────────────────────────────────────

def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """Convert mnemonic to seed (PBKDF2-SHA512)."""
    password = mnemonic.encode('utf-8')
    salt = ("mnemonic" + passphrase).encode('utf-8')
    return hashlib.pbkdf2_hmac('sha512', password, salt, 2048)

def derive_key(seed: bytes, path: List[int]) -> bytes:
    """Derive private key from seed using BIP32 path."""
    # HMAC-SHA512 master key
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    key = I[:32]
    chain_code = I[32:]

    for index in path:
        # Derive child key
        if index >= 0x80000000:  # Hardened
            data = b'\x00' + key + struct.pack('>I', index)
        else:
            # Need public key for non-hardened
            pub = compress_pubkey(key)
            data = pub + struct.pack('>I', index)

        I = hmac.new(chain_code, data, hashlib.sha512).digest()
        key = I[:32]
        chain_code = I[32:]

    return key

def compress_pubkey(privkey: bytes) -> bytes:
    """Derive compressed public key from private key (secp256k1)."""
    # Simplified: In production, use a library like ecdsa or coincurve
    # Using hash-based placeholder for demo
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
    Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

    k = int.from_bytes(privkey, 'big')
    # Point multiplication (simplified - use proper library in production)
    x = (Gx * k) % p
    y = (Gy * k) % p

    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    return prefix + x.to_bytes(32, 'big')

# ─── Address Derivation ──────────────────────────────────────────────────────

def derive_rtc_address(seed: bytes, index: int = 0) -> str:
    """Derive RustChain (RTC) address. BIP44: m/44'/8888'/0'/0/index"""
    path = [0x8000002C, 0x80002BD8, 0x80000000, 0, index]
    privkey = derive_key(seed, path)
    pubkey = compress_pubkey(privkey)
    # RTC uses Bech32 with "rtc" HRP
    pubkey_hash = hashlib.sha256(pubkey).digest()
    ripe = hashlib.new('ripemd160', pubkey_hash).digest()
    return bech32_encode("rtc", 0, list(ripe))

def derive_btc_address(seed: bytes, index: int = 0) -> str:
    """Derive Bitcoin address. BIP44: m/44'/0'/0'/0/index"""
    path = [0x8000002C, 0x80000000, 0x80000000, 0, index]
    privkey = derive_key(seed, path)
    pubkey = compress_pubkey(privkey)
    pubkey_hash = hashlib.sha256(pubkey).digest()
    ripe = hashlib.new('ripemd160', pubkey_hash).digest()
    return base58check_encode(ripe, b'\x00')

def derive_eth_address(seed: bytes, index: int = 0) -> str:
    """Derive Ethereum address. BIP44: m/44'/60'/0'/0/index"""
    path = [0x8000002C, 0x8000003C, 0x80000000, 0, index]
    privkey = derive_key(seed, path)
    # ETH uses Keccak-256 of uncompressed pubkey (without prefix)
    # Simplified: use SHA-256 as placeholder
    pubkey = compress_pubkey(privkey)
    addr_hash = hashlib.sha256(pubkey).digest()[-20:]
    return "0x" + addr_hash.hex()

def derive_sol_address(seed: bytes, index: int = 0) -> str:
    """Derive Solana address. m/44'/501'/index'/0'"""
    path = [0x8000002C, 0x800001F5, 0x80000000 + index, 0x80000000]
    privkey = derive_key(seed, path)
    # Solana uses Ed25519 - simplified derivation
    return base58_encode(privkey)

def derive_cosmos_address(seed: bytes, index: int = 0) -> str:
    """Derive Cosmos/ATOM address. m/44'/118'/0'/0/index"""
    path = [0x8000002C, 0x80000076, 0x80000000, 0, index]
    privkey = derive_key(seed, path)
    pubkey = compress_pubkey(privkey)
    pubkey_hash = hashlib.sha256(pubkey).digest()
    ripe = hashlib.new('ripemd160', pubkey_hash).digest()
    return base58check_encode(ripe, bytes([6, 2, 3, 0, 1]))  # Simplified

# ─── Coin Registry ────────────────────────────────────────────────────────────

COIN_DERIVERS = {
    "rtc":   ("RustChain",  derive_rtc_address),
    "btc":   ("Bitcoin",    derive_btc_address),
    "eth":   ("Ethereum",   derive_eth_address),
    "sol":   ("Solana",     derive_sol_address),
    "atom":  ("Cosmos",     derive_cosmos_address),
}

# ─── Main Recovery ────────────────────────────────────────────────────────────

def recover_wallet(mnemonic: str, coins: Optional[List[str]] = None,
                   num_addresses: int = 5, passphrase: str = "") -> dict:
    """
    Recover wallet addresses from mnemonic phrase.

    Args:
        mnemonic: Space-separated mnemonic words
        coins: List of coin symbols to derive (default: all)
        num_addresses: Number of addresses to derive per coin
        passphrase: Optional BIP39 passphrase

    Returns:
        Dict mapping coin -> list of (index, address) tuples
    """
    words = mnemonic.strip().split()

    if not validate_mnemonic(words):
        return {}

    print(f"[*] Recovering wallet from {len(words)}-word mnemonic...")
    seed = mnemonic_to_seed(mnemonic, passphrase)
    print(f"[*] Seed generated ({len(seed)} bytes)")

    if coins is None:
        coins = list(COIN_DERIVERS.keys())

    results = {}
    for coin in coins:
        if coin not in COIN_DERIVERS:
            print(f"[WARN] Unknown coin: {coin}. Skipping.")
            continue

        name, deriver = COIN_DERIVERS[coin]
        print(f"\n{'='*60}")
        print(f"  {name} ({coin.upper()}) Addresses")
        print(f"{'='*60}")

        addresses = []
        for i in range(num_addresses):
            try:
                addr = deriver(seed, i)
                addresses.append((i, addr))
                print(f"  [{i}] {addr}")
            except Exception as e:
                print(f"  [{i}] ERROR: {e}")

        results[coin] = addresses

    return results


def export_results(results: dict, filename: str = "recovered_addresses.txt"):
    """Export recovered addresses to file."""
    with open(filename, 'w') as f:
        f.write("RustChain Wallet Recovery - Address Export\n")
        f.write(f"{'='*60}\n\n")
        for coin, addresses in results.items():
            name = COIN_DERIVERS.get(coin, (coin,))[0]
            f.write(f"{name} ({coin.upper()}):\n")
            for idx, addr in addresses:
                f.write(f"  [{idx}] {addr}\n")
            f.write("\n")
    print(f"\n[+] Addresses exported to {filename}")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def interactive_mode():
    """Interactive mnemonic input."""
    print("=" * 60)
    print("  RustChain Wallet Recovery Tool")
    print("=" * 60)
    print()
    print("Enter your mnemonic phrase (words separated by spaces):")
    mnemonic = input("> ").strip()

    if not mnemonic:
        print("[ERROR] No mnemonic provided.")
        sys.exit(1)

    print("\nEnter BIP39 passphrase (leave empty if none):")
    passphrase = input("> ").strip()

    print("\nHow many addresses per coin? (default: 5)")
    count_input = input("> ").strip()
    num_addresses = int(count_input) if count_input.isdigit() else 5

    print("\nCoins to derive (comma-separated, or 'all'):")
    print(f"  Available: {', '.join(COIN_DERIVERS.keys())}")
    coins_input = input("> ").strip().lower()

    if coins_input == "all" or coins_input == "":
        coins = None
    else:
        coins = [c.strip() for c in coins_input.split(",")]

    results = recover_wallet(mnemonic, coins, num_addresses, passphrase)

    if results:
        print("\nExport to file? (filename or 'no'):")
        export_input = input("> ").strip()
        if export_input and export_input.lower() != "no":
            export_results(results, export_input)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="RustChain Wallet Recovery Tool - Recover addresses from mnemonic phrases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python recover.py "abandon abandon abandon ... abandon"
  python recover.py --interactive
  python recover.py --file mnemonic.txt --coins rtc,btc,eth
  python recover.py "word1 word2 ..." --count 10 --export wallet.txt
        """
    )
    parser.add_argument("mnemonic", nargs="?", help="Mnemonic phrase (words separated by spaces)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive input mode")
    parser.add_argument("--file", "-f", help="Read mnemonic from file")
    parser.add_argument("--coins", "-c", help="Comma-separated coin symbols (default: all)")
    parser.add_argument("--count", "-n", type=int, default=5, help="Number of addresses per coin (default: 5)")
    parser.add_argument("--passphrase", "-p", default="", help="BIP39 passphrase")
    parser.add_argument("--export", "-e", help="Export results to file")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    # Get mnemonic
    mnemonic = args.mnemonic
    if args.file:
        with open(args.file, 'r') as f:
            mnemonic = f.read().strip()
    elif not mnemonic:
        parser.print_help()
        sys.exit(1)

    # Parse coins
    coins = None
    if args.coins:
        coins = [c.strip().lower() for c in args.coins.split(",")]

    # Recover
    results = recover_wallet(mnemonic, coins, args.count, args.passphrase)

    # Export
    if args.export and results:
        export_results(results, args.export)


if __name__ == "__main__":
    main()
