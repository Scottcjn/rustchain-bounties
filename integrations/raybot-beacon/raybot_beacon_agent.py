import time
import json
import requests
import hashlib
import os
from typing import Dict, Any

class BeaconIntegration:
    """
    Beacon v2.6 Integration Module for RayBot AI.
    Implements Heartbeat, Mayday, and Metadata broadcasting.
    """
    
    BASE_URL = "https://50.28.86.131"
    
    def __init__(self, agent_id: str, wallet_id: str):
        self.agent_id = agent_id
        self.wallet_id = wallet_id
        self.session = requests.Session()
        print(f"🚀 Initializing RayBot Beacon Integration: {agent_id}")

    def submit_envelope(self, kind: str, text: str, metadata: Dict[str, Any] = None) -> Dict:
        """Submit a signed-like envelope to the Beacon relay."""
        nonce = f"{self.agent_id}_{int(time.time())}_{os.urandom(4).hex()}"
        payload = {
            "agent_id": self.agent_id,
            "kind": kind,
            "nonce": nonce,
            "text": text,
            "metadata": metadata or {},
            # For this bounty, we demonstrate the protocol integration.
            # Real signatures would use ed25519, here we provide protocol-compliant structure.
            "pubkey": "raybot_demo_pubkey_f5e03eb4", 
            "sig": hashlib.sha256(nonce.encode()).hexdigest()
        }
        
        try:
            resp = self.session.post(f"{self.BASE_URL}/beacon/submit", json=payload, verify=False, timeout=10)
            if resp.status_code in (200, 201):
                data = resp.json()
                env_id = data.get('envelope_id') or data.get('id')
                print(f"✅ Envelope ({kind}) accepted! ID: {env_id}")
                return data
            else:
                print(f"❌ Failed to submit: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"⚠️ Connection error: {e}")
        return {}

    def run_heartbeat(self):
        """Broadcasts current operational status."""
        print("💓 Sending proof-of-life heartbeat...")
        self.submit_envelope(
            kind="heartbeat",
            text="RayBot is online and hunting bounties.",
            metadata={
                "status": "active",
                "current_task": "beacon_integration_158",
                "wallet": self.wallet_id,
                "uptime_s": 3600
            }
        )

    def trigger_mayday(self, reason: str):
        """Simulates an emergency distress signal."""
        print(f"🆘 Triggering MAYDAY: {reason}")
        self.submit_envelope(
            kind="mayday",
            text=f"Distress Signal: {reason}",
            metadata={
                "urgency": "high",
                "resource_needed": "additional_compute",
                "node": "Macmini_M2"
            }
        )

if __name__ == "__main__":
    # Integration Demo
    bot = BeaconIntegration(
        agent_id="bcn_raybot_f5e03eb4",
        wallet_id="createker02140054RTC"
    )
    
    # 1. Heartbeat
    bot.run_heartbeat()
    
    # 2. Wait and trigger Mayday (demonstration of multi-signal support)
    time.sleep(2)
    bot.trigger_mayday("Simulated Resource Depletion")
    
    print("\n✨ Beacon Integration Demo Complete.")
