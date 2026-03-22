"""Tests for RustChain Python SDK.

Copyright (c) 2026 思捷娅科技 (SJYKJ)
MIT License
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from rustchain import RustChainClient, RustChainError, NodeUnhealthyError
from rustchain import MinerNotFoundError, InvalidSignatureError, RateLimitError
from rustchain import BadRequestError
from rustchain.client import RustChainSyncClient, HealthInfo, EpochInfo, StatsInfo
from rustchain.client import ChallengeResponse, AttestationResult, WithdrawalInfo
from rustchain.exceptions import RustChainError as BaseError


# ── Fixture data ───────────────────────────────────────────────────────────

HEALTH_OK = {"ok": True, "uptime_s": 31284, "version": "2.2.1-rip200", "db_rw": True, "tip_age_slots": 0, "backup_age_hours": 8.2}
HEALTH_BAD = {"ok": False, "uptime_s": 10, "version": "2.2.1", "db_rw": False, "tip_age_slots": 99, "backup_age_hours": 48.0}
EPOCH_DATA = {"epoch": 104, "slot": 15066, "blocks_per_epoch": 144, "enrolled_miners": 30, "epoch_pot": 1.5, "total_supply_rtc": 8388608}
STATS_DATA = {"block_time": 600, "chain_id": "rustchain-mainnet-v2", "epoch": 104, "features": ["RIP-0005"], "total_balance": 412913.41, "total_miners": 487, "version": "2.2.1", "pending_withdrawals": 0}
BALANCE_DATA = {"balance": 42.5}
MINERS_DATA = [{"miner_pk": "0xabc", "balance": 10.0}, {"miner_pk": "0xdef", "balance": 20.0}]
CHALLENGE_DATA = {"challenge": "0xdeadbeef", "expires_at": 3600}
ATTEST_RESULT = {"accepted": True, "message": "OK"}
ENROLL_RESULT = {"enrolled": True}
WITHDRAW_HISTORY = [{"withdrawal_id": "w1", "status": "pending", "amount": 10.0, "miner_pk": "0xabc"}]
WITHDRAW_STATUS = {"withdrawal_id": "w1", "status": "completed", "amount": 10.0, "miner_pk": "0xabc"}


# ── Exception tests ────────────────────────────────────────────────────────

class TestExceptions:
    def test_base_error(self):
        e = RustChainError("test", status_code=500)
        assert str(e) == "test"
        assert e.status_code == 500

    def test_node_unhealthy(self):
        e = NodeUnhealthyError("down")
        assert e.status_code is None

    def test_miner_not_found(self):
        e = MinerNotFoundError("nope", status_code=404)
        assert e.status_code == 404

    def test_rate_limit(self):
        e = RateLimitError("slow down", status_code=429)
        assert "slow" in str(e)

    def test_bad_request(self):
        e = BadRequestError("bad", status_code=400)
        assert e.status_code == 400

    def test_inheritance(self):
        assert issubclass(NodeUnhealthyError, RustChainError)
        assert issubclass(MinerNotFoundError, RustChainError)
        assert issubclass(RateLimitError, RustChainError)


# ── Data model tests ───────────────────────────────────────────────────────

class TestDataModels:
    def test_health_info(self):
        h = HealthInfo.from_dict(HEALTH_OK)
        assert h.ok is True
        assert h.version == "2.2.1-rip200"
        assert h.uptime_s == 31284

    def test_epoch_info(self):
        e = EpochInfo.from_dict(EPOCH_DATA)
        assert e.epoch == 104
        assert e.enrolled_miners == 30
        assert e.total_supply_rtc == 8388608

    def test_stats_info(self):
        s = StatsInfo.from_dict(STATS_DATA)
        assert s.chain_id == "rustchain-mainnet-v2"
        assert s.total_miners == 487

    def test_challenge_response(self):
        c = ChallengeResponse.from_dict(CHALLENGE_DATA)
        assert c.challenge == "0xdeadbeef"

    def test_attestation_result(self):
        a = AttestationResult.from_dict(ATTEST_RESULT)
        assert a.accepted is True

    def test_withdrawal_info(self):
        w = WithdrawalInfo.from_dict(WITHDRAW_HISTORY[0])
        assert w.status == "pending"

    def test_health_frozen(self):
        h = HealthInfo.from_dict(HEALTH_OK)
        try:
            h.ok = False
            assert False, "Should be frozen"
        except AttributeError:
            pass


# ── Async client tests ─────────────────────────────────────────────────────

class TestAsyncClient:
    @pytest.fixture
    def client(self):
        return RustChainClient(base_url="https://mock.local")

    @staticmethod
    def _resp(status=200, data=None):
        """Create a mock aiohttp response."""
        r = AsyncMock()
        r.status = status
        r.text = AsyncMock(return_value=json.dumps(data) if data else "")
        # Make it work as async context manager
        r.__aenter__ = AsyncMock(return_value=r)
        r.__aexit__ = AsyncMock(return_value=False)
        return r

    @staticmethod
    def _mock_session(resp):
        """Create a mock session that returns resp from request()."""
        s = MagicMock()
        s.request = MagicMock(return_value=resp)
        s.close = AsyncMock()
        return s

    @pytest.mark.asyncio
    async def test_health_ok(self, client):
        client._session = self._mock_session(self._resp(200, HEALTH_OK))
        h = await client.health()
        assert h.ok is True
        assert h.version == "2.2.1-rip200"

    @pytest.mark.asyncio
    async def test_health_unhealthy(self, client):
        client._session = self._mock_session(self._resp(200, HEALTH_BAD))
        with pytest.raises(NodeUnhealthyError):
            await client.health()

    @pytest.mark.asyncio
    async def test_epoch(self, client):
        client._session = self._mock_session(self._resp(200, EPOCH_DATA))
        e = await client.epoch()
        assert e.epoch == 104

    @pytest.mark.asyncio
    async def test_stats(self, client):
        client._session = self._mock_session(self._resp(200, STATS_DATA))
        s = await client.stats()
        assert s.total_miners == 487

    @pytest.mark.asyncio
    async def test_balance(self, client):
        client._session = self._mock_session(self._resp(200, BALANCE_DATA))
        assert await client.balance("0xabc") == 42.5

    @pytest.mark.asyncio
    async def test_balance_404(self, client):
        client._session = self._mock_session(self._resp(404, {"error": "not found"}))
        with pytest.raises(MinerNotFoundError):
            await client.balance("0xdead")

    @pytest.mark.asyncio
    async def test_miners_list(self, client):
        client._session = self._mock_session(self._resp(200, MINERS_DATA))
        r = await client.miners()
        assert len(r) == 2

    @pytest.mark.asyncio
    async def test_attest_challenge(self, client):
        client._session = self._mock_session(self._resp(200, CHALLENGE_DATA))
        r = await client.attest_challenge("0xabc")
        assert r.challenge == "0xdeadbeef"

    @pytest.mark.asyncio
    async def test_attest_submit(self, client):
        client._session = self._mock_session(self._resp(200, ATTEST_RESULT))
        r = await client.attest_submit("0xabc", "ch", "resp")
        assert r.accepted is True

    @pytest.mark.asyncio
    async def test_attest_submit_with_proof(self, client):
        client._session = self._mock_session(self._resp(200, ATTEST_RESULT))
        proof = {"cv": 0.05}
        r = await client.attest_submit("0xabc", "ch", "resp", proof)
        assert r.accepted is True

    @pytest.mark.asyncio
    async def test_epoch_enroll(self, client):
        client._session = self._mock_session(self._resp(200, ENROLL_RESULT))
        r = await client.epoch_enroll("0xabc")
        assert r["enrolled"] is True

    @pytest.mark.asyncio
    async def test_withdraw_register(self, client):
        client._session = self._mock_session(self._resp(200, {"registered": True}))
        r = await client.withdraw_register("0xabc", "0xdef")
        assert r["registered"] is True

    @pytest.mark.asyncio
    async def test_withdraw_request(self, client):
        client._session = self._mock_session(self._resp(200, {"requested": True}))
        r = await client.withdraw_request("0xabc", 10, "sig")
        assert r["requested"] is True

    @pytest.mark.asyncio
    async def test_withdraw_history(self, client):
        client._session = self._mock_session(self._resp(200, WITHDRAW_HISTORY))
        r = await client.withdraw_history("0xabc")
        assert len(r) == 1
        assert r[0].status == "pending"

    @pytest.mark.asyncio
    async def test_withdraw_history_empty(self, client):
        client._session = self._mock_session(self._resp(200, []))
        assert await client.withdraw_history("0xabc") == []

    @pytest.mark.asyncio
    async def test_withdraw_status(self, client):
        client._session = self._mock_session(self._resp(200, WITHDRAW_STATUS))
        r = await client.withdraw_status("w1")
        assert r.status == "completed"

    @pytest.mark.asyncio
    async def test_rate_limit(self, client):
        client._session = self._mock_session(self._resp(429, {"error": "rate limited"}))
        with pytest.raises(RateLimitError):
            await client.health()

    @pytest.mark.asyncio
    async def test_bad_request(self, client):
        client._session = self._mock_session(self._resp(400, {"error": "invalid"}))
        with pytest.raises(BadRequestError):
            await client.health()

    @pytest.mark.asyncio
    async def test_server_error(self, client):
        client._session = self._mock_session(self._resp(500, "boom"))
        with pytest.raises(RustChainError) as exc:
            await client.health()
        assert exc.value.status_code == 500

    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        close_mock = AsyncMock()
        client.close = close_mock
        async with client:
            pass
        close_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_explorer_blocks(self, client):
        client._session = self._mock_session(self._resp(200, [{"hash": "0x123"}]))
        r = await client.explorer.blocks()
        assert len(r) == 1

    @pytest.mark.asyncio
    async def test_explorer_blocks_404(self, client):
        client._session = self._mock_session(self._resp(404, {"error": "not found"}))
        assert await client.explorer.blocks() == []

    @pytest.mark.asyncio
    async def test_metrics(self, client):
        mr = AsyncMock()
        mr.status = 200
        mr.text = AsyncMock(return_value="# Prometheus not available")
        mr.__aenter__ = AsyncMock(return_value=mr)
        mr.__aexit__ = AsyncMock(return_value=False)
        s = MagicMock()
        s.get = MagicMock(return_value=mr)
        client._session = s
        m = await client.metrics()
        assert "Prometheus" in m


# ── Sync client tests ──────────────────────────────────────────────────────

class TestSyncClient:
    @pytest.fixture
    def client(self):
        return RustChainSyncClient(base_url="https://mock.local")

    def _req(self, status=200, data=None):
        r = MagicMock()
        r.status_code = status
        r.text = json.dumps(data) if data else ""
        return r

    def _setup(self, client, resp):
        client._session = MagicMock()
        client._session.request.return_value = resp

    def test_health_ok(self, client):
        self._setup(client, self._req(200, HEALTH_OK))
        h = client.health()
        assert h.ok is True

    def test_health_unhealthy(self, client):
        self._setup(client, self._req(200, HEALTH_BAD))
        with pytest.raises(NodeUnhealthyError):
            client.health()

    def test_epoch(self, client):
        self._setup(client, self._req(200, EPOCH_DATA))
        assert client.epoch().epoch == 104

    def test_stats(self, client):
        self._setup(client, self._req(200, STATS_DATA))
        assert client.stats().total_miners == 487

    def test_balance(self, client):
        self._setup(client, self._req(200, BALANCE_DATA))
        assert client.balance("0xabc") == 42.5

    def test_balance_404(self, client):
        self._setup(client, self._req(404, {"error": "not found"}))
        with pytest.raises(MinerNotFoundError):
            client.balance("0xdead")

    def test_miners(self, client):
        self._setup(client, self._req(200, MINERS_DATA))
        assert len(client.miners()) == 2

    def test_attest_challenge(self, client):
        self._setup(client, self._req(200, CHALLENGE_DATA))
        assert client.attest_challenge("0xabc").challenge == "0xdeadbeef"

    def test_attest_submit(self, client):
        self._setup(client, self._req(200, ATTEST_RESULT))
        assert client.attest_submit("0xabc", "ch", "resp").accepted is True

    def test_epoch_enroll(self, client):
        self._setup(client, self._req(200, ENROLL_RESULT))
        assert client.epoch_enroll("0xabc")["enrolled"] is True

    def test_withdraw_register(self, client):
        self._setup(client, self._req(200, {"registered": True}))
        assert client.withdraw_register("0xabc", "0xdef")["registered"] is True

    def test_withdraw_request(self, client):
        self._setup(client, self._req(200, {"requested": True}))
        assert client.withdraw_request("0xabc", 10, "sig")["requested"] is True

    def test_withdraw_history(self, client):
        self._setup(client, self._req(200, WITHDRAW_HISTORY))
        assert len(client.withdraw_history("0xabc")) == 1

    def test_withdraw_status(self, client):
        self._setup(client, self._req(200, WITHDRAW_STATUS))
        assert client.withdraw_status("w1").status == "completed"

    def test_context_manager(self, client):
        client.close = MagicMock()
        with client:
            pass
        client.close.assert_called_once()

    def test_explorer_blocks(self, client):
        self._setup(client, self._req(200, [{"hash": "0x123"}]))
        assert len(client.explorer.blocks()) == 1

    def test_explorer_blocks_404(self, client):
        self._setup(client, self._req(404, {"error": "not found"}))
        assert client.explorer.blocks() == []
