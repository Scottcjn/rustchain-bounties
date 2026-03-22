"""RustChain client for interacting with RustChain nodes."""

from typing import Optional, Dict, Any
import httpx

from .models import HealthStatus, EpochInfo, Miner, Balance, TransferResult, AttestationStatus
from .exceptions import (
    RustChainError,
    ConnectionError,
    TimeoutError,
    ValidationError,
    AuthenticationError,
    NotFoundError,
    ServerError,
    RateLimitError,
    TransferError,
    InsufficientFundsError,
    InvalidSignatureError,
)
from .explorer import Explorer


class RustChainClient:
    """RustChain client for interacting with RustChain nodes.
    
    Example:
        >>> import asyncio
        >>> from rustchain import RustChainClient
        >>> 
        >>> async def main():
        ...     async with RustChainClient() as client:
        ...         health = await client.health()
        ...         print(health.status)
        >>> 
        >>> asyncio.run(main())
    """
    
    def __init__(
        self,
        base_url: str = "http://50.28.86.131:9100",
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize RustChain client.
        
        Args:
            base_url: Base URL for RustChain node API (default: http://50.28.86.131:9100)
            timeout: Request timeout in seconds (default: 30.0)
            headers: Additional headers to include in requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None
        self.explorer = Explorer(self)
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self):
        """Initialize HTTP client connection."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self.headers,
            )
    
    async def close(self):
        """Close HTTP client connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to RustChain API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
        
        Returns:
            Response JSON data
        
        Raises:
            ConnectionError: If connection fails
            TimeoutError: If request times out
            ValidationError: If validation fails (400)
            AuthenticationError: If authentication fails (401)
            NotFoundError: If resource not found (404)
            RateLimitError: If rate limit exceeded (429)
            ServerError: If server error (5xx)
        """
        if self._client is None:
            await self.connect()
        
        try:
            response = await self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=data,
            )
            
            # Handle HTTP errors
            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise ValidationError(
                    error_data.get("message", "Validation error"),
                    code=error_data.get("code")
                )
            elif response.status_code == 401:
                raise AuthenticationError("Authentication failed")
            elif response.status_code == 404:
                raise NotFoundError("Resource not found")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "Rate limit exceeded",
                    retry_after=int(retry_after) if retry_after else None
                )
            elif response.status_code >= 500:
                raise ServerError(f"Server error: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.ConnectError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}: {str(e)}")
        except httpx.TimeoutException as e:
            raise TimeoutError(f"Request timed out: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise RustChainError(f"HTTP error: {str(e)}")
    
    async def health(self) -> HealthStatus:
        """Check node health status.
        
        Returns:
            HealthStatus object with node health information
        
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns an error
        """
        response = await self._request("GET", "/health")
        return HealthStatus(**response)
    
    async def epoch(self) -> EpochInfo:
        """Get current epoch information.
        
        Returns:
            EpochInfo object with epoch details
        
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns an error
        """
        response = await self._request("GET", "/epoch")
        return EpochInfo(**response)
    
    async def miners(
        self,
        limit: int = 100,
        active_only: bool = True
    ) -> list[Miner]:
        """Get list of active miners.
        
        Args:
            limit: Maximum number of miners to return (default: 100)
            active_only: Only return active miners (default: True)
        
        Returns:
            List of Miner objects
        
        Raises:
            ConnectionError: If connection fails
            ServerError: If server returns an error
        """
        params = {"limit": limit}
        if active_only:
            params["active"] = "true"
        
        response = await self._request("GET", "/api/miners", params=params)
        return [Miner(**miner) for miner in response.get("miners", [])]
    
    async def balance(self, wallet_id: str) -> Balance:
        """Check RTC balance for a wallet.
        
        Args:
            wallet_id: Wallet ID or address
        
        Returns:
            Balance object with wallet balance information
        
        Raises:
            NotFoundError: If wallet not found
            ConnectionError: If connection fails
            ServerError: If server returns an error
        """
        response = await self._request("GET", f"/api/wallets/{wallet_id}/balance")
        return Balance(**response)
    
    async def transfer(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        signature: str,
        fee: Optional[float] = None,
    ) -> TransferResult:
        """Transfer RTC between wallets.
        
        Args:
            from_address: Sender wallet address
            to_address: Recipient wallet address
            amount: Amount to transfer
            signature: Transaction signature
            fee: Optional custom fee
        
        Returns:
            TransferResult object with transaction details
        
        Raises:
            ValidationError: If parameters are invalid
            InsufficientFundsError: If sender has insufficient funds
            InvalidSignatureError: If signature is invalid
            TransferError: If transfer fails
            ConnectionError: If connection fails
            ServerError: If server returns an error
        """
        data = {
            "from": from_address,
            "to": to_address,
            "amount": amount,
            "signature": signature,
        }
        if fee is not None:
            data["fee"] = fee
        
        try:
            response = await self._request("POST", "/api/transfers", data=data)
            return TransferResult(**response)
        except ValidationError as e:
            if "insufficient" in str(e.message).lower():
                raise InsufficientFundsError(e.message)
            elif "signature" in str(e.message).lower():
                raise InvalidSignatureError(e.message)
            raise
    
    async def attestation_status(self, miner_id: str) -> AttestationStatus:
        """Get attestation status for a miner.
        
        Args:
            miner_id: Miner ID
        
        Returns:
            AttestationStatus object with attestation details
        
        Raises:
            NotFoundError: If miner not found
            ConnectionError: If connection fails
            ServerError: If server returns an error
        """
        response = await self._request("GET", f"/api/miners/{miner_id}/attestation")
        return AttestationStatus(**response)