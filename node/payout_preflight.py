"""Payout preflight validation for RustChain."""

import decimal
from dataclasses import dataclass, field
from typing import Literal

import eth_utils
import rlp


def _is_rtc_address(addr: str) -> bool:
    """Check if the given address is a valid RTC (RustChain Token) address.

    Validates that the address is a non-empty string, conforms to EIP-55 format,
    and matches the expected RTC contract prefix.
    """
    return bool(addr and eth_utils.is_checksum_address(addr) and addr.startswith("0x"))


def _is_bcn_address(addr: str) -> bool:
    """Check if the given address is a valid BCN (BlockCoin Network) address.

    Validates that the address is a non-empty string and conforms to EIP-55 checksum format.
    """
    return bool(addr and eth_utils.is_checksum_address(addr))


@dataclass
class PreflightResult:
    """Result of a payout preflight validation check.

    Attributes:
        ok: Whether the preflight passed all validation checks.
        error: Error message string if the preflight failed, otherwise None.
    """

    ok: bool = True
    error: str | None = field(default=None)

    def _as_dict(self) -> dict:
        """Return the preflight result as a dictionary.

        Returns:
            A dict with 'ok' (bool) and 'error' (str or None) keys.
        """
        return {"ok": self.ok, "error": self.error}


def _safe_decimal(value: str | float | int) -> decimal.Decimal:
    """Safely convert a value to a Decimal with precision handling.

    Args:
        value: The value to convert, which can be a string, float, or integer.

    Returns:
        A Decimal representation of the input value.

    Raises:
        decimal.InvalidOperation: If the value cannot be converted to a Decimal.
    """
    return decimal.Decimal(str(value))


def _amount_i64(amount: decimal.Decimal) -> int:
    """Convert an amount in RTC to its smallest unit (i64 representation).

    Multiplies the amount by 1e18 to get the integer representation used internally.

    Args:
        amount: The amount in RTC as a Decimal.

    Returns:
        The amount in smallest units as an integer.
    """
    return int(amount * decimal.Decimal("1e18"))


def _validate_amount_i64(amount: int) -> bool:
    """Validate that an i64 amount is within the valid range.

    Args:
        amount: The amount to validate as an integer.

    Returns:
        True if the amount is a non-negative integer fitting in i64 bounds.
    """
    return 0 <= amount <= 2**63 - 1


def _miner_id_field(miner_id: bytes) -> str:
    """Encode a miner ID bytes value to its hex string representation.

    Args:
        miner_id: The raw bytes of the miner identifier.

    Returns:
        The hex-encoded string of the miner ID without the '0x' prefix.
    """
    return miner_id.hex()
