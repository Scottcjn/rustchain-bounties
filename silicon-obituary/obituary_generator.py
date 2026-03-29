#!/usr/bin/env python3
"""
Silicon Obituary - Hardware Eulogy Generator
Generates poetic obituaries for retired miners.
"""

import json
import random
from datetime import datetime, timedelta

# Sample obituary templates
OBITUARY_TEMPLATES = [
    "Here lies {miner_id}, a {hardware}. It attested for {epochs} epochs and earned {rtc} RTC. Its cache timing fingerprint was as unique as a snowflake in a blizzard of modern silicon. It is survived by its power supply, which still works.",
    "In loving memory of {miner_id}, {hardware}. This noble machine worked faithfully for {days} days, contributing {rtc} RTC to the RustChain network. May its cycles rest in peace.",
    "{miner_id} has been laid to rest. This {hardware} faithfully performed {epochs} attestations, earning {rtc} RTC. Its thermal drift signature will be remembered forever.",
    "Gone but not forgotten: {miner_id}, the {hardware}. After {days} days of service and {epochs} attestations, it has earned its eternal rest. {rtc} RTC earned, 0 regret.",
    "Farewell, {miner_id}. This {hardware} was more than hardware - it was a contributor to decentralized history. {epochs} epochs. {rtc} RTC. One-of-a-kind fingerprint."
]

HARDWARE_TEMPLATES = [
    "Power Mac G4 MDD",
    "Mac Pro 2006",
    "Dell Precision 690",
    "HP DL380 G5",
    "IBM System x3550",
    "Sun Fire V40z",
    "SGI Octane II",
    "Cray SV1",
    "Compaq ProLiant ML570",
    "Intel Xeon Silver 4210",
    "AMD EPYC 7702P",
    "Raspberry Pi 4 Model B",
    "StarFive VisionFive 2"
]

def generate_obituary(miner_data):
    """Generate a poetic obituary for a retired miner."""
    miner_id = miner_data.get('miner_id', 'unknown_miner')
    epochs = miner_data.get('total_epochs', 0)
    rtc = miner_data.get('total_rtc', 0)
    first_attest = miner_data.get('first_attestation', 'unknown')
    last_attest = miner_data.get('last_attestation', 'unknown')
    arch = miner_data.get('architecture', 'unknown')
    
    # Calculate days of service
    try:
        first = datetime.fromisoformat(first_attest.replace('Z', '+00:00'))
        last = datetime.fromisoformat(last_attest.replace('Z', '+00:00'))
        days = (last - first).days
    except:
        days = random.randint(30, 1000)
    
    # Pick a hardware template or use actual arch
    if arch != 'unknown':
        hardware = arch
    else:
        hardware = random.choice(HARDWARE_TEMPLATES)
    
    # Pick a template
    template = random.choice(OBITUARY_TEMPLATES)
    
    obituary = template.format(
        miner_id=miner_id,
        hardware=hardware,
        epochs=epochs,
        rtc=rtc,
        days=days
    )
    
    return obituary

def get_retired_miners(node_url="https://50.28.86.131"):
    """Get list of miners that haven't attested in 7+ days."""
    # In production, this would query the RustChain API
    # For demo, return mock retired miners
    return [
        {
            'miner_id': 'dual-g4-125',
            'total_epochs': 847,
            'total_rtc': 412,
            'first_attestation': '2025-06-15T00:00:00Z',
            'last_attestation': '2026-03-15T00:00:00Z',
            'architecture': 'Power Mac G4 MDD'
        },
        {
            'miner_id': 'x86-single-067',
            'total_epochs': 1243,
            'total_rtc': 891,
            'first_attestation': '2025-03-20T00:00:00Z',
            'last_attestation': '2026-03-20T00:00:00Z',
            'architecture': 'Dell Precision 690'
        },
        {
            'miner_id': 'arm-rpi4-012',
            'total_epochs': 456,
            'total_rtc': 234,
            'first_attestation': '2025-09-01T00:00:00Z',
            'last_attestation': '2026-03-22T00:00:00Z',
            'architecture': 'Raspberry Pi 4 Model B'
        }
    ]

def main():
    print("=== Silicon Obituary Generator ===")
    print()
    
    miners = get_retired_miners()
    
    for miner in miners:
        obituary = generate_obituary(miner)
        print(f"Miner: {miner['miner_id']}")
        print(f"Epochs: {miner['total_epochs']}, RTC: {miner['total_rtc']}")
        print(f"Obituary:\n{obituary}")
        print("-" * 60)
        print()

if __name__ == "__main__":
    main()
