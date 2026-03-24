# SPDX-License-Identifier: MIT
"""Data models for RustChain API responses."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Health:
    ok: bool = False
    version: str = ""
    uptime_s: float = 0.0
    db_rw: bool = False
    tip_age_slots: int = 0
    backup_age_hours: float = 0.0


@dataclass
class Epoch:
    epoch: int = 0
    slot: int = 0
    blocks_per_epoch: int = 144
    enrolled_miners: int = 0
    epoch_pot: float = 0.0
    total_supply_rtc: float = 0.0


@dataclass
class Miner:
    miner: str = ""
    device_arch: str = ""
    device_family: str = ""
    hardware_type: str = ""
    antiquity_multiplier: float = 0.0
    entropy_score: float = 0.0
    last_attest: Optional[int] = None
    first_attest: Optional[int] = None


@dataclass
class Balance:
    wallet_id: str = ""
    balance: float = 0.0
    pending: float = 0.0
    amount_rtc: float = 0.0
    amount_i64: int = 0
    miner_id: str = ""


@dataclass
class Block:
    height: int = 0
    hash: str = ""
    timestamp: int = 0
    miner: str = ""
    transactions: int = 0


@dataclass
class Transaction:
    txid: str = ""
    from_wallet: str = ""
    to_wallet: str = ""
    amount: float = 0.0
    timestamp: int = 0
