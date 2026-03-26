"""
RustChain Block Explorer Client
Provides access to the block explorer API (recent blocks, transactions, etc.).
"""

import json
import ssl
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from .exceptions import APIError, NetworkError


class ExplorerClient:
    """
    Client for the RustChain block explorer API.

    Usage::

        explorer = ExplorerClient()
        blocks = explorer.blocks(limit=10)
        txs = explorer.transactions(wallet_id="my-wallet")

    The explorer client shares the same base URL as :class:`RustChainClient`
    but targets the ``/explorer/`` prefix.
    """

    DEFAULT_BASE_URL = "https://50.28.86.131"

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: int = 30,
        retry_count: int = 3,
        verify_ssl: bool = True,
    ) -> None:
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.retry_count = retry_count
        self.verify_ssl = verify_ssl

        self._ctx: Optional[ssl.SSLContext] = None
        if not verify_ssl:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self._ctx = ctx

    def _get(self, endpoint: str) -> Any:
        url = f"{self.base_url}{endpoint}"
        headers = {"Accept": "application/json"}
        req = urllib.request.Request(url, headers=headers, method="GET")

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
                if attempt == self.retry_count - 1:
                    body = e.read().decode("utf-8", errors="replace")
                    try:
                        body_json = json.loads(body)
                    except Exception:
                        body_json = None
                    raise APIError(
                        f"HTTP {e.code}: {e.reason}",
                        status_code=e.code,
                        response_body=body_json,
                    )
            except urllib.error.URLError as e:
                if attempt == self.retry_count - 1:
                    raise NetworkError(f"Connection failed: {e.reason}")

            if attempt < self.retry_count - 1:
                time.sleep(1.0 * (attempt + 1))

        raise APIError("Max retries exceeded")

    def blocks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch recent blocks from the explorer.

        Args:
            limit: Number of recent blocks to return (default 20, max 100).

        Returns:
            List of block dicts with keys: block_hash, height, timestamp,
            tx_count, miner, reward, ...
        """
        return self._get(f"/explorer/blocks?limit={limit}")

    def transactions(
        self,
        wallet_id: Optional[str] = None,
        block_hash: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Fetch transactions, optionally filtered.

        Args:
            wallet_id: Filter transactions by wallet ID.
            block_hash: Filter transactions by block hash.
            limit: Number of transactions to return (default 20, max 100).

        Returns:
            List of transaction dicts with keys: tx_hash, from, to,
            amount, fee, timestamp, block_height, ...
        """
        params = [f"limit={limit}"]
        if wallet_id:
            params.append(f"wallet_id={wallet_id}")
        if block_hash:
            params.append(f"block_hash={block_hash}")
        query = "?" + "&".join(params)
        return self._get(f"/explorer/transactions{query}")

    def block_detail(self, block_hash: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific block.

        Args:
            block_hash: The block hash or height.

        Returns:
            Block dict with full details including all transactions.
        """
        return self._get(f"/explorer/block/{block_hash}")

    def transaction_detail(self, tx_hash: str) -> Dict[str, Any]:
        """
        Fetch detailed information for a specific transaction.

        Args:
            tx_hash: The transaction hash.

        Returns:
            Transaction dict with full details.
        """
        return self._get(f"/explorer/tx/{tx_hash}")
