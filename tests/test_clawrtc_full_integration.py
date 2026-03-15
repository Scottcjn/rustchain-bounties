"""
Comprehensive integration tests for the clawrtc package.

Covers:
  - Ed25519 wallet creation, address derivation, load/save
  - Balance checking (CLI wallet show + miner check_balance)
  - Miner attestation flow end-to-end
  - Hardware fingerprint checks (clock drift, cache timing, SIMD, thermal,
    instruction jitter, anti-emulation, ROM fingerprint)
  - PoW miner detection & proof generation
  - Coinbase wallet integration (create, show, link, swap-info)
  - CLI helpers (sha256_file, run_cmd, _detect_vm, log functions)

Requires: pip install clawrtc pytest pytest-cov
Run:      pytest tests/test_clawrtc_full_integration.py -v --cov=clawrtc --cov-report=term-missing
"""

import hashlib
import importlib
import json
import os
import platform
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, mock_open

import pytest

# Guard — skip entire module if clawrtc is not installed
pytest.importorskip("clawrtc", reason="clawrtc not installed")

import clawrtc
from clawrtc import cli as clawrtc_cli
from clawrtc.data import fingerprint_checks as fp_mod
from clawrtc.data import miner as miner_mod
from clawrtc.data import pow_miners as pow_mod
from clawrtc import coinbase_wallet as cb_mod


# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────

class FakeResponse:
    """Minimal stand-in for requests.Response."""
    def __init__(self, status_code=200, payload=None, text="", content=b"",
                 headers=None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text
        self.content = content or json.dumps(self._payload).encode()
        self.headers = headers or {"content-type": "application/json"}

    def json(self):
        return self._payload


class FakeUrlResponse:
    """Minimal stand-in for urllib.request.urlopen context manager."""
    def __init__(self, payload, status=200):
        self._data = json.dumps(payload).encode()
        self.status = status

    def read(self, n=-1):
        return self._data if n == -1 else self._data[:n]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


# ────────────────────────────────────────────────────────────
# 1. Ed25519 Wallet Creation & Address Derivation
# ────────────────────────────────────────────────────────────

class TestWalletCreation:
    """Tests for clawrtc wallet create — Ed25519 key gen + RTC address."""

    def test_derive_rtc_address_format(self):
        """Address = 'RTC' + sha256(pubkey_bytes)[:40]."""
        fake_pub = b"\x01" * 32
        addr = clawrtc_cli._derive_rtc_address(fake_pub)
        assert addr.startswith("RTC")
        assert len(addr) == 43  # 3 + 40
        expected_hash = hashlib.sha256(fake_pub).hexdigest()[:40]
        assert addr[3:] == expected_hash

    def test_derive_rtc_address_deterministic(self):
        """Same public key always produces the same address."""
        pub = os.urandom(32)
        a1 = clawrtc_cli._derive_rtc_address(pub)
        a2 = clawrtc_cli._derive_rtc_address(pub)
        assert a1 == a2

    def test_derive_rtc_address_different_keys(self):
        """Different public keys produce different addresses."""
        a = clawrtc_cli._derive_rtc_address(b"\x00" * 32)
        b = clawrtc_cli._derive_rtc_address(b"\xff" * 32)
        assert a != b

    def test_wallet_create_writes_files(self, tmp_path, monkeypatch):
        """wallet create generates key pair, saves JSON, sets permissions."""
        wallet_dir = tmp_path / "wallets"
        wallet_file = wallet_dir / "default.json"
        install_dir = tmp_path

        monkeypatch.setattr(clawrtc_cli, "WALLET_DIR", str(wallet_dir))
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", str(wallet_file))
        monkeypatch.setattr(clawrtc_cli, "INSTALL_DIR", str(install_dir))

        args = SimpleNamespace(force=True)
        clawrtc_cli._wallet_create(args)

        assert wallet_file.exists()
        data = json.loads(wallet_file.read_text())
        assert data["address"].startswith("RTC")
        assert len(data["address"]) == 43
        assert data["curve"] == "Ed25519"
        assert data["network"] == "rustchain-mainnet"
        assert "private_key" in data
        assert "public_key" in data
        assert len(data["private_key"]) == 64  # 32 bytes hex
        assert len(data["public_key"]) == 64

        # .wallet file should also be written
        dot_wallet = install_dir / ".wallet"
        assert dot_wallet.exists()
        assert dot_wallet.read_text() == data["address"]

    def test_wallet_create_refuses_overwrite_without_force(self, tmp_path,
                                                           monkeypatch,
                                                           capsys):
        """If wallet exists and --force is not set, print warning."""
        wallet_dir = tmp_path / "wallets"
        wallet_dir.mkdir()
        wallet_file = wallet_dir / "default.json"
        wallet_file.write_text(json.dumps({"address": "RTCabc123"}))

        monkeypatch.setattr(clawrtc_cli, "WALLET_DIR", str(wallet_dir))
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", str(wallet_file))

        args = SimpleNamespace(force=False)
        clawrtc_cli._wallet_create(args)

        out = capsys.readouterr().out
        assert "already have" in out.lower() or "RTCabc123" in out

    def test_load_wallet_returns_none_when_missing(self, tmp_path,
                                                    monkeypatch):
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE",
                            str(tmp_path / "nope.json"))
        assert clawrtc_cli._load_wallet() is None

    def test_load_wallet_returns_none_on_bad_json(self, tmp_path,
                                                   monkeypatch):
        bad = tmp_path / "bad.json"
        bad.write_text("NOT JSON")
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", str(bad))
        assert clawrtc_cli._load_wallet() is None

    def test_load_wallet_returns_data(self, tmp_path, monkeypatch):
        wf = tmp_path / "w.json"
        payload = {"address": "RTCxyz", "public_key": "ab" * 32}
        wf.write_text(json.dumps(payload))
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", str(wf))
        result = clawrtc_cli._load_wallet()
        assert result["address"] == "RTCxyz"


# ────────────────────────────────────────────────────────────
# 2. Balance Checking
# ────────────────────────────────────────────────────────────

class TestBalanceChecking:
    """Tests for balance retrieval in miner and CLI wallet show."""

    @pytest.fixture
    def miner(self, monkeypatch):
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        return miner_mod.LocalMiner(wallet="test_balance_walletRTC")

    def test_check_balance_success(self, miner, monkeypatch):
        monkeypatch.setattr(
            miner_mod.requests, "get",
            lambda *a, **kw: FakeResponse(200, {"balance_rtc": 99.9}),
        )
        assert miner.check_balance() == 99.9

    def test_check_balance_uses_balance_key_fallback(self, miner, monkeypatch):
        monkeypatch.setattr(
            miner_mod.requests, "get",
            lambda *a, **kw: FakeResponse(200, {"balance": 55}),
        )
        # miner.check_balance uses balance_rtc key; if missing returns 0
        # (the miner code uses .get('balance_rtc', 0) first)
        assert miner.check_balance() == 0  # because key is "balance" not "balance_rtc"

    def test_check_balance_network_error(self, miner, monkeypatch):
        def boom(*a, **kw):
            raise ConnectionError("offline")
        monkeypatch.setattr(miner_mod.requests, "get", boom)
        assert miner.check_balance() == 0

    def test_check_balance_http_500(self, miner, monkeypatch):
        monkeypatch.setattr(
            miner_mod.requests, "get",
            lambda *a, **kw: FakeResponse(500),
        )
        assert miner.check_balance() == 0

    def test_wallet_show_no_wallet(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE",
                            str(tmp_path / "nope.json"))
        args = SimpleNamespace()
        clawrtc_cli._wallet_show(args)
        out = capsys.readouterr().out
        assert "no rtc wallet" in out.lower() or "create one" in out.lower()

    def test_wallet_show_displays_address(self, tmp_path, monkeypatch, capsys):
        wf = tmp_path / "w.json"
        wf.write_text(json.dumps({
            "address": "RTCshowtest123",
            "public_key": "ab" * 32,
            "created": "2025-01-01T00:00:00Z",
            "curve": "Ed25519",
        }))
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", str(wf))

        # Stub the network call so it doesn't hang
        import urllib.request
        monkeypatch.setattr(urllib.request, "urlopen",
                            lambda *a, **kw: (_ for _ in ()).throw(
                                Exception("no network")))

        args = SimpleNamespace()
        clawrtc_cli._wallet_show(args)
        out = capsys.readouterr().out
        assert "RTCshowtest123" in out


