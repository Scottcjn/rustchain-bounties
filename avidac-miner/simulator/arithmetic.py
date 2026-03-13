"""
AVIDAC 40-bit Arithmetic Primitives

Implements all arithmetic operations for the AVIDAC's 40-bit word size.
AVIDAC uses parallel binary arithmetic with two's complement representation.
"""

# 40-bit masks
MASK_40 = 0xFFFFFFFFFF  # 40 bits all ones (0b111...111, 40 times)
MASK_20 = 0xFFFFF       # 20 bits all ones (for instructions)
MASK_39 = 0x7FFFFFFFFF  # 39 bits (for signed magnitude check)

# Sign bit position (bit 39, the leftmost bit)
SIGN_BIT = 1 << 39


def mask_40bit(value: int) -> int:
    """Mask value to 40 bits."""
    return value & MASK_40


def to_signed_40bit(value: int) -> int:
    """
    Convert 40-bit unsigned to signed (two's complement).
    
    In two's complement, if the sign bit (bit 39) is set,
    the value is negative and we subtract 2^40.
    """
    if value & SIGN_BIT:
        return value - (1 << 40)
    return value


def to_unsigned_40bit(value: int) -> int:
    """
    Convert signed integer to 40-bit unsigned representation.
    Handles negative values using two's complement.
    """
    if value < 0:
        return (1 << 40) + value
    return value & MASK_40


def add_40bit(a: int, b: int) -> tuple:
    """
    40-bit addition with overflow detection.
    
    Returns:
        (result, overflow) where overflow is True if result exceeded 40 bits
    """
    result = a + b
    overflow = result > MASK_40
    return mask_40bit(result), overflow


def sub_40bit(a: int, b: int) -> tuple:
    """
    40-bit subtraction.
    
    Returns:
        (result, borrow) where borrow is True if a < b
    """
    result = a - b
    borrow = result < 0
    if borrow:
        result += (1 << 40)
    return mask_40bit(result), borrow


def multiply_40bit(a: int, b: int) -> tuple:
    """
    40-bit multiplication producing 80-bit result.
    
    AVIDAC stores the result in MQ:AC format:
    - MQ (Multiplier/Quotient register): high 40 bits
    - AC (Accumulator): low 40 bits
    
    Returns:
        (mq, ac) where mq is high 40 bits, ac is low 40 bits
    """
    product = a * b
    # 80-bit result split into two 40-bit halves
    mq = (product >> 40) & MASK_40  # High 40 bits
    ac = product & MASK_40           # Low 40 bits
    return mq, ac


def divide_40bit(dividend_hi: int, dividend_lo: int, divisor: int) -> tuple:
    """
    80-bit by 40-bit division.
    
    AVIDAC divides MQ:AC (80 bits) by memory (40 bits).
    
    Args:
        dividend_hi: High 40 bits (MQ)
        dividend_lo: Low 40 bits (AC)
        divisor: 40-bit divisor
    
    Returns:
        (quotient, remainder) both 40-bit
    """
    if divisor == 0:
        raise ZeroDivisionError("Division by zero")
    
    # Combine into 80-bit dividend
    dividend = (dividend_hi << 40) | dividend_lo
    quotient = dividend // divisor
    remainder = dividend % divisor
    
    return mask_40bit(quotient), mask_40bit(remainder)


def rotate_left_40bit(value: int, shift: int) -> int:
    """
    40-bit circular left rotation.
    
    Bits shifted out on the left re-enter on the right.
    """
    shift = shift % 40
    if shift == 0:
        return value
    return mask_40bit((value << shift) | (value >> (40 - shift)))


def rotate_right_40bit(value: int, shift: int) -> int:
    """
    40-bit circular right rotation.
    
    Bits shifted out on the right re-enter on the left.
    """
    shift = shift % 40
    if shift == 0:
        return value
    return mask_40bit((value >> shift) | (value << (40 - shift)))


def shift_left_40bit(value: int, shift: int) -> int:
    """
    40-bit logical left shift (zeros shifted in from right).
    """
    shift = min(shift, 40)
    return mask_40bit(value << shift)


def shift_right_40bit(value: int, shift: int) -> int:
    """
    40-bit logical right shift (zeros shifted in from left).
    """
    shift = min(shift, 40)
    return value >> shift


