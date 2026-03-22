#!/usr/bin/env python3
"""
Anchor BCOS attestation to RustChain on merge.
Called by action.yml on push to main/master.
"""

import json
import os
import sys

try:
    import httpx
    _client_lib = "httpx"
except ImportError:
    import urllib.request
    _client_lib = "urllib"


def post_json(url: str, data: dict, timeout: int = 30) -> dict:
    body = json.dumps(data).encode()
    if _client_lib == "httpx":
        with httpx.Client(verify=False, timeout=timeout) as c:
            r = c.post(url, content=body, headers={"Content-Type": "application/json"})
            r.raise_for_status()
            return r.json()
    else:
        req = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())


def main() -> None:
    cert_id = os.environ.get("CERT_ID", "")
    node_url = os.environ.get("NODE_URL", "https://50.28.86.131").rstrip("/")
    repo = os.environ.get("REPO", "")
    sha = os.environ.get("SHA", "")

    if not cert_id or cert_id == "BCOS-unknown":
        print("[BCOS anchor] No valid cert ID, skipping anchor.", flush=True)
        return

    payload = {
        "cert_id": cert_id,
        "repo": repo,
        "commit_sha": sha,
        "event": "merge",
    }

    anchor_url = f"{node_url}/bcos/anchor"
    print(f"[BCOS anchor] Anchoring {cert_id} to {anchor_url}", flush=True)

    try:
        result = post_json(anchor_url, payload)
        tx_id = result.get("tx_id") or result.get("transaction_id", "")
        print(f"[BCOS anchor] Anchored! TX: {tx_id}", flush=True)
    except Exception as e:
        # Non-fatal: anchor failure should not break CI
        print(f"[BCOS anchor] Warning: could not anchor to RustChain: {e}", flush=True)
        print("::warning::BCOS anchor to RustChain failed (non-fatal)", flush=True)


if __name__ == "__main__":
    main()
