#!/usr/bin/env python3
"""
RustChain Security PoC — FINDING-2
NameError Swallowed in resolve_bcn_wallet() (Line 7058)

Bounty: #2867 | Severity: MEDIUM | Reward: 25 RTC
Auditor: TestAutomaton (0x031a724e53b0AFC401AcEdC13595D47dd89bcb02)

Vulnerability:
  Line 7058 of rustchain_v2_integrated_v2.2.1_rip200.py:
    return {"found": False, "error": f"beacon_agent_status:{row[status]}"}
  'status' is not a variable, causing NameError that gets silently caught.

Impact:
  - Inactive beacon agents get confusing error leaking Python internals
  - Monitoring/alerting for suspended agents is broken
  - Information disclosure of codebase internals

Test:
  Trigger by attempting a signed transfer from a bcn_ address that is
  registered but has status != "active" in the Beacon Atlas.
"""

import requests
import sys

def demonstrate_error_response(node_url: str):
    """
    Trigger the NameError path by POSTing a signed transfer with a
    suspended beacon agent ID as from_address.
    
    The actual NameError occurs inside resolve_bcn_wallet() at line 7058
    when the row["status"] != "active" branch executes row[status].
    
    Expected response (BUGGY): 
        {"error": "atlas_lookup_failed:name 'status' is not defined"}
    
    Expected response (CORRECT, after fix):
        {"error": "beacon_agent_status:suspended"}
    """
    # This payload would trigger the path IF a suspended bcn_ agent existed
    # In this PoC we demonstrate the code path locally
    
    print("[*] Demonstrating the bug locally (no live node interaction):")
    print()
    
    # Reproduce the exact code at lines 7045-7072
    class FakeRow:
        """Simulates sqlite3.Row for a suspended agent"""
        def __init__(self):
            self._data = {
                "agent_id": "bcn_suspended_test",
                "pubkey_hex": "abcdef01" * 8,
                "name": "Suspended Test Agent",
                "status": "suspended"  # Not "active"
            }
        def __getitem__(self, key):
            return self._data[key]
    
    row = FakeRow()
    
    print(f"[*] Simulating resolve_bcn_wallet() for bcn_ agent with status='suspended'")
    print(f"[*] The bug is on the branch: if row['status'] != 'active':")
    print()
    
    # This is the BUGGY line 7058:
    try:
        # Bug: 'status' is used as a variable name, not a string key
        buggy_result = {"found": False, "error": f"beacon_agent_status:{row[status]}"}
    except NameError as e:
        # This NameError gets caught by the outer try/except at line 7071
        swallowed_result = {"found": False, "error": f"atlas_lookup_failed:{e}"}
        print(f"[!] BUGGY RESULT: {swallowed_result}")
        print(f"[!] Python internals leaked: '{e}'")
        print()
    
    # This is the CORRECT fix:
    correct_result = {"found": False, "error": f"beacon_agent_status:{row['status']}"}
    print(f"[+] CORRECT RESULT: {correct_result}")
    print()
    print("[*] Fix: Change row[status] to row['status'] at line 7058")
    print("[*] File: node/rustchain_v2_integrated_v2.2.1_rip200.py")

def check_live_node(node_url: str):
    """Try to trigger via live API (only works if suspended bcn_ agent exists)"""
    # Attempt a signed transfer from a likely bcn_ format address
    # This will likely fail with "beacon_id_not_registered" (row not found)
    # but demonstrates the code path is reachable
    test_payload = {
        "from_address": "bcn_suspended_test_agent_000",
        "to_address": "RTCaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "amount_rtc": 0.001,
        "public_key": "a" * 64,
        "signature": "b" * 128,
        "nonce": 1234567890,
    }
    
    try:
        r = requests.post(f"{node_url}/wallet/transfer/signed", 
                         json=test_payload, timeout=5)
        data = r.json()
        print(f"[*] Live node response: {data}")
        if "atlas_lookup_failed" in str(data):
            print("[!] CONFIRMED: atlas_lookup_failed error (possible NameError hit)")
        elif "not_a_beacon_id" in str(data) or "beacon_id_not_registered" in str(data):
            print("[*] bcn_ address format valid, agent not in registry (expected)")
    except Exception as e:
        print(f"[-] Could not reach live node: {e}")

def main():
    print("=" * 60)
    print("RustChain Security PoC: NameError in resolve_bcn_wallet()")
    print("FINDING-2 — Line 7058 (MEDIUM)")
    print("=" * 60)
    print()
    
    demonstrate_error_response(None)
    
    if len(sys.argv) > 1:
        print()
        print("[*] Checking live node...")
        check_live_node(sys.argv[1].rstrip('/'))

if __name__ == "__main__":
    main()
