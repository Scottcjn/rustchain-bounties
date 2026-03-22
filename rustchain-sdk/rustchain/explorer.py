"""Explorer API for RustChain SDK."""

from typing import Optional
import httpx

from .models import Block, Transaction, ExplorerBlocks, ExplorerTransactions
from .exceptions import NotFoundError, ServerError


class Explorer:
    """Explorer API for querying blocks and transactions."""
    
    def __init__(self, client):
        """Initialize Explorer.
        
        Args:
            client: RustChain client instance
        """
        self._client = client
    
    async def blocks(
        self,
        limit: int = 10,
        page: int = 1,
        epoch: Optional[int] = None
    ) -> ExplorerBlocks:
        """Get recent blocks.
        
        Args:
            limit: Number of blocks to return (default: 10)
            page: Page number for pagination (default: 1)
            epoch: Filter by epoch number (optional)
        
        Returns:
            ExplorerBlocks with list of Block objects
        
        Raises:
            ServerError: If server returns an error
        """
        params = {"limit": limit, "page": page}
        if epoch is not None:
            params["epoch"] = epoch
        
        response = await self._client._request("GET", "/api/blocks", params=params)
        
        blocks = [Block(**block) for block in response.get("blocks", [])]
        
        return ExplorerBlocks(
            blocks=blocks,
            total=response.get("total", len(blocks)),
            page=page,
            per_page=limit
        )
    
    async def block(self, height: int) -> Block:
        """Get a specific block by height.
        
        Args:
            height: Block height
        
        Returns:
            Block object
        
        Raises:
            NotFoundError: If block is not found
            ServerError: If server returns an error
        """
        response = await self._client._request("GET", f"/api/blocks/{height}")
        return Block(**response)
    
    async def transactions(
        self,
        limit: int = 10,
        page: int = 1,
        wallet: Optional[str] = None
    ) -> ExplorerTransactions:
        """Get recent transactions.
        
        Args:
            limit: Number of transactions to return (default: 10)
            page: Page number for pagination (default: 1)
            wallet: Filter by wallet address (optional)
        
        Returns:
            ExplorerTransactions with list of Transaction objects
        
        Raises:
            ServerError: If server returns an error
        """
        params = {"limit": limit, "page": page}
        if wallet:
            params["wallet"] = wallet
        
        response = await self._client._request("GET", "/api/transactions", params=params)
        
        transactions = [Transaction(**tx) for tx in response.get("transactions", [])]
        
        return ExplorerTransactions(
            transactions=transactions,
            total=response.get("total", len(transactions)),
            page=page,
            per_page=limit
        )
    
    async def transaction(self, tx_hash: str) -> Transaction:
        """Get a specific transaction by hash.
        
        Args:
            tx_hash: Transaction hash
        
        Returns:
            Transaction object
        
        Raises:
            NotFoundError: If transaction is not found
            ServerError: If server returns an error
        """
        response = await self._client._request("GET", f"/api/transactions/{tx_hash}")
        return Transaction(**response)