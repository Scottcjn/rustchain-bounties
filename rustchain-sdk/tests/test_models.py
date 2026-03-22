"""Tests for RustChain models."""

import pytest
from datetime import datetime
from rustchain.models import (
    HealthStatus,
    EpochInfo,
    Miner,
    Balance,
    TransferResult,
    Block,
    Transaction,
    AttestationStatus,
    ExplorerBlocks,
    ExplorerTransactions,
)


class TestHealthStatus:
    """Tests for HealthStatus model."""
    
    def test_health_status_creation(self):
        """Test creating HealthStatus."""
        health = HealthStatus(status="healthy", version="1.0.0")
        assert health.status == "healthy"
        assert health.version == "1.0.0"
    
    def test_health_status_optional_fields(self):
        """Test HealthStatus with optional fields."""
        health = HealthStatus(
            status="degraded",
            uptime=3600,
            peers=5
        )
        assert health.status == "degraded"
        assert health.uptime == 3600
        assert health.peers == 5


class TestEpochInfo:
    """Tests for EpochInfo model."""
    
    def test_epoch_info_creation(self):
        """Test creating EpochInfo."""
        epoch = EpochInfo(current_epoch=100, start_height=1000)
        assert epoch.current_epoch == 100
        assert epoch.start_height == 1000
    
    def test_epoch_info_with_timestamps(self):
        """Test EpochInfo with timestamps."""
        now = datetime.now()
        epoch = EpochInfo(
            current_epoch=50,
            start_height=500,
            start_time=now,
            total_blocks=100
        )
        assert epoch.start_time == now
        assert epoch.total_blocks == 100


class TestMiner:
    """Tests for Miner model."""
    
    def test_miner_creation(self):
        """Test creating Miner."""
        miner = Miner(
            id="miner123",
            address="addr123",
            stake=150.5,
            blocks_mined=25
        )
        assert miner.id == "miner123"
        assert miner.stake == 150.5
        assert miner.blocks_mined == 25
    
    def test_miner_with_attestation(self):
        """Test Miner with attestation status."""
        miner = Miner(
            id="miner456",
            address="addr456",
            stake=200.0,
            blocks_mined=50,
            attestation_status="verified"
        )
        assert miner.attestation_status == "verified"


class TestBalance:
    """Tests for Balance model."""
    
    def test_balance_creation(self):
        """Test creating Balance."""
        balance = Balance(
            wallet_id="wallet1",
            address="addr1",
            balance=100.0
        )
        assert balance.wallet_id == "wallet1"
        assert balance.balance == 100.0
    
    def test_balance_with_pending(self):
        """Test Balance with pending amount."""
        balance = Balance(
            wallet_id="wallet2",
            address="addr2",
            balance=50.0,
            pending=10.0,
            locked=5.0
        )
        assert balance.pending == 10.0
        assert balance.locked == 5.0


class TestTransferResult:
    """Tests for TransferResult model."""
    
    def test_transfer_result_creation(self):
        """Test creating TransferResult."""
        result = TransferResult(
            tx_hash="tx123",
            from_address="addr1",
            to_address="addr2",
            amount=10.0
        )
        assert result.tx_hash == "tx123"
        assert result.amount == 10.0
    
    def test_transfer_result_with_fee(self):
        """Test TransferResult with fee."""
        result = TransferResult(
            tx_hash="tx456",
            from_address="addr1",
            to_address="addr2",
            amount=100.0,
            fee=0.1,
            status="confirmed"
        )
        assert result.fee == 0.1
        assert result.status == "confirmed"


class TestBlock:
    """Tests for Block model."""
    
    def test_block_creation(self):
        """Test creating Block."""
        now = datetime.now()
        block = Block(
            height=1000,
            hash="block_hash",
            previous_hash="prev_hash",
            timestamp=now,
            miner="miner1"
        )
        assert block.height == 1000
        assert block.hash == "block_hash"
        assert block.timestamp == now
    
    def test_block_with_transactions(self):
        """Test Block with transaction count."""
        now = datetime.now()
        block = Block(
            height=2000,
            hash="block_hash2",
            previous_hash="prev_hash2",
            timestamp=now,
            miner="miner2",
            transactions=15,
            size=1024
        )
        assert block.transactions == 15
        assert block.size == 1024


class TestTransaction:
    """Tests for Transaction model."""
    
    def test_transaction_creation(self):
        """Test creating Transaction."""
        tx = Transaction(
            tx_hash="tx789",
            from_address="addr1",
            to_address="addr2",
            amount=25.0
        )
        assert tx.tx_hash == "tx789"
        assert tx.amount == 25.0
    
    def test_transaction_with_block(self):
        """Test Transaction with block info."""
        now = datetime.now()
        tx = Transaction(
            tx_hash="tx999",
            from_address="addr1",
            to_address="addr2",
            amount=50.0,
            block_height=500,
            status="confirmed",
            timestamp=now
        )
        assert tx.block_height == 500
        assert tx.status == "confirmed"


class TestAttestationStatus:
    """Tests for AttestationStatus model."""
    
    def test_attestation_status_creation(self):
        """Test creating AttestationStatus."""
        status = AttestationStatus(
            miner_id="miner1",
            status="active"
        )
        assert status.miner_id == "miner1"
        assert status.status == "active"
    
    def test_attestation_status_with_score(self):
        """Test AttestationStatus with score."""
        status = AttestationStatus(
            miner_id="miner2",
            status="verified",
            score=0.95,
            epoch=100
        )
        assert status.score == 0.95
        assert status.epoch == 100


class TestExplorerBlocks:
    """Tests for ExplorerBlocks model."""
    
    def test_explorer_blocks_creation(self):
        """Test creating ExplorerBlocks."""
        now = datetime.now()
        blocks = [
            Block(
                height=i,
                hash=f"hash{i}",
                previous_hash=f"prev{i}",
                timestamp=now,
                miner=f"miner{i}"
            )
            for i in range(10)
        ]
        
        explorer_blocks = ExplorerBlocks(
            blocks=blocks,
            total=100,
            page=1,
            per_page=10
        )
        
        assert len(explorer_blocks.blocks) == 10
        assert explorer_blocks.total == 100
        assert explorer_blocks.page == 1


class TestExplorerTransactions:
    """Tests for ExplorerTransactions model."""
    
    def test_explorer_transactions_creation(self):
        """Test creating ExplorerTransactions."""
        transactions = [
            Transaction(
                tx_hash=f"tx{i}",
                from_address=f"addr{i}",
                to_address=f"addr{i+1}",
                amount=i * 10.0
            )
            for i in range(5)
        ]
        
        explorer_txs = ExplorerTransactions(
            transactions=transactions,
            total=50,
            page=1,
            per_page=5
        )
        
        assert len(explorer_txs.transactions) == 5
        assert explorer_txs.total == 50
        assert explorer_txs.per_page == 5