"""
Unit tests for example.py
Bounty: Issue #1589 - EASY BOUNTY: 2 RTC
"""

import pytest
import sys
import os

# Import the module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from example import *

class TestAdd:
    """Test cases for add function."""
    
    def test_add_positive(self):
        """Test adding positive numbers."""
        assert add(2, 3) == 5
    
    def test_add_negative(self):
        """Test adding negative numbers."""
        assert add(-1, -2) == -3
    
    def test_add_zero(self):
        """Test adding with zero."""
        assert add(0, 5) == 5
        assert add(5, 0) == 5

class TestMultiply:
    """Test cases for multiply function."""
    
    def test_multiply_positive(self):
        """Test multiplying positive numbers."""
        assert multiply(3, 4) == 12
    
    def test_multiply_by_zero(self):
        """Test multiplying by zero."""
        assert multiply(5, 0) == 0
    
    def test_multiply_negative(self):
        """Test multiplying negative numbers."""
        assert multiply(-2, -3) == 6

class TestDivide:
    """Test cases for divide function."""
    
    def test_divide_positive(self):
        """Test dividing positive numbers."""
        assert divide(10, 2) == 5
    
    def test_divide_negative(self):
        """Test dividing negative numbers."""
        assert divide(-10, 2) == -5
    
    def test_divide_by_zero(self):
        """Test division by zero raises error."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)

# Edge cases
class TestEdgeCases:
    """Test edge cases."""
    
    def test_add_large_numbers(self):
        """Test adding large numbers."""
        assert add(10**6, 10**6) == 2 * 10**6
    
    def test_multiply_identity(self):
        """Test multiply by 1 (identity)."""
        assert multiply(42, 1) == 42

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
