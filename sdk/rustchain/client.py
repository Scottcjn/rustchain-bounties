"""RustChain client — sync and async."""
from typing import Any, Dict, List, Optional
import requests
from .exceptions import APIError, ConnectionError, ValidationError
from .explorer import Explorer, AsyncExplorer

DEFAULT_BASE_URL = "https://50.28.86.131"

class RustChainClient:
    """Synchronous RustChain client."""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: int = 30, verify_ssl: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session = requests.Session()
        self._session.verify = verify_ssl
        self.explorer = Explorer(self)
    
    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        try:
            resp = self._session.get(f"{self.base_url}{path}", params=params, timeout=self.timeout)
        except requests.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}: {e}")
        except requests.Timeout:
            raise ConnectionError(f"Request to {self.base_url}{path} timed out")
        if resp.status_code >= 400:
            raise APIError(resp.status_code, resp.text[:200])
        return resp.json()
    
    def _post(self, path: str, data: Optional[Dict] = None) -> Any:
        try:
            resp = self._session.post(f"{self.base_url}{path}", json=data, timeout=self.timeout)
        except requests.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}: {e}")
        if resp.status_code >= 400:
            raise APIError(resp.status_code, resp.text[:200])
        return resp.json()
    
    def health(self) -> Dict[str, Any]:
        """Check node health."""
        return self._get("/health")
    
    def epoch(self) -> Dict[str, Any]:
        """Get current epoch info."""
        return self._get("/epoch")
    
    def miners(self) -> List[Dict[str, Any]]:
        """List active miners."""
        return self._get("/api/miners")
    
    def balance(self, wallet_id: str) -> Dict[str, Any]:
        """Check RTC balance for a wallet."""
        if not wallet_id:
            raise ValidationError("wallet_id cannot be empty")
        return self._get(f"/api/balance/{wallet_id}")
    
    def transfer(self, from_wallet: str, to_wallet: str, amount: float, signature: str) -> Dict[str, Any]:
        """Submit a signed transfer."""
        if amount <= 0:
            raise ValidationError("amount must be positive")
        return self._post("/api/transfer", {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": signature,
        })
    
    def attestation_status(self, miner_id: str) -> Dict[str, Any]:
        """Check attestation status for a miner."""
        return self._get(f"/api/attestation/{miner_id}")
    
    def close(self) -> None:
        self._session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class AsyncRustChainClient:
    """Async RustChain client using httpx."""
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: int = 30, verify_ssl: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._client = None
        self.explorer = AsyncExplorer(self)
    
    async def _ensure_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, verify=self.verify_ssl)
    
    async def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        await self._ensure_client()
        try:
            resp = await self._client.get(path, params=params)
        except Exception as e:
            raise ConnectionError(f"Failed: {e}")
        if resp.status_code >= 400:
            raise APIError(resp.status_code, resp.text[:200])
        return resp.json()
    
    async def _post(self, path: str, data: Optional[Dict] = None) -> Any:
        await self._ensure_client()
        try:
            resp = await self._client.post(path, json=data)
        except Exception as e:
            raise ConnectionError(f"Failed: {e}")
        if resp.status_code >= 400:
            raise APIError(resp.status_code, resp.text[:200])
        return resp.json()
    
    async def health(self) -> Dict[str, Any]:
        return await self._get("/health")
    
    async def epoch(self) -> Dict[str, Any]:
        return await self._get("/epoch")
    
    async def miners(self) -> List[Dict[str, Any]]:
        return await self._get("/api/miners")
    
    async def balance(self, wallet_id: str) -> Dict[str, Any]:
        if not wallet_id:
            raise ValidationError("wallet_id cannot be empty")
        return await self._get(f"/api/balance/{wallet_id}")
    
    async def transfer(self, from_wallet: str, to_wallet: str, amount: float, signature: str) -> Dict[str, Any]:
        if amount <= 0:
            raise ValidationError("amount must be positive")
        return await self._post("/api/transfer", {
            "from": from_wallet, "to": to_wallet, "amount": amount, "signature": signature,
        })
    
    async def attestation_status(self, miner_id: str) -> Dict[str, Any]:
        return await self._get(f"/api/attestation/{miner_id}")
    
    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
