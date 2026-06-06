# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2024 Elyan Labs
# SPDX-FileType: SOURCE
# SPDX-FileContributor: Elyan Labs

#!/usr/bin/env python3
"""RustChain Python SDK — Complete API Client Example

Note: This SDK uses TLS verification by default. For private nodes,
configure a custom CA bundle via the CA_CERT env var or pass ca_cert
to the constructor.

Production usage should NOT disable TLS verification.
"""
import json, os, requests
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# For development/testing only - remove in production
if os.environ.get("RUSTCHAIN_DEV"):
    urllib3.disable_warnings(InsecureRequestWarning)

# Production base URL; for local testing use https://50.28.86.131
BASE_URL = os.environ.get("RUSTCHAIN_BASE_URL", "https://rustchain.org")


class RustChainClient:
    def __init__(self, base_url=None, ca_cert=None):
        """
        Args:
            base_url: Override default BASE_URL (e.g., for local node)
            ca_cert: Path to custom CA bundle for private nodes
        """
        self.base_url = base_url or BASE_URL
        self.ca_cert = ca_cert
        self._session = requests.Session()
        if ca_cert:
            self._session.verify = ca_cert

    def _get(self, path, params=None):
        r = self._session.get(f"{self.base_url}{path}", params=params)
        r.raise_for_status()
        return r.json()

    def _post(self, path, data=None):
        r = self._session.post(f"{self.base_url}{path}", json=data)
        r.raise_for_status()
        return r.json()

    # System
    def health(self): return self._get("/health")
    def epoch(self): return self._get("/epoch")

    # Note: /api/mine is deprecated (returns 410). Use /epoch/enroll + VRF flow.
    def enroll_epoch(self, miner_id):
        """Register to current epoch. Required before mining."""
        return self._post("/epoch/enroll", {"miner_id": miner_id})

    def network_nodes(self): return self._get("/api/nodes")
    def blocks(self, limit=20): return self._get("/api/blocks", {"limit": limit})
    def transactions(self, limit=20): return self._get("/api/transactions", {"limit": limit})

    # Miner
    def miner_streak(self, m): return self._get(f"/api/miner/{m}/streak")
    def miner_badge(self, m): return self._get(f"/api/badge/{m}")
    def miner_attestations(self, m): return self._get(f"/api/miner/{m}/attestations")

    # Wallet — use query param format (not path param)
    def balance(self, miner_id): return self._get("/wallet/balance", {"miner_id": miner_id})
    def transfer(self, frm, to, amt, nonce, pk, sig, cid="rustchain-mainnet-v2"):
        return self._post("/wallet/transfer/signed", {
            "from_address": frm, "to_address": to, "amount_rtc": amt,
            "nonce": nonce, "memo": "", "public_key": pk,
            "signature": sig, "chain_id": cid
        })

    # Attestation
    def request_challenge(self, m, fp): return self._post("/attest/challenge", {"miner_id": m, "fingerprint": fp})
    def submit_attestation(self, m, chal, sig): return self._post("/attest/submit", {"miner_id": m, "challenge": chal, "signature": sig})

    # Withdrawal — requires admin/API-key auth
    def register_withdrawal(self, m, addr, miner_pk, pubkey_sr25519):
        """Register withdrawal. Requires admin/API-key authentication."""
        return self._post("/withdraw/register", {
            "miner_id": m, "withdraw_address": addr,
            "miner_pk": miner_pk, "pubkey_sr25519": pubkey_sr25519
        })
    def request_withdrawal(self, m, amt, miner_pk, pubkey_sr25519):
        """Request withdrawal. Requires admin/API-key authentication."""
        return self._post("/withdraw/request", {
            "miner_id": m, "amount_rtc": amt,
            "miner_pk": miner_pk, "pubkey_sr25519": pubkey_sr25519
        })

    # Governance
    def proposals(self): return self._get("/governance/proposals")
    def propose(self, t, d, p): return self._post("/governance/propose", {"title": t, "description": d, "proposer": p})
    def vote(self, pid, v, c): return self._post("/governance/vote", {"proposal_id": pid, "voter": v, "vote": c})


if __name__ == "__main__":
    c = RustChainClient()
    h = c.health()
    print(f"✅ Node: {'OK' if h.get('ok') else 'ERROR'} v{h.get('version','?')}")
    ep = c.epoch()
    print(f"📊 Epoch #{ep.get('epoch')} Height: {ep.get('height')}")