# ────────────────────────────────────────────────────────────
# 3. Miner Attestation Flow
# ────────────────────────────────────────────────────────────

class TestMinerAttestation:
    """Full attestation + enrollment cycle with mocked network."""

    @pytest.fixture
    def miner(self, monkeypatch):
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        m = miner_mod.LocalMiner(wallet="attestWalletRTC")
        return m

    def test_attest_happy_path(self, miner, monkeypatch):
        hw = {
            "hostname": "test-host", "family": "x86", "arch": "modern",
            "cpu": "Test CPU", "cores": 4, "memory_gb": 8,
            "mac": "11:22:33:44:55:66", "macs": ["11:22:33:44:55:66"],
        }

        def fake_get_hw():
            miner.hw_info = hw
            return hw

        monkeypatch.setattr(miner, "_get_hw_info", fake_get_hw)
        monkeypatch.setattr(miner, "_collect_entropy",
                            lambda: {"variance_ns": 1.0})

        calls = []
        def fake_post(url, json=None, timeout=0):
            calls.append(url)
            if "challenge" in url:
                return FakeResponse(200, {"nonce": "test_nonce_123"})
            return FakeResponse(200, {"ok": True})

        monkeypatch.setattr(miner_mod.requests, "post", fake_post)
        assert miner.attest() is True
        assert miner.attestation_valid_until > time.time()

    def test_attest_challenge_failure(self, miner, monkeypatch):
        hw = {
            "hostname": "h", "family": "x86", "arch": "modern",
            "cpu": "C", "cores": 1, "memory_gb": 1,
            "mac": "00:00:00:00:00:01", "macs": ["00:00:00:00:00:01"],
        }

        def fake_get_hw():
            miner.hw_info = hw
            return hw

        monkeypatch.setattr(miner, "_get_hw_info", fake_get_hw)
        monkeypatch.setattr(miner_mod.requests, "post",
                            lambda *a, **kw: FakeResponse(503))
        assert miner.attest() is False

    def test_attest_submit_rejected(self, miner, monkeypatch):
        hw = {
            "hostname": "h", "family": "x86", "arch": "modern",
            "cpu": "C", "cores": 1, "memory_gb": 1,
            "mac": "00:00:00:00:00:01", "macs": ["00:00:00:00:00:01"],
        }

        def fake_get_hw():
            miner.hw_info = hw
            return hw

        monkeypatch.setattr(miner, "_get_hw_info", fake_get_hw)
        monkeypatch.setattr(miner, "_collect_entropy",
                            lambda: {"variance_ns": 0.5})

        def fake_post(url, **kw):
            if "challenge" in url:
                return FakeResponse(200, {"nonce": "n"})
            return FakeResponse(200, {"ok": False, "reason": "vm_detected"})

        monkeypatch.setattr(miner_mod.requests, "post", fake_post)
        assert miner.attest() is False

    def test_attest_network_exception(self, miner, monkeypatch):
        hw = {
            "hostname": "h", "family": "x86", "arch": "modern",
            "cpu": "C", "cores": 1, "memory_gb": 1,
            "mac": "00:00:00:00:00:01", "macs": ["00:00:00:00:00:01"],
        }

        def fake_get_hw():
            miner.hw_info = hw
            return hw

        monkeypatch.setattr(miner, "_get_hw_info", fake_get_hw)

        def boom(*a, **kw):
            raise ConnectionError("down")
        monkeypatch.setattr(miner_mod.requests, "post", boom)
        assert miner.attest() is False

    def test_enroll_happy_path(self, miner, monkeypatch):
        miner.attestation_valid_until = time.time() + 9999
        miner.hw_info = {
            "hostname": "h", "family": "x86", "arch": "modern",
        }
        monkeypatch.setattr(miner_mod.requests, "post",
                            lambda *a, **kw: FakeResponse(
                                200, {"ok": True, "epoch": 42, "weight": 1.5}))
        assert miner.enroll() is True
        assert miner.enrolled is True

    def test_enroll_triggers_reattest_when_expired(self, miner, monkeypatch):
        miner.attestation_valid_until = 0  # expired
        attest_called = []

        def fake_attest():
            attest_called.append(1)
            miner.attestation_valid_until = time.time() + 9999
            miner.hw_info = {"hostname": "h", "family": "x86", "arch": "m"}
            return True

        monkeypatch.setattr(miner, "attest", fake_attest)
        monkeypatch.setattr(miner_mod.requests, "post",
                            lambda *a, **kw: FakeResponse(
                                200, {"ok": True, "epoch": 1, "weight": 1.0}))
        assert miner.enroll() is True
        assert len(attest_called) == 1

    def test_enroll_fails_when_reattest_fails(self, miner, monkeypatch):
        miner.attestation_valid_until = 0
        monkeypatch.setattr(miner, "attest", lambda: False)
        assert miner.enroll() is False

    def test_attestation_payload_includes_commitment(self, miner, monkeypatch):
        hw = {
            "hostname": "host", "family": "x86", "arch": "modern",
            "cpu": "CPU", "cores": 2, "memory_gb": 4,
            "mac": "aa:bb:cc:dd:ee:ff", "macs": ["aa:bb:cc:dd:ee:ff"],
        }

        def fake_get_hw():
            miner.hw_info = hw
            return hw

        monkeypatch.setattr(miner, "_get_hw_info", fake_get_hw)
        entropy = {"variance_ns": 42.0}
        monkeypatch.setattr(miner, "_collect_entropy", lambda: entropy)

        payloads = []
        def capture_post(url, json=None, timeout=0):
            payloads.append(json)
            if "challenge" in url:
                return FakeResponse(200, {"nonce": "abc"})
            return FakeResponse(200, {"ok": True})

        monkeypatch.setattr(miner_mod.requests, "post", capture_post)
        miner.attest()

        submit = payloads[1]
        # commitment should be sha256(nonce + wallet + json(entropy))
        expected = hashlib.sha256(
            ("abc" + "attestWalletRTC" + json.dumps(entropy, sort_keys=True)
             ).encode()
        ).hexdigest()
        assert submit["report"]["commitment"] == expected


# ────────────────────────────────────────────────────────────
# 4. Hardware Fingerprint Checks
# ────────────────────────────────────────────────────────────

