import pytest
from wallet_helper import validate_wallet_name

def test_validate_wallet_name_valid():
    """Test valid wallet names are accepted"""
    valid_names = [
        "ViViANlEE",
        "alexw18",
        "jOhNdOe123"
    ]

    for name in valid_names:
        result, _ = validate_wallet_name(name)
        assert result is True, f"Failed validation for valid name: {name}"

def test_validate_wallet_name_invalid_chars():
    """Test invalid wallet names containing illegal characters"""
    invalid_names = [
        "invalid@name",
        "has space",
        "special!char",
        "name-with-dash",
        "under_line",
        "dot.name",
        "name$db"
    ]

    for name in invalid_names:
        result, message = validate_wallet_name(name)
        assert result is False, f"Invalid name accepted: {name}"
        assert "Invalid characters" in message, "Incorrect error message for invalid characters"

def test_validate_wallet_name_length():
    """Test invalid wallet names based on length"""
    invalid_names = [
        "abc",  # too short
        "ab",  # too short
        "a",  # too short
        "abcdUNiiiiiiiiiiiiiiiiiiiiiiiiiiiii",  # exactly 30 chars
        "abcdUNiiiiiiiiiiiiiiiiiiiiiiiiiiiiix",  # 31 chars (too long)
        "abcdefghijklmnopqrstuvwxyz123456",  # 30 chars, valid pattern
        "abcdEFGiiiiiiiiiiiiiiiiiiiiiiiiiii!."  # 31 chars with invalid chars
    ]

    for name in invalid_names:
        if len(name) < 4:
            result, message = validate_wallet_name(name)
            assert result is False, f"Short name accepted: {name}"
            assert "must be at least 4 characters" in message
        elif len(name) > 30:
            result, message = validate_wallet_name(name)
            assert result is False, f"Long name accepted: {name}"
            assert "more than 30" in message
        elif len(name) == 30 and name.isalnum():
            result, message = validate_wallet_name(name)
            assert result is True, f"Valid 30-char name rejected: {name}"

def test_validate_wallet_name_case_variations():
    """Test valid wallet names with different case variations"""
    valid_names = [
        "AllUpperFORTYTWO",
        "ALLUPPER42",
        "ALLUPPER42!",
        "MixedCaseWalL3T",
        "Lower42",
        "OneTwo4",
        "ThreeFourFIVE5"
    ]

    for name in valid_names:
        name_without_illegal_chars = name[:-1] if not name.isalnum() else name

        if name == name_without_illegal_chars:
            result, _ = validate_wallet_name(name)
            assert result is True, f"Failed validation for valid name: {name}"
        else:
            result, message = validate_wallet_name(name)
            assert result is False, f"Invalid name accepted: {name}"
            assert "Invalid characters" in message, "Incorrect error message for invalid characters"

def test_validate_wallet_name_pattern():
    """Test invalid wallet names based on pattern"""
    invalid_names = [
        "alllowercase",
        "ALLUPPERCASE",
        "ALllower45",
        "noNumbersHere",
        "NumbersALl56",
        "ALlupper90"
    ]

    for name in invalid_names:
        if name.islower() or (name.isupper() and name.isalpha()):
            result, message = validate_wallet_name(name)
            assert result is False, f"Invalid name accepted: {name}"
            assert "must include at least one uppercase and one lowercase letter" in message or \
                   "must contain at least one number" in message
        elif name.isupper() and any(c.isdigit() for c in name):
            result, _ = validate_wallet_name(name)
            assert result is True, f"Failed validation for valid name: {name}"

def test_validate_wallet_name_special_cases():
    """Test special cases for wallet name validation"""
    # Test minimum length valid name
    result, _ = validate_wallet_name("Ab1")
    assert result is False, "Name below minimum length accepted"

    # Test exact minimum length valid name
    result, _ = validate_wallet_name("Abcd2")
    assert result is True, "Valid minimum length name rejected"

    # Test mixed case with same character
    result, message = validate_wallet_name("aA1")
    assert result is False, "Name below minimum length accepted"
    assert "must be at least 4 characters" in message, "Incorrect error message"

    # Test exact maximum length valid name
    valid_name = "AbcdUNiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
    result, _ = validate_wallet_name(valid_name)
    assert result is True, "Valid maximum length name rejected"

    # Test maximum length plus one
    invalid_name = "AbcdUNiiiiiiiiiiiiiiiiiiiiiiiiiiiiix"
    result, message = validate_wallet_name(invalid_name)
    assert result is False, "Name exceeding maximum length accepted"
    assert "more than 30" in message, "Incorrect error message"

    # Test name ending with special character
    result, message = validate_wallet_name("ValidName1!")
    assert result is False, "Name with special character accepted"
    assert "Invalid characters" in message, "Incorrect error message for invalid characters"

    # Test name containing only numbers
    result, message = validate_wallet_name("12345")
    assert result is False, "Name with only numbers accepted"
    assert "must include at least one uppercase and one lowercase letter" in message, "Incorrect error message"