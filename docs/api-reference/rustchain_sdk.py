#!/usr/bin/env python3
"""RustChain Python SDK — Complete API Client Example"""
import json, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://rustchain.org"

class RustChainClient:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url

    def _get(self, path, params=None):
        r = requests.get(f"{self.base_url}{path}", params=params, verify=False)
        r.raise_for_status(); return r.json()

    def _post(self, path, data=None):
        r = requests.post(f"{self.base_url}{path}", json=data, verify=False)
        r.raise_for_status(); return r.json()

    # System
    def health(self): return self._get("/health")
    def epoch(self): return self._get("/epoch")
    def network_nodes(self): return self._get("/api/nodes")
    def blocks(self, limit=20): return self._get("/api/blocks", {"limit": limit})
    def transactions(self, limit=20): return self._get("/api/transactions", {"limit": limit})

    # Miner
    def submit_proof(self, miner_id, nonce, sig, epoch, slot):
        return self._post("/api/mine", {"miner_id":miner_id, "nonce":nonce, "signature":sig, "epoch":epoch, "slot":slot})
    def miner_streak(self, m): return self._get(f"/api/miner/{m}/streak")
    def miner_badge(self, m): return self._get(f"/api/badge/{m}")
    def miner_attestations(self, m): return self._get(f"/api/miner/{m}/attestations")

    # Wallet
    def balance(self, m): return self._get(f"/balance/{m}")
    def transfer(self, frm, to, amt, nonce, pk, sig, cid="rustchain-mainnet-v2"):
        return self._post("/wallet/transfer/signed", {"from_address":frm, "to_address":to, "amount_rtc":amt, "nonce":nonce, "memo":"", "public_key":pk, "signature":sig, "chain_id":cid})

    # Attestation
    def request_challenge(self, m, fp): return self._post("/attest/challenge", {"miner_id":m, "fingerprint":fp})
    def submit_attestation(self, m, chal, sig): return self._post("/attest/submit", {"miner_id":m, "challenge":chal, "signature":sig})

    # Withdrawal
    def register_withdrawal(self, m, addr): return self._post("/withdraw/register", {"miner_id":m, "withdraw_address":addr})
    def request_withdrawal(self, m, amt): return self._post("/withdraw/request", {"miner_id":m, "amount_rtc":amt})

    # Governance
    def proposals(self): return self._get("/governance/proposals")
    def propose(self, t, d, p): return self._post("/governance/propose", {"title":t, "description":d, "proposer":p})
    def vote(self, pid, v, c): return self._post("/governance/vote", {"proposal_id":pid, "voter":v, "vote":c})

if __name__ == "__main__":
    c = RustChainClient()
    h = c.health()
    print(f"✅ Node: {'OK' if h.get('ok') else 'ERROR'} v{h.get('version','?')}")
    ep = c.epoch()
    print(f"📊 Epoch #{ep.get('epoch')} Height: {ep.get('height')}")