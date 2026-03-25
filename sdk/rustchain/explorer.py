"""RustChain Explorer — block and transaction queries."""
from typing import Any, Dict, List, Optional

class Explorer:
    """Explorer interface for querying blocks and transactions."""
    
    def __init__(self, client: Any) -> None:
        self._client = client
    
    def blocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent blocks."""
        return self._client._get(f"/api/explorer/blocks", params={"limit": limit})
    
    def transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        return self._client._get(f"/api/explorer/transactions", params={"limit": limit})
    
    def block(self, block_id: str) -> Dict[str, Any]:
        """Get a specific block by ID."""
        return self._client._get(f"/api/explorer/blocks/{block_id}")

class AsyncExplorer:
    """Async explorer interface."""
    
    def __init__(self, client: Any) -> None:
        self._client = client
    
    async def blocks(self, limit: int = 10) -> List[Dict[str, Any]]:
        return await self._client._get(f"/api/explorer/blocks", params={"limit": limit})
    
    async def transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        return await self._client._get(f"/api/explorer/transactions", params={"limit": limit})
    
    async def block(self, block_id: str) -> Dict[str, Any]:
        return await self._client._get(f"/api/explorer/blocks/{block_id}")