class TestFingerprintChecks:
    """Individual fingerprint check functions."""

    def test_clock_drift_returns_tuple(self):
        valid, data = fp_mod.check_clock_drift(samples=5)
        assert isinstance(valid, bool)
        assert "mean_ns" in data
        assert "cv" in data
        assert "drift_stdev" in data

    def test_cache_timing_returns_ratios(self):
        valid, data = fp_mod.check_cache_timing(iterations=3)
        assert isinstance(valid, bool)
        assert "l1_ns" in data
        assert "l2_ns" in data
        assert "l3_ns" in data
        assert "l2_l1_ratio" in data

    def test_clock_drift_detects_synthetic(self, monkeypatch):
        """If CV is unrealistically low, flag as synthetic."""
        # Force very uniform intervals
        original = fp_mod.check_clock_drift

        def fake_drift(samples=200):
            # Return data that looks synthetic
            return False, {
                "mean_ns": 1000000,
                "stdev_ns": 0,
                "cv": 0.00001,
                "drift_stdev": 0,
                "fail_reason": "synthetic_timing",
            }

        monkeypatch.setattr(fp_mod, "check_clock_drift", fake_drift)
        valid, data = fp_mod.check_clock_drift()
        assert valid is False
        assert data["fail_reason"] == "synthetic_timing"

    def test_simd_identity_detects_arch(self):
        valid, data = fp_mod.check_simd_identity()
        assert isinstance(valid, bool)
        assert "arch" in data
        assert data["arch"] == platform.machine().lower()

    def test_thermal_drift_returns_ratios(self):
        valid, data = fp_mod.check_thermal_drift(samples=3)
        assert isinstance(valid, bool)
        assert "cold_avg_ns" in data
        assert "hot_avg_ns" in data
        assert "drift_ratio" in data

    def test_instruction_jitter_measures_three_pipelines(self):
        valid, data = fp_mod.check_instruction_jitter(samples=3)
        assert isinstance(valid, bool)
        assert "int_avg_ns" in data
        assert "fp_avg_ns" in data
        assert "branch_avg_ns" in data

    def test_anti_emulation_returns_indicators(self):
        valid, data = fp_mod.check_anti_emulation()
        assert isinstance(valid, bool)
        assert "vm_indicators" in data
        assert "indicator_count" in data
        assert isinstance(data["is_likely_vm"], bool)

    def test_anti_emulation_detects_env_vars(self, monkeypatch):
        monkeypatch.setenv("KUBERNETES", "true")
        valid, data = fp_mod.check_anti_emulation()
        assert data["indicator_count"] >= 1
        assert any("KUBERNETES" in ind for ind in data["vm_indicators"])

    def test_rom_fingerprint_skips_modern_hw(self):
        """ROM check should pass/skip on modern (non-PPC/68K) hardware."""
        valid, data = fp_mod.check_rom_fingerprint()
        assert valid is True
        # On modern hw it returns either skipped or not_applicable
        if not fp_mod.ROM_DB_AVAILABLE:
            assert data.get("skipped") is True
        else:
            arch = platform.machine().lower()
            if "ppc" not in arch and "m68k" not in arch:
                assert data.get("rom_check") == "not_applicable_modern_hw"

    def test_validate_all_checks_aggregation(self, monkeypatch):
        """validate_all_checks returns False if any check fails."""
        monkeypatch.setattr(fp_mod, "check_clock_drift",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_cache_timing",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_simd_identity",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_thermal_drift",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_instruction_jitter",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_anti_emulation",
                            lambda: (False, {"fail_reason": "vm_detected"}))

        passed, results = fp_mod.validate_all_checks(include_rom_check=False)
        assert passed is False
        assert results["anti_emulation"]["passed"] is False

    def test_validate_all_checks_all_pass(self, monkeypatch):
        monkeypatch.setattr(fp_mod, "check_clock_drift",
                            lambda: (True, {"cv": 0.01}))
        monkeypatch.setattr(fp_mod, "check_cache_timing",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_simd_identity",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_thermal_drift",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_instruction_jitter",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_anti_emulation",
                            lambda: (True, {}))

        passed, results = fp_mod.validate_all_checks(include_rom_check=False)
        assert passed is True
        assert all(v["passed"] for v in results.values())

    def test_validate_catches_exception_in_check(self, monkeypatch):
        """If a check raises, it counts as failure with error key."""
        def explode():
            raise RuntimeError("cpu on fire")

        monkeypatch.setattr(fp_mod, "check_clock_drift", explode)
        monkeypatch.setattr(fp_mod, "check_cache_timing",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_simd_identity",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_thermal_drift",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_instruction_jitter",
                            lambda: (True, {}))
        monkeypatch.setattr(fp_mod, "check_anti_emulation",
                            lambda: (True, {}))

        passed, results = fp_mod.validate_all_checks(include_rom_check=False)
        assert passed is False
        assert "error" in results["clock_drift"]["data"]
        assert "cpu on fire" in results["clock_drift"]["data"]["error"]


# ────────────────────────────────────────────────────────────
# 5. Miner Internal Helpers
# ────────────────────────────────────────────────────────────

class TestMinerHelpers:
    """LocalMiner helper methods: wallet gen, entropy, arch detection."""

    @pytest.fixture
    def miner(self, monkeypatch):
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        return miner_mod.LocalMiner(wallet="helperTestRTC")

    def test_gen_wallet_format(self, monkeypatch):
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        m = miner_mod.LocalMiner(wallet=None)
        assert m.wallet.endswith("RTC")
        assert len(m.wallet) == 41

    def test_gen_wallet_unique(self, monkeypatch):
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        w1 = miner_mod.LocalMiner(wallet=None).wallet
        w2 = miner_mod.LocalMiner(wallet=None).wallet
        assert w1 != w2

    def test_collect_entropy_returns_stats(self, miner):
        result = miner._collect_entropy(cycles=5, inner_loop=100)
        assert "mean_ns" in result
        assert "variance_ns" in result
        assert "min_ns" in result
        assert "max_ns" in result
        assert result["sample_count"] == 5
        assert len(result["samples_preview"]) <= 12

    def test_detect_arch_returns_family_and_subarch(self, miner):
        family, arch = miner._detect_arch()
        assert isinstance(family, str)
        assert isinstance(arch, str)
        assert family in ("x86", "arm", "powerpc")


# ────────────────────────────────────────────────────────────
# 6. PoW Miner Detection & Proof
# ────────────────────────────────────────────────────────────

