"""
rustchain.explorer
~~~~~~~~~~~~~~~~~~

Block explorer API wrapper providing access to recent blocks and
transactions on the RustChain network.

These classes are not typically instantiated directly — they are
available as ``client.explorer`` on both sync and async clients.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

from rustchain.errors import RustChainAPIError, RustChainConnectionError, RustChainTimeoutError
from rustchain.models import Block, Transaction


class AsyncExplorerAPI:
    """Async block explorer — used internally by :class:`AsyncRustChainClient`.

    Parameters:
        http: An ``httpx.AsyncClient`` managed by the parent client.
        base_url: RustChain node base URL.
    """

    def __init__(self, http: "httpx.AsyncClient", base_url: str) -> None:
        self._http = http
        self._base_url = base_url.rstrip("/")

    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Issue a GET request and return the parsed JSON body."""
        import httpx as _httpx

        url = f"{self._base_url}{path}"
        try:
            resp = await self._http.get(url, params=params)
        except _httpx.ConnectError as exc:
            raise RustChainConnectionError(f"Cannot reach {url}") from exc
        except _httpx.TimeoutException as exc:
            raise RustChainTimeoutError(f"Timeout fetching {url}") from exc

        if resp.status_code >= 400:
            raise RustChainAPIError(
                f"Explorer API error: {resp.status_code}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()

    async def blocks(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Block]:
        """Fetch recent blocks from the explorer.

        Args:
            limit: Maximum number of blocks to return (default 10).
            offset: Pagination offset.

        Returns:
            List of :class:`Block` objects, most-recent first.
        """
        data = await self._get(
            "/api/explorer/blocks",
            params={"limit": limit, "offset": offset},
        )
        raw_blocks = data if isinstance(data, list) else data.get("blocks", data.get("data", []))
        return [Block.from_dict(b) for b in raw_blocks]

    async def block(self, height_or_hash: int | str) -> Block:
        """Fetch a single block by height (int) or hash (str)."""
        path = f"/api/explorer/blocks/{height_or_hash}"
        data = await self._get(path)
        payload = data if "height" in data or "hash" in data else data.get("block", data)
        return Block.from_dict(payload)

    async def transactions(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Transaction]:
        """Fetch recent transactions from the explorer.

        Args:
            limit: Maximum number of transactions to return (default 10).
            offset: Pagination offset.

        Returns:
            List of :class:`Transaction` objects, most-recent first.
        """
        data = await self._get(
            "/api/explorer/transactions",
            params={"limit": limit, "offset": offset},
        )
        raw_txs = data if isinstance(data, list) else data.get("transactions", data.get("data", []))
        return [Transaction.from_dict(t) for t in raw_txs]

    async def transaction(self, tx_hash: str) -> Transaction:
        """Fetch a single transaction by its hash."""
        data = await self._get(f"/api/explorer/transactions/{tx_hash}")
        payload = data if "tx_hash" in data or "hash" in data else data.get("transaction", data)
        return Transaction.from_dict(payload)

    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Full-text search across blocks, transactions, and wallets."""
        data = await self._get("/api/explorer/search", params={"q": query})
        return data if isinstance(data, list) else data.get("results", [])


class ExplorerAPI:
    """Synchronous block explorer — used internally by :class:`RustChainClient`.

    Wraps :class:`AsyncExplorerAPI` via ``httpx.Client`` (sync).
    """

    def __init__(self, http: "httpx.Client", base_url: str) -> None:
        self._http = http
        self._base_url = base_url.rstrip("/")

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        import httpx as _httpx

        url = f"{self._base_url}{path}"
        try:
            resp = self._http.get(url, params=params)
        except _httpx.ConnectError as exc:
            raise RustChainConnectionError(f"Cannot reach {url}") from exc
        except _httpx.TimeoutException as exc:
            raise RustChainTimeoutError(f"Timeout fetching {url}") from exc

        if resp.status_code >= 400:
            raise RustChainAPIError(
                f"Explorer API error: {resp.status_code}",
                status_code=resp.status_code,
                response_body=resp.text,
            )
        return resp.json()

    def blocks(self, limit: int = 10, offset: int = 0) -> List[Block]:
        """Fetch recent blocks. See :meth:`AsyncExplorerAPI.blocks`."""
        data = self._get(
            "/api/explorer/blocks",
            params={"limit": limit, "offset": offset},
        )
        raw_blocks = data if isinstance(data, list) else data.get("blocks", data.get("data", []))
        return [Block.from_dict(b) for b in raw_blocks]

    def block(self, height_or_hash: int | str) -> Block:
        """Fetch a single block by height or hash."""
        path = f"/api/explorer/blocks/{height_or_hash}"
        data = self._get(path)
        payload = data if "height" in data or "hash" in data else data.get("block", data)
        return Block.from_dict(payload)

    def transactions(self, limit: int = 10, offset: int = 0) -> List[Transaction]:
        """Fetch recent transactions. See :meth:`AsyncExplorerAPI.transactions`."""
        data = self._get(
            "/api/explorer/transactions",
            params={"limit": limit, "offset": offset},
        )
        raw_txs = data if isinstance(data, list) else data.get("transactions", data.get("data", []))
        return [Transaction.from_dict(t) for t in raw_txs]

    def transaction(self, tx_hash: str) -> Transaction:
        """Fetch a single transaction by hash."""
        data = self._get(f"/api/explorer/transactions/{tx_hash}")
        payload = data if "tx_hash" in data or "hash" in data else data.get("transaction", data)
        return Transaction.from_dict(payload)

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Full-text search across blocks, transactions, and wallets."""
        data = self._get("/api/explorer/search", params={"q": query})
        return data if isinstance(data, list) else data.get("results", [])
