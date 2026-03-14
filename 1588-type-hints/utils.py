#!/usr/bin/env python3
"""RustChain utility functions with type hints"""
from typing import Optional, List, Dict, Any, Union

def validate_address(address: str) -> bool:
    """Validate RTC wallet address format"""
    if not address or not isinstance(address, str):
        return False
    if not address.startswith("RTC"):
        return False
    if len(address) != 42:
        return False
    return True

def format_balance(balance_wei: int, decimals: int = 18) -> float:
    """Convert balance from wei to RTC"""
    return balance_wei / (10 ** decimals)

def parse_transaction(tx_data: Dict[str, Any]) -> Dict[str, Union[str, int, bool]]:
    """Parse transaction data into readable format"""
    return {
        "hash": tx_data.get("hash", ""),
        "from": tx_data.get("from", ""),
        "to": tx_data.get("to", ""),
        "value": int(tx_data.get("value", 0), 16) if isinstance(tx_data.get("value"), str) else tx_data.get("value", 0),
        "success": tx_data.get("status", "0x1") == "0x1"
    }

def calculate_gas_cost(gas_used: int, gas_price_wei: int) -> float:
    """Calculate transaction gas cost in RTC"""
    total_wei = gas_used * gas_price_wei
    return format_balance(total_wei)

def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries"""
    return {**dict1, **dict2}

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary"""
    return dictionary.get(key, default)

def format_block_number(block: Union[int, str]) -> int:
    """Format block number from hex or int"""
    if isinstance(block, str):
        return int(block, 16)
    return block

def filter_transactions(transactions: List[Dict[str, Any]], address: Optional[str] = None, min_value: Optional[int] = None) -> List[Dict[str, Any]]:
    """Filter transactions by address and/or minimum value"""
    result = transactions
    if address:
        result = [tx for tx in result if tx.get("from") == address or tx.get("to") == address]
    if min_value is not None:
        result = [tx for tx in result if int(tx.get("value", 0), 16 if isinstance(tx.get("value"), str) else 10) >= min_value]
    return result
