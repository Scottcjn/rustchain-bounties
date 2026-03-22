"""
rustchain.client
~~~~~~~~~~~~~~~~

Async and sync HTTP clients for the RustChain node API.

Usage (sync)::

    client = RustChainClient("https://50.28.86.131")
    print(client.health())
    client.close()

Usage (async)::

    async with AsyncRustChainClient("https://50.28.86.131") as client:
        print(await client.health())
"""

from __future__ import annotations

import ssl
from typing import Any, Dict, List, Optional

import httpx

from rustchain.errors import (
    RustChainAPIError,
    RustChainAuthError,
    RustChainConnectionError,
    RustChainTimeoutError,
    RustChainValidationError,
)
from rustchain.explorer import AsyncExplorerAPI, ExplorerAPI
from rustchain.models import (
    AttestationStatus,
    Balance,
    Block,
    EpochInfo,
    HealthStatus,
    Miner,
    TransferResult,
    Transaction,
)


# Default timeout in seconds
_DEFAULT_TIMEOUT = 30.0

# Headers sent on every request
_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "rustchain-python-sdk/1.0.0",
}


def _make_ssl_context() -> ssl.SSLContext:
    """Create an SSL context that tolerates self-signed node certs."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _normalise_url(url: str) -> str:
    """Strip trailing slashes and ensure a scheme."""
    url = url.rstrip("/")
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


# ===================================================================
# Async Client
# ===================================================================


class AsyncRustChainClient:
    """Async (httpx) client for the RustChain node API.

    Parameters:
        base_url: Node URL, e.g. ``"https://50.28.86.131"``.
        timeout: Request timeout in seconds (default 30).
        api_key: Optional API key for authenticated endpoints.
        verify_ssl: Whether to verify TLS certificates (default False
            because many RustChain nodes use self-signed certs).
        headers: Additional HTTP headers.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        api_key: Optional[str] = None,
        verify_ssl: bool = False,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._base_url = _normalise_url(base_url)
        self._timeout = timeout
        self._api_key = api_key

        merged_headers = {**_DEFAULT_HEADERS, **(headers or {})}
        if api_key:
            merged_headers["Authorization"] = f"Bearer {api_key}"

        verify: Any = _make_ssl_context() if not verify_ssl else True
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=merged_headers,
            verify=verify,
        )
        self.explorer = AsyncExplorerAPI(self._http, self._base_url)

    # -- lifecycle --

    async def __aenter__(self) -> "AsyncRustChainClient":
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    # -- internal helpers --

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        try:
            resp = await self._http.request(method, url, params=params, json=json)
        except httpx.ConnectError as exc:
            raise RustChainConnectionError(
                f"Cannot connect to RustChain node at {self._base_url}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise RustChainTimeoutError(
                f"Request to {url} timed out after {self._timeout}s"
            ) from exc

        if resp.status_code in (401, 403):
            raise RustChainAuthError(
                message=f"Auth error {resp.status_code}: {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        if resp.status_code >= 400:
            raise RustChainAPIError(
                message=f"API error {resp.status_code}: {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        if resp.status_code == 204:
            return {}
        return resp.json()

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("GET", path, params=params)

    async def _post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return await self._request("POST", path, json=json)

    # -- public API --

    async def health(self) -> HealthStatus:
        """Check node health.

        Returns:
            :class:`HealthStatus` with node version, uptime, block height, etc.
        """
        data = await self._get("/health")
        return HealthStatus.from_dict(data)

    async def epoch(self) -> EpochInfo:
        """Get current epoch information.

        Returns:
            :class:`EpochInfo` with epoch number, progress, difficulty, etc.
        """
        data = await self._get("/epoch")
        return EpochInfo.from_dict(data)

    async def miners(self, limit: int = 50, offset: int = 0) -> List[Miner]:
        """List active miners.

        Args:
            limit: Maximum miners to return (default 50).
            offset: Pagination offset.

        Returns:
            List of :class:`Miner` objects.
        """
        data = await self._get("/api/miners", params={"limit": limit, "offset": offset})
        raw = data if isinstance(data, list) else data.get("miners", data.get("data", []))
        return [Miner.from_dict(m) for m in raw]

    async def balance(self, wallet_id: str) -> Balance:
        """Check RTC balance for a wallet.

        Args:
            wallet_id: The wallet address / ID to query.

        Returns:
            :class:`Balance` with available, locked, and pending amounts.

        Raises:
            RustChainValidationError: If ``wallet_id`` is empty.
        """
        if not wallet_id or not wallet_id.strip():
            raise RustChainValidationError("wallet_id", "wallet_id must not be empty")
        data = await self._get(f"/api/wallets/{wallet_id}/balance")
        return Balance.from_dict(data, wallet_id=wallet_id)

    async def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: float,
        signature: str,
    ) -> TransferResult:
        """Execute a signed RTC transfer.

        Args:
            from_wallet: Sender wallet ID.
            to_wallet: Recipient wallet ID.
            amount: Amount of RTC to transfer (must be > 0).
            signature: Cryptographic signature authorizing the transfer.

        Returns:
            :class:`TransferResult` with tx hash, status, and fee.

        Raises:
            RustChainValidationError: If any argument is invalid.
        """
        if not from_wallet or not from_wallet.strip():
            raise RustChainValidationError("from_wallet", "from_wallet must not be empty")
        if not to_wallet or not to_wallet.strip():
            raise RustChainValidationError("to_wallet", "to_wallet must not be empty")
        if amount <= 0:
            raise RustChainValidationError("amount", "amount must be positive")
        if not signature or not signature.strip():
            raise RustChainValidationError("signature", "signature must not be empty")

        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": signature,
        }
        data = await self._post("/api/transfers", json=payload)
        return TransferResult.from_dict(data)

    async def attestation_status(self, miner_id: str) -> AttestationStatus:
        """Check Proof-of-Antiquity attestation status for a miner.

        Args:
            miner_id: The miner's ID.

        Returns:
            :class:`AttestationStatus` with validity, score, and hardware info.

        Raises:
            RustChainValidationError: If ``miner_id`` is empty.
        """
        if not miner_id or not miner_id.strip():
            raise RustChainValidationError("miner_id", "miner_id must not be empty")
        data = await self._get(f"/api/miners/{miner_id}/attestation")
        return AttestationStatus.from_dict(data, miner_id=miner_id)

    # -- convenience methods --

    async def node_info(self) -> Dict[str, Any]:
        """Return raw node info (version, network, capabilities)."""
        return await self._get("/api/info")

    async def peers(self) -> List[Dict[str, Any]]:
        """List connected peers."""
        data = await self._get("/api/peers")
        return data if isinstance(data, list) else data.get("peers", [])


