#!/usr/bin/env python3
"""Unit tests for rtc_balance.py"""

import pytest
import json
from unittest.mock import patch, MagicMock
from rtc_balance import extract_balance, extract_epoch, format_balance, RTC_USD


class TestExtractBalance:
    """Test extract_balance function with various JSON shapes."""

    def test_balance_direct(self):
        """Test when balance is at top level with 'amount_rtc' key."""
        data = {"amount_rtc": 100.5}
        assert extract_balance(data) == 100.5

    def test_balance_key(self):
        """Test when balance is at top level with 'balance' key."""
        data = {"balance": 50.25}
        assert extract_balance(data) == 50.25

    def test_balance_nested_result(self):
        """Test when balance is nested under 'result' key."""
        data = {"result": {"amount_rtc": 75.0}}
        assert extract_balance(data) == 75.0

    def test_balance_nested_data(self):
        """Test when balance is nested under 'data' key."""
        data = {"data": {"amount_rtc": 200.0}}
        assert extract_balance(data) == 200.0

    def test_balance_wallet_nested(self):
        """Test when balance is nested under 'wallet' key."""
        data = {"wallet": {"balance": 30.0}}
        assert extract_balance(data) == 30.0

    def test_balance_empty(self):
        """Test when data is empty."""
        assert extract_balance({}) is None

    def test_balance_none(self):
        """Test when data is None (edge case)."""
        data = {"result": None}
        assert extract_balance(data) is None


class TestExtractEpoch:
    """Test extract_epoch function."""

    def test_epoch_top_level(self):
        data = {"epoch": 42}
        assert extract_epoch(data) == 42

    def test_epoch_nested(self):
        data = {"result": {"epoch": 100}}
        assert extract_epoch(data) == 100

    def test_epoch_missing(self):
        assert extract_epoch({}) is None


class TestFormatBalance:
    """Test format_balance function."""

    def test_format_positive(self):
        result = format_balance(100.5)
        assert "100.50" in result
        assert "RTC" in result
        assert "$10.05" in result or "$10.05" in result  # 100.5 * 0.10

    def test_format_zero(self):
        result = format_balance(0)
        assert "0" in result

    def test_format_large(self):
        result = format_balance(10000)
        assert "10,000" in result or "10000" in result
        assert "$1,000" in result or "$1000" in result
