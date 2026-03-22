"""
Tests for Wallet Manager - #2302
"""
import pytest
from wallet import WalletManager

class TestWalletManager:
    def test_init(self):
        manager = WalletManager()
        assert manager.name == "RustChain Wallet Manager"
    
    def test_create_wallet(self):
        manager = WalletManager()
        wallet = manager.create_wallet()
        assert "address" in wallet
        assert wallet["status"] == "created"
    
    def test_transfer(self):
        manager = WalletManager()
        result = manager.transfer("addr1", "addr2", 100)
        assert result["status"] == "completed"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
