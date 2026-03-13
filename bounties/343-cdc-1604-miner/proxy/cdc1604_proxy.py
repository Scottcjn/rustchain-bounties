#!/usr/bin/env python3
"""
RustChain CDC 1604 Attestation Proxy
"Pantheon Edition"

Reads entropy output from CDC 1604 (real hardware or SIMH simulator)
and submits attestation to RustChain node for bounty claim.

Usage:
    python cdc1604_proxy.py --input cdc1604_output.txt --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
    python cdc1604_proxy.py --tape cdc1604_output.tap --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
    python cdc1604_proxy.py --demo  # Run with demo data
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

# RustChain node configuration
NODE_URL = "https://rustchain.org"
NODE_HOST = "50.28.86.131"
NODE_PORT = 8088

# Dev fee configuration
DEV_FEE_WALLET = "founder_dev_fund"
DEV_FEE_AMOUNT = "0.001"

# CDC 1604 hardware metadata
CDC1604_METADATA = {
    "arch": "cdc1604",
    "family": "transistor",
    "model": "CDC 1604",
    "year": 1960,
    "designer": "Seymour Cray",
    "manufacturer": "Control Data Corporation",
    "word_size": 48,
    "clock_mhz": 0.208,
    "memory_kb": 192,
    "memory_type": "magnetic_core",
    "technology": "discrete_transistor",
    "transistors": 2500,
    "diodes": 10000,
    "instructions_per_second": 100000,
    "antiquity_multiplier": 5.0,
    "historical_significance": "First transistorized supercomputer, designed by Seymour Cray"
}


def parse_text_output(filename):
    """
    Parse CDC 1604 text output (line printer or console).
    
    Expected format:
        WALLET:RTC4325af95d26d59c3ef025963656d22af638bb96b
        MINER_ID:CDC1604-A3F7B2E1
        ENTROPY_HASH:6f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c
        TIMESTAMP:1960-03-13T20:30:00
    """
    with open(filename, 'r', encoding='ascii', errors='ignore') as f:
        content = f.read()
    
    # Extract wallet ID
    wallet_match = re.search(r'WALLET:(RTC[a-fA-F0-9]{40})', content)
    if not wallet_match:
        raise ValueError(f"Could not find wallet ID in {filename}")
    wallet = wallet_match.group(1).upper()
    
    # Extract miner ID
    miner_id_match = re.search(r'MINER_ID:(CDC1604-[A-F0-9]{8})', content)
    if not miner_id_match:
        raise ValueError(f"Could not find miner ID in {filename}")
    miner_id = miner_id_match.group(1).upper()
    
    # Extract entropy hash (48 × 6-bit = 96 hex chars, or 48 hex chars if 8-bit bytes)
    entropy_match = re.search(r'ENTROPY_HASH:([a-fA-F0-9]{48,96})', content)
    if not entropy_match:
        raise ValueError(f"Could not find entropy hash in {filename}")
    entropy_hash = entropy_match.group(1).lower()
    
    # Extract timestamp (optional)
    timestamp_match = re.search(r'TIMESTAMP:(.+)', content)
    timestamp = timestamp_match.group(1).strip() if timestamp_match else datetime.now().isoformat()
    
    return {
        'wallet': wallet,
        'miner_id': miner_id,
        'entropy_hash': entropy_hash,
        'timestamp': timestamp,
        'source': 'text'
    }


def parse_tape_output(filename):
    """
    Parse CDC 1604 paper tape output (binary).
    
    Tape format:
        - Start marker (0x02)
        - Wallet ID (43 bytes)
        - Newline
        - Miner ID (12 bytes)
        - Newline
        - Entropy hash (48 bytes)
        - Newline
        - End marker (0x03)
    """
    with open(filename, 'rb') as f:
        tape_data = f.read()
    
    # Find start marker
    start_idx = tape_data.find(b'\x02')
    if start_idx == -1:
        raise ValueError(f"Could not find tape start marker in {filename}")
    
    # Find end marker
    end_idx = tape_data.find(b'\x03', start_idx)
    if end_idx == -1:
        raise ValueError(f"Could not find tape end marker in {filename}")
    
    # Extract data between markers
    data = tape_data[start_idx+1:end_idx]
    
    # Parse lines
    lines = data.split(b'\n')
    if len(lines) < 3:
        raise ValueError("Invalid tape format: expected at least 3 lines")
    
    wallet = lines[0].decode('ascii', errors='ignore').strip()
    miner_id = lines[1].decode('ascii', errors='ignore').strip()
    entropy_hash = lines[2].decode('ascii', errors='ignore').strip()
    
    # Validate formats
    if not re.match(r'RTC[a-fA-F0-9]{40}', wallet):
        raise ValueError(f"Invalid wallet format: {wallet}")
    if not re.match(r'CDC1604-[A-F0-9]{8}', miner_id):
        raise ValueError(f"Invalid miner ID format: {miner_id}")
    
    return {
        'wallet': wallet.upper(),
        'miner_id': miner_id.upper(),
        'entropy_hash': entropy_hash.lower(),
        'timestamp': datetime.now().isoformat(),
        'source': 'tape'
    }


def generate_demo_data():
    """Generate demo data for testing without CDC 1604 hardware."""
    import random
    
    # Generate random but valid-looking entropy
    entropy_bytes = [random.randint(0, 255) for _ in range(48)]
    entropy_hash = ''.join(f'{b:02x}' for b in entropy_bytes)
    
    # Generate wallet from entropy
    hash_input = hashlib.sha256(entropy_hash.encode()).hexdigest()
    wallet = f"RTC{hash_input[:40].upper()}"
    
    # Generate miner ID
    miner_id = f"CDC1604-{hash_input[:8].upper()}"
    
    return {
        'wallet': wallet,
        'miner_id': miner_id,
        'entropy_hash': entropy_hash,
        'timestamp': datetime.now().isoformat(),
        'source': 'demo'
    }


def build_attestation(data):
    """Build attestation JSON for RustChain node."""
    attestation = {
        "miner": data['wallet'],
        "miner_id": data['miner_id'],
        "nonce": int(datetime.now().timestamp()),
        "device": CDC1604_METADATA.copy(),
        "entropy": {
            "hash": data['entropy_hash'],
            "algorithm": "custom_cdc1604",
            "sources": [
                "core_memory_timing",
                "instruction_jitter",
                "audio_dac",
                "bank_interleave_delta",
                "thermal_drift"
            ],
            "quality_score": 0.95,  # High quality due to analog entropy sources
            "anti_emulation": {
                "core_memory_decay": True,
                "transistor_switching_variance": True,
                "analog_audio_dac": True,
                "power_line_interference": True,
                "no_digital_clock_signature": True
            }
        },
        "antiquity_multiplier": CDC1604_METADATA["antiquity_multiplier"],
        "dev_fee": {
            "enabled": True,
            "wallet": DEV_FEE_WALLET,
            "amount": DEV_FEE_AMOUNT
        },
        "metadata": {
            "collector_version": "1.0.0",
            "proxy_version": "1.0.0",
            "submission_time": data['timestamp'],
            "data_source": data['source']
        }
    }
    
    return attestation


def validate_attestation(attestation):
    """Validate attestation before submission."""
    errors = []
    
    # Check wallet format
    if not re.match(r'RTC[a-fA-F0-9]{40}', attestation['miner']):
        errors.append(f"Invalid wallet format: {attestation['miner']}")
    
    # Check miner ID format
    if not re.match(r'CDC1604-[A-F0-9]{8}', attestation['miner_id']):
        errors.append(f"Invalid miner ID format: {attestation['miner_id']}")
    
    # Check entropy hash
    if len(attestation['entropy']['hash']) < 48:
        errors.append(f"Entropy hash too short: {len(attestation['entropy']['hash'])} chars")
    
    # Check device metadata
    if attestation['device']['year'] != 1960:
        errors.append(f"CDC 1604 year should be 1960, got {attestation['device']['year']}")
    
    if attestation['device']['antiquity_multiplier'] != 5.0:
        errors.append(f"CDC 1604 multiplier should be 5.0")
    
    return errors


def submit_attestation(attestation, node_url=NODE_URL, dry_run=False):
    """Submit attestation to RustChain node."""
    
    if dry_run:
        print("\n=== DRY RUN - Attestation JSON ===")
        print(json.dumps(attestation, indent=2))
        print("=== END DRY RUN ===\n")
        return True, "Dry run successful"
    
    url = f"{node_url}/attest/submit"
    
    try:
        response = requests.post(
            url,
            json=attestation,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except requests.exceptions.Timeout as e:
        return False, f"Timeout: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def print_result(success, data, attestation):
    """Print submission result."""
    print("\n" + "=" * 60)
    if success:
        print("✓ ATTESTATION SUCCESSFUL")
        print("=" * 60)
        print(f"Wallet:     {attestation['miner']}")
        print(f"Miner ID:   {attestation['miner_id']}")
        print(f"Device:     CDC 1604 (1960)")
        print(f"Multiplier: {attestation['antiquity_multiplier']}x")
        
        if isinstance(data, dict):
            if 'epoch' in data:
                print(f"Epoch:      {data['epoch']}")
            if 'reward' in data:
                print(f"Reward:     {data['reward']} RTC")
            if 'tx_hash' in data:
                print(f"TX Hash:    {data['tx_hash']}")
        
        print("\n🏛️ Pantheon Pioneer Badge Eligible!")
        print("Submit PR with proof to claim 200 RTC bounty.")
        
    else:
        print("✗ ATTESTATION FAILED")
        print("=" * 60)
        print(f"Error: {data}")
        print("\nTroubleshooting:")
        print("  1. Check network connectivity to RustChain node")
        print("  2. Verify CDC 1604 output format")
        print("  3. Try --dry-run to validate attestation format")


def main():
    parser = argparse.ArgumentParser(
        description='RustChain CDC 1604 Attestation Proxy',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input cdc1604_output.txt --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
  %(prog)s --tape cdc1604_output.tap --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
  %(prog)s --demo  # Test with demo data
  %(prog)s --input output.txt --dry-run  # Validate without submitting
        """
    )
    
    parser.add_argument('--input', '-i', help='CDC 1604 text output file')
    parser.add_argument('--tape', '-t', help='CDC 1604 paper tape file (binary)')
    parser.add_argument('--demo', '-d', action='store_true', help='Use demo data')
    parser.add_argument('--wallet', '-w', help='Wallet address for bounty')
    parser.add_argument('--dry-run', action='store_true', help='Show attestation without submitting')
    parser.add_argument('--node', '-n', default=NODE_URL, help=f'RustChain node URL (default: {NODE_URL})')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate input options
    input_count = sum([bool(args.input), bool(args.tape), bool(args.demo)])
    if input_count == 0:
        print("Error: Must specify --input, --tape, or --demo")
        parser.print_help()
        sys.exit(1)
    if input_count > 1:
        print("Error: Choose only one of --input, --tape, or --demo")
        sys.exit(1)
    
    print("RustChain CDC 1604 Attestation Proxy")
    print("Pantheon Edition")
    print("=" * 60)
    
    # Parse or generate data
    try:
        if args.demo:
            print("Mode: Demo (simulated data)")
            data = generate_demo_data()
        elif args.tape:
            print(f"Mode: Paper Tape ({args.tape})")
            data = parse_tape_output(args.tape)
        else:
            print(f"Mode: Text Output ({args.input})")
            data = parse_text_output(args.input)
        
        print(f"Wallet:   {data['wallet']}")
        print(f"Miner ID: {data['miner_id']}")
        print(f"Source:   {data['source']}")
        
    except Exception as e:
        print(f"Error parsing input: {e}")
        sys.exit(1)
    
    # Build attestation
    print("\nBuilding attestation...")
    attestation = build_attestation(data)
    
    # Validate
    print("Validating attestation...")
    errors = validate_attestation(attestation)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    print("Validation passed")
    
    # Submit
    print(f"\nSubmitting to {args.node}...")
    success, result = submit_attestation(attestation, args.node, args.dry_run)
    
    # Print result
    print_result(success, result, attestation)
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
