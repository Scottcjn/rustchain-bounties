import unittest

# Mock implementation of the server function

def rustchain_balance():
    return {'balance': 100}, 200

class TestMCPBalance(unittest.TestCase):
    def test_balance_query(self):
        response = rustchain_balance()
        self.assertEqual(response[1], 200)

if __name__ == '__main__':
    unittest.main()