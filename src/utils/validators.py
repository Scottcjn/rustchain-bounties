"""Validation utilities with type hints for RustChain Bounties.

This module provides validation functions with complete type annotations
for bounty submissions, miner registrations, and reward claims.
"""

from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
import hashlib


def validate_reward_amount(amount: Union[int, float, Decimal]) -> bool:
    """Validate that a reward amount is positive and within bounds.
    
    Args:
        amount: The reward amount to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    if isinstance(amount, Decimal):
        numeric_value = float(amount)
    else:
        numeric_value = float(amount)
    
    return numeric_value > 0 and numeric_value < 1000000


def validate_submission_hash(
    submission_hash: str,
    expected_algorithm: str = "sha256"
) -> bool:
    """Validate a submission hash format.
    
    Args:
        submission_hash: The hash string to validate.
        expected_algorithm: The expected hashing algorithm.
        
    Returns:
        True if the hash format is valid.
    """
    hash_lengths: Dict[str, int] = {
        "sha256": 64,
        "sha512": 128,
        "md5": 32,
    }
    
    expected_length = hash_lengths.get(expected_algorithm, 64)
    
    if len(submission_hash) != expected_length:
        return False
    
    try:
        int(submission_hash, 16)
        return True
    except ValueError:
        return False


def validate_miner_config(config: Dict[str, Any]) -> List[str]:
    """Validate miner configuration dictionary.
    
    Args:
        config: The configuration dictionary to validate.
        
    Returns:
        List of validation error messages (empty if valid).
    """
    errors: List[str] = []
    
    required_fields: List[str] = ["miner_id", "endpoint", "public_key"]
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(config[field], str):
            errors.append(f"Field {field} must be a string")
    
    if "port" in config:
        port_value = config["port"]
        if not isinstance(port_value, int) or port_value < 1 or port_value > 65535:
            errors.append("Port must be an integer between 1 and 65535")
    
    return errors


def compute_verification_hash(data: Dict[str, Any]) -> str:
    """Compute a verification hash for bounty data.
    
    Args:
        data: The data dictionary to hash.
        
    Returns:
        SHA256 hash of the serialized data.
    """
    data_string = str(sorted(data.items()))
    hash_object = hashlib.sha256(data_string.encode())
    return hash_object.hexdigest()


def validate_claim_request(
    claim_data: Dict[str, Any]
) -> Dict[str, Union[bool, List[str]]]:
    """Validate a reward claim request.
    
    Args:
        claim_data: The claim request data.
        
    Returns:
        Dictionary with validation result and any errors.
    """
    errors: List[str] = []
    
    if "miner_id" not in claim_data:
        errors.append("miner_id is required")
    
    if "bounty_id" not in claim_data:
        errors.append("bounty_id is required")
    
    if "proof" not in claim_data:
        errors.append("proof of completion is required")
    elif not isinstance(claim_data["proof"], str):
        errors.append("proof must be a string")
    
    if "timestamp" in claim_data:
        if not isinstance(claim_data["timestamp"], (int, float)):
            errors.append("timestamp must be numeric")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
    }


def filter_active_bounties(
    bounties: List[Dict[str, Any]],
    status_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filter bounties by status.
    
    Args:
        bounties: List of bounty dictionaries.
        status_filter: Optional status to filter by.
        
    Returns:
        Filtered list of bounties.
    """
    if status_filter is None:
        return [b for b in bounties if b.get("status") == "active"]
    
    return [b for b in bounties if b.get("status") == status_filter]


def aggregate_rewards(
    reward_list: List[Dict[str, Any]],
    group_by: str = "miner_id"
) -> Dict[str, float]:
    """Aggregate rewards by a specified field.
    
    Args:
        reward_list: List of reward dictionaries.
        group_by: Field name to group by.
        
    Returns:
        Dictionary mapping group values to total rewards.
    """
    aggregated: Dict[str, float] = {}
    
    for reward in reward_list:
        key = reward.get(group_by, "unknown")
        amount = float(reward.get("amount", 0))
        
        if key in aggregated:
            aggregated[key] += amount
        else:
            aggregated[key] = amount
    
    return aggregated