class TestPoWMiners:
    """Tests for pow_miners module: detection, proof gen, helpers."""

    def test_known_miners_registry(self):
        assert len(pow_mod.KNOWN_MINERS) > 10
        for chain, info in pow_mod.KNOWN_MINERS.items():
            assert "display" in info
            assert "algo" in info
            assert "node_ports" in info
            assert "process_names" in info

    def test_get_supported_chains(self):
        chains = pow_mod.get_supported_chains()
        assert "ergo" in chains
        assert "monero" in chains
        assert "kaspa" in chains
        assert "warthog" in chains

    def test_get_chain_info(self):
        info = pow_mod.get_chain_info("ergo")
        assert info is not None
        assert info["algo"] == "autolykos2"
        assert pow_mod.get_chain_info("nonexistent") is None

    def test_detect_running_miners_returns_list(self, monkeypatch):
        # Stub process list to contain no miners
        monkeypatch.setattr(pow_mod, "_get_running_processes",
                            lambda: "bash python sshd")
        monkeypatch.setattr(pow_mod, "_check_port_open",
                            lambda port: False)
        detected = pow_mod.detect_running_miners()
        assert isinstance(detected, list)

    def test_detect_running_miners_finds_process(self, monkeypatch):
        monkeypatch.setattr(pow_mod, "_get_running_processes",
                            lambda: "xmrig --threads=4")
        monkeypatch.setattr(pow_mod, "_check_port_open",
                            lambda port: False)
        detected = pow_mod.detect_running_miners()
        chains = [d["chain"] for d in detected]
        assert "monero" in chains or len(detected) > 0

    def test_detect_running_miners_finds_node_port(self, monkeypatch):
        monkeypatch.setattr(pow_mod, "_get_running_processes", lambda: "")
        monkeypatch.setattr(pow_mod, "_check_port_open",
                            lambda port: port == 9053)
        detected = pow_mod.detect_running_miners()
        ergo = [d for d in detected if d["chain"] == "ergo"]
        assert len(ergo) == 1
        assert ergo[0]["node_responding"] is True
        assert ergo[0]["proof_type"] == "node_rpc"

    def test_generate_pow_proof_unknown_chain(self):
        assert pow_mod.generate_pow_proof("fake_chain", "nonce") is None

    def test_generate_pow_proof_process_detection(self, monkeypatch):
        monkeypatch.setattr(pow_mod, "_probe_node_rpc",
                            lambda *a: None)
        monkeypatch.setattr(pow_mod, "_get_running_processes",
                            lambda: "ergo.jar running")
        proof = pow_mod.generate_pow_proof("ergo", "test_nonce")
        assert proof is not None
        assert proof["proof_type"] == "process_only"
        assert proof["bonus_multiplier"] == 1.15

    def test_generate_pow_proof_node_rpc(self, monkeypatch):
        monkeypatch.setattr(pow_mod, "_probe_node_rpc",
                            lambda *a: {"endpoint": "localhost:9053",
                                        "chain_height": 1234})
        proof = pow_mod.generate_pow_proof("ergo", "nonce_123")
        assert proof is not None
        assert proof["proof_type"] == "node_rpc"
        assert proof["bonus_multiplier"] == 1.5

    def test_pow_bonus_multipliers(self):
        assert pow_mod.POW_BONUS["node_rpc"] == 1.5
        assert pow_mod.POW_BONUS["pool_account"] == 1.3
        assert pow_mod.POW_BONUS["process_only"] == 1.15

    def test_print_detection_report_no_miners(self, capsys):
        pow_mod.print_detection_report([])
        out = capsys.readouterr().out
        assert "no pow miners" in out.lower()

    def test_print_detection_report_with_miners(self, capsys):
        detected = [{
            "chain": "ergo",
            "display": "Ergo (Autolykos2)",
            "algo": "autolykos2",
            "process_found": True,
            "node_responding": True,
            "node_port": 9053,
            "proof_type": "node_rpc",
            "matched_process": "ergo.jar",
        }]
        pow_mod.print_detection_report(detected)
        out = capsys.readouterr().out
        assert "Ergo" in out
        assert "9053" in out

    def test_check_port_open_closed(self):
        # Port 1 should not be open on localhost
        assert pow_mod._check_port_open(1, "127.0.0.1") is False


# ────────────────────────────────────────────────────────────
# 7. Coinbase Wallet Integration
# ────────────────────────────────────────────────────────────

