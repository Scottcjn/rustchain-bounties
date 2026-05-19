"""
Unit and integration tests for the dashboard API health endpoints and error redaction.

Verifies that client responses contain generic details while server logs retain
full exception context for database, Solana RPC, and wRTC mint failures.
"""

import asyncio
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bridge import dashboard_api


class TestBridgeHealth:
    """Test suite for dashboard health check endpoints."""

    @pytest.fixture
    def mock_db(self) -> MagicMock:
        """Return a mocked database connection."""
        mock = MagicMock()
        mock.is_healthy = AsyncMock(return_value=True)
        return mock

    @pytest.fixture
    def mock_solana(self) -> MagicMock:
        """Return a mocked Solana RPC client."""
        mock = MagicMock()
        mock.is_healthy = AsyncMock(return_value=True)
        return mock

    @pytest.fixture
    def mock_wrtc(self) -> MagicMock:
        """Return a mocked wRTC mint checker."""
        mock = MagicMock()
        mock.is_healthy = AsyncMock(return_value=True)
        return mock

    @pytest.fixture
    def healthy_dashboard(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock
    ) -> dashboard_api.DashboardAPI:
        """Return a DashboardAPI instance with all dependencies healthy."""
        return dashboard_api.DashboardAPI(
            db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc
        )

    @pytest.mark.asyncio
    async def test_health_all_ok(self, healthy_dashboard: dashboard_api.DashboardAPI) -> None:
        """Health endpoint returns OK when all components are healthy."""
        result = await healthy_dashboard.health()
        assert result["status"] == "healthy"
        assert result["database"] == "ok"
        assert result["solana_rpc"] == "ok"
        assert result["wrtc_mint"] == "ok"

    @pytest.mark.asyncio
    async def test_health_database_down(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Client response hides database exception details; server logs full error."""
        mock_db.is_healthy.side_effect = ConnectionRefusedError("Cannot connect to DB")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            result = await api.health()

        assert result["database"] == "unavailable"
        assert result["database_detail"] == "The database service is temporarily unavailable."
        assert "Cannot connect to DB" in caplog.text
        assert "ConnectionRefusedError" in caplog.text

    @pytest.mark.asyncio
    async def test_health_solana_down(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Client response hides Solana RPC exception details; server logs full error."""
        mock_solana.is_healthy.side_effect = TimeoutError("RPC timeout")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            result = await api.health()

        assert result["solana_rpc"] == "unavailable"
        assert result["solana_rpc_detail"] == "The Solana RPC service is temporarily unavailable."
        assert "RPC timeout" in caplog.text
        assert "TimeoutError" in caplog.text

    @pytest.mark.asyncio
    async def test_health_wrtc_mint_down(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Client response hides wRTC mint exception details; server logs full error."""
        mock_wrtc.is_healthy.side_effect = RuntimeError("Mint check failed")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            result = await api.health()

        assert result["wrtc_mint"] == "unavailable"
        assert result["wrtc_mint_detail"] == "The wRTC mint check service is temporarily unavailable."
        assert "Mint check failed" in caplog.text
        assert "RuntimeError" in caplog.text

    @pytest.mark.asyncio
    async def test_health_all_down(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """All dependencies fail; client gets generic messages, server logs all exceptions."""
        mock_db.is_healthy.side_effect = ConnectionError("DB connection lost")
        mock_solana.is_healthy.side_effect = TimeoutError("Solana RPC timeout")
        mock_wrtc.is_healthy.side_effect = ValueError("Invalid wRTC response")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            result = await api.health()

        assert result["status"] == "degraded"
        assert result["database"] == "unavailable"
        assert result["solana_rpc"] == "unavailable"
        assert result["wrtc_mint"] == "unavailable"
        assert "DB connection lost" in caplog.text
        assert "Solana RPC timeout" in caplog.text
        assert "Invalid wRTC response" in caplog.text

    @pytest.mark.asyncio
    async def test_health_partial_failure(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Only one component fails; status is degraded but others report ok."""
        mock_solana.is_healthy.side_effect = Exception("Unexpected RPC error")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            result = await api.health()

        assert result["status"] == "degraded"
        assert result["database"] == "ok"
        assert result["solana_rpc"] == "unavailable"
        assert result["wrtc_mint"] == "ok"
        assert "Unexpected RPC error" in caplog.text

    @pytest.mark.asyncio
    async def test_health_timeout_isolation(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock
    ) -> None:
        """Timeout on one service does not cascade to others."""
        mock_wrtc.is_healthy.side_effect = asyncio.TimeoutError("wRTC timed out")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        result = await api.health()
        assert result["database"] == "ok"
        assert result["solana_rpc"] == "ok"
        assert result["wrtc_mint"] == "unavailable"
        assert result["status"] == "degraded"


class TestHealthEndpointIntegration:
    """Integration-style tests for the health endpoint serialization."""

    @pytest.mark.asyncio
    async def test_health_response_json_serializable(self, healthy_dashboard: dashboard_api.DashboardAPI) -> None:
        """Health response can be serialized to JSON without error."""
        result = await healthy_dashboard.health()
        json.dumps(result)

    @pytest.mark.asyncio
    async def test_health_contains_expected_keys(self, healthy_dashboard: dashboard_api.DashboardAPI) -> None:
        """Health response contains all required keys."""
        result = await healthy_dashboard.health()
        expected_keys = {"status", "database", "solana_rpc", "wrtc_mint", "database_detail", "solana_rpc_detail", "wrtc_mint_detail"}
        assert expected_keys.issubset(result.keys())

    @pytest.mark.asyncio
    async def test_health_detail_field_omitted_on_success(self, healthy_dashboard: dashboard_api.DashboardAPI) -> None:
        """Detail fields are not present when the service is healthy."""
        result = await healthy_dashboard.health()
        assert "database_detail" not in result or result["database_detail"] is None
        assert "solana_rpc_detail" not in result or result["solana_rpc_detail"] is None
        assert "wrtc_mint_detail" not in result or result["wrtc_mint_detail"] is None

    @pytest.mark.asyncio
    async def test_health_detail_field_present_on_failure(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock
    ) -> None:
        """Detail fields are present and contain user‑safe messages on failure."""
        mock_db.is_healthy.side_effect = Exception("sensitive")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)
        result = await api.health()
        assert "database_detail" in result
        assert "sensitive" not in result["database_detail"]

    @pytest.mark.asyncio
    async def test_health_logging_includes_traceback(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Exception traceback is logged on server‑side."""
        mock_db.is_healthy.side_effect = ConnectionError("Conn lost")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            await api.health()

        assert any("Traceback" in record.message for record in caplog.records)

    @pytest.mark.asyncio
    async def test_health_concurrent_failures_logged_separately(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Multiple concurrent failures each produce a separate log record."""
        mock_db.is_healthy.side_effect = OSError("DB err")
        mock_solana.is_healthy.side_effect = OSError("Solana err")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            await api.health()

        # Expect two separate ERROR logs (one for each failed check)
        error_logs = [rec for rec in caplog.records if rec.levelno == logging.ERROR]
        assert len(error_logs) == 2

    @pytest.mark.asyncio
    async def test_health_exception_types_logged(
        self, mock_db: MagicMock, mock_solana: MagicMock, mock_wrtc: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Exception type is included in server log."""
        mock_solana.is_healthy.side_effect = PermissionError("Access denied")
        api = dashboard_api.DashboardAPI(db=mock_db, solana_rpc=mock_solana, wrtc_mint=mock_wrtc)

        with caplog.at_level(logging.ERROR):
            await api.health()

        assert "PermissionError" in caplog.text