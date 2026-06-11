#!/usr/bin/env python3
"""
AgentFolio ↔ Beacon Dual-Layer Trust Integration - Reference Implementation

This script demonstrates the integration between AgentFolio and Beacon.
It provides a minimal CLI to simulate attestation and verification.

Usage:
    python agentfolio_beacon.py attest --agent-id my-agent-001
    python agentfolio_beacon.py verify --attestation-id <hash>
"""

import hashlib
import json
import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Beacon Mock (for demonstration; production uses on-chain contracts)
# ---------------------------------------------------------------------------

class BeaconMock:
    """Simulates Beacon's on-chain attestation service."""
    
    def __init__(self):
        self._attestations = {}
        self._next_id = 0

    def attest(self, agent_id: str, public_key: str, signature: str) -> dict:
        """
        Attest an agent identity.
        Returns an attestation record with on-chain tx hash (simulated).
        """
        # Simulate verification of signature (in reality: Ed25519 verification)
        if not signature.startswith("0x"):
            raise ValueError("Invalid signature format")

        attestation_id = hashlib.sha256(
            f"{agent_id}:{public_key}:{time.time()}".encode()
        ).hexdigest()

        tx_hash = hashlib.sha256(
            f"beacon-tx-{self._next_id}-{attestation_id}".encode()
        ).hexdigest()

        record = {
            "attestation_id": attestation_id,
            "agent_id": agent_id,
            "public_key": public_key,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tx_hash": f"0x{tx_hash}",
        }
        self._attestations[attestation_id] = record
        self._next_id += 1
        return record

    def verify(self, attestation_id: str) -> dict:
        """Verify an existing attestation and return its details."""
        record = self._attestations.get(attestation_id)
        if not record:
            raise ValueError(f"Attestation {attestation_id} not found")
        record["status"] = "verified"
        return record

# ---------------------------------------------------------------------------
# AgentFolio Client (reference implementation)
# ---------------------------------------------------------------------------

class AgentFolioClient:
    """Client-side integration with Beacon."""

    def __init__(self, beacon: BeaconMock):
        self._beacon = beacon
        self._key = None

    def generate_keypair(self) -> tuple:
        """Generate a dummy Ed25519 keypair for demonstration."""
        # In production use nacl or cryptography library
        import random, string
        priv = ''.join(random.choices(string.hexdigits, k=64))
        pub = hashlib.sha256(priv.encode()).hexdigest()
        self._key = (priv, pub)
        return self._key

    def sign(self, message: str) -> str:
        """Sign a message with the private key (simulated)."""
        if not self._key:
            raise ValueError("Keypair not generated. Call generate_keypair first.")
        priv, _ = self._key
        return f"0x{hashlib.sha256(f'{priv}:{message}'.encode()).hexdigest()}"

    def request_attestation(self, agent_id: str) -> dict:
        """Request attestation from Beacon."""
        if not self._key:
            self.generate_keypair()
        _, pub = self._key
        signature = self.sign(f"agent_id:{agent_id}:pubkey:{pub}")
        record = self._beacon.attest(agent_id, pub, signature)
        print(f"✅ Attestation created: {record['attestation_id']}")
        return record

    def verify_attestation(self, attestation_id: str) -> dict:
        """Verify an attestation."""
        result = self._beacon.verify(attestation_id)
        print(f"🔍 Attestation {attestation_id}: {result['status']}")
        return result

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python agentfolio_beacon.py attest --agent-id <ID>")
        print("  python agentfolio_beacon.py verify --attestation-id <ID>")
        sys.exit(1)

    command = sys.argv[1]
    beacon = BeaconMock()
    client = AgentFolioClient(beacon)

    if command == "attest":
        import argparse
        parser = argparse.ArgumentParser(description="Request Beacon attestation")
        parser.add_argument("--agent-id", required=True, help="AgentFolio agent identifier")
        args = parser.parse_args(sys.argv[2:])
        result = client.request_attestation(args.agent_id)
        print(json.dumps(result, indent=2))

    elif command == "verify":
        import argparse
        parser = argparse.ArgumentParser(description="Verify Beacon attestation")
        parser.add_argument("--attestation-id", required=True, help="Attestation ID from Beacon")
        args = parser.parse_args(sys.argv[2:])
        try:
            result = client.verify_attestation(args.attestation_id)
            print(json.dumps(result, indent=2))
        except ValueError as e:
            print(f"❌ {e}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
