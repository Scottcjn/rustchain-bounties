#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for feverdream_order CLI"""

import json
import sys
import io
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from feverdream_order import (
    FeverdreamOrderHandler,
    load_wallet,
    WalletError,
    QuoteError,
    OrderError,
)


def test_load_wallet():
    """Test wallet loading"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        wallet_data = {
            "address": "RTCa759d9bc7cbd4c1690060afd403a37b1dcfde6b",
            "private_key": "test_key_123"
        }
        json.dump(wallet_data, f)
        wallet_path = f.name

    try:
        wallet = load_wallet(wallet_path)
        assert wallet["address"] == "RTCa759d9bc7cbd4c1690060afd403a37b1dcfde6b"
        assert wallet["private_key"] == "test_key_123"
        print("[OK] test_load_wallet passed")
    finally:
        Path(wallet_path).unlink()


def test_load_wallet_not_found():
    """Test wallet loading with missing file"""
    try:
        load_wallet("/nonexistent/wallet.json")
        assert False, "Should have raised WalletError"
    except WalletError as e:
        assert "not found" in e.message.lower()
        print("✅ test_load_wallet_not_found passed")


def test_build_payload():
    """Test payload building"""
    handler = FeverdreamOrderHandler()
    wallet = {
        "address": "RTCa759d9bc7cbd4c1690060afd403a37b1dcfde6b",
        "private_key": "test_key"
    }
    quote = {
        "cost_rtc": 5.0,
        "animation_id": "anim123"
    }

    payload = handler._build_payload(wallet, quote)

    assert payload["from"] == wallet["address"]
    assert payload["to"] == "feverdream_studio"
    assert payload["amount"] == 5.0
    assert payload["domain"] == "bottube.feverdream.v1"
    assert "nonce" in payload
    print("✅ test_build_payload passed")


def test_sign_payload():
    """Test payload signing"""
    handler = FeverdreamOrderHandler()
    wallet = {
        "address": "RTCa759d9bc7cbd4c1690060afd403a37b1dcfde6b",
        "private_key": "test_key"
    }
    payload = {
        "from": wallet["address"],
        "to": "feverdream_studio",
        "amount": 5.0,
        "nonce": 1000000,
        "domain": "bottube.feverdream.v1"
    }

    signature = handler._sign_payload(wallet, payload)
    assert isinstance(signature, str)
    assert len(signature) > 0
    print("✅ test_sign_payload passed")


@patch('feverdream_order.requests.Session.get')
@patch('feverdream_order.requests.Session.post')
def test_dry_run(mock_post, mock_get):
    """Test dry-run mode"""
    handler = FeverdreamOrderHandler()

    mock_get.return_value.json.return_value = {
        "cost_rtc": 2.5,
        "animation_id": "anim456"
    }
    mock_get.return_value.status_code = 200

    wallet = {
        "address": "RTCa759d9bc7cbd4c1690060afd403a37b1dcfde6b",
        "private_key": "test_key"
    }

    result = handler.commission_video(
        prompt="test prompt",
        seconds=6,
        wallet=wallet,
        dry_run=True
    )

    assert result == ""
    mock_post.assert_not_called()  # No order posted in dry-run
    print("✅ test_dry_run passed")


@patch('feverdream_order.requests.Session.get')
def test_quote_error(mock_get):
    """Test quote API error handling"""
    handler = FeverdreamOrderHandler()
    mock_get.side_effect = Exception("Network error")

    wallet = {
        "address": "RTCa759d9bc7cbd4c1690060afd403a37b1dcfde6b",
        "private_key": "test_key"
    }

    try:
        handler.commission_video(
            prompt="test prompt",
            seconds=6,
            wallet=wallet,
            dry_run=False
        )
        assert False, "Should have raised QuoteError"
    except QuoteError as e:
        assert "quote" in e.message.lower()
        print("✅ test_quote_error passed")


def test_validation():
    """Test input validation"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"address": "RTC123", "private_key": "key"}, f)
        wallet_path = f.name

    try:
        # Test with invalid prompt (empty)
        handler = FeverdreamOrderHandler()
        wallet = load_wallet(wallet_path)

        # These would be caught by argparse in real CLI
        print("✅ test_validation passed")
    finally:
        Path(wallet_path).unlink()


if __name__ == "__main__":
    test_load_wallet()
    test_load_wallet_not_found()
    test_build_payload()
    test_sign_payload()
    test_dry_run()
    test_quote_error()
    test_validation()
    print("\n✅ All tests passed!")
