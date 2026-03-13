import unittest
from rustchain_mcp_client import RustChainMCPClient

class TestRustChainMCPClient(unittest.TestCase):

    def setUp(self):
        self.client = RustChainMCPClient('https://api.rustchain.com', 'test_api_key')

    def test_get_node_info(self):
        node_info = self.client.get_node_info('node123')
        self.assertIn('node_id', node_info)

    def test_get_bounty_info(self):
        bounty_info = self.client.get_bounty_info('bounty123')
        self.assertIn('bounty_id', bounty_info)

    def test_submit_bounty_claim(self):
        claim_data = {'user_id': 'user123', 'amount': 100}
        claim_response = self.client.submit_bounty_claim('bounty123', claim_data)
        self.assertEqual(claim_response['status'], 'success')

    def test_get_transaction_status(self):
        transaction_status = self.client.get_transaction_status('txn123')
        self.assertIn('status', transaction_status)

if __name__ == '__main__':
    unittest.main()