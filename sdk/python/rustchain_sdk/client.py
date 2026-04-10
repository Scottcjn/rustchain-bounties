"""
RustChain Python SDK — Core Client
==================================
"""

import json
import time
import http.client
import ssl
from typing import Optional, Any
from urllib.parse import urlencode

__all__ = ["RustChain"]


class RustChainError(Exception):
    """Base exception for RustChain SDK errors."""
    pass


class NodeOfflineError(RustChainError):
    """Raised when the RustChain node is unreachable."""
    pass


class APIError(RustChainError):
    """Raised when the API returns an error response."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


def _json_default(o):
    """JSON serializer for objects not serializable by default."""
    if hasattr(o, "__dict__"):
        return o.__dict__
    raise TypeError(f"Object of type {type(o)} is not JSON serializable")


class RustChain:
    """
    Python client for RustChain node API.

    Args:
        node_url: URL of the RustChain node (default: https://50.28.86.131)
        timeout: Request timeout in seconds (default: 10)
        insecure: Allow self-signed certificates (default: True for self-signed nodes)

    Example:
        >>> from rustchain import RustChain
        >>> rc = RustChain()
        >>> health = rc.health()
        >>> balance = rc.get_balance("my-wallet")
    """

    def __init__(
        self,
        node_url: str = "https://50.28.86.131",
        timeout: int = 10,
        insecure: bool = True,
    ):
        self.node_url = node_url.rstrip("/")
        self.timeout = timeout
        self.insecure = insecure
        self._ctx: Optional[ssl.SSLContext] = None
        if insecure:
            self._ctx = ssl.create_default_context()
            self._ctx.check_hostname = False
            self._ctx.verify_mode = ssl.CERT_NONE

    # ── HTTP Client ────────────────────────────────────────────────────────
    def _request(self, method: str, path: str, body: Optional[dict] = None) -> dict:
        """Make an HTTP request to the RustChain node."""
        url = self.node_url.replace("https://", "").replace("http://", "")
        parts = url.split("/", 1)
        host = parts[0]
        base_path = "/" + parts[1] if len(parts) > 1 else ""
        full_path = base_path + "/" + path.lstrip("/")

        try:
            if self.node_url.startswith("https"):
                conn = http.client.HTTPSConnection(host, timeout=self.timeout, context=self._ctx)
            else:
                conn = http.client.HTTPConnection(host, timeout=self.timeout)

            headers = {"Accept": "application/json", "User-Agent": "rustchain-sdk/0.1.0"}
            if body:
                headers["Content-Type"] = "application/json"
                body_bytes = json.dumps(body).encode()
            else:
                body_bytes = None

            conn.request(method, full_path, headers=headers, body=body_bytes)
            resp = conn.getresponse()
            data = resp.read().decode("utf-8", errors="replace")
            conn.close()

            if resp.status >= 400:
                raise APIError(f"API error {resp.status}: {data[:200]}", resp.status)

            if not data.strip():
                return {}
            return json.loads(data)

        except http.client.HTTPException as e:
            raise NodeOfflineError(f"Failed to connect to node: {e}") from e
        except json.JSONDecodeError as e:
            raise RustChainError(f"Invalid JSON response: {e}\n{data[:200]}") from e

    def get(self, path: str) -> dict:
        """Make a GET request."""
        return self._request("GET", path)

    def post(self, path: str, body: Optional[dict] = None) -> dict:
        """Make a POST request."""
        return self._request("POST", path, body)

    # ── Node Health ────────────────────────────────────────────────────────
    def health(self) -> dict:
        """
        Check node health.

        Returns:
            {
                "ok": bool,
                "version": str,
                "uptime_s": int,
                "db_rw": bool,
                "backup_age_hours": float,
                "tip_age_slots": int
            }

        Raises:
            NodeOfflineError: If the node is unreachable.

        Example:
            >>> rc.health()
            {'ok': True, 'version': '2.2.1-rip200', 'uptime_s': 212580, ...}
        """
        return self.get("/health")

    def is_online(self) -> bool:
        """Check if the node is online."""
        try:
            return self.health().get("ok", False)
        except NodeOfflineError:
            return False

    # ── Wallet ────────────────────────────────────────────────────────────
    def get_balance(self, wallet: str) -> dict:
        """
        Get the RTC balance of a wallet.

        Args:
            wallet: Wallet name (e.g. "nox-ventures")

        Returns:
            {"balance": float, "address": str, ...}

        Example:
            >>> rc.get_balance("nox-ventures")
            {'balance': 42.5, 'address': 'nox-ventures'}
        """
        return self.get(f"/wallet/balance?wallet_id={wallet}")

    def create_wallet(self, name: str) -> dict:
        """
        Register a new wallet on the network.

        Args:
            name: Desired wallet name

        Returns:
            {"wallet": str, "created": bool, ...}
        """
        return self.post("/wallet/create", {"name": name})

    # ── Miners ─────────────────────────────────────────────────────────────
    def get_miners(self, limit: Optional[int] = None) -> dict:
        """
        List all active miners.

        Args:
            limit: Maximum number of miners to return (default: all)

        Returns:
            {"miners": [...], "pagination": {...}}

        Example:
            >>> data = rc.get_miners()
            >>> for m in data["miners"][:5]:
            ...     print(m["miner"], m["antiquity_multiplier"])
        """
        path = "/api/miners"
        if limit:
            path += f"?limit={limit}"
        return self.get(path)

    def get_miner(self, miner_id: str) -> Optional[dict]:
        """Get a specific miner by ID."""
        data = self.get_miners()
        for m in data.get("miners", []):
            if m.get("miner") == miner_id:
                return m
        return None

    def is_miner_active(self, miner_id: str) -> bool:
        """Check if a miner is currently active and attesting."""
        miner = self.get_miner(miner_id)
        return bool(miner and miner.get("is_active"))

    # ── Epoch ──────────────────────────────────────────────────────────────
    def get_epoch(self) -> dict:
        """
        Get current epoch information.

        Returns:
            {
                "current_epoch": int,
                "slots_elapsed": int,
                "slots_remaining": int,
                "time_to_next": str (e.g. "3h 21m")
            }
        """
        health = self.health()
        uptime_s = health.get("uptime_s", 0)
        EPOCH_LENGTH = 2016
        SLOT_TIME_S = 15
        slots_elapsed = uptime_s / SLOT_TIME_S
        epoch = int(slots_elapsed / EPOCH_LENGTH)
        slot_in = int(slots_elapsed % EPOCH_LENGTH)
        remaining = EPOCH_LENGTH - slot_in
        remaining_s = remaining * SLOT_TIME_S
        h = int(remaining_s // 3600)
        m = int((remaining_s % 3600) // 60)
        return {
            "current_epoch": epoch,
            "slots_elapsed": slot_in,
            "slots_remaining": remaining,
            "slots_total": EPOCH_LENGTH,
            "time_to_next_epoch": f"{h}h {m}m" if h > 0 else f"{m}m",
            "uptime_seconds": uptime_s,
            "version": health.get("version"),
        }

    # ── Attestation ────────────────────────────────────────────────────────
    def submit_attestation(
        self,
        wallet: str,
        hardware_fingerprint: str,
        signature: str,
    ) -> dict:
        """
        Submit a hardware attestation for a wallet.

        Args:
            wallet: Wallet name
            hardware_fingerprint: Device fingerprint string
            signature: Cryptographic signature

        Returns:
            {"success": bool, "attestation_id": str, ...}
        """
        return self.post("/api/attest", {
            "wallet": wallet,
            "hardware_fingerprint": hardware_fingerprint,
            "signature": signature,
        })

    # ── Transfer ───────────────────────────────────────────────────────────
    def transfer(self, from_wallet: str, to_wallet: str, amount: float) -> dict:
        """
        Transfer RTC between wallets.

        Args:
            from_wallet: Sender wallet name
            to_wallet: Recipient wallet name
            amount: Amount in RTC

        Returns:
            {"success": bool, "tx_id": str, ...}
        """
        return self.post("/api/transfer", {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
        })

    # ── Network Stats ──────────────────────────────────────────────────────
    def network_stats(self) -> dict:
        """
        Get overall network statistics.

        Returns:
            {
                "node": {...health},
                "network": {
                    "active_miners": int,
                    "current_epoch": int,
                    "total_rtc": float
                }
            }
        """
        health = self.health()
        miners_data = self.get_miners()
        miners = miners_data.get("miners", [])
        epoch_info = self.get_epoch()
        active = sum(1 for m in miners if m.get("is_active"))
        return {
            "node": {
                "url": self.node_url,
                "online": health.get("ok", False),
                "version": health.get("version"),
                "uptime_hours": round(health.get("uptime_s", 0) / 3600, 1),
            },
            "network": {
                "active_miners": active,
                "total_miners": len(miners),
                "current_epoch": epoch_info["current_epoch"],
                "slots_remaining": epoch_info["slots_remaining"],
                "time_to_next_epoch": epoch_info["time_to_next_epoch"],
            },
        }

    # ── Lottery ───────────────────────────────────────────────────────────
    def lottery_eligibility(self, wallet: str) -> dict:
        """
        Check if a wallet is eligible for the epoch lottery.

        Args:
            wallet: Wallet name

        Returns:
            {"eligible": bool, "tickets": int, "wallet": str}
        """
        return self.get(f"/api/lottery?wallet_id={wallet}")

    # ── Retry wrapper ──────────────────────────────────────────────────────
    def get_with_retry(self, path: str, retries: int = 3, delay: float = 1.0) -> dict:
        """
        Make a GET request with automatic retry on failure.

        Args:
            path: API path
            retries: Number of retries (default: 3)
            delay: Delay between retries in seconds (default: 1.0)

        Returns:
            API response dict
        """
        last_error = None
        for attempt in range(retries):
            try:
                return self.get(path)
            except (NodeOfflineError, APIError) as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(delay * (attempt + 1))
        raise last_error or RustChainError("All retries failed")
