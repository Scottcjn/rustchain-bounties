"""
Tests for the CLI wrapper (click commands).
"""

from __future__ import annotations

import json

import pytest
import respx
from click.testing import CliRunner

from rustchain.cli import cli

from .conftest import (
    ATTESTATION_RESPONSE,
    BALANCE_RESPONSE,
    BLOCKS_RESPONSE,
    EPOCH_RESPONSE,
    HEALTH_RESPONSE,
    MINERS_RESPONSE,
    NODE_URL,
    TRANSACTIONS_RESPONSE,
)


@pytest.fixture()
def runner():
    return CliRunner()


class TestCLIHealth:
    def test_health_command(self, runner, mock_api):
        result = runner.invoke(cli, ["--node", NODE_URL, "health"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "ok"
        assert data["block_height"] == 142857


class TestCLIEpoch:
    def test_epoch_command(self, runner, mock_api):
        result = runner.invoke(cli, ["--node", NODE_URL, "epoch"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["epoch"] == 47


class TestCLIMiners:
    def test_miners_command(self, runner, mock_api):
        result = runner.invoke(cli, ["--node", NODE_URL, "miners", "--limit", "2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 2


class TestCLIBalance:
    def test_balance_command(self, runner, mock_api):
        result = runner.invoke(cli, ["--node", NODE_URL, "balance", "RTC_test_wallet"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["balance"] == 1500.75


class TestCLIAttestation:
    def test_attestation_command(self, runner, mock_api):
        result = runner.invoke(cli, ["--node", NODE_URL, "attestation", "miner-alpha-001"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["valid"] is True


class TestCLIBlocks:
    def test_blocks_command(self, runner, mock_api):
        result = runner.invoke(cli, ["--node", NODE_URL, "blocks", "--limit", "2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 2


class TestCLITransactions:
    def test_transactions_command(self, runner, mock_api):
        result = runner.invoke(cli, ["--node", NODE_URL, "transactions"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


class TestCLIErrorHandling:
    def test_server_error_shows_message(self, runner):
        with respx.mock(base_url=NODE_URL) as router:
            router.get("/health").respond(status_code=500, text="fail")
            result = runner.invoke(cli, ["--node", NODE_URL, "health"])
            assert result.exit_code == 1
            assert "Error" in result.output


class TestCLIVersion:
    def test_version_flag(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower() or "." in result.output
