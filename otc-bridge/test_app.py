"""
OTC Bridge - Test Suite
"""
import unittest
import json
import sys
sys.path.insert(0, '.')

from app import app, db, Order, Escrow, Trade, CryptoEscrow, RustChainClient


class TestOTCBridge(unittest.TestCase):
    """Test cases for OTC Bridge API"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        # Reset database for each test
        db.orders.clear()
        db.escrows.clear()
        db.trades.clear()
        db.trade_history.clear()
    
    def test_create_order(self):
        """Test creating a new order"""
        data = {
            "wallet_address": "test_wallet_123",
            "order_type": "sell",
            "crypto_asset": "ETH",
            "rtc_amount": 100.0,
            "price_per_rtc": 0.10
        }
        
        response = self.client.post(
            '/api/orders',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        result = json.loads(response.data)
        self.assertIn('order', result)
        self.assertEqual(result['order']['rtc_amount'], 100.0)
        self.assertEqual(result['order']['order_type'], 'sell')
    
    def test_list_orders(self):
        """Test listing orders"""
        # Create an order first
        data = {
            "wallet_address": "test_wallet_123",
            "order_type": "sell",
            "crypto_asset": "ETH",
            "rtc_amount": 100.0,
            "price_per_rtc": 0.10
        }
        self.client.post('/api/orders', data=json.dumps(data), content_type='application/json')
        
        # List orders
        response = self.client.get('/api/orders?status=open')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(len(result['orders']), 1)
    
    def test_invalid_order_type(self):
        """Test invalid order type validation"""
        data = {
            "wallet_address": "test_wallet_123",
            "order_type": "invalid",
            "crypto_asset": "ETH",
            "rtc_amount": 100.0,
            "price_per_rtc": 0.10
        }
        
        response = self.client.post(
            '/api/orders',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_missing_field(self):
        """Test missing required field"""
        data = {
            "wallet_address": "test_wallet_123",
            "order_type": "sell"
            # Missing other fields
        }
        
        response = self.client.post(
            '/api/orders',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_health_endpoint(self):
        """Test health check"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.data)
        self.assertEqual(result['status'], 'ok')


class TestCryptoEscrow(unittest.TestCase):
    """Test crypto escrow functionality"""
    
    def test_create_eth_escrow(self):
        """Test ETH escrow creation"""
        result = CryptoEscrow.create_eth_escrow(
            buyer="0xBuyer123",
            seller="0xSeller456",
            amount=1.0,
            asset="ETH"
        )
        
        self.assertIn('escrow_address', result)
        self.assertEqual(result['status'], 'pending_deposit')


class TestRustChainClient(unittest.TestCase):
    """Test RustChain client"""
    
    def test_client_init(self):
        """Test client initialization"""
        client = RustChainClient()
        self.assertEqual(client.node_url, "https://50.28.86.131")
        
        custom_client = RustChainClient(node_url="https://custom.node")
        self.assertEqual(custom_client.node_url, "https://custom.node")


if __name__ == '__main__':
    unittest.main()