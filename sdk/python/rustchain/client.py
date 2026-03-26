"""
RustChain Core Client
Async/sync HTTP client for the RustChain blockchain API.
"""

import asyncio
import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from .exceptions import APIError, AuthenticationError, NetworkError, ValidationError


class RustChainClient:
    """
    Main client for interacting with the RustChain blockchain.

    Supports both sync and async usage:

        # Sync
        client = RustChainClient()
        health = client.health()

        # Async
        client = RustChainClient()
        health = await client.health_async()
        miners = await client.miners_async()

    Args:
        base_url: Base URL of the RustChain node (default: https://50.28.86.131)
        api_key: Optional API key for authenticated endpoints.
        timeout: Request timeout in seconds (default: 30).
        retry_count: Number of retries on transient failure (default: 3).
        verify_ssl: Whether to verify SSL certificates (default: True for safety;
            automatically disabled if the node uses a self-signed cert).
    """

    DEFAULT_BASE_URL = "https://50.28.86.131"

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
        retry_count: int = 3,
        verify_ssl: bool = True,
    ) -> None:
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.retry_count = retry_count
        self.verify_ssl = verify_ssl

        self._ctx: Optional[ssl.SSLContext] = None
        if not verify_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self._ctx = ctx

    # ------------------------------------------------------------------
    # Sync HTTP helpers
    # ------------------------------------------------------------------

    def _build_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> urllib.request.Request:
        url = f"{self.base_url}{endpoint}"
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = json.dumps(data).encode("utf-8") if data else None
        return urllib.request.Request(url, data=body, headers=headers, method=method)

    def _do_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        req = self._build_request(method, endpoint, data)

        last_err: Exception = Exception("unknown")
        for attempt in range(self.retry_count):
            try:
                with urllib.request.urlopen(
                    req, context=self._ctx, timeout=self.timeout
                ) as resp:
                    text = resp.read().decode("utf-8")
                    if not text:
                        return {}
                    return json.loads(text)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="replace")
                if e.code in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed: {e.reason}"
                    )
                if attempt == self.retry_count - 1:
                    raise APIError(
                        f"HTTP {e.code}: {e.reason}",
                        status_code=e.code,
                        response_body=self._maybe_json(body),
                    )
            except urllib.error.URLError as e:
                if attempt == self.retry_count - 1:
                    raise NetworkError(f"Connection failed: {e.reason}")
            except Exception as e:
                last_err = e
                if attempt == self.retry_count - 1:
                    raise APIError(str(last_err))

            if attempt < self.retry_count - 1:
                time.sleep(1.0 * (attempt + 1))

        raise APIError(str(last_err))

    @staticmethod
    def _maybe_json(text: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(text)
        except Exception:
            return None

    def _get(self, endpoint: str) -> Dict[str, Any]:
        return self._do_request("GET", endpoint)

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return self._do_request("POST", endpoint, data)

    # ------------------------------------------------------------------
    # Async HTTP helpers
    # ------------------------------------------------------------------

    async def _do_request_async(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        import aiohttp

        url = f"{self.base_url}{endpoint}"
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        ssl_ctx = self._ctx if not self.verify_ssl else None
        timeout = aiohttp.ClientTimeout(total=self.timeout)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(
                method, url, json=data, headers=headers, ssl=ssl_ctx
            ) as resp:
                if resp.status in (401, 403):
                    raise AuthenticationError(
                        f"Authentication failed: {resp.reason}"
                    )
                if resp.status >= 400:
                    body = await resp.text()
                    raise APIError(
                        f"HTTP {resp.status}: {resp.reason}",
                        status_code=resp.status,
                        response_body=self._maybe_json(body),
                    )
                text = await resp.text()
                if not text:
                    return {}
                return json.loads(text)

    # ------------------------------------------------------------------
    # Public API — sync
    # ------------------------------------------------------------------

    def health(self) -> Dict[str, Any]:
        """
        Check node health status.

        Returns:
            Dict with keys: ok (bool), version (str), uptime_s (int), ...

        Raises:
            APIError: If the node is unhealthy.
            NetworkError: If the node cannot be reached.
        """
        return self._get("/health")

    def epoch(self) -> Dict[str, Any]:
        """
        Get current epoch information.

        Returns:
            Dict with keys: epoch (int), blocks_per_epoch (int),
            epoch_pot (float), slot (int), ...
        """
        return self._get("/epoch")

    def miners(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List active miners on the network.

        Args:
            limit: Maximum number of miners to return.
            offset: Number of miners to skip (pagination).

        Returns:
            List of miner dicts with keys: miner, antiquity_multiplier,
            device_arch, device_family, hardware_type, last_attest, ...
        """
        params: List[str] = []
        if limit is not None:
            params.append(f"limit={limit}")
        if offset is not None:
            params.append(f"offset={offset}")
        query = ("?" + "&".join(params)) if params else ""
        return self._get(f"/api/miners{query}")

    def balance(self, wallet_id: str) -> Dict[str, Any]:
        """
        Check the RTC balance for a wallet.

        Args:
            wallet_id: Wallet ID or address.

        Returns:
            Dict with keys: balance (float), wallet_id (str), ...

        Raises:
            ValidationError: If wallet_id is empty.
        """
        if not wallet_id or not wallet_id.strip():
            raise ValidationError("wallet_id must be non-empty")
        return self._get(f"/wallet/balance?miner_id={wallet_id.strip()}")

    def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: float,
        signature: str,
    ) -> Dict[str, Any]:
        """
        Submit a signed RTC transfer.

        Args:
            from_wallet: Source wallet ID.
            to_wallet: Destination wallet ID.
            amount: Amount of RTC to transfer.
            signature: Ed25519 signature of the transfer payload.

        Returns:
            Dict with keys: success (bool), tx_hash (str), ...

        Raises:
            ValidationError: If parameters are invalid.
            TransferError: If the transfer is rejected.
        """
        if not from_wallet or not to_wallet:
            raise ValidationError("from_wallet and to_wallet must be non-empty")
        if amount <= 0:
            raise ValidationError("amount must be positive")
        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": signature,
        }
        return self._post("/wallet/transfer/signed", payload)

    def attestation_status(self, miner_id: str) -> Dict[str, Any]:
        """
        Check the attestation status for a miner.

        Args:
            miner_id: The miner ID to check.

        Returns:
            Dict with keys: miner_id, last_attest (str),
            consecutive_days (int), eligible (bool), ...

        Raises:
            ValidationError: If miner_id is empty.
        """
        if not miner_id or not miner_id.strip():
            raise ValidationError("miner_id must be non-empty")
        return self._get(f"/attest/status?miner_id={miner_id.strip()}")

    def lottery_eligibility(self, miner_id: str) -> Dict[str, Any]:
        """
        Check lottery eligibility for a miner.

        Args:
            miner_id: Miner wallet ID.

        Returns:
            Dict with keys: eligible (bool), slot (int),
            slot_producer (str), rotation_size (int), ...
        """
        return self._get(f"/lottery/eligibility?miner_id={miner_id}")

    def submit_attestation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit an attestation to the network.

        Args:
            payload: Attestation payload dict (miner_id, signature, ...).

        Returns:
            Dict with keys: success (bool), tx_hash (str), ...
        """
        return self._post("/attest/submit", payload)

    def stats(self) -> Dict[str, Any]:
        """
        Get network-wide statistics.

        Returns:
            Dict with aggregate stats (total miners, total stake, ...).
        """
        return self._get("/stats")

    # ------------------------------------------------------------------
    # Public API — async
    # ------------------------------------------------------------------

    async def health_async(self) -> Dict[str, Any]:
        """Async version of :meth:`health`."""
        return await self._do_request_async("GET", "/health")

    async def epoch_async(self) -> Dict[str, Any]:
        """Async version of :meth:`epoch`."""
        return await self._do_request_async("GET", "/epoch")

    async def miners_async(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Async version of :meth:`miners`."""
        params: List[str] = []
        if limit is not None:
            params.append(f"limit={limit}")
        if offset is not None:
            params.append(f"offset={offset}")
        query = ("?" + "&".join(params)) if params else ""
        return await self._do_request_async("GET", f"/api/miners{query}")

    async def balance_async(self, wallet_id: str) -> Dict[str, Any]:
        """Async version of :meth:`balance`."""
        return await self._do_request_async(
            "GET", f"/wallet/balance?miner_id={wallet_id.strip()}"
        )

    async def transfer_async(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: float,
        signature: str,
    ) -> Dict[str, Any]:
        """Async version of :meth:`transfer`."""
        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": signature,
        }
        return await self._do_request_async("POST", "/wallet/transfer/signed", payload)

    async def attestation_status_async(self, miner_id: str) -> Dict[str, Any]:
        """Async version of :meth:`attestation_status`."""
        return await self._do_request_async(
            "GET", f"/attest/status?miner_id={miner_id.strip()}"
        )

    async def lottery_eligibility_async(self, miner_id: str) -> Dict[str, Any]:
        """Async version of :meth:`lottery_eligibility`."""
        return await self._do_request_async(
            "GET", f"/lottery/eligibility?miner_id={miner_id}"
        )

    async def submit_attestation_async(
        self, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Async version of :meth:`submit_attestation`."""
        return await self._do_request_async("POST", "/attest/submit", payload)

    async def stats_async(self) -> Dict[str, Any]:
        """Async version of :meth:`stats`."""
        return await self._do_request_async("GET", "/stats")

    # ------------------------------------------------------------------
    # Convenience factory
    # ------------------------------------------------------------------

    @classmethod
    def create(cls, **kwargs: Any) -> "RustChainClient":
        """Alias for ``RustChainClient(**kwargs)``."""
        return cls(**kwargs)
