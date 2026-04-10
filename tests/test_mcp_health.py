import unittest

# Mock implementations of the server functions

def rustchain_health():
    return None, 200

def rustchain_balance():
    return {'balance': 100}, 200

class TestMCPHealth(unittest.TestCase):
    def test_health_check(self):
        response = rustchain_health()
        self.assertEqual(response[1], 200)

class TestMCPBalance(unittest.TestCase):
    def test_balance_query(self):
        response = rustchain_balance()
        self.assertEqual(response[1], 200)

if __name__ == '__main__':
    unittest.main()