def arithmetic_shift_right_40bit(value: int, shift: int) -> int:
    """
    40-bit arithmetic right shift (sign-extended).
    
    Preserves the sign bit for signed arithmetic.
    """
    shift = min(shift, 40)
    if shift == 0:
        return value
    
    sign = value & SIGN_BIT
    result = value >> shift
    
    # Sign-extend: fill vacated bits with sign bit
    if sign:
        mask = MASK_40 ^ ((1 << (40 - shift)) - 1)
        result |= mask
    
    return mask_40bit(result)


def bitwise_and_40bit(a: int, b: int) -> int:
    """40-bit bitwise AND."""
    return mask_40bit(a & b)


def bitwise_or_40bit(a: int, b: int) -> int:
    """40-bit bitwise OR."""
    return mask_40bit(a | b)


def bitwise_xor_40bit(a: int, b: int) -> int:
    """40-bit bitwise XOR."""
    return mask_40bit(a ^ b)


def bitwise_not_40bit(value: int) -> int:
    """40-bit bitwise NOT (complement)."""
    return mask_40bit(~value)


def is_zero_40bit(value: int) -> bool:
    """Check if 40-bit value is zero."""
    return (value & MASK_40) == 0


def is_negative_40bit(value: int) -> bool:
    """Check if 40-bit value is negative (sign bit set)."""
    return bool(value & SIGN_BIT)


def sha256_rotr_32(value: int, shift: int) -> int:
    """
    32-bit right rotation for SHA256.
    
    SHA256 operates on 32-bit words, so we need this for the hash function.
    AVIDAC's 40-bit words can hold 32-bit values with 8 bits to spare.
    """
    MASK_32 = 0xFFFFFFFF
    value = value & MASK_32
    shift = shift % 32
    return ((value >> shift) | (value << (32 - shift))) & MASK_32


def sha256_shr_32(value: int, shift: int) -> int:
    """
    32-bit right shift for SHA256.
    """
    MASK_32 = 0xFFFFFFFF
    value = value & MASK_32
    return (value >> shift) & MASK_32


# SHA256 helper functions (operate on 32-bit values within 40-bit words)

MASK_32 = 0xFFFFFFFF

def ch_32(x: int, y: int, z: int) -> int:
    """SHA256 Ch function: (x AND y) XOR (NOT x AND z)"""
    x &= MASK_32
    y &= MASK_32
    z &= MASK_32
    return ((x & y) ^ (~x & z)) & MASK_32


def maj_32(x: int, y: int, z: int) -> int:
    """SHA256 Maj function: (x AND y) XOR (x AND z) XOR (y AND z)"""
    x &= MASK_32
    y &= MASK_32
    z &= MASK_32
    return ((x & y) ^ (x & z) ^ (y & z)) & MASK_32


def sigma0_32(x: int) -> int:
    """SHA256 Σ0 function: ROTR(x,2) XOR ROTR(x,13) XOR ROTR(x,22)"""
    return (sha256_rotr_32(x, 2) ^ sha256_rotr_32(x, 13) ^ sha256_rotr_32(x, 22)) & MASK_32


def sigma1_32(x: int) -> int:
    """SHA256 Σ1 function: ROTR(x,6) XOR ROTR(x,11) XOR ROTR(x,25)"""
    return (sha256_rotr_32(x, 6) ^ sha256_rotr_32(x, 11) ^ sha256_rotr_32(x, 25)) & MASK_32


def gamma0_32(x: int) -> int:
    """SHA256 σ0 function: ROTR(x,7) XOR ROTR(x,18) XOR SHR(x,3)"""
    return (sha256_rotr_32(x, 7) ^ sha256_rotr_32(x, 18) ^ sha256_shr_32(x, 3)) & MASK_32


def gamma1_32(x: int) -> int:
    """SHA256 σ1 function: ROTR(x,17) XOR ROTR(x,19) XOR SHR(x,10)"""
    return (sha256_rotr_32(x, 17) ^ sha256_rotr_32(x, 19) ^ sha256_shr_32(x, 10)) & MASK_32


def add_32bit(a: int, b: int) -> int:
    """32-bit addition with wraparound."""
    return (a + b) & MASK_32
