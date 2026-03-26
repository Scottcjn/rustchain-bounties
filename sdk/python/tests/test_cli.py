"""
Unit tests for the RustChain CLI.
"""

import pytest
from unittest.mock import patch, MagicMock

from rustchain.cli import main


class TestCLI:
    def test_balance_command(self):
        with patch("rustchain.cli._balance") as mock:
            mock.return_value = None
            result = main(["balance", "my-wallet"])
            assert result == 0
            mock.assert_called_once()

    def test_health_command(self):
        with patch("rustchain.cli._health") as mock:
            mock.return_value = None
            result = main(["health"])
            assert result == 0
            mock.assert_called_once()

    def test_epoch_command(self):
        with patch("rustchain.cli._epoch") as mock:
            mock.return_value = None
            result = main(["epoch"])
            assert result == 0
            mock.assert_called_once()

    def test_miners_command(self):
        with patch("rustchain.cli._miners") as mock:
            mock.return_value = None
            result = main(["miners"])
            assert result == 0
            mock.assert_called_once()

    def test_miners_with_limit(self):
        with patch("rustchain.cli._miners") as mock:
            mock.return_value = None
            result = main(["miners", "--limit", "10"])
            assert result == 0
            args, kwargs = mock.call_args
            assert kwargs["limit"] == 10

    def test_blocks_command(self):
        with patch("rustchain.cli._explorer_blocks") as mock:
            mock.return_value = None
            result = main(["blocks"])
            assert result == 0
            args, kwargs = mock.call_args
            assert kwargs["limit"] == 20

    def test_blocks_with_custom_limit(self):
        with patch("rustchain.cli._explorer_blocks") as mock:
            mock.return_value = None
            result = main(["blocks", "--limit", "50"])
            assert result == 0
            args, kwargs = mock.call_args
            assert kwargs["limit"] == 50

    def test_txs_command(self):
        with patch("rustchain.cli._explorer_txs") as mock:
            mock.return_value = None
            result = main(["txs"])
            assert result == 0

    def test_txs_with_wallet_id(self):
        with patch("rustchain.cli._explorer_txs") as mock:
            mock.return_value = None
            result = main(["txs", "my-wallet"])
            assert result == 0
            args, kwargs = mock.call_args
            assert kwargs["wallet_id"] == "my-wallet"

    def test_base_url_passed_to_commands(self):
        with patch("rustchain.cli._health") as mock:
            mock.return_value = None
            result = main(["--base-url", "https://custom.example.com", "health"])
            assert result == 0
            args, kwargs = mock.call_args
            assert kwargs["base_url"] == "https://custom.example.com"

    def test_api_key_passed_to_commands(self):
        with patch("rustchain.cli._health") as mock:
            mock.return_value = None
            result = main(["--api-key", "secret-key", "health"])
            assert result == 0
            args, kwargs = mock.call_args
            assert kwargs["api_key"] == "secret-key"

    def test_no_verify_ssl_passed(self):
        with patch("rustchain.cli._health") as mock:
            mock.return_value = None
            result = main(["--no-verify-ssl", "health"])
            assert result == 0
            args, kwargs = mock.call_args
            assert kwargs["verify_ssl"] is False

    def test_version_flag(self):
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_missing_command_shows_error(self):
        # argparse handles this by exiting with code 2
        # We just verify it doesn't crash
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 2
