"""
RustChain Client - Python SDK for RustChain and BoTTube APIs
"""

import os
import requests
from typing import Optional, Dict, List, Any


class RustChainClient:
    """Client for interacting with RustChain node APIs"""
    
    def __init__(self, node_url: str = None):
        self.node_url = node_url or os.environ.get(
            "RUSTCHAIN_NODE_URL", 
            "https://50.28.86.131"
        )
        self.session = requests.Session()
        # Disable SSL verification for IP-based URLs with certificate mismatch
        if "50.28.86.131" in self.node_url:
            self.session.verify = False
    
    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make GET request to RustChain node"""
        url = f"{self.node_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def _post(self, endpoint: str, data: dict = None) -> dict:
        """Make POST request to RustChain node"""
        url = f"{self.node_url}{endpoint}"
        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def health(self) -> Dict[str, Any]:
        """
        Check node health status
        
        Returns:
            dict: Health status including 'ok', 'version', 'uptime_s', etc.
        """
        return self._get("/health")
    
    def get_epoch(self) -> Dict[str, Any]:
        """
        Get current epoch information
        
        Returns:
            dict: Epoch info including 'epoch', 'slot', 'blocks_per_epoch', etc.
        """
        return self._get("/epoch")
    
    def get_miners(self) -> List[Dict[str, Any]]:
        """
        List active miners
        
        Returns:
            list: Active miners with hardware, attestation info
        """
        return self._get("/api/miners")
    
    def get_balance(self, wallet_name: str) -> Dict[str, Any]:
        """
        Check wallet balance
        
        Args:
            wallet_name: Wallet name or miner_id
            
        Returns:
            dict: Balance information
        """
        return self._get("/wallet/balance", params={"miner_id": wallet_name})
    
    def transfer(self, from_wallet: str, to_wallet: str, amount: float, 
                 admin_key: str = None) -> Dict[str, Any]:
        """
        Transfer RTC between wallets
        
        Args:
            from_wallet: Source wallet name
            to_wallet: Destination wallet name  
            amount: Amount in RTC
            admin_key: Admin key for authorization (required)
            
        Returns:
            dict: Transfer status
        """
        if not admin_key:
            raise ValueError("Admin key required for transfers")
        
        data = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "admin_key": admin_key
        }
        return self._post("/wallet/transfer", data)
    
    def register_wallet(self, wallet_name: str) -> Dict[str, Any]:
        """
        Register a new wallet
        
        Args:
            wallet_name: Desired wallet name
            
        Returns:
            dict: Registration status
        """
        return self._post("/wallet/register", {"miner_id": wallet_name})
    
    def get_bounties(self) -> List[Dict[str, Any]]:
        """
        List open bounties (if endpoint available)
        
        Returns:
            list: Open bounties
        """
        # May not be available on all nodes
        try:
            return self._get("/api/bounties")
        except requests.exceptions.HTTPError:
            return []


class BoTTubeClient:
    """Client for interacting with BoTTube APIs"""
    
    def __init__(self, api_key: str = None, base_url: str = "https://bottube.ai/api"):
        self.api_key = api_key or os.environ.get("BOTTUBE_API_KEY")
        self.base_url = base_url
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search videos on BoTTube
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            list: Video results
        """
        response = self.session.get(
            f"{self.base_url}/videos/search",
            params={"q": query, "limit": limit},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("results", [])
    
    def get_video(self, video_id: str) -> Dict[str, Any]:
        """
        Get video details
        
        Args:
            video_id: Video ID
            
        Returns:
            dict: Video information
        """
        response = self.session.get(
            f"{self.base_url}/videos/{video_id}",
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get platform statistics
        
        Returns:
            dict: Platform stats
        """
        response = self.session.get(
            f"{self.base_url}/stats",
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def upload(self, video_path: str, title: str, description: str = "",
               tags: List[str] = None) -> Dict[str, Any]:
        """
        Upload a video
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: Video tags
            
        Returns:
            dict: Upload status
        """
        with open(video_path, "rb") as f:
            files = {"file": f}
            data = {
                "title": title,
                "description": description,
                "tags": ",".join(tags or [])
            }
            response = self.session.post(
                f"{self.base_url}/videos/upload",
                files=files,
                data=data,
                timeout=300
            )
        response.raise_for_status()
        return response.json()


# Convenience function for quick usage
def get_default_clients() -> tuple:
    """
    Get default RustChain and BoTTube clients
    
    Returns:
        tuple: (RustChainClient, BoTTubeClient)
    """
    return RustChainClient(), BoTTubeClient()
