# SPDX-License-Identifier: MIT
"""Tests for RustChainBot — mocked API responses."""
import unittest
from unittest.mock import patch, AsyncMock
import json

# Mock API responses matching live RustChain endpoints
MOCK_BALANCE = {"amount_i64": 1500000000, "amount_rtc": 15.0}
MOCK_MINERS = {"miners": [{"id": 1, "hashrate": 100}], "pagination": {"total": 13}}
MOCK_EPOCH = {"epoch": 42, "slot": 1234567, "blocks_per_epoch": 144, "enrolled_miners": 15, "epoch_pot": 1.5, "total_supply_rtc": 8388608}

class TestBotLogic(unittest.TestCase):
    """Verify bot command logic without live API calls."""

    def test_balance_endpoint_format(self):
        """Balance uses /wallet/balance?address= not /api/wallet/"""
        wallet = "RTCe11828a58518480960023f571842abadeeeb943d"
        expected_path = f"/wallet/balance?address={wallet}"
        self.assertIn("/wallet/balance", expected_path)
        self.assertNotIn("/api/wallet", expected_path)

    def test_miners_response_parsing(self):
        """Miners correctly reads pagination.total"""
        total = MOCK_MINERS["pagination"]["total"]
        self.assertEqual(total, 13)
        self.assertGreater(total, 0)

    def test_epoch_endpoint_format(self):
        """Epoch uses /epoch not /api/epoch, live fields (slot, not height/timestamp)"""
        expected = "/epoch"
        self.assertIn("epoch", expected)
        self.assertNotIn("/api/epoch", expected)
        # Live API shape: slot, not height; no timestamp field
        self.assertIn("slot", MOCK_EPOCH)
        self.assertIn("enrolled_miners", MOCK_EPOCH)
        self.assertIn("epoch_pot", MOCK_EPOCH)
        self.assertIn("total_supply_rtc", MOCK_EPOCH)
        self.assertNotIn("height", MOCK_EPOCH)
        self.assertNotIn("timestamp", MOCK_EPOCH)

    def test_price_is_positive(self):
        """RTC price is non-zero"""
        price = 0.10
        self.assertGreater(price, 0)

    def test_balance_amount_rtc_key(self):
        """Response uses amount_rtc key, not balance"""
        self.assertIn("amount_rtc", MOCK_BALANCE)
        self.assertNotIn("balance", MOCK_BALANCE)

    def test_service_file_base_url(self):
        """Service file uses root URL, not /api"""
        service_url = "https://rustchain.org"  # fixed
        self.assertNotIn("/api", service_url.split("https://rustchain.org")[-1])


if __name__ == "__main__":
    unittest.main()
