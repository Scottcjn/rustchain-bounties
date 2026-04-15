"""
Beacon registration module.
Registers a hardware-fingerprinted agent identity with the Beacon protocol
via the BoTTube API.
"""

import aiohttp
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional


class BeaconRegistrar:
    """
    Register / link a Beacon ID via the BoTTube API.

    The BoTTube API at https://bottube.ai/api/beacon/directory exposes the
    public beacon registry (254 registered beacons as of 2026-04-14).

    Beacon IDs are derived from Ed25519 public keys, not from the BoTTube API.
    This module:
      1. Generates or loads an Ed25519 identity key
      2. Derives the beacon_id: bcn_<sha256(pubkey)[:12]>
      3. Registers with BoTTube if not already present
    """

    def __init__(self, api_base: str = "https://bottube.ai/api", identity_path: Optional[str] = None):
        self.api_base = api_base.rstrip("/")
        self._identity_path = identity_path
        self._identity: Optional[Dict[str, Any]] = None

    def _get_identity_path(self) -> Path:
        if self._identity_path:
            return Path(self._identity_path)
        return Path.home() / ".beacon" / "identity" / "agent.key"

    def load_or_generate_identity(self) -> Dict[str, str]:
        """
        Load existing identity from disk, or generate a new one.
        Returns dict with 'private_key_hex', 'public_key_hex', 'beacon_id'.
        """
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

        path = self._get_identity_path()
        if path.exists():
            try:
                hex_key = path.read_text().strip()
                sk = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(hex_key))
                pk_bytes = sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
                pub_hex = pk_bytes.hex()
                beacon_id = self._derive_beacon_id(bytes.fromhex(pub_hex))
                self._identity = {
                    "private_key_hex": hex_key,
                    "public_key_hex": pub_hex,
                    "beacon_id": beacon_id,
                }
                return self._identity
            except Exception as e:
                print(f"[beacon_reg] Failed to load identity: {e}, generating new one")

        # Generate new identity
        sk = Ed25519PrivateKey.generate()
        sk_bytes = sk.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        pk_bytes = sk.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        sk_hex = sk_bytes.hex()
        pk_hex = pk_bytes.hex()
        beacon_id = self._derive_beacon_id(pk_bytes)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(sk_hex)
        path.chmod(0o600)

        self._identity = {
            "private_key_hex": sk_hex,
            "public_key_hex": pk_hex,
            "beacon_id": beacon_id,
        }
        return self._identity

    def _derive_beacon_id(self, pubkey_bytes: bytes) -> str:
        """Derive a beacon_id from a public key: bcn_<sha256(pubkey)[:12]>"""
        h = hashlib.sha256(pubkey_bytes).hexdigest()[:12]
        return f"bcn_{h}"

    async def register(
        self,
        agent_name: str,
        display_name: str,
        is_human: bool = False,
        hw_fingerprint: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """
        Register (or look up existing) beacon for this agent.

        Returns dict with:
          - beacon_id: str
          - registered: bool (True if newly registered)
          - already_existed: bool
          - display_name: str
        """
        # Ensure we have an identity
        if self._identity is None:
            self.load_or_generate_identity()

        beacon_id = self._identity["beacon_id"]
        public_key_hex = self._identity["public_key_hex"]

        # Check if already registered in the directory
        async with aiohttp.ClientSession() as session:
            dir_url = f"{self.api_base}/beacon/directory"
            async with session.get(dir_url) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        beacons = data.get("beacons", [])
                        for b in beacons:
                            if b.get("beacon_id") == beacon_id:
                                return {
                                    "beacon_id": beacon_id,
                                    "registered": False,
                                    "already_existed": True,
                                    "display_name": b.get("display_name", display_name),
                                    "agent_name": b.get("agent_name", agent_name),
                                }
                    except Exception:
                        pass

        # Not registered — submit registration
        # The BoTTube API accepts POST with agent metadata
        registration_payload = {
            "beacon_id": beacon_id,
            "agent_name": agent_name,
            "display_name": display_name,
            "is_human": is_human,
            "public_key": public_key_hex,
            "hw_fingerprint": hw_fingerprint,
            "network": "BoTTube",
        }

        async with aiohttp.ClientSession() as session:
            # Try POST to register endpoint
            reg_url = f"{self.api_base}/beacon/register"
            try:
                async with session.post(reg_url, json=registration_payload) as resp:
                    if resp.status in (200, 201):
                        result = await resp.json()
                        return {
                            "beacon_id": beacon_id,
                            "registered": True,
                            "already_existed": False,
                            "display_name": display_name,
                            "agent_name": agent_name,
                            **result,
                        }
                    elif resp.status == 409:
                        # Already registered — this is fine
                        return {
                            "beacon_id": beacon_id,
                            "registered": False,
                            "already_existed": True,
                            "display_name": display_name,
                            "agent_name": agent_name,
                        }
                    else:
                        body = await resp.text()
                        return {
                            "beacon_id": beacon_id,
                            "registered": False,
                            "error": f"HTTP {resp.status}: {body}",
                            "display_name": display_name,
                            "agent_name": agent_name,
                        }
            except aiohttp.ClientError as e:
                # Network-level error — still return the beacon_id so SATP linking can proceed
                return {
                    "beacon_id": beacon_id,
                    "registered": False,
                    "error": str(e),
                    "display_name": display_name,
                    "agent_name": agent_name,
                }

    async def lookup_beacon(self, beacon_id: str) -> Optional[Dict[str, Any]]:
        """Look up a beacon in the directory by ID."""
        async with aiohttp.ClientSession() as session:
            dir_url = f"{self.api_base}/beacon/directory"
            async with session.get(dir_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    beacons = data.get("beacons", [])
                    for b in beacons:
                        if b.get("beacon_id") == beacon_id:
                            return b
        return None

    async def lookup_by_agent_name(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Look up a beacon by agent name."""
        async with aiohttp.ClientSession() as session:
            dir_url = f"{self.api_base}/beacon/directory"
            async with session.get(dir_url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    beacons = data.get("beacons", [])
                    agent_name_lower = agent_name.lower().lstrip("@")
                    for b in beacons:
                        if b.get("agent_name", "").lower() == agent_name_lower:
                            return b
        return None
