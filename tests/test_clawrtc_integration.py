import importlib
from types import SimpleNamespace

import pytest


pytest.importorskip("clawrtc", reason="Install clawrtc first: pip install clawrtc")


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", headers=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        return self._payload


@pytest.fixture
def miner_mod(monkeypatch):
    mod = importlib.import_module("clawrtc.data.miner")
    # Prevent expensive hardware checks on LocalMiner startup.
    monkeypatch.setattr(mod, "FINGERPRINT_AVAILABLE", False, raising=False)
    return mod


def test_wallet_creation_format(miner_mod):
    miner = miner_mod.LocalMiner(wallet=None)

    assert miner.wallet.endswith("RTC")
    assert len(miner.wallet) == 41  # 38 hex chars + "RTC"
    assert all(c in "0123456789abcdef" for c in miner.wallet[:-3])


def test_check_balance_success_and_failure(monkeypatch, miner_mod):
    miner = miner_mod.LocalMiner(wallet="abc123RTC")

    monkeypatch.setattr(
        miner_mod.requests,
        "get",
        lambda *_args, **_kwargs: FakeResponse(200, {"balance_rtc": 42.5}),
    )
    assert miner.check_balance() == 42.5

    monkeypatch.setattr(
        miner_mod.requests,
        "get",
        lambda *_args, **_kwargs: FakeResponse(500, text="boom"),
    )
    assert miner.check_balance() == 0


def test_attestation_flow_submits_expected_payload(monkeypatch, miner_mod):
    miner = miner_mod.LocalMiner(wallet="walletXYZRTC")

    hw = {
        "hostname": "unit-host",
        "family": "modern",
        "arch": "x86_64",
        "cpu": "Unit Test CPU",
        "cores": 8,
        "memory_gb": 16,
        "mac": "aa:bb:cc:dd:ee:ff",
        "macs": ["aa:bb:cc:dd:ee:ff"],
    }

    monkeypatch.setattr(miner, "_get_hw_info", lambda: hw)
    monkeypatch.setattr(miner, "_collect_entropy", lambda: {"variance_ns": 0.123, "samples": 48})
    miner.fingerprint_data = {"all_passed": True, "checks": {"clock_drift": {"passed": True}}}

    calls = []

    def fake_post(url, json=None, timeout=0):
        calls.append((url, json, timeout))
        if url.endswith("/attest/challenge"):
            return FakeResponse(200, {"nonce": "n0nce"})
        if url.endswith("/attest/submit"):
            return FakeResponse(200, {"ok": True})
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr(miner_mod.requests, "post", fake_post)

    assert miner.attest() is True
    assert len(calls) == 2

    submit_payload = calls[1][1]
    assert submit_payload["miner"] == "walletXYZRTC"
    assert submit_payload["nonce"] == "n0nce"
    assert submit_payload["signals"]["hostname"] == "unit-host"
    assert submit_payload["signals"]["macs"] == ["aa:bb:cc:dd:ee:ff"]
    assert submit_payload["fingerprint"]["all_passed"] is True
    assert miner.attestation_valid_until > 0


def test_enroll_re_attests_when_expired(monkeypatch, miner_mod):
    miner = miner_mod.LocalMiner(wallet="walletXYZRTC")
    miner.hw_info = {"hostname": "h", "family": "modern", "arch": "x86_64"}
    miner.attestation_valid_until = 0

    called = {"attest": 0}

    def fake_attest():
        called["attest"] += 1
        miner.hw_info = {"hostname": "h", "family": "modern", "arch": "x86_64"}
        miner.attestation_valid_until = 9999999999
        return True

    monkeypatch.setattr(miner, "attest", fake_attest)
    monkeypatch.setattr(
        miner_mod.requests,
        "post",
        lambda *_args, **_kwargs: FakeResponse(200, {"ok": True, "epoch": 123, "weight": 1.0}),
    )

    assert miner.enroll() is True
    assert called["attest"] == 1
    assert miner.enrolled is True


def test_fingerprint_validate_all_checks_aggregates(monkeypatch):
    fp = importlib.import_module("clawrtc.data.fingerprint_checks")

    monkeypatch.setattr(fp, "check_clock_drift", lambda: (True, {"x": 1}))
    monkeypatch.setattr(fp, "check_cache_timing", lambda: (True, {"x": 1}))
    monkeypatch.setattr(fp, "check_simd_identity", lambda: (True, {"x": 1}))
    monkeypatch.setattr(fp, "check_thermal_drift", lambda: (False, {"fail_reason": "entropy_too_low"}))
    monkeypatch.setattr(fp, "check_instruction_jitter", lambda: (True, {"x": 1}))
    monkeypatch.setattr(fp, "check_anti_emulation", lambda: (True, {"x": 1}))

    all_passed, results = fp.validate_all_checks(include_rom_check=False)

    assert all_passed is False
    assert results["thermal_drift"]["passed"] is False
    assert "fail_reason" in results["thermal_drift"]["data"]


def test_fingerprint_validate_catches_exceptions(monkeypatch):
    fp = importlib.import_module("clawrtc.data.fingerprint_checks")

    monkeypatch.setattr(fp, "check_clock_drift", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(fp, "check_cache_timing", lambda: (True, {}))
    monkeypatch.setattr(fp, "check_simd_identity", lambda: (True, {}))
    monkeypatch.setattr(fp, "check_thermal_drift", lambda: (True, {}))
    monkeypatch.setattr(fp, "check_instruction_jitter", lambda: (True, {}))
    monkeypatch.setattr(fp, "check_anti_emulation", lambda: (True, {}))

    all_passed, results = fp.validate_all_checks(include_rom_check=False)

    assert all_passed is False
    assert results["clock_drift"]["passed"] is False
    assert "boom" in results["clock_drift"]["data"]["error"]
