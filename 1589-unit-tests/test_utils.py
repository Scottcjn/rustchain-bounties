#!/usr/bin/env python3
"""Unit tests for RustChain utility functions"""
import unittest

def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract b from a"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def is_valid_rtc_address(address):
    """Validate RTC address format"""
    if not address or not isinstance(address, str):
        return False
    if not address.startswith("RTC"):
        return False
    if len(address) != 42:
        return False
    return True

def format_balance(balance_wei):
    """Convert wei to RTC"""
    return balance_wei / 1e18

class TestMathFunctions(unittest.TestCase):
    """Test math utility functions"""
    
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
    
    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract(0, 5), -5)
    
    def test_multiply(self):
        self.assertEqual(multiply(3, 4), 12)
        self.assertEqual(multiply(0, 100), 0)
    
    def test_divide(self):
        self.assertEqual(divide(10, 2), 5)
        self.assertAlmostEqual(divide(7, 2), 3.5)
        with self.assertRaises(ValueError):
            divide(10, 0)

class TestAddressValidation(unittest.TestCase):
    """Test address validation"""
    
    def test_valid_address(self):
        valid = "RTC1234567890abcdef1234567890abcdef1234"
        self.assertTrue(is_valid_rtc_address(valid))
    
    def test_invalid_address_no_prefix(self):
        invalid = "1234567890abcdef1234567890abcdef12345678"
        self.assertFalse(is_valid_rtc_address(invalid))
    
    def test_invalid_address_wrong_length(self):
        invalid = "RTC123"
        self.assertFalse(is_valid_rtc_address(invalid))

class TestBalanceFormatting(unittest.TestCase):
    """Test balance formatting"""
    
    def test_format_balance(self):
        self.assertEqual(format_balance(1e18), 1.0)
        self.assertEqual(format_balance(5e17), 0.5)

if __name__ == "__main__":
    unittest.main()
