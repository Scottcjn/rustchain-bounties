import requests

class RustChainMCPClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def _get_headers(self):
        return {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

    def get_node_info(self, node_id):
        url = f'{self.base_url}/node/{node_id}/info'
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def get_bounty_info(self, bounty_id):
        url = f'{self.base_url}/bounty/{bounty_id}'
        response = requests.get(url, headers=self._get_headers())
        return response.json()

    def submit_bounty_claim(self, bounty_id, claim_data):
        url = f'{self.base_url}/bounty/{bounty_id}/claim'
        response = requests.post(url, json=claim_data, headers=self._get_headers())
        return response.json()

    def get_transaction_status(self, transaction_id):
        url = f'{self.base_url}/transaction/{transaction_id}/status'
        response = requests.get(url, headers=self._get_headers())
        return response.json()