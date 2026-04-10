import unittest
from integrations.rustchain-mcp.server import app

class TestMCPEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Test for health check
    def test_health_check(self):
        response = self.app.get('/rustchain_health')
        self.assertEqual(response.status_code, 200)

    # Test for balance query
    def test_balance_query(self):
        response = self.app.get('/rustchain_balance')
        self.assertEqual(response.status_code, 200)

    # Test for miners listing
    def test_miners_listing(self):
        response = self.app.get('/rustchain_miners')
        self.assertEqual(response.status_code, 200)

    # Test for epoch info
    def test_epoch_info(self):
        response = self.app.get('/rustchain_epoch')
        self.assertEqual(response.status_code, 200)

    # Test for wallet creation
    def test_wallet_creation(self):
        response = self.app.post('/rustchain_create_wallet')
        self.assertEqual(response.status_code, 201)

    # Test for attestation submission
    def test_attestation_submission(self):
        response = self.app.post('/rustchain_submit_attestation')
        self.assertEqual(response.status_code, 202)

    # Test for open bounties
    def test_bounties_listing(self):
        response = self.app.get('/rustchain_bounties')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()