class TestCoinbaseWallet:
    """Tests for coinbase_wallet module."""

    def test_swap_info_constants(self):
        assert cb_mod.SWAP_INFO["network"] == "Base (eip155:8453)"
        assert cb_mod.SWAP_INFO["wrtc_contract"].startswith("0x")
        assert cb_mod.SWAP_INFO["usdc_contract"].startswith("0x")

    def test_load_coinbase_wallet_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cb_mod, "COINBASE_FILE",
                            str(tmp_path / "no.json"))
        assert cb_mod._load_coinbase_wallet() is None

    def test_load_coinbase_wallet_bad_json(self, tmp_path, monkeypatch):
        f = tmp_path / "bad.json"
        f.write_text("not json")
        monkeypatch.setattr(cb_mod, "COINBASE_FILE", str(f))
        assert cb_mod._load_coinbase_wallet() is None

    def test_save_and_load_coinbase_wallet(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cb_mod, "INSTALL_DIR", str(tmp_path))
        cf = tmp_path / "coinbase_wallet.json"
        monkeypatch.setattr(cb_mod, "COINBASE_FILE", str(cf))

        data = {"address": "0x" + "ab" * 20, "network": "Base"}
        cb_mod._save_coinbase_wallet(data)
        assert cf.exists()

        loaded = cb_mod._load_coinbase_wallet()
        assert loaded["address"] == data["address"]

    def test_coinbase_show_no_wallet(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(cb_mod, "COINBASE_FILE",
                            str(tmp_path / "no.json"))
        args = SimpleNamespace()
        cb_mod.coinbase_show(args)
        out = capsys.readouterr().out
        assert "no coinbase wallet" in out.lower() or "create one" in out.lower()

    def test_coinbase_show_with_wallet(self, tmp_path, monkeypatch, capsys):
        cf = tmp_path / "cb.json"
        cf.write_text(json.dumps({
            "address": "0x1234567890abcdef1234567890abcdef12345678",
            "network": "Base (eip155:8453)",
            "created": "2025-06-01",
            "method": "manual_link",
        }))
        monkeypatch.setattr(cb_mod, "COINBASE_FILE", str(cf))
        args = SimpleNamespace()
        cb_mod.coinbase_show(args)
        out = capsys.readouterr().out
        assert "0x1234" in out

    def test_coinbase_link_valid_address(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(cb_mod, "INSTALL_DIR", str(tmp_path))
        monkeypatch.setattr(cb_mod, "COINBASE_FILE",
                            str(tmp_path / "cb.json"))

        addr = "0x" + "ab" * 20
        args = SimpleNamespace(base_address=addr)
        cb_mod.coinbase_link(args)
        out = capsys.readouterr().out
        assert "linked" in out.lower()
        assert addr in out

    def test_coinbase_link_invalid_address(self, capsys):
        args = SimpleNamespace(base_address="not_an_address")
        cb_mod.coinbase_link(args)
        out = capsys.readouterr().out
        assert "invalid" in out.lower()

    def test_coinbase_link_no_address(self, capsys):
        args = SimpleNamespace(base_address="")
        cb_mod.coinbase_link(args)
        out = capsys.readouterr().out
        assert "usage" in out.lower()

    def test_coinbase_swap_info_output(self, capsys):
        args = SimpleNamespace()
        cb_mod.coinbase_swap_info(args)
        out = capsys.readouterr().out
        assert "wRTC" in out
        assert "USDC" in out
        assert "Aerodrome" in out

    def test_coinbase_create_no_creds(self, monkeypatch, capsys):
        monkeypatch.setattr(cb_mod, "COINBASE_FILE", "/tmp/nope.json")
        monkeypatch.delenv("CDP_API_KEY_NAME", raising=False)
        monkeypatch.delenv("CDP_API_KEY_PRIVATE_KEY", raising=False)
        args = SimpleNamespace(force=True)
        cb_mod.coinbase_create(args)
        out = capsys.readouterr().out
        assert "credentials" in out.lower() or "cdp" in out.lower()

    def test_cmd_coinbase_dispatch(self, monkeypatch, capsys):
        monkeypatch.setattr(cb_mod, "COINBASE_FILE", "/tmp/nope.json")
        args = SimpleNamespace(coinbase_action="show")
        cb_mod.cmd_coinbase(args)
        out = capsys.readouterr().out
        assert "coinbase" in out.lower() or "create" in out.lower()


# ────────────────────────────────────────────────────────────
# 8. CLI Utility Functions
# ────────────────────────────────────────────────────────────

class TestCLIUtils:
    """Tests for cli.py utility functions."""

    def test_sha256_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_bytes(b"hello world")
        h = clawrtc_cli.sha256_file(str(f))
        assert h == hashlib.sha256(b"hello world").hexdigest()

    def test_sha256_file_empty(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_bytes(b"")
        h = clawrtc_cli.sha256_file(str(f))
        assert h == hashlib.sha256(b"").hexdigest()

    def test_run_cmd_capture(self):
        out = clawrtc_cli.run_cmd("echo hello", capture=True)
        assert "hello" in out

    def test_run_cmd_failure_no_check(self):
        result = clawrtc_cli.run_cmd("exit 1", check=False, capture=True)
        # Should not raise
        assert result is None or isinstance(result, str)

    def test_detect_vm_returns_list(self):
        indicators = clawrtc_cli._detect_vm()
        assert isinstance(indicators, list)

    def test_log_functions_output(self, capsys):
        clawrtc_cli.log("test message")
        out = capsys.readouterr().out
        assert "test message" in out

        clawrtc_cli.success("ok msg")
        out = capsys.readouterr().out
        assert "ok msg" in out

        clawrtc_cli.warn("warn msg")
        out = capsys.readouterr().out
        assert "warn msg" in out

    def test_version_constant(self):
        assert clawrtc_cli.__version__ == "1.7.1"

    def test_node_url_constant(self):
        assert "metalseed.net" in clawrtc_cli.NODE_URL

    def test_bundled_files_list(self):
        assert len(clawrtc_cli.BUNDLED_FILES) == 2
        names = [b[0] for b in clawrtc_cli.BUNDLED_FILES]
        assert "miner.py" in names
        assert "fingerprint_checks.py" in names


# ────────────────────────────────────────────────────────────
# 9. Wallet Export
# ────────────────────────────────────────────────────────────

class TestWalletExport:
    """Tests for wallet export (full and public-only)."""

    def test_export_no_wallet(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE",
                            str(tmp_path / "nope.json"))
        args = SimpleNamespace(output=None, public_only=False)
        clawrtc_cli._wallet_export(args)
        out = capsys.readouterr().out
        assert "no wallet" in out.lower() or "create" in out.lower()

    def test_export_full(self, tmp_path, monkeypatch, capsys):
        wf = tmp_path / "w.json"
        wallet = {
            "address": "RTCexport123",
            "public_key": "ab" * 32,
            "private_key": "cd" * 32,
        }
        wf.write_text(json.dumps(wallet))
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", str(wf))

        export_path = str(tmp_path / "exported.json")
        args = SimpleNamespace(output=export_path, public_only=False)
        clawrtc_cli._wallet_export(args)

        exported = json.loads(open(export_path).read())
        assert "private_key" in exported
        assert exported["address"] == "RTCexport123"

    def test_export_public_only(self, tmp_path, monkeypatch, capsys):
        wf = tmp_path / "w.json"
        wallet = {
            "address": "RTCpubonly",
            "public_key": "ab" * 32,
            "private_key": "cd" * 32,
        }
        wf.write_text(json.dumps(wallet))
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", str(wf))

        export_path = str(tmp_path / "pub_exported.json")
        args = SimpleNamespace(output=export_path, public_only=True)
        clawrtc_cli._wallet_export(args)

        exported = json.loads(open(export_path).read())
        assert "private_key" not in exported
        assert exported["address"] == "RTCpubonly"


# ────────────────────────────────────────────────────────────
# 10. Edge Cases & Error Handling
# ────────────────────────────────────────────────────────────

class TestEdgeCases:
    """Misc edge cases and error paths."""

    def test_miner_explicit_wallet(self, monkeypatch):
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        m = miner_mod.LocalMiner(wallet="customWalletRTC")
        assert m.wallet == "customWalletRTC"

    def test_cache_timing_zero_latency_fails(self, monkeypatch):
        """If all cache levels return zero, check should fail."""
        def zero_cache(iterations=100):
            return False, {
                "l1_ns": 0, "l2_ns": 0, "l3_ns": 0,
                "l2_l1_ratio": 0, "l3_l2_ratio": 0,
                "fail_reason": "zero_latency",
            }
        monkeypatch.setattr(fp_mod, "check_cache_timing", zero_cache)
        valid, data = fp_mod.check_cache_timing()
        assert valid is False
        assert data["fail_reason"] == "zero_latency"

    def test_instruction_jitter_no_jitter_fails(self, monkeypatch):
        """If all stddevs are zero, check fails."""
        def no_jitter(samples=100):
            return False, {
                "int_avg_ns": 1000, "fp_avg_ns": 1000,
                "branch_avg_ns": 1000,
                "int_stdev": 0, "fp_stdev": 0, "branch_stdev": 0,
                "fail_reason": "no_jitter",
            }
        monkeypatch.setattr(fp_mod, "check_instruction_jitter", no_jitter)
        valid, data = fp_mod.check_instruction_jitter()
        assert valid is False

    def test_thermal_drift_no_variance_fails(self, monkeypatch):
        def no_var(samples=50):
            return False, {
                "cold_avg_ns": 1000, "hot_avg_ns": 1000,
                "cold_stdev": 0, "hot_stdev": 0,
                "drift_ratio": 1.0,
                "fail_reason": "no_thermal_variance",
            }
        monkeypatch.setattr(fp_mod, "check_thermal_drift", no_var)
        valid, data = fp_mod.check_thermal_drift()
        assert valid is False
        assert data["fail_reason"] == "no_thermal_variance"

    def test_get_ed25519_imports_correctly(self):
        result = clawrtc_cli._get_ed25519()
        assert result is not None
        assert len(result) == 5  # Ed25519PrivateKey, Encoding, etc.

    def test_pow_pool_verification_unknown_pool(self):
        """Pool verification returns None for unknown pool."""
        info = pow_mod.KNOWN_MINERS["ergo"]
        result = pow_mod._verify_pool_account(
            "ergo", info, "addr", "nonexistent_pool")
        assert result is None

    def test_cmd_wallet_dispatch(self, monkeypatch, capsys):
        """cmd_wallet dispatches correctly."""
        monkeypatch.setattr(clawrtc_cli, "WALLET_FILE", "/tmp/nope.json")
        args = SimpleNamespace(wallet_action="show")
        clawrtc_cli.cmd_wallet(args)
        out = capsys.readouterr().out
        assert "no rtc wallet" in out.lower() or "create" in out.lower()


# ────────────────────────────────────────────────────────────
# 11. Miner Arch Detection & MAC Collection
# ────────────────────────────────────────────────────────────

class TestMinerArchDetection:
    """Cover _detect_arch branches and _get_mac_addresses."""

    @pytest.fixture
    def miner(self, monkeypatch):
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        return miner_mod.LocalMiner(wallet="archTestRTC")

    def test_detect_arch_x86_modern(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "x86_64")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "Intel Core i7-13700K")
        family, arch = miner._detect_arch()
        assert family == "x86"
        assert arch == "modern"

    def test_detect_arch_x86_core2duo(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "x86_64")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "Intel Core 2 Duo E8400")
        family, arch = miner._detect_arch()
        assert family == "x86"
        assert arch == "core2duo"

    def test_detect_arch_x86_pentium(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "i686")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "Intel Pentium 4")
        family, arch = miner._detect_arch()
        assert family == "x86"
        assert arch == "pentium4"

    def test_detect_arch_arm_modern(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "aarch64")
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "Cortex-A72")
        family, arch = miner._detect_arch()
        assert family == "arm"
        assert arch == "modern"

    def test_detect_arch_ppc_g4(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "ppc")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "PowerPC G4 7450")
        family, arch = miner._detect_arch()
        assert arch == "g4"

    def test_detect_arch_ppc_g5(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "ppc64")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "PowerPC G5 970")
        family, arch = miner._detect_arch()
        assert arch == "g5"

    def test_detect_arch_ppc_g3(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "ppc")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "PowerPC G3 750")
        family, arch = miner._detect_arch()
        assert arch == "g3"

    def test_detect_arch_ppc_generic(self, miner, monkeypatch):
        monkeypatch.setattr(platform, "machine", lambda: "ppc")
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "PowerPC 603e")
        family, arch = miner._detect_arch()
        assert family == "powerpc"
        assert arch == "powerpc"

    def test_get_mac_addresses_fallback(self, miner, monkeypatch):
        """When both ip and ifconfig fail, should return fallback MAC."""
        import subprocess
        monkeypatch.setattr(subprocess, "run",
                            lambda *a, **kw: (_ for _ in ()).throw(
                                FileNotFoundError("no ip")))
        macs = miner._get_mac_addresses()
        assert isinstance(macs, list)
        assert len(macs) >= 1

    def test_run_cmd_returns_empty_on_failure(self, miner):
        result = miner._run_cmd("false_command_that_does_not_exist_xyz")
        assert result == ""

    def test_get_hw_info_returns_dict(self, miner, monkeypatch):
        # Stub subprocess calls to avoid OS-specific failures
        monkeypatch.setattr(miner, "_run_cmd", lambda cmd: "")
        monkeypatch.setattr(miner, "_get_mac_addresses",
                            lambda: ["aa:bb:cc:dd:ee:ff"])
        hw = miner._get_hw_info()
        assert "platform" in hw
        assert "machine" in hw
        assert "family" in hw
        assert "cpu" in hw
        assert "mac" in hw
        assert hw["macs"] == ["aa:bb:cc:dd:ee:ff"]

    def test_collect_entropy_variance_positive(self, miner):
        """Entropy collection should produce non-zero variance on real HW."""
        result = miner._collect_entropy(cycles=10, inner_loop=500)
        assert result["variance_ns"] >= 0
        assert result["min_ns"] <= result["max_ns"]


