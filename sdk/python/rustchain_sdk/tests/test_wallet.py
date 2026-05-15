"""
Tests for RustChainWallet.
"""

import pytest
from rustchain_sdk.wallet import RustChainWallet


class TestRustChainWalletCreate:
    """Test wallet creation."""

    def test_create_wallet_128bit(self):
        """Create a 12-word (128-bit) wallet."""
        wallet = RustChainWallet.create(strength=128)
        assert wallet.address.startswith("RTC")
        assert len(wallet.address) == 3 + 40  # "RTC" + 40 hex chars
        assert len(wallet.seed_phrase) == 12

    def test_create_wallet_256bit(self):
        """Create a 24-word (256-bit) wallet."""
        wallet = RustChainWallet.create(strength=256)
        assert wallet.address.startswith("RTC")
        assert len(wallet.seed_phrase) == 24

    def test_create_wallet_invalid_strength(self):
        """Invalid strength raises ValueError."""
        with pytest.raises(ValueError, match="Strength must be 128"):
            RustChainWallet.create(strength=64)

    def test_wallet_address_is_deterministic_from_seed(self):
        """Same seed phrase always produces same address."""
        wallet1 = RustChainWallet.create(strength=128)
        wallet2 = RustChainWallet.from_seed_phrase(wallet1.seed_phrase)
        assert wallet1.address == wallet2.address

    def test_wallet_address_unique_per_wallet(self):
        """Two wallets have different addresses."""
        wallet1 = RustChainWallet.create(strength=128)
        wallet2 = RustChainWallet.create(strength=128)
        assert wallet1.address != wallet2.address


class TestRustChainWalletProperties:
    """Test wallet properties."""

    def test_address_property(self):
        """Address property returns correct address."""
        wallet = RustChainWallet.create(strength=128)
        assert wallet.address == wallet._address
        assert wallet.address.startswith("RTC")

    def test_public_key_hex_property(self):
        """Public key hex is a 64-char hex string."""
        wallet = RustChainWallet.create(strength=128)
        assert len(wallet.public_key_hex) == 64
        assert all(c in "0123456789abcdef" for c in wallet.public_key_hex)

    def test_seed_phrase_property(self):
        """Seed phrase is a list of words."""
        wallet = RustChainWallet.create(strength=128)
        assert isinstance(wallet.seed_phrase, list)
        assert len(wallet.seed_phrase) == 12
        assert all(isinstance(w, str) for w in wallet.seed_phrase)

    def test_private_key_hex_property(self):
        """Private key hex is a 64-char hex string."""
        wallet = RustChainWallet.create(strength=128)
        assert len(wallet.private_key_hex) == 64
        assert all(c in "0123456789abcdef" for c in wallet.private_key_hex)


class TestRustChainWalletSign:
    """Test signing operations."""

    def test_sign_returns_bytes(self):
        """Sign returns bytes of correct length."""
        wallet = RustChainWallet.create(strength=128)
        message = b"hello world"
        signature = wallet.sign(message)
        assert isinstance(signature, bytes)
        assert len(signature) == 64  # Ed25519 signature size

    def test_sign_is_deterministic(self):
        """Same message and key always produce same signature."""
        wallet = RustChainWallet.create(strength=128)
        message = b"hello world"
        sig1 = wallet.sign(message)
        sig2 = wallet.sign(message)
        assert sig1 == sig2

    def test_sign_different_messages_different_signatures(self):
        """Different messages produce different signatures."""
        wallet = RustChainWallet.create(strength=128)
        sig1 = wallet.sign(b"message one")
        sig2 = wallet.sign(b"message two")
        assert sig1 != sig2


