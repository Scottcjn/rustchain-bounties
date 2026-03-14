#!/usr/bin/env python3
"""
BoTTube API Python SDK Wrapper
"""

import requests

class BoTTubeAPI:
    def __init__(self, base_url="https://api.bottube.com"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_balance(self, address):
        """Get account balance"""
        return self._call("getBalance", {"address": address})
    
    def get_block(self, block_number):
        """Get block by number"""
        return self._call("getBlock", {"blockNumber": block_number})
    
    def get_transaction(self, tx_hash):
        """Get transaction by hash"""
        return self._call("getTransaction", {"txHash": tx_hash})
    
    def get_latest_blocks(self, count=10):
        """Get latest N blocks"""
        return self._call("getLatestBlocks", {"count": count})
    
    def _call(self, method, params):
        """Internal API call"""
        response = self.session.post(
            f"{self.base_url}/api/v1/{method}",
            json=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

# Usage example
if __name__ == "__main__":
    api = BoTTubeAPI()
    print(api.get_balance("RTC1234567890abcdef..."))
