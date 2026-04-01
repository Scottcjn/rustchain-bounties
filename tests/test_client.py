"""
RustChain SDK — Basic tests.
Requires: pip install pytest pytest-asyncio httpx
Run:     pytest tests/ -v
"""

import pytest
from rustchain.client import RustChainClient
from rustchain.models import (
    HealthResponse,
    EpochResponse,
    Miner,
    BalanceResponse,
    TransferResponse,
    AttestationResponse,
    LotteryEligibility,
    Fingerprint,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Client pointing at the live public node with SSL verification disabled."""
    return RustChainClient(
        base_url="https://rustchain.org",
        verify_ssl=False,
        timeout=15.0,
        max_retries=3,
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health(client):
    """GET /health returns ok=True and a version string."""
    h = client.health()
    assert isinstance(h, HealthResponse)
    assert h.ok is True
    assert isinstance(h.version, str)
    assert h.version.startswith("2.")


def test_health_fields(client):
    """All documented /health fields are present and correctly typed."""
    h = client.health()
    assert isinstance(h.uptime_s, int)
    assert isinstance(h.db_rw, bool)
    assert isinstance(h.backup_age_hours, float)
    assert isinstance(h.tip_age_slots, int)


# ---------------------------------------------------------------------------
# Epoch
# ---------------------------------------------------------------------------

def test_get_epoch(client):
    """GET /epoch returns a valid EpochResponse."""
    e = client.get_epoch()
    assert isinstance(e, EpochResponse)
    assert e.epoch >= 0
    assert e.blocks_per_epoch == 144
    assert isinstance(e.epoch_pot, float)
    assert e.epoch_pot > 0
    assert e.enrolled_miners >= 0


def test_epoch_serialization_round_trip(client):
    """EpochResponse.from_dict produces identical fields to the raw dict."""
    raw = {"epoch": 1, "slot": 10, "blocks_per_epoch": 144, "epoch_pot": 1.5, "enrolled_miners": 3}
    e = EpochResponse.from_dict(raw)
    assert e.epoch == 1
    assert e.slot == 10
    assert e.blocks_per_epoch == 144


# ---------------------------------------------------------------------------
# Miners
# ---------------------------------------------------------------------------

def test_get_miners_returns_list(client):
    """GET /api/miners returns a non-empty list of Miner objects."""
    miners = client.get_miners()
    assert isinstance(miners, list)
    assert len(miners) >= 1


def test_miner_fields(client):
    """Each miner has all required fields."""
    miners = client.get_miners()
    for m in miners:
        assert isinstance(m, Miner)
        assert isinstance(m.miner, str)
        assert isinstance(m.device_family, str)
        assert isinstance(m.device_arch, str)
        assert isinstance(m.antiquity_multiplier, float)
        assert 0.0 <= m.antiquity_multiplier <= 10.0
        assert isinstance(m.entropy_score, float)
        assert isinstance(m.last_attest, int)


def test_miner_serialization_round_trip(client):
    """Miner.from_dict round-trips correctly."""
    raw = {
        "miner": "test-miner-001",
        "device_family": "PowerPC",
        "device_arch": "G4",
        "hardware_type": "PowerPC G4 (Vintage)",
        "antiquity_multiplier": 2.5,
        "entropy_score": 0.85,
        "last_attest": 1770000000,
    }
    m = Miner.from_dict(raw)
    assert m.antiquity_multiplier == 2.5
    assert m.miner == "test-miner-001"


# ---------------------------------------------------------------------------
# Wallet Balance
# ---------------------------------------------------------------------------

def test_get_balance_known_miner(client):
    """GET /wallet/balance?miner_id=eafc6f14eab6d5c... returns a BalanceResponse."""
    miner_id = "eafc6f14eab6d5c5362fe651e5e6c23581892a37RTC"
    bal = client.get_balance(miner_id)
    assert isinstance(bal, BalanceResponse)
    assert bal.miner_id == miner_id
    assert bal.amount_rtc >= 0
    assert bal.amount_i64 >= 0


def test_balance_i64_consistency(client):
    """amount_i64 should equal amount_rtc * 1_000_000 (micro-RTC)."""
    raw = {"miner_id": "t", "amount_rtc": 1.5, "amount_i64": 1500000}
    from rustchain.models import BalanceResponse
    bal = BalanceResponse.from_dict(raw)
    assert bal.amount_i64 == int(bal.amount_rtc * 1_000_000)


# ---------------------------------------------------------------------------
# Lottery Eligibility
# ---------------------------------------------------------------------------

def test_get_lottery_eligibility(client):
    """GET /lottery/eligibility returns a LotteryEligibility object."""
    # Use a known real miner from /api/miners
    miners = client.get_miners()
    assert len(miners) >= 1
    le = client.get_lottery_eligibility(miners[0].miner)
    assert isinstance(le, LotteryEligibility)
    assert isinstance(le.eligible, bool)
    assert isinstance(le.rotation_size, int)
    assert le.rotation_size >= 0
    assert isinstance(le.slot, int)
    assert le.slot >= 0


# ---------------------------------------------------------------------------
# Model round-trips
# ---------------------------------------------------------------------------

def test_fingerprint_to_dict():
    """Fingerprint.to_dict returns a correctly-structured dict."""
    fp = Fingerprint(
        clock_skew={"value_ns": 1234},
        cache_timing={"l1_latency_ns": 1.2},
        simd_identity={"alv": True},
        thermal_entropy={"drift": 0.5},
        instruction_jitter={"jitter_ps": 10.0},
        behavioral_heuristics={"hypervisor": False},
    )
    d = fp.to_dict()
    assert d["clock_skew"]["value_ns"] == 1234
    assert d["behavioral_heuristics"]["hypervisor"] is False


def test_transfer_response_from_dict():
    raw = {
        "ok": True,
        "verified": True,
        "phase": "pending",
        "tx_hash": "abc123",
        "amount_rtc": 1.5,
        "chain_id": "rustchain-mainnet-v2",
        "confirms_in_hours": 24.0,
    }
    t = TransferResponse.from_dict(raw)
    assert t.ok is True
    assert t.verified is True
    assert t.tx_hash == "abc123"
    assert t.amount_rtc == 1.5


def test_attestation_response_success():
    raw = {
        "success": True,
        "enrolled": True,
        "epoch": 62,
        "multiplier": 2.5,
        "next_settlement_slot": 9216,
    }
    a = AttestationResponse.from_dict(raw)
    assert a.success is True
    assert a.enrolled is True
    assert a.epoch == 62
    assert a.multiplier == 2.5


def test_attestation_response_failure():
    raw = {
        "success": False,
        "error": "VM_DETECTED",
        "check_failed": "behavioral_heuristics",
        "detail": "Hypervisor signature detected in CPUID",
    }
    a = AttestationResponse.from_dict(raw)
    assert a.success is False
    assert a.error == "VM_DETECTED"
    assert a.check_failed == "behavioral_heuristics"


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------

def test_context_manager():
    """RustChainClient can be used as a context manager."""
    with RustChainClient(base_url="https://rustchain.org", verify_ssl=False) as client:
        h = client.health()
        assert h.ok is True


# ---------------------------------------------------------------------------
# Client instantiation (no network)
# ---------------------------------------------------------------------------

def test_client_default_url():
    c = RustChainClient()
    assert c.base_url == "https://rustchain.org"
    assert c.verify_ssl is True


def test_client_custom_url_and_ssl():
    c = RustChainClient(
        base_url="http://192.168.1.100:8099",
        verify_ssl=False,
        timeout=5.0,
        max_retries=1,
    )
    assert "192.168.1.100" in c.base_url
    assert c.verify_ssl is False
    assert c.timeout == 5.0
