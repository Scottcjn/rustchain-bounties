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

    def _create_test_order(self, wallet_address="test_wallet_123", order_type="sell", crypto_asset="ETH", rtc_amount=100.0, price_per_rtc=0.10):
        data = {
            "wallet_address": wallet_address,
            "order_type": order_type,
            "crypto_asset": crypto_asset,
            "rtc_amount": rtc_amount,
            "price_per_rtc": price_per_rtc
        }
        response = self.client.post(
            '/api/orders',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        return json.loads(response.data)['order']['id']

    def _create_test_escrow(self, order_id, buyer_wallet="buyer_wallet", seller_wallet="seller_wallet", crypto_asset="ETH", crypto_amount=1.0):
        data = {
            "order_id": order_id,
            "buyer_wallet": buyer_wallet,
            "seller_wallet": seller_wallet,
            "crypto_asset": crypto_asset,
            "crypto_amount": crypto_amount
        }
        response = self.client.post(
            '/api/escrow/create',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        return json.loads(response.data)['escrow']['id']
    
    def test_create_order(self):
        """Test creating a new order"""
        order_id = self._create_test_order()
        result = db.get_order(order_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.rtc_amount, 100.0)
        self.assertEqual(result.order_type, 'sell')
    
    def test_list_orders(self):
        """Test listing orders"""
        self._create_test_order()
        
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

    def test_deposit_escrow_crypto_by_buyer(self):
        order_id = self._create_test_order()
        escrow_id = self._create_test_escrow(order_id, buyer_wallet="buyer_wallet_1", seller_wallet="seller_wallet_1")

        data = {
            "escrow_id": escrow_id,
            "depositor_wallet": "buyer_wallet_1",
            "deposit_type": "crypto"
        }
        response = self.client.post(
            '/api/escrow/deposit',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        escrow = db.get_escrow(escrow_id)
        self.assertTrue(escrow.crypto_deposited)
        self.assertFalse(escrow.rtc_locked)
        self.assertIsNone(escrow.rtc_signed_tx)

    def test_deposit_escrow_rtc_by_seller_with_signed_tx(self):
        order_id = self._create_test_order()
        escrow_id = self._create_test_escrow(order_id, buyer_wallet="buyer_wallet_2", seller_wallet="seller_wallet_2")

        data = {
            "escrow_id": escrow_id,
            "depositor_wallet": "seller_wallet_2",
            "deposit_type": "rtc",
            "signed_tx": "mock_signed_rtc_tx_123"
        }
        response = self.client.post(
            '/api/escrow/deposit',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        escrow = db.get_escrow(escrow_id)
        self.assertTrue(escrow.rtc_locked)
        self.assertEqual(escrow.rtc_signed_tx, "mock_signed_rtc_tx_123")
        self.assertFalse(escrow.crypto_deposited)

    def test_deposit_escrow_missing_signed_tx_for_rtc(self):
        order_id = self._create_test_order()
        escrow_id = self._create_test_escrow(order_id, buyer_wallet="buyer_wallet_3", seller_wallet="seller_wallet_3")

        data = {
            "escrow_id": escrow_id,
            "depositor_wallet": "seller_wallet_3",
            "deposit_type": "rtc"
        }
        response = self.client.post(
            '/api/escrow/deposit',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        result = json.loads(response.data)
        self.assertIn("Missing signed_tx for RTC deposit", result['error'])

    def test_execute_trade_success_with_signed_tx(self):
        order_id = self._create_test_order()
        escrow_id = self._create_test_escrow(order_id, buyer_wallet="buyer_wallet_4", seller_wallet="seller_wallet_4")

        # Simulate crypto deposit by buyer
        self.client.post(
            '/api/escrow/deposit',
            data=json.dumps({"escrow_id": escrow_id, "depositor_wallet": "buyer_wallet_4", "deposit_type": "crypto"}),
            content_type='application/json'
        )

        # Simulate RTC deposit by seller with signed_tx
        self.client.post(
            '/api/escrow/deposit',
            data=json.dumps({"escrow_id": escrow_id, "depositor_wallet": "seller_wallet_4", "deposit_type": "rtc", "signed_tx": "mock_signed_rtc_tx_456"}),
            content_type='application/json'
        )

        # Mock the RustChainClient.transfer method
        with unittest.mock.patch.object(RustChainClient, 'transfer') as mock_transfer:
            mock_transfer.return_value = {"ok": True, "tx_hash": "mock_tx_hash_789"}

            response = self.client.post(
                '/api/trade/execute',
                data=json.dumps({"escrow_id": escrow_id}),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
            mock_transfer.assert_called_once_with(
                from_wallet="seller_wallet_4",
                to_wallet="buyer_wallet_4",
                amount=100.0,
                signed_tx="mock_signed_rtc_tx_456"
            )
            trade = db.get_trade(db.get_escrow(escrow_id).trade_id)
            self.assertEqual(trade.status, "completed")
            self.assertEqual(trade.rtc_tx_hash, "mock_tx_hash_789")


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