# ===================================================================
# Sync Client
# ===================================================================


class RustChainClient:
    """Synchronous client for the RustChain node API.

    Same interface as :class:`AsyncRustChainClient` but using blocking I/O.

    Parameters:
        base_url: Node URL, e.g. ``"https://50.28.86.131"``.
        timeout: Request timeout in seconds (default 30).
        api_key: Optional API key for authenticated endpoints.
        verify_ssl: Whether to verify TLS certificates (default False).
        headers: Additional HTTP headers.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = _DEFAULT_TIMEOUT,
        api_key: Optional[str] = None,
        verify_ssl: bool = False,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self._base_url = _normalise_url(base_url)
        self._timeout = timeout
        self._api_key = api_key

        merged_headers = {**_DEFAULT_HEADERS, **(headers or {})}
        if api_key:
            merged_headers["Authorization"] = f"Bearer {api_key}"

        verify: Any = _make_ssl_context() if not verify_ssl else True
        self._http = httpx.Client(
            timeout=httpx.Timeout(timeout),
            headers=merged_headers,
            verify=verify,
        )
        self.explorer = ExplorerAPI(self._http, self._base_url)

    # -- lifecycle --

    def __enter__(self) -> "RustChainClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    # -- internal helpers --

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        try:
            resp = self._http.request(method, url, params=params, json=json)
        except httpx.ConnectError as exc:
            raise RustChainConnectionError(
                f"Cannot connect to RustChain node at {self._base_url}"
            ) from exc
        except httpx.TimeoutException as exc:
            raise RustChainTimeoutError(
                f"Request to {url} timed out after {self._timeout}s"
            ) from exc

        if resp.status_code in (401, 403):
            raise RustChainAuthError(
                message=f"Auth error {resp.status_code}: {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        if resp.status_code >= 400:
            raise RustChainAPIError(
                message=f"API error {resp.status_code}: {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        if resp.status_code == 204:
            return {}
        return resp.json()

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("GET", path, params=params)

    def _post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Any:
        return self._request("POST", path, json=json)

    # -- public API (mirrors async client) --

    def health(self) -> HealthStatus:
        """Check node health. See :meth:`AsyncRustChainClient.health`."""
        data = self._get("/health")
        return HealthStatus.from_dict(data)

    def epoch(self) -> EpochInfo:
        """Get current epoch information. See :meth:`AsyncRustChainClient.epoch`."""
        data = self._get("/epoch")
        return EpochInfo.from_dict(data)

    def miners(self, limit: int = 50, offset: int = 0) -> List[Miner]:
        """List active miners. See :meth:`AsyncRustChainClient.miners`."""
        data = self._get("/api/miners", params={"limit": limit, "offset": offset})
        raw = data if isinstance(data, list) else data.get("miners", data.get("data", []))
        return [Miner.from_dict(m) for m in raw]

    def balance(self, wallet_id: str) -> Balance:
        """Check RTC balance. See :meth:`AsyncRustChainClient.balance`."""
        if not wallet_id or not wallet_id.strip():
            raise RustChainValidationError("wallet_id", "wallet_id must not be empty")
        data = self._get(f"/api/wallets/{wallet_id}/balance")
        return Balance.from_dict(data, wallet_id=wallet_id)

    def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: float,
        signature: str,
    ) -> TransferResult:
        """Execute a signed RTC transfer. See :meth:`AsyncRustChainClient.transfer`."""
        if not from_wallet or not from_wallet.strip():
            raise RustChainValidationError("from_wallet", "from_wallet must not be empty")
        if not to_wallet or not to_wallet.strip():
            raise RustChainValidationError("to_wallet", "to_wallet must not be empty")
        if amount <= 0:
            raise RustChainValidationError("amount", "amount must be positive")
        if not signature or not signature.strip():
            raise RustChainValidationError("signature", "signature must not be empty")

        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": signature,
        }
        data = self._post("/api/transfers", json=payload)
        return TransferResult.from_dict(data)

    def attestation_status(self, miner_id: str) -> AttestationStatus:
        """Check attestation status. See :meth:`AsyncRustChainClient.attestation_status`."""
        if not miner_id or not miner_id.strip():
            raise RustChainValidationError("miner_id", "miner_id must not be empty")
        data = self._get(f"/api/miners/{miner_id}/attestation")
        return AttestationStatus.from_dict(data, miner_id=miner_id)

    def node_info(self) -> Dict[str, Any]:
        """Return raw node info. See :meth:`AsyncRustChainClient.node_info`."""
        return self._get("/api/info")

    def peers(self) -> List[Dict[str, Any]]:
        """List connected peers. See :meth:`AsyncRustChainClient.peers`."""
        data = self._get("/api/peers")
        return data if isinstance(data, list) else data.get("peers", [])