class TestRustChainWalletTransfer:
    """Test transfer signing."""

    def test_sign_transfer_returns_dict(self):
        """sign_transfer returns a properly structured dict."""
        wallet = RustChainWallet.create(strength=128)
        transfer = wallet.sign_transfer("RTCrecipient123", 1000, fee=5)
        assert isinstance(transfer, dict)
        assert "from" in transfer
        assert "to" in transfer
        assert "amount" in transfer
        assert "fee" in transfer
        assert "timestamp" in transfer
        assert "signature" in transfer

    def test_sign_transfer_amount_and_fee(self):
        """Transfer contains correct amount and fee."""
        wallet = RustChainWallet.create(strength=128)
        transfer = wallet.sign_transfer("RTCrecipient123", 500, fee=10)
        assert transfer["amount"] == 500
        assert transfer["fee"] == 10
        assert transfer["to"] == "RTCrecipient123"

    def test_sign_transfer_timestamp_is_recent(self):
        """Transfer timestamp is a recent unix timestamp."""
        import time
        wallet = RustChainWallet.create(strength=128)
        before = int(time.time())
        transfer = wallet.sign_transfer("RTCrecipient123", 500, fee=0)
        after = int(time.time())
        assert before <= transfer["timestamp"] <= after


class TestRustChainWalletExportImport:
    """Test wallet export and import."""

    def test_export_returns_dict(self):
        """Export returns a JSON-serializable dict."""
        wallet = RustChainWallet.create(strength=128)
        data = wallet.export()
        assert isinstance(data, dict)
        assert "version" in data
        assert "address" in data
        assert "seed_phrase" in data
        assert data["version"] == 1

    def test_import_restores_wallet(self):
        """Importing exported data restores wallet."""
        original = RustChainWallet.create(strength=128)
        data = original.export()
        restored = RustChainWallet.import_(data)
        assert restored.address == original.address
        assert restored.seed_phrase == original.seed_phrase

    def test_import_unknown_version_raises(self):
        """Importing unknown version raises ValueError."""
        with pytest.raises(ValueError, match="Unknown export version"):
            RustChainWallet.import_({"version": 99, "seed_phrase": []})

    def test_from_seed_phrase_12_words(self):
        """12-word seed phrase creates valid wallet."""
        words = ["abandon"] * 12
        wallet = RustChainWallet.from_seed_phrase(words)
        assert wallet.address.startswith("RTC")
        assert len(wallet.seed_phrase) == 12

    def test_from_seed_phrase_invalid_length_raises(self):
        """Invalid word count raises ValueError."""
        with pytest.raises(ValueError, match="Seed phrase must be 12 or 24"):
            RustChainWallet.from_seed_phrase(["abandon"] * 10)

class TestRustChainWalletEdgeCases:
    """Additional wallet edge-case tests for import and signing helpers."""

    def test_from_seed_phrase_unknown_word_still_derives_wallet(self):
        """from_seed_phrase derives from arbitrary words without wordlist lookup."""
        words = ["not-a-bip39-word"] * 12
        wallet = RustChainWallet.from_seed_phrase(words)
        assert wallet.seed_phrase == words
        assert wallet.address.startswith("RTC")
        assert len(wallet.private_key_hex) == 64

    def test_import_missing_seed_phrase_raises_key_error(self):
        """Import requires the exported seed_phrase field."""
        with pytest.raises(KeyError):
            RustChainWallet.import_({"version": 1})

    def test_sign_transfer_default_fee_is_zero(self):
        """Transfers omit fee argument default to zero."""
        wallet = RustChainWallet.create(strength=128)
        transfer = wallet.sign_transfer("RTCrecipient123", 42)
        assert transfer["fee"] == 0
        assert transfer["amount"] == 42
        assert len(transfer["signature"]) == 128

    def test_repr_contains_address_without_private_key_or_seed(self):
        """repr is safe: address only, no private key or seed words."""
        wallet = RustChainWallet.create(strength=128)
        rendered = repr(wallet)
        assert wallet.address in rendered
        assert wallet.private_key_hex not in rendered
        assert " ".join(wallet.seed_phrase) not in rendered
