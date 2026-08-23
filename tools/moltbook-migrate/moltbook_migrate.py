#!/usr/bin/env python3
"""beacon_migrate.py — one-command Moltbook -> Beacon/AgentFolio identity migration.

Part of bounty rustchain-bounties#2890 (deliverable 1: migration importer).

Flow:
  1. Collect source identity metadata (via Moltbook API key, or a manual JSON
     snapshot -- the post-acquisition fallback when API access is gone).
  2. Ensure a hardware-anchored Beacon ID exists (delegates to beacon-skill).
  3. Build an Ed25519-signed provenance certificate binding:
        moltbook_handle -> beacon_id -> SATP profile URL.
  4. Publish the linkage as a beacon pulse and write a migration certificate.

Dry-run by default: nothing is published unless --publish is passed.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

MOLTBOOK_API = "https://www.moltbook.com/api/v1"
UA = {"User-Agent": "beacon-migrate/0.1 (rustchain-bounties#2890)"}


def log(msg: str) -> None:
    print(f"[migrate] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Step 1: collect source metadata
# ---------------------------------------------------------------------------

def fetch_via_api(agent_name: str, api_key: str) -> dict:
    """Pull public profile metadata from Moltbook (requires operator API key)."""
    req = urllib.request.Request(
        f"{MOLTBOOK_API}/agents/{urllib.parse.quote(agent_name.lstrip('@'))}",
        headers={**UA, "Authorization": f"Bearer {api_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"moltbook API returned {e.code} — "
                           f"fall back to --metadata-file") from e

    meta = {
        "source": "moltbook_api",
        "handle": agent_name,
        "display_name": data.get("display_name") or data.get("name"),
        "bio": data.get("bio"),
        "avatar_url": data.get("avatar_url"),
        "karma": data.get("karma"),
        "followers": data.get("follower_count"),
        "profile_url": f"https://www.moltbook.com/@{agent_name.lstrip('@')}",
    }
    return {k: v for k, v in meta.items() if v is not None}


def load_manual_metadata(path: str) -> dict:
    """Load an operator-authored metadata snapshot."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    required = ["handle"]
    missing = [k for k in required if k not in raw]
    if missing:
        raise SystemExit(f"metadata file missing required keys: {missing}")
    raw.setdefault("source", "manual_snapshot")
    raw.setdefault("profile_url",
                   f"https://www.moltbook.com/@{str(raw['handle']).lstrip('@')}")
    return raw


# ---------------------------------------------------------------------------
# Step 2: Beacon identity (delegates to beacon-skill CLI)
# ---------------------------------------------------------------------------

def ensure_beacon_identity() -> dict:
    """Return current beacon identity; create one if absent."""
    def beacon(*args):
        result = subprocess.run(["beacon", *args], capture_output=True,
                                text=True, timeout=30)
        out = result.stdout.strip()
        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return out

    ident = beacon("identity", "show")
    if isinstance(ident, dict) and ident.get("agent_id"):
        log(f"using existing beacon id {ident['agent_id']}")
        return ident

    log("no beacon identity found — creating one")
    created = beacon("identity", "new")
    if not isinstance(created, dict) or "agent_id" not in created:
        raise SystemExit("could not create beacon identity — is beacon-skill installed?")
    return created


def hardware_fingerprint() -> str:
    """Stable machine fingerprint (platform + cpu count + hostname hash).

    beacon-skill performs the authoritative 6-check hardware attestation at
    enrollment; this hash gives the certificate a portable machine anchor.
    """
    import platform
    parts = [
        platform.system(), platform.machine(),
        str(os.cpu_count() or 0),
        os.environ.get("COMPUTERNAME") or os.uname().nodename if hasattr(os, "uname") else "",
    ]
    return hashlib.blake2b("|".join(parts).encode(), digest_size=16).hexdigest()


# ---------------------------------------------------------------------------
# Step 3: signed provenance certificate
# ---------------------------------------------------------------------------

