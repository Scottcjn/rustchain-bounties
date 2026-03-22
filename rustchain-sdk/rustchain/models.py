"""Data models for RustChain SDK."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """Node health status."""
    status: str = Field(..., description="Health status (e.g., 'healthy', 'degraded')")
    version: Optional[str] = Field(None, description="Node version")
    uptime: Optional[int] = Field(None, description="Uptime in seconds")
    peers: Optional[int] = Field(None, description="Number of connected peers")
    timestamp: Optional[datetime] = Field(None, description="Status timestamp")


class EpochInfo(BaseModel):
    """Epoch information."""
    current_epoch: int = Field(..., description="Current epoch number")
    start_height: int = Field(..., description="Starting block height")
    end_height: Optional[int] = Field(None, description="Ending block height")
    start_time: Optional[datetime] = Field(None, description="Epoch start time")
    end_time: Optional[datetime] = Field(None, description="Epoch end time")
    total_blocks: Optional[int] = Field(None, description="Total blocks in epoch")
    active_miners: Optional[int] = Field(None, description="Number of active miners")


class Miner(BaseModel):
    """Miner information."""
    id: str = Field(..., description="Miner ID")
    address: str = Field(..., description="Miner address")
    stake: float = Field(..., description="Miner stake")
    blocks_mined: int = Field(..., description="Total blocks mined")
    last_active: Optional[datetime] = Field(None, description="Last active timestamp")
    attestation_status: Optional[str] = Field(None, description="Attestation status")
    reputation: Optional[float] = Field(None, description="Miner reputation score")


class Balance(BaseModel):
    """Wallet balance."""
    wallet_id: str = Field(..., description="Wallet ID")
    address: str = Field(..., description="Wallet address")
    balance: float = Field(..., description="RTC balance")
    pending: Optional[float] = Field(None, description="Pending balance")
    locked: Optional[float] = Field(None, description="Locked balance")
    last_updated: Optional[datetime] = Field(None, description="Last updated timestamp")


class TransferResult(BaseModel):
    """Transfer result."""
    tx_hash: str = Field(..., description="Transaction hash")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    amount: float = Field(..., description="Transfer amount")
    fee: Optional[float] = Field(None, description="Transaction fee")
    timestamp: Optional[datetime] = Field(None, description="Transfer timestamp")
    status: Optional[str] = Field(None, description="Transfer status")


class Block(BaseModel):
    """Block information."""
    height: int = Field(..., description="Block height")
    hash: str = Field(..., description="Block hash")
    previous_hash: str = Field(..., description="Previous block hash")
    timestamp: datetime = Field(..., description="Block timestamp")
    miner: str = Field(..., description="Miner ID")
    transactions: Optional[int] = Field(None, description="Number of transactions")
    size: Optional[int] = Field(None, description="Block size in bytes")
    epoch: Optional[int] = Field(None, description="Epoch number")
    attestations: Optional[int] = Field(None, description="Number of attestations")


class Transaction(BaseModel):
    """Transaction information."""
    tx_hash: str = Field(..., description="Transaction hash")
    from_address: str = Field(..., description="Sender address")
    to_address: str = Field(..., description="Recipient address")
    amount: float = Field(..., description="Transaction amount")
    fee: Optional[float] = Field(None, description="Transaction fee")
    timestamp: Optional[datetime] = Field(None, description="Transaction timestamp")
    block_height: Optional[int] = Field(None, description="Block height")
    status: Optional[str] = Field(None, description="Transaction status")
    type: Optional[str] = Field(None, description="Transaction type")


class AttestationStatus(BaseModel):
    """Attestation status."""
    miner_id: str = Field(..., description="Miner ID")
    status: str = Field(..., description="Attestation status")
    last_attestation: Optional[datetime] = Field(None, description="Last attestation time")
    hardware_hash: Optional[str] = Field(None, description="Hardware attestation hash")
    score: Optional[float] = Field(None, description="Attestation score")
    epoch: Optional[int] = Field(None, description="Current epoch")


class ExplorerBlocks(BaseModel):
    """Explorer blocks response."""
    blocks: List[Block] = Field(..., description="List of blocks")
    total: int = Field(..., description="Total number of blocks")
    page: Optional[int] = Field(None, description="Current page")
    per_page: Optional[int] = Field(None, description="Blocks per page")


class ExplorerTransactions(BaseModel):
    """Explorer transactions response."""
    transactions: List[Transaction] = Field(..., description="List of transactions")
    total: int = Field(..., description="Total number of transactions")
    page: Optional[int] = Field(None, description="Current page")
    per_page: Optional[int] = Field(None, description="Transactions per page")