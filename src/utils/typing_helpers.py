"""Type-hinted helper functions for RustChain Bounties.

This module provides utility functions with full PEP 484 type annotations
for use across the RustChain bounties ecosystem.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import re


def validate_address(address: str) -> bool:
    """Validate a blockchain address format.
    
    Args:
        address: The blockchain address to validate.
        
    Returns:
        True if the address is valid, False otherwise.
    """
    if not address or not isinstance(address, str):
        return False
    
    pattern = r"^(0x)?[a-fA-F0-9]{40}$"
    return bool(re.match(pattern, address))


def calculate_reward(
    base_amount: float,
    multiplier: float = 1.0,
    bonus: float = 0.0
) -> float:
    """Calculate the total reward for a bounty completion.
    
    Args:
        base_amount: The base reward amount in RTC.
        multiplier: A multiplier for difficulty or performance.
        bonus: Additional bonus amount.
        
    Returns:
        The total calculated reward.
    """
    if base_amount < 0:
        raise ValueError("Base amount cannot be negative")
    if multiplier < 0:
        raise ValueError("Multiplier cannot be negative")
    if bonus < 0:
        raise ValueError("Bonus cannot be negative")
    
    return (base_amount * multiplier) + bonus


def parse_bounty_data(
    raw_data: Dict[str, Any]
) -> Tuple[Optional[str], Optional[int], Optional[datetime]]:
    """Parse raw bounty data into structured format.
    
    Args:
        raw_data: Dictionary containing raw bounty information.
        
    Returns:
        Tuple of (bounty_id, reward_amount, created_date).
    """
    bounty_id: Optional[str] = raw_data.get("id")
    reward_amount: Optional[int] = raw_data.get("reward")
    created_date: Optional[datetime] = None
    
    if "created_at" in raw_data:
        try:
            created_date = datetime.fromisoformat(raw_data["created_at"])
        except (ValueError, TypeError):
            created_date = None
    
    return bounty_id, reward_amount, created_date


def format_timestamp(
    dt: datetime,
    include_time: bool = True
) -> str:
    """Format a datetime object as a string.
    
    Args:
        dt: The datetime object to format.
        include_time: Whether to include time in the output.
        
    Returns:
        Formatted timestamp string.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    if include_time:
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        return dt.strftime("%Y-%m-%d")


def check_miner_status(
    miner_id: str,
    active_miners: List[str],
    pending_miners: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Check the status of a miner in the network.
    
    Args:
        miner_id: The unique identifier of the miner.
        active_miners: List of currently active miner IDs.
        pending_miners: Optional list of pending miner IDs.
        
    Returns:
        Dictionary with status information.
    """
    if pending_miners is None:
        pending_miners = []
    
    status: str = "inactive"
    if miner_id in active_miners:
        status = "active"
    elif miner_id in pending_miners:
        status = "pending"
    
    return {
        "miner_id": miner_id,
        "status": status,
        "is_active": status == "active",
        "is_pending": status == "pending",
    }


def merge_bounty_lists(
    list_a: List[Dict[str, Any]],
    list_b: List[Dict[str, Any]],
    key_field: str = "id"
) -> List[Dict[str, Any]]:
    """Merge two lists of bounty data, removing duplicates.
    
    Args:
        list_a: First list of bounty dictionaries.
        list_b: Second list of bounty dictionaries.
        key_field: The field name to use for duplicate detection.
        
    Returns:
        Merged list with duplicates removed.
    """
    seen_ids: set = set()
    merged: List[Dict[str, Any]] = []
    
    for bounty in list_a + list_b:
        bounty_id = bounty.get(key_field)
        if bounty_id is not None and bounty_id not in seen_ids:
            seen_ids.add(bounty_id)
            merged.append(bounty)
    
    return merged


def sanitize_input(text: Optional[str], max_length: int = 1000) -> str:
    """Sanitize user input text.
    
    Args:
        text: The input text to sanitize.
        max_length: Maximum allowed length.
        
    Returns:
        Sanitized text string.
    """
    if text is None:
        return ""
    
    cleaned = text.strip()
    cleaned = cleaned[:max_length]
    
    return cleaned
