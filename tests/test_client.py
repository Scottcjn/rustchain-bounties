import unittest
from rustchain.client import RustChainClient

class TestRustChainClient(unittest.TestCase):
    def setUp(self):
        self.client = RustChainClient(base_url="http://mock.rustchain.local")
        
    def test_get_status_fallback(self):
        status = self.client.get_status()
        self.assertEqual(status["status"], "mock_ok")

if __name__ == "__main__":
    unittest.main()
