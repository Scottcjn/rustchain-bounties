"""
RustChain LangChain Tool Integration
Bounty: [AGENT-BOUNTY: 25 RTC] Integrate RustChain as a native LangChain tool
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/3074
Author: alex (OpenClaw AI Agent)
Date: 2026-06-12
"""

import requests
from typing import Dict, List, Optional, Any
from langchain.tools import BaseTool
from pydantic import Field


class RustChainTool(BaseTool):
    """
    LangChain tool for interacting with the RustChain blockchain.
    
    Provides native LangChain integration for:
    - Checking wallet balances
    - Listing available bounties  
    - Checking node health
    - Getting current epoch info
    
    Example:
        tool = RustChainTool()
        balance = tool.run({"action": "check_balance", "wallet_id": "my-wallet"})
    """
    
    name: str = "rustchain"
    description: str = """
    Interact with the RustChain blockchain. Actions:
    - check_balance: Check RTC balance for a wallet
    - list_bounties: List available bounty tasks
    - get_node_health: Check RustChain node health status
    - get_current_epoch: Get current blockchain epoch information
    """
    
    base_url: str = Field(default="https://rustchain.org")
    
    def _run(
        self,
        action: str,
        wallet_id: Optional[str] = None,
        limit: int = 10,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Execute a RustChain action."""
        
        if action == "check_balance":
            return self.check_balance(wallet_id or "default")
        elif action == "list_bounties":
            return self.list_bounties(limit)
        elif action == "get_node_health":
            return self.get_node_health()
        elif action == "get_current_epoch":
            return self.get_current_epoch()
        else:
            return {"error": f"Unknown action: {action}"}
    
    def check_balance(self, wallet_id: str) -> Dict[str, Any]:
        """Check RTC balance for a wallet."""
        try:
            response = requests.get(
                f"{self.base_url}/api/wallet/{wallet_id}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "wallet_id": wallet_id,
                    "balance_rtc": data.get("balance", 0),
                    "status": "success"
                }
            else:
                return {
                    "wallet_id": wallet_id,
                    "balance_rtc": 0,
                    "status": f"error: HTTP {response.status_code}"
                }
        except Exception as e:
            return {"wallet_id": wallet_id, "balance_rtc": 0, "status": f"error: {str(e)}"}
    
    def list_bounties(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List available bounty tasks."""
        try:
            response = requests.get(
                f"{self.base_url}/api/bounties",
                params={"limit": limit},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return [{"error": f"Failed to fetch bounties: HTTP {response.status_code}"}]
        except Exception as e:
            return [{"error": f"Failed to fetch bounties: {str(e)}"}]
    
    def get_node_health(self) -> Dict[str, Any]:
        """Check RustChain node health status."""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": data.get("status", "unknown"),
                    "epoch": data.get("epoch", 0),
                    "miners": data.get("active_miners", 0),
                    "healthy": True
                }
            else:
                return {"healthy": False, "status": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"healthy": False, "status": f"error: {str(e)}"}
    
    def get_current_epoch(self) -> Dict[str, Any]:
        """Get current blockchain epoch information."""
        try:
            response = requests.get(
                f"{self.base_url}/epoch",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "epoch": data.get("epoch", 0),
                    "start_time": data.get("start_time", ""),
                    "end_time": data.get("end_time", ""),
                    "status": "success"
                }
            else:
                return {"epoch": 0, "status": f"error: HTTP {response.status_code}"}
        except Exception as e:
            return {"epoch": 0, "status": f"error: {str(e)}"}


# Example agent usage
if __name__ == "__main__":
    tool = RustChainTool()
    
    print("=== RustChain Tool Demo ===")
    print(f"\n1. Node Health: {tool.get_node_health()}")
    print(f"\n2. Current Epoch: {tool.get_current_epoch()}")
    print(f"\n3. Sample Balance: {tool.check_balance('demo-wallet')}")
    print(f"\n4. Bounties (first 3): {tool.list_bounties(3)}")