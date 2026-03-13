"""
Tests for AVIDAC 40-bit arithmetic primitives.
"""

import pytest
import sys
import os

# Add simulator directory to path
simulator_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, simulator_dir)

from arithmetic import (
    MASK_40, MASK_20, MASK_32, SIGN_BIT,
    mask_40bit, to_signed_40bit, to_unsigned_40bit,
    add_40bit, sub_40bit, multiply_40bit, divide_40bit,
    rotate_left_40bit, rotate_right_40bit,
    shift_left_40bit, shift_right_40bit, arithmetic_shift_right_40bit,
    bitwise_and_40bit, bitwise_or_40bit, bitwise_xor_40bit, bitwise_not_40bit,
    is_zero_40bit, is_negative_40bit,
    sha256_rotr_32, sha256_shr_32,
    ch_32, maj_32, sigma0_32, sigma1_32, gamma0_32, gamma1_32, add_32bit
)


class TestMasking:
    """Test masking operations."""
    
    def test_mask_40bit_basic(self):
        """Test basic 40-bit masking."""
        assert mask_40bit(0xFFFFFFFFFF) == 0xFFFFFFFFFF
        assert mask_40bit(0x10000000000) == 0  # 41st bit masked out
        assert mask_40bit(0x1FFFFFFFFFFFF) == 0xFFFFFFFFFF
    
    def test_mask_40bit_negative(self):
        """Test masking negative values."""
        assert mask_40bit(-1) == 0xFFFFFFFFFF
        assert mask_40bit(-100) == (1 << 40) - 100
    
    def test_sign_bit(self):
        """Test sign bit constant."""
        assert SIGN_BIT == 1 << 39
        assert SIGN_BIT == 0x8000000000


class TestSignedConversion:
    """Test signed/unsigned conversion."""
    
    def test_to_signed_positive(self):
        """Test converting positive values to signed."""
        assert to_signed_40bit(0) == 0
        assert to_signed_40bit(1) == 1
        assert to_signed_40bit(0x7FFFFFFFFF) == 0x7FFFFFFFFF
    
    def test_to_signed_negative(self):
        """Test converting negative values to signed."""
        assert to_signed_40bit(0x8000000000) == -0x8000000000
        assert to_signed_40bit(0xFFFFFFFFFF) == -1
        assert to_signed_40bit(0xFFFFFFFFFE) == -2
    
    def test_to_unsigned_roundtrip(self):
        """Test unsigned conversion roundtrip."""
        for val in [0, 1, 100, 0x7FFFFFFFFF, 0xFFFFFFFFFF]:
            signed = to_signed_40bit(val)
            unsigned = to_unsigned_40bit(signed)
            assert unsigned == val


class TestAddition:
    """Test 40-bit addition."""
    
    def test_add_basic(self):
        """Test basic addition."""
        result, overflow = add_40bit(10, 20)
        assert result == 30
        assert not overflow
    
    def test_add_overflow(self):
        """Test addition with overflow."""
        result, overflow = add_40bit(0xFFFFFFFFFF, 1)
        assert result == 0
        assert overflow
    
    def test_add_zero(self):
        """Test addition with zero."""
        result, overflow = add_40bit(12345, 0)
        assert result == 12345
        assert not overflow


class TestSubtraction:
    """Test 40-bit subtraction."""
    
    def test_sub_basic(self):
        """Test basic subtraction."""
        result, borrow = sub_40bit(30, 10)
        assert result == 20
        assert not borrow
    
    def test_sub_borrow(self):
        """Test subtraction with borrow."""
        result, borrow = sub_40bit(0, 1)
        assert result == 0xFFFFFFFFFF
        assert borrow
    
    def test_sub_zero(self):
        """Test subtraction of zero."""
        result, borrow = sub_40bit(12345, 0)
        assert result == 12345
        assert not borrow


class TestMultiplication:
    """Test 40-bit multiplication."""
    
    def test_mul_basic(self):
        """Test basic multiplication."""
        mq, ac = multiply_40bit(100, 200)
        assert mq == 0
        assert ac == 20000
    
    def test_mul_large(self):
        """Test multiplication producing 80-bit result."""
        # 2^20 * 2^20 = 2^40 (requires MQ)
        a = 1 << 20
        b = 1 << 20
        mq, ac = multiply_40bit(a, b)
        assert mq == 1
        assert ac == 0
    
    def test_mul_zero(self):
        """Test multiplication by zero."""
        mq, ac = multiply_40bit(12345, 0)
        assert mq == 0
        assert ac == 0


class TestDivision:
    """Test 80-bit by 40-bit division."""
    
    def test_div_basic(self):
        """Test basic division."""
        quotient, remainder = divide_40bit(0, 100, 10)
        assert quotient == 10
        assert remainder == 0
    
    def test_div_with_remainder(self):
        """Test division with remainder."""
        quotient, remainder = divide_40bit(0, 100, 30)
        assert quotient == 3
        assert remainder == 10
    
    def test_div_zero_divisor(self):
        """Test division by zero raises error."""
        with pytest.raises(ZeroDivisionError):
            divide_40bit(0, 100, 0)


class TestRotation:
    """Test rotation operations."""
    
    def test_rotate_left_basic(self):
        """Test basic left rotation."""
        val = 0x1
        result = rotate_left_40bit(val, 1)
        assert result == 0x2
    
    def test_rotate_left_wrap(self):
        """Test left rotation with wrap-around."""
        val = 1 << 39  # Sign bit
        result = rotate_left_40bit(val, 1)
        assert result == 1  # Wraps to bit 0
    
    def test_rotate_right_basic(self):
        """Test basic right rotation."""
        val = 0x2
        result = rotate_right_40bit(val, 1)
        assert result == 0x1
    
    def test_rotate_right_wrap(self):
        """Test right rotation with wrap-around."""
        val = 0x1
        result = rotate_right_40bit(val, 1)
        assert result == (1 << 39)  # Wraps to sign bit
    
    def test_rotate_full_circle(self):
        """Test rotation by 40 bits returns original."""
        val = 0xDEADBEEF12
        assert rotate_left_40bit(val, 40) == val
        assert rotate_right_40bit(val, 40) == val


class TestShifts:
    """Test shift operations."""
    
    def test_shift_left(self):
        """Test left shift."""
        assert shift_left_40bit(1, 1) == 2
        assert shift_left_40bit(1, 10) == 1024
    
    def test_shift_right(self):
        """Test right shift."""
        assert shift_right_40bit(1024, 10) == 1
        assert shift_right_40bit(2, 1) == 1
    
    def test_arithmetic_shift_right_positive(self):
        """Test arithmetic right shift of positive number."""
        assert arithmetic_shift_right_40bit(0x10, 1) == 0x8
    
    def test_arithmetic_shift_right_negative(self):
        """Test arithmetic right shift of negative number (sign-extended)."""
        val = 0xFFFFFFFFFF  # -1 in 40-bit
        result = arithmetic_shift_right_40bit(val, 4)
        assert result == 0xFFFFFFFFFF  # Still -1 (sign-extended)


class TestBitwise:
    """Test bitwise operations."""
    
    def test_and(self):
        """Test bitwise AND."""
        assert bitwise_and_40bit(0xF, 0x5) == 0x5
        assert bitwise_and_40bit(0xFFFFFFFFFF, 0x123) == 0x123
    
    def test_or(self):
        """Test bitwise OR."""
        assert bitwise_or_40bit(0xF, 0x5) == 0xF
        assert bitwise_or_40bit(0x100, 0x200) == 0x300
    
    def test_xor(self):
        """Test bitwise XOR."""
        assert bitwise_xor_40bit(0xF, 0x5) == 0xA
        assert bitwise_xor_40bit(0x123, 0x123) == 0
    
    def test_not(self):
        """Test bitwise NOT."""
        assert bitwise_not_40bit(0) == 0xFFFFFFFFFF
        assert bitwise_not_40bit(0xFFFFFFFFFF) == 0
    
    def test_flags(self):
        """Test zero and negative flags."""
        assert is_zero_40bit(0)
        assert not is_zero_40bit(1)
        assert not is_negative_40bit(0x7FFFFFFFFF)
        assert is_negative_40bit(0x8000000000)


class TestSHA256Helpers:
    """Test SHA256 helper functions."""
    
    def test_rotr_32_basic(self):
        """Test 32-bit right rotation."""
        assert sha256_rotr_32(0x1, 1) == 0x80000000
        assert sha256_rotr_32(0x80000000, 1) == 0x40000000  # 0x80000000 >> 1 = 0x40000000
    
    def test_shr_32(self):
        """Test 32-bit right shift."""
        assert sha256_shr_32(0x100, 1) == 0x80
        assert sha256_shr_32(0x100, 8) == 0x1
    
    def test_ch_function(self):
        """Test SHA256 Ch function."""
        # Ch(x,y,z) = (x AND y) XOR (NOT x AND z)
        result = ch_32(0xFFFFFFFF, 0xAAAAAAAA, 0x55555555)
        assert result == 0xAAAAAAAA  # When x=1, result=y
    
    def test_maj_function(self):
        """Test SHA256 Maj function."""
        # Maj(x,y,z) = (x AND y) XOR (x AND z) XOR (y AND z)
        result = maj_32(0xFFFFFFFF, 0xFFFFFFFF, 0x00000000)
        assert result == 0xFFFFFFFF  # Majority is 1
    
    def test_sigma_functions(self):
        """Test SHA256 sigma functions."""
        # Just verify they run without error and produce 32-bit results
        val = 0x12345678
        assert sigma0_32(val) & 0xFFFFFFFF == sigma0_32(val)
        assert sigma1_32(val) & 0xFFFFFFFF == sigma1_32(val)
        assert gamma0_32(val) & 0xFFFFFFFF == gamma0_32(val)
        assert gamma1_32(val) & 0xFFFFFFFF == gamma1_32(val)
    
    def test_add_32bit(self):
        """Test 32-bit addition with wraparound."""
        assert add_32bit(0xFFFFFFFF, 1) == 0
        assert add_32bit(0x7FFFFFFF, 1) == 0x80000000


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
