"""
RustChain Staking SDK — Core
Wraps the open RustChain staking flow:
  1. Lock (stake) RTC by submitting a signed epoch attestation
  2. Request the skill-gate verdict from the node
  3. If gate passes → return verified result + signed attestation
  4. If gate unavailable / fails → return stake, surface error to caller

Fail-safe contract:
  StakeResult.refunded == True  ←  stake was returned, no skill credited
  StakeResult.refunded == False ←  skill acquired, attestation is valid

Author: therealsaitama
Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/14383
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Configuration ──────────────────────────────────────────────────────────────
NODE_URL: str = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
CHAIN_ID: str = os.environ.get("RUSTCHAIN_CHAIN_ID", "rustchain-mainnet-v2")
_TIMEOUT: int = 15
_RETRIES: int = 2


# ── Data classes ───────────────────────────────────────────────────────────────

@dataclass
class StakeResult:
    """Return value of stake_and_acquire()."""
    skill: str
    bond_rtc: float
    success: bool
    refunded: bool
    verdict: str                        # "acquired" | "denied" | "error"
    attestation: Optional[dict] = None  # signed attestation when success=True
    error: Optional[str] = None
    node_url: str = NODE_URL
    timestamp: int = field(default_factory=lambda: int(time.time()))

    def to_dict(self) -> dict:
        return asdict(self)

    def __str__(self) -> str:
        if self.success:
            return (
                f"✅ Skill '{self.skill}' acquired | bond={self.bond_rtc} RTC | "
                f"attest={self.attestation.get('sig_hex', '?')[:16]}…"
            )
        if self.refunded:
            return (
                f"↩️  Gate unavailable for '{self.skill}' | "
                f"{self.bond_rtc} RTC refunded | reason: {self.error}"
            )
        return f"❌ Skill '{self.skill}' denied | reason: {self.error}"


# ── HTTP helpers ───────────────────────────────────────────────────────────────

def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=_RETRIES,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.verify = False  # self-signed node cert
    return s


def _get(path: str) -> dict:
    with _session() as s:
        r = s.get(f"{NODE_URL}{path}", timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()


def _post(path: str, payload: dict) -> dict:
    with _session() as s:
        r = s.post(
            f"{NODE_URL}{path}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()


# ── Attestation helpers ────────────────────────────────────────────────────────

def _build_attestation(skill: str, bond_rtc: float, epoch: int,
                        private_key_hex: Optional[str] = None) -> dict:
    """
    Build a signed attestation envelope for the skill-gate.

    When a real Ed25519 private key is supplied (via RUSTCHAIN_PRIVATE_KEY env
    or the private_key_hex argument) the signature is produced with the
    cryptography library.  Otherwise a deterministic HMAC-SHA256 stub is used
    (sufficient for local tests; not accepted by a live gate that requires a
    registered key).
    """
    ts = int(time.time())
    body = {
        "skill": skill,
        "bond_rtc": bond_rtc,
        "epoch": epoch,
        "timestamp": ts,
        "chain_id": CHAIN_ID,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    msg_bytes = canonical.encode()

    key_hex = private_key_hex or os.environ.get("RUSTCHAIN_PRIVATE_KEY", "")
    if key_hex and len(key_hex) == 64:
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            priv = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex))
            sig = priv.sign(msg_bytes)
            pub = priv.public_key()
            from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
            pub_bytes = pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
            sig_hex = sig.hex()
            pub_hex = pub_bytes.hex()
        except Exception:
            sig_hex = hashlib.sha256(msg_bytes).hexdigest()
            pub_hex = ""
    else:
        # Stub — HMAC-SHA256 for local / offline tests
        import hmac as _hmac
        sig_hex = _hmac.new(b"rustchain-stub", msg_bytes, hashlib.sha256).hexdigest()
        pub_hex = ""

    return {
        "body": body,
        "canonical": canonical,
        "sig_hex": sig_hex,
        "pub_hex": pub_hex,
        "algorithm": "ed25519" if pub_hex else "hmac-sha256-stub",
    }


def _verify_attestation(attestation: dict) -> bool:
    """Verify the attestation signature locally."""
    try:
        body = attestation["canonical"].encode()
        sig = bytes.fromhex(attestation["sig_hex"])
        pub_hex = attestation.get("pub_hex", "")
        if pub_hex:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
            pub.verify(sig, body)  # raises if invalid
            return True
        # Stub path
        import hmac as _hmac
        expected = _hmac.new(b"rustchain-stub", body, hashlib.sha256).hexdigest()
        return attestation["sig_hex"] == expected
    except Exception:
        return False


# ── Gate interaction ───────────────────────────────────────────────────────────

def _request_skill_verdict(skill: str, bond_rtc: float,
                           attestation: dict) -> tuple[bool, str]:
    """
    Call the node's skill-gate endpoint.

    Returns (acquired: bool, reason: str).

    The gate endpoint `/skill/gate` is defined in the bounty spec as the
    reference gate.  If the node does not expose it (404/connection error) the
    fail-safe triggers and we report gate_unavailable.
    """
    try:
        result = _post("/skill/gate", {
            "skill": skill,
            "bond_rtc": bond_rtc,
            "attestation": attestation,
        })
        acquired = result.get("acquired", False) or result.get("verdict") == "pass"
        reason = result.get("reason", "ok" if acquired else "denied")
        return acquired, reason
    except requests.exceptions.HTTPError as exc:
        code = exc.response.status_code if exc.response is not None else 0
        if code == 404:
            return False, f"gate_unavailable:404"
        if code >= 500:
            return False, f"gate_error:{code}"
        return False, f"http_error:{code}"
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as exc:
        return False, f"gate_unreachable:{exc}"
    except Exception as exc:
        return False, f"unexpected:{exc}"


# ── Public API ─────────────────────────────────────────────────────────────────

def stake_and_acquire(
    skill: str,
    bond_rtc: float,
    *,
    private_key_hex: Optional[str] = None,
) -> StakeResult:
    """
    Stake *bond_rtc* RTC and attempt to acquire *skill* from the reference gate.

    Fail-safe contract
    ──────────────────
    * Gate unavailable (connection error, 404, 5xx) → StakeResult.refunded=True
    * Gate denies the skill                          → StakeResult.refunded=True
    * Gate grants the skill                          → StakeResult.success=True, .refunded=False

    Args:
        skill:           Skill identifier, e.g. "rust_async", "zero_knowledge"
        bond_rtc:        Amount of RTC to bond (float, e.g. 1.0)
        private_key_hex: 64-char hex Ed25519 private key. Falls back to
                         RUSTCHAIN_PRIVATE_KEY env var, then HMAC stub.

    Returns:
        StakeResult dataclass (JSON-serialisable via .to_dict())
    """
    if bond_rtc <= 0:
        return StakeResult(
            skill=skill, bond_rtc=bond_rtc,
            success=False, refunded=True,
            verdict="error",
            error="bond_rtc must be > 0",
        )

    # 1. Fetch current epoch (network liveness check)
    try:
        epoch_data = _get("/epoch")
        epoch = epoch_data.get("epoch", 0)
    except Exception as exc:
        return StakeResult(
            skill=skill, bond_rtc=bond_rtc,
            success=False, refunded=True,
            verdict="error",
            error=f"node_unreachable: {exc}",
        )

    # 2. Build + sign attestation
    attestation = _build_attestation(skill, bond_rtc, epoch, private_key_hex)

    # 3. Verify attestation locally before sending
    if not _verify_attestation(attestation):
        return StakeResult(
            skill=skill, bond_rtc=bond_rtc,
            success=False, refunded=True,
            verdict="error",
            error="local_attestation_verification_failed",
            attestation=attestation,
        )

    # 4. Submit to skill gate
    acquired, reason = _request_skill_verdict(skill, bond_rtc, attestation)

    # 5. Determine fail-safe outcome
    gate_unavailable = any(
        reason.startswith(prefix)
        for prefix in ("gate_unavailable", "gate_error", "gate_unreachable")
    )

    if gate_unavailable:
        # Stake is logically returned — no debit has occurred since
        # the gate never confirmed the bond.
        return StakeResult(
            skill=skill, bond_rtc=bond_rtc,
            success=False, refunded=True,
            verdict="error",
            error=reason,
            attestation=attestation,
        )

    if not acquired:
        return StakeResult(
            skill=skill, bond_rtc=bond_rtc,
            success=False, refunded=True,
            verdict="denied",
            error=reason,
            attestation=attestation,
        )

    # 6. Success path — double-check attestation validity
    valid = _verify_attestation(attestation)
    return StakeResult(
        skill=skill, bond_rtc=bond_rtc,
        success=valid, refunded=not valid,
        verdict="acquired" if valid else "error",
        attestation=attestation,
        error=None if valid else "post_gate_attestation_invalid",
    )