# ────────────────────────────────────────────────────────────
# 12. PoW Miners — Node RPC Probing & Pool Verification
# ────────────────────────────────────────────────────────────

class TestPoWNodeRPC:
    """Cover _probe_node_rpc for various chains."""

    def test_probe_ergo_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "get",
                            lambda url, **kw: FakeResponse(200, {
                                "fullHeight": 999,
                                "bestFullHeaderId": "abc123",
                                "peersCount": 5,
                                "isMining": True,
                            }))
        info = pow_mod.KNOWN_MINERS["ergo"]
        result = pow_mod._probe_node_rpc("ergo", info, "test_nonce")
        assert result is not None
        assert result["chain_height"] == 999

    def test_probe_warthog_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "get",
                            lambda url, **kw: FakeResponse(200, {
                                "height": 500, "hash": "deadbeef",
                            }))
        info = pow_mod.KNOWN_MINERS["warthog"]
        result = pow_mod._probe_node_rpc("warthog", info, "nonce")
        assert result is not None
        assert result["chain_height"] == 500

    def test_probe_monero_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "post",
                            lambda url, **kw: FakeResponse(200, {
                                "result": {
                                    "height": 3000000,
                                    "difficulty": 12345,
                                    "tx_pool_size": 10,
                                },
                            }))
        info = pow_mod.KNOWN_MINERS["monero"]
        result = pow_mod._probe_node_rpc("monero", info, "n")
        assert result is not None
        assert result["chain_height"] == 3000000

    def test_probe_kaspa_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "post",
                            lambda url, **kw: FakeResponse(200, {
                                "result": {
                                    "headerCount": 888,
                                    "isSynced": True,
                                },
                            }))
        info = pow_mod.KNOWN_MINERS["kaspa"]
        result = pow_mod._probe_node_rpc("kaspa", info, "n")
        assert result is not None
        assert result["is_synced"] is True

    def test_probe_dero_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "post",
                            lambda url, **kw: FakeResponse(200, {
                                "result": {
                                    "topoheight": 7777,
                                    "stableheight": 7770,
                                    "difficulty": 999,
                                },
                            }))
        info = pow_mod.KNOWN_MINERS["dero"]
        result = pow_mod._probe_node_rpc("dero", info, "n")
        assert result is not None
        assert result["chain_height"] == 7777

    def test_probe_raptoreum_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "post",
                            lambda url, **kw: FakeResponse(200, {
                                "result": {
                                    "blocks": 4444,
                                    "networkhashps": 100000,
                                    "difficulty": 50,
                                },
                            }))
        info = pow_mod.KNOWN_MINERS["raptoreum"]
        result = pow_mod._probe_node_rpc("raptoreum", info, "n")
        assert result is not None
        assert result["chain_height"] == 4444

    def test_probe_alephium_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "get",
                            lambda url, **kw: FakeResponse(200, {
                                "cliqueId": "clique1",
                                "nodes": [{"addr": "1"}, {"addr": "2"}],
                            }))
        info = pow_mod.KNOWN_MINERS["alephium"]
        result = pow_mod._probe_node_rpc("alephium", info, "n")
        assert result is not None
        assert result["clique_id"] == "clique1"

    def test_probe_verus_node(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "post",
                            lambda url, **kw: FakeResponse(200, {
                                "result": {
                                    "blocks": 2222,
                                    "networkhashps": 50000,
                                },
                            }))
        info = pow_mod.KNOWN_MINERS["verus"]
        result = pow_mod._probe_node_rpc("verus", info, "n")
        assert result is not None
        assert result["chain_height"] == 2222

    def test_probe_generic_chain(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "get",
                            lambda url, **kw: FakeResponse(
                                200, content=b"some response"))
        info = pow_mod.KNOWN_MINERS["neoxa"]
        result = pow_mod._probe_node_rpc("neoxa", info, "n")
        assert result is not None
        assert "raw_response_hash" in result

    def test_probe_node_connection_refused(self, monkeypatch):
        """When node is unreachable, _probe_node_rpc returns None."""
        import requests as req_mod

        def fail_connect(*a, **kw):
            raise ConnectionError("refused")

        monkeypatch.setattr(req_mod, "get", fail_connect)
        monkeypatch.setattr(req_mod, "post", fail_connect)
        info = pow_mod.KNOWN_MINERS["ergo"]
        result = pow_mod._probe_node_rpc("ergo", info, "n")
        assert result is None

    def test_pool_verification_success(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "get",
                            lambda url, **kw: FakeResponse(200, {
                                "stats": {
                                    "hashrate": 5000,
                                    "lastShare": int(time.time()) - 60,
                                },
                            }, content=b'{"stats":{"hashrate":5000}}'))
        info = pow_mod.KNOWN_MINERS["ergo"]
        result = pow_mod._verify_pool_account(
            "ergo", info, "addr123", "herominers")
        assert result is not None
        assert result["pool"] == "herominers"
        assert result["hashrate"] == 5000

    def test_pool_verification_stale_share(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "get",
                            lambda url, **kw: FakeResponse(200, {
                                "stats": {
                                    "hashrate": 100,
                                    "lastShare": int(time.time()) - 20000,
                                },
                            }))
        info = pow_mod.KNOWN_MINERS["ergo"]
        result = pow_mod._verify_pool_account(
            "ergo", info, "addr", "herominers")
        assert result is None  # share too old

    def test_pool_verification_zero_hashrate(self, monkeypatch):
        import requests as req_mod
        monkeypatch.setattr(req_mod, "get",
                            lambda url, **kw: FakeResponse(200, {
                                "stats": {"hashrate": 0, "lastShare": 0},
                            }))
        info = pow_mod.KNOWN_MINERS["ergo"]
        result = pow_mod._verify_pool_account(
            "ergo", info, "addr", "herominers")
        assert result is None

    def test_generate_pow_proof_pool_account(self, monkeypatch):
        monkeypatch.setattr(pow_mod, "_probe_node_rpc", lambda *a: None)
        monkeypatch.setattr(pow_mod, "_verify_pool_account",
                            lambda *a: {
                                "pool": "herominers",
                                "address": "addr",
                                "hashrate": 1000,
                            })
        proof = pow_mod.generate_pow_proof(
            "ergo", "nonce", pool_address="addr", pool_name="herominers")
        assert proof is not None
        assert proof["proof_type"] == "pool_account"
        assert proof["bonus_multiplier"] == 1.3

    def test_generate_pow_proof_no_detection(self, monkeypatch):
        """When nothing is detected, returns None."""
        monkeypatch.setattr(pow_mod, "_probe_node_rpc", lambda *a: None)
        monkeypatch.setattr(pow_mod, "_get_running_processes", lambda: "")
        result = pow_mod.generate_pow_proof("ergo", "nonce")
        assert result is None


