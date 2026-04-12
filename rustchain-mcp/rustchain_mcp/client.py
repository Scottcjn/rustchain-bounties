"""HTTP client for RustChain node."""
import ssl
import urllib.request
import urllib.error
import json
from typing import Optional, Dict, Any


class RustChainClient:
    """Client for interacting with RustChain node API."""
    
    def __init__(self, node_url: str = "https://50.28.86.131", timeout: int = 30):
        self.node_url = node_url.rstrip("/")
        self.timeout = timeout
        self._ctx = ssl.create_default_context()
        self._ctx.check_hostname = False
        self._ctx.verify_mode = ssl.CERT_NONE
    
    def _request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an HTTP request to the RustChain node."""
        url = f"{self.node_url}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        
        try:
            with urllib.request.urlopen(req, context=self._ctx, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise RustChainError(f"HTTP {e.code}: {error_body}", code=e.code)
        except urllib.error.URLError as e:
            raise RustChainError(f"Connection failed: {e.reason}", code=None)
    
    def health(self) -> Dict[str, Any]:
        """Check node health."""
        return self._request("GET", "/health")
    
    def wallet_balance(self, miner_id: str) -> Dict[str, Any]:
        """Query wallet/miner balance."""
        return self._request("GET", f"/wallet/balance?miner_id={miner_id}")
    
    def epoch(self) -> Dict[str, Any]:
        """Get current epoch info."""
        return self._request("GET", "/epoch")
    
    def miners(self, limit: int = 100) -> Dict[str, Any]:
        """List active miners."""
        return self._request("GET", f"/miners?limit={limit}")
    
    def create_wallet(self, miner_id: str, public_key: str) -> Dict[str, Any]:
        """Register a new wallet."""
        return self._request("POST", "/wallet/create", {
            "miner_id": miner_id,
            "public_key": public_key
        })
    
    def submit_attestation(self, miner_id: str, fingerprint: str, signature: str, epoch: int) -> Dict[str, Any]:
        """Submit hardware attestation."""
        return self._request("POST", "/attest/submit", {
            "miner_id": miner_id,
            "fingerprint": fingerprint,
            "signature": signature,
            "epoch": epoch
        })
    
    def bounties(self, status: str = "open", limit: int = 50) -> Dict[str, Any]:
        """List open bounties from the bounties repo."""
        # This would need to query GitHub API
        raise NotImplementedError("Use rustchain_bounties tool for this")


class RustChainError(Exception):
    """RustChain API error."""
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.code = code
