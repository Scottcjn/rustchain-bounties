"""
Unit tests for sdk/python/rustchain_sdk/wallet.py — internal helpers.

Covers: _to_words, _from_words, _sha256d, _hmac_sha512, RustChainWallet._generate_address.
"""

import hashlib
import hmac
import os
import sys

import pytest


# ---------------------------------------------------------------------------
# Import helper
# ---------------------------------------------------------------------------

@pytest.fixture()
def wallet_mod():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "python"))
    from rustchain_sdk import wallet as mod
    yield mod
    sys.path.pop(0)


# ===========================================================================
# _to_words / _from_words
# ===========================================================================

class TestToWords:
    """Tests for wallet._to_words."""

    def test_converts_bytes_to_words(self, wallet_mod):
        data = b"\x00\x00\x00\x01"
        words = wallet_mod._to_words(data, wallet_mod._BIP39_WORDLIST)
        assert len(words) == 2
        assert all(isinstance(w, str) for w in words)

    def test_word_indices_are_modulo_wordlist(self, wallet_mod):
        """Each pair of bytes maps to an index % len(wordlist)."""
        data = b"\xff\xff"
        words = wallet_mod._to_words(data, wallet_mod._BIP39_WORDLIST)
        idx = int.from_bytes(b"\xff\xff", "big") % len(wallet_mod._BIP39_WORDLIST)
        assert words[0] == wallet_mod._BIP39_WORDLIST[idx]

    def test_single_byte_pair(self, wallet_mod):
        data = b"\x00\x00"
        words = wallet_mod._to_words(data, wallet_mod._BIP39_WORDLIST)
        assert len(words) == 1
        assert words[0] == wallet_mod._BIP39_WORDLIST[0]  # "abandon"

    def test_empty_bytes(self, wallet_mod):
        assert wallet_mod._to_words(b"", wallet_mod._BIP39_WORDLIST) == []


class TestFromWords:
    """Tests for wallet._from_words."""

    def test_roundtrip(self, wallet_mod):
        original = b"\x01\x02\x03\x04"
        words = wallet_mod._to_words(original, wallet_mod._BIP39_WORDLIST)
        restored = wallet_mod._from_words(words, wallet_mod._BIP39_WORDLIST)
        assert restored == original

    def test_roundtrip_long(self, wallet_mod):
        original = b"\xab\xcd\xef\x00\x11\x22\x33\x44"
        words = wallet_mod._to_words(original, wallet_mod._BIP39_WORDLIST)
        restored = wallet_mod._from_words(words, wallet_mod._BIP39_WORDLIST)
        assert restored == original

    def test_unknown_word_raises(self, wallet_mod):
        with pytest.raises(ValueError, match="Unknown word"):
            wallet_mod._from_words(["not_a_real_bip39_word_xyz"], wallet_mod._BIP39_WORDLIST)


# ===========================================================================
# _sha256d
# ===========================================================================

class TestSha256d:
    """Tests for wallet._sha256d."""

    def test_returns_32_bytes(self, wallet_mod):
        result = wallet_mod._sha256d(b"test data")
        assert len(result) == 32

    def test_deterministic(self, wallet_mod):
        data = b"same input"
        assert wallet_mod._sha256d(data) == wallet_mod._sha256d(data)

    def test_different_inputs_different_outputs(self, wallet_mod):
        assert wallet_mod._sha256d(b"aaa") != wallet_mod._sha256d(b"bbb")

    def test_is_double_sha256(self, wallet_mod):
        data = b"verify double hash"
        expected = hashlib.sha256(hashlib.sha256(data).digest()).digest()
        assert wallet_mod._sha256d(data) == expected


# ===========================================================================
# _hmac_sha512
# ===========================================================================

class TestHmacSha512:
    """Tests for wallet._hmac_sha512."""

    def test_returns_64_bytes(self, wallet_mod):
        result = wallet_mod._hmac_sha512(b"key", b"data")
        assert len(result) == 64

    def test_matches_stdlib(self, wallet_mod):
        key, data = b"test-key", b"test-data"
        expected = hmac.new(key, data, hashlib.sha512).digest()
        assert wallet_mod._hmac_sha512(key, data) == expected

    def test_different_keys_different_output(self, wallet_mod):
        assert wallet_mod._hmac_sha512(b"key1", b"data") != wallet_mod._hmac_sha512(b"key2", b"data")

    def test_different_data_different_output(self, wallet_mod):
        assert wallet_mod._hmac_sha512(b"key", b"data1") != wallet_mod._hmac_sha512(b"key", b"data2")


# ===========================================================================
# RustChainWallet._generate_address
# ===========================================================================

class TestGenerateAddress:
    """Tests for RustChainWallet._generate_address."""

    def test_address_starts_with_rtc(self, wallet_mod):
        w = wallet_mod.RustChainWallet.create(strength=128)
        assert w.address.startswith("RTC")

    def test_address_is_hex_after_prefix(self, wallet_mod):
        w = wallet_mod.RustChainWallet.create()
        hex_part = w.address[3:]
        assert len(hex_part) == 40  # 20 bytes = 40 hex chars
        int(hex_part, 16)  # should not raise

    def test_deterministic_from_same_private_key(self, wallet_mod):
        """Same private key should always produce the same address."""
        w1 = wallet_mod.RustChainWallet.create()
        addr1 = wallet_mod.RustChainWallet._generate_address(w1._private_key)
        addr2 = wallet_mod.RustChainWallet._generate_address(w1._private_key)
        assert addr1 == addr2

    def test_different_private_keys_different_addresses(self, wallet_mod):
        w1 = wallet_mod.RustChainWallet.create()
        w2 = wallet_mod.RustChainWallet.create()
        assert w1.address != w2.address