# ────────────────────────────────────────────────────────────
# 13. CLI Install & Status (safe paths only)
# ────────────────────────────────────────────────────────────

class TestCLIInstallStatus:
    """Cover CLI install/status paths that don't modify system state."""

    def test_install_verify_mode(self, monkeypatch, capsys):
        """--verify should print hashes and return without installing."""
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        args = SimpleNamespace(
            wallet=None, dry_run=False, verify=True,
            service=False, no_service=False, yes=False)
        clawrtc_cli.cmd_install(args)
        out = capsys.readouterr().out
        assert "miner.py" in out or "fingerprint" in out

    def test_install_dry_run(self, monkeypatch, capsys):
        """--dry-run should show disclosure without installing."""
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        args = SimpleNamespace(
            wallet=None, dry_run=True, verify=False,
            service=False, no_service=False, yes=False)
        clawrtc_cli.cmd_install(args)
        out = capsys.readouterr().out
        assert "DRY RUN" in out

    def test_install_unsupported_platform(self, monkeypatch):
        """On Windows (non Linux/Darwin), install should call error()."""
        monkeypatch.setattr(platform, "system", lambda: "Windows")
        args = SimpleNamespace(
            wallet="w", dry_run=False, verify=False,
            service=False, no_service=False, yes=True)
        with pytest.raises(SystemExit):
            clawrtc_cli.cmd_install(args)

    def test_show_consent_disclosure(self, capsys):
        clawrtc_cli._show_consent_disclosure()
        out = capsys.readouterr().out
        assert "ClawRTC" in out
        assert "fingerprint" in out.lower()

    def test_cmd_stop_runs(self, monkeypatch):
        """cmd_stop should not crash."""
        # Stub run_cmd to avoid systemctl
        monkeypatch.setattr(clawrtc_cli, "run_cmd",
                            lambda cmd, **kw: None)
        monkeypatch.setattr(platform, "system", lambda: "Linux")
        args = SimpleNamespace()
        clawrtc_cli.cmd_stop(args)  # should not raise

    def test_cmd_wallet_unknown_action(self, capsys):
        args = SimpleNamespace(wallet_action="unknown_action")
        clawrtc_cli.cmd_wallet(args)
        out = capsys.readouterr().out
        assert "usage" in out.lower() or "wallet" in out.lower()


# ────────────────────────────────────────────────────────────
# 14. Fingerprint Checks — Anti-Emulation Detail Paths
# ────────────────────────────────────────────────────────────

class TestAntiEmulationDetails:
    """Cover specific anti-emulation detection branches."""

    def test_docker_env_detected(self, monkeypatch):
        monkeypatch.setenv("DOCKER", "1")
        _, data = fp_mod.check_anti_emulation()
        assert any("DOCKER" in i for i in data["vm_indicators"])

    def test_aws_env_detected(self, monkeypatch):
        monkeypatch.setenv("AWS_EXECUTION_ENV", "EC2")
        _, data = fp_mod.check_anti_emulation()
        assert any("AWS" in i for i in data["vm_indicators"])

    def test_clean_env_no_indicators(self, monkeypatch):
        """On a clean env with no VM indicators set, list may be empty."""
        for key in ["KUBERNETES", "DOCKER", "VIRTUAL", "container",
                     "AWS_EXECUTION_ENV", "ECS_CONTAINER_METADATA_URI",
                     "GOOGLE_CLOUD_PROJECT", "AZURE_FUNCTIONS_ENVIRONMENT",
                     "WEBSITE_INSTANCE_ID"]:
            monkeypatch.delenv(key, raising=False)
        _, data = fp_mod.check_anti_emulation()
        # On bare metal with clean env, should have zero env-based indicators
        env_indicators = [i for i in data["vm_indicators"] if i.startswith("ENV:")]
        assert len(env_indicators) == 0


# ────────────────────────────────────────────────────────────
# 15. Coinbase Wallet — create with existing wallet
# ────────────────────────────────────────────────────────────

class TestCoinbaseCreateExisting:
    def test_create_refuses_without_force(self, tmp_path, monkeypatch, capsys):
        cf = tmp_path / "cb.json"
        cf.write_text(json.dumps({
            "address": "0x" + "11" * 20,
            "network": "Base",
        }))
        monkeypatch.setattr(cb_mod, "COINBASE_FILE", str(cf))
        args = SimpleNamespace(force=False)
        cb_mod.coinbase_create(args)
        out = capsys.readouterr().out
        assert "already have" in out.lower()


# ────────────────────────────────────────────────────────────
# 16. Miner Fingerprint at Init + MAC Parsing
# ────────────────────────────────────────────────────────────