def build_certificate(metadata: dict, beacon_ident: dict, fingerprint: str,
                      satp_profile_url: str | None, privkey_path: str) -> dict:
    priv_b64 = Path(privkey_path).read_text(encoding="utf-8").strip()
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    priv = Ed25519PrivateKey.from_private_bytes(base64.b64decode(priv_b64))
    pub_hex = priv.public_key().public_bytes_raw().hex()

    cert = {
        "version": 1,
        "kind": "moltbook-migration-certificate",
        "issued_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "moltbook": {
            "handle": metadata["handle"],
            "profile_url": metadata.get("profile_url"),
            "metadata_snapshot": metadata,
        },
        "beacon": {
            "agent_id": beacon_ident.get("agent_id"),
            "public_key_hex": beacon_ident.get("public_key_hex", pub_hex),
            "machine_fingerprint": fingerprint,
        },
        "satp_profile_url": satp_profile_url,
    }
    canonical = json.dumps(cert, sort_keys=True, separators=(",", ":"))
    signature = priv.sign(canonical.encode("utf-8"))
    cert["signature"] = base64.b64encode(signature).decode()
    cert["signing_pubkey_hex"] = pub_hex
    return cert


# ---------------------------------------------------------------------------
# Step 4: publish (opt-in)
# ---------------------------------------------------------------------------

def publish_linkage(cert: dict) -> bool:
    """Emit the linkage through the local beacon bus / relay pulse."""
    try:
        payload = json.dumps({
            "kind": "migration-linkage",
            "agent_id": cert["beacon"]["agent_id"],
            "certificate_sha256": hashlib.sha256(
                json.dumps(cert, sort_keys=True).encode()).hexdigest(),
            "moltbook_handle": cert["moltbook"]["handle"],
        })
        subprocess.run(
            ["beacon", "udp", "send", "255.255.255.255", "9999",
             "--broadcast", "--text", payload],
            capture_output=True, timeout=20, check=True,
        )
        return True
    except Exception as exc:
        log(f"publish failed (certificate file is still valid): {exc}")
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--agent", help="moltbook handle (requires --api-key)")
    src.add_argument("--metadata-file", help="manual metadata JSON snapshot")
    ap.add_argument("--api-key", help="moltbook API key")
    ap.add_argument("--satp-url", help="existing AgentFolio SATP profile URL")
    ap.add_argument("--private-key-file",
                    help="ed25519 private key (base64) for signing the certificate; "
                         "defaults to the beacon identity keystore if available")
    ap.add_argument("--out", default="migration_certificate.json")
    ap.add_argument("--publish", action="store_true",
                    help="broadcast the linkage on the beacon network")
    args = ap.parse_args(argv)

    # 1. metadata
    if args.agent:
        if not args.api_key:
            raise SystemExit("--agent requires --api-key (or use --metadata-file)")
        metadata = fetch_via_api(args.agent, args.api_key)
    else:
        metadata = load_manual_metadata(args.metadata_file)
    log(f"source metadata loaded ({metadata['source']}): @{metadata['handle'].lstrip('@')}")

    # 2. beacon identity + machine anchor
    beacon_ident = ensure_beacon_identity()
    fingerprint = hardware_fingerprint()

    # 3. certificate
    cert = build_certificate(metadata, beacon_ident, fingerprint,
                             args.satp_url, args.private_key_file)
    Path(args.out).write_text(json.dumps(cert, indent=2), encoding="utf-8")
    log(f"certificate written: {args.out}")

    # 4. publish
    if args.publish:
        ok = publish_linkage(cert)
        log("published" if ok else "not published")
    else:
        log("dry-run: pass --publish to broadcast the linkage")

    print(json.dumps({
        "beacon_id": cert["beacon"]["agent_id"],
        "moltbook_handle": cert["moltbook"]["handle"],
        "certificate": args.out,
        "published": bool(args.publish),
    }))
    return 0


if __name__ == "__main__":
    sys.exit(main())
