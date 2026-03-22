import requests

class RustChainClient:
    def __init__(self, base_url="https://api.rustchain.dev"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def get_status(self):
        """Fetch network status"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Simple mock fallback if network is unreachable
            return {"status": "mock_ok", "error": str(e)}

    def get_block(self, height):
        """Fetch a specific block by height"""
        response = self.session.get(f"{self.base_url}/block/{height}")
        response.raise_for_status()
        return response.json()