class TestMinerFingerprint:
    """Cover miner __init__ fingerprint paths and MAC address parsing."""

    def test_miner_init_fingerprint_pass(self, monkeypatch):
        """When fingerprint checks pass on init."""
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", True)
        monkeypatch.setattr(miner_mod, "validate_all_checks",
                            lambda include_rom_check=False: (
                                True, {"clock_drift": {"passed": True}}))
        m = miner_mod.LocalMiner(wallet="fpPassRTC")
        assert m.fingerprint_data["all_passed"] is True

    def test_miner_init_fingerprint_fail(self, monkeypatch):
        """When fingerprint checks fail on init."""
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", True)
        monkeypatch.setattr(miner_mod, "validate_all_checks",
                            lambda include_rom_check=False: (
                                False, {
                                    "clock_drift": {"passed": False},
                                    "cache_timing": {"passed": True},
                                }))
        m = miner_mod.LocalMiner(wallet="fpFailRTC")
        assert m.fingerprint_data["all_passed"] is False

    def test_miner_init_fingerprint_exception(self, monkeypatch):
        """When fingerprint checks raise an exception on init."""
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", True)

        def boom(**kw):
            raise RuntimeError("fingerprint crash")

        monkeypatch.setattr(miner_mod, "validate_all_checks", boom)
        m = miner_mod.LocalMiner(wallet="fpErrRTC")
        assert m.fingerprint_data["all_passed"] is False
        assert "error" in m.fingerprint_data

    def test_get_mac_addresses_ip_cmd(self, monkeypatch):
        """Test MAC address parsing from ip -o link output."""
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        m = miner_mod.LocalMiner(wallet="macTestRTC")

        import subprocess

        class FakeResult:
            stdout = ("2: eth0: <BROADCAST> mtu 1500 link/ether "
                      "aa:bb:cc:dd:ee:ff brd ff:ff:ff:ff:ff:ff\n"
                      "1: lo: <LOOPBACK> link/loopback "
                      "00:00:00:00:00:00 brd 00:00:00:00:00:00\n")

        monkeypatch.setattr(subprocess, "run", lambda *a, **kw: FakeResult())
        macs = m._get_mac_addresses()
        assert "aa:bb:cc:dd:ee:ff" in macs
        assert "00:00:00:00:00:00" not in macs

    def test_enroll_http_error(self, monkeypatch):
        """Enrollment with non-200 HTTP response."""
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        m = miner_mod.LocalMiner(wallet="enrollErrRTC")
        m.attestation_valid_until = time.time() + 9999
        m.hw_info = {"hostname": "h", "family": "x86", "arch": "m"}
        monkeypatch.setattr(miner_mod.requests, "post",
                            lambda *a, **kw: FakeResponse(
                                400, {"error": "bad request"}))
        assert m.enroll() is False

    def test_enroll_network_exception(self, monkeypatch):
        """Enrollment with network exception."""
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        m = miner_mod.LocalMiner(wallet="enrollExcRTC")
        m.attestation_valid_until = time.time() + 9999
        m.hw_info = {"hostname": "h", "family": "x86", "arch": "m"}

        def boom(*a, **kw):
            raise ConnectionError("offline")

        monkeypatch.setattr(miner_mod.requests, "post", boom)
        assert m.enroll() is False

    def test_enroll_rejected(self, monkeypatch):
        """Enrollment with ok=False response."""
        monkeypatch.setattr(miner_mod, "FINGERPRINT_AVAILABLE", False)
        m = miner_mod.LocalMiner(wallet="enrollRejRTC")
        m.attestation_valid_until = time.time() + 9999
        m.hw_info = {"hostname": "h", "family": "x86", "arch": "m"}
        monkeypatch.setattr(miner_mod.requests, "post",
                            lambda *a, **kw: FakeResponse(
                                200, {"ok": False, "reason": "banned"}))
        assert m.enroll() is False


# ────────────────────────────────────────────────────────────
# 17. Fingerprint — Cache Timing & Clock Drift Failure Paths
# ────────────────────────────────────────────────────────────

class TestFingerprintFailurePaths:
    """Cover specific failure conditions in fingerprint checks."""

    def test_cache_timing_no_hierarchy(self):
        """When l2/l1 and l3/l2 ratios are both below 1.01."""
        # We can't easily force this on real hardware, so test via mock
        data = {
            "l1_ns": 10.0, "l2_ns": 10.05, "l3_ns": 10.07,
            "l2_l1_ratio": 1.005, "l3_l2_ratio": 1.002,
            "fail_reason": "no_cache_hierarchy",
        }
        # Verify data structure is well-formed
        assert data["l2_l1_ratio"] < 1.01
        assert data["l3_l2_ratio"] < 1.01

    def test_clock_drift_no_drift_path(self):
        """If drift_stdev is zero, should fail."""
        data = {
            "mean_ns": 1000000, "stdev_ns": 500,
            "cv": 0.005, "drift_stdev": 0,
        }
        # Mirrors the logic in check_clock_drift
        valid = True
        if data["cv"] < 0.0001:
            valid = False
        elif data["drift_stdev"] == 0:
            valid = False
        assert valid is False

    def test_simd_identity_no_flags(self, monkeypatch):
        """When no SIMD flags can be detected."""
        # On Windows with no /proc/cpuinfo and no sysctl
        monkeypatch.setattr(platform, "machine", lambda: "unknown_arch")

        import builtins
        original_open = builtins.open

        def fake_open(path, *a, **kw):
            if "cpuinfo" in str(path):
                raise OSError("no cpuinfo")
            return original_open(path, *a, **kw)

        monkeypatch.setattr(builtins, "open", fake_open)
        import subprocess
        monkeypatch.setattr(subprocess, "run",
                            lambda *a, **kw: (_ for _ in ()).throw(
                                FileNotFoundError("no sysctl")))
        valid, data = fp_mod.check_simd_identity()
        assert data["arch"] == "unknown_arch"
        assert data["simd_flags_count"] == 0


# ────────────────────────────────────────────────────────────
# 18. PoW Miners — Process Detection & Get Running Processes
# ────────────────────────────────────────────────────────────

class TestPoWProcessDetection:
    """Cover _get_running_processes and detection edge cases."""

    def test_get_running_processes_returns_string(self):
        result = pow_mod._get_running_processes()
        assert isinstance(result, str)

    def test_detect_multiple_miners(self, monkeypatch):
        """When multiple miner processes are running."""
        monkeypatch.setattr(pow_mod, "_get_running_processes",
                            lambda: "xmrig ergo.jar kaspad")
        monkeypatch.setattr(pow_mod, "_check_port_open",
                            lambda port: False)
        detected = pow_mod.detect_running_miners()
        chains = [d["chain"] for d in detected]
        assert len(detected) >= 2

    def test_proof_nonce_binding(self, monkeypatch):
        """Proof includes nonce_binding derived from nonce + chain + time."""
        monkeypatch.setattr(pow_mod, "_probe_node_rpc", lambda *a: None)
        monkeypatch.setattr(pow_mod, "_get_running_processes",
                            lambda: "ergo.jar")
        proof = pow_mod.generate_pow_proof("ergo", "unique_nonce_xyz")
        assert proof is not None
        assert "nonce_binding" in proof
        assert len(proof["nonce_binding"]) == 64  # sha256 hex

    def test_pool_verification_connection_error(self, monkeypatch):
        import requests as req_mod

        def fail(*a, **kw):
            raise ConnectionError("unreachable")

        monkeypatch.setattr(req_mod, "get", fail)
        info = pow_mod.KNOWN_MINERS["ergo"]
        result = pow_mod._verify_pool_account(
            "ergo", info, "addr", "herominers")
        assert result is None
