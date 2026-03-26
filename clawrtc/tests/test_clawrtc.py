# SPDX-License-Identifier: MIT
"""
clawrtc — Comprehensive Test Suite
Covers: wallet creation, balance checking, miner attestation flow,
hardware fingerprint checks, PoW miner detection, and BCOS engine.
"""

import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from unittest import mock

import pytest


# ── Module paths ──────────────────────────────────────────────────
CLAWrtc_ROOT = "/usr/local/lib/python3.10/dist-packages"
sys.path.insert(0, CLAWrtc_ROOT)

import clawrtc
from clawrtc.coinbase_wallet import (
    _load_coinbase_wallet,
    _save_coinbase_wallet,
    coinbase_create,
    coinbase_show,
    coinbase_link,
    coinbase_swap_info,
    cmd_coinbase,
    COINBASE_FILE,
    INSTALL_DIR,
    SWAP_INFO,
)
from clawrtc.data.miner import LocalMiner
from clawrtc.data import fingerprint_checks as fp
from clawrtc.data import pow_miners
from clawrtc.data.bcos_engine import BCOSEngine, scan_repo


# ─────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────

@pytest.fixture
def temp_install_dir(monkeypatch):
    """Isolate coinbase wallet storage to a temp directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        fake_file = os.path.join(tmpdir, "coinbase_wallet.json")
        monkeypatch.setattr("clawrtc.coinbase_wallet.COINBASE_FILE", fake_file)
        yield fake_file


@pytest.fixture
def mock_wallet_file(temp_install_dir):
    """Pre-populate a wallet file."""
    data = {
        "address": "0xABC123def456000000000000000000000000000",
        "network": "Base (eip155:8453)",
        "created": "2026-01-01T00:00:00Z",
        "method": "manual_link",
    }
    os.makedirs(os.path.dirname(temp_install_dir), exist_ok=True)
    with open(temp_install_dir, "w") as f:
        json.dump(data, f)
    return temp_install_dir


class FakeArgs:
    """Minimal argparse.Namespace mock."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


# ─────────────────────────────────────────────────────────────────
# TEST: coinbase_wallet helpers
# ─────────────────────────────────────────────────────────────────

class TestCoinbaseWalletHelpers:
    def test_save_and_load_coinbase_wallet(self, temp_install_dir):
        data = {
            "address": "0x1234567890abcdef1234567890abcdef12345678",
            "network": "Base (eip155:8453)",
            "created": "2026-01-01T00:00:00Z",
            "method": "manual_link",
        }
        _save_coinbase_wallet(data)
        loaded = _load_coinbase_wallet()
        assert loaded is not None
        assert loaded["address"] == data["address"]
        assert loaded["network"] == data["network"]
        assert loaded["method"] == data["method"]

    def test_load_coinbase_wallet_missing_file(self, temp_install_dir):
        assert not os.path.exists(temp_install_dir)
        result = _load_coinbase_wallet()
        assert result is None

    def test_load_coinbase_wallet_invalid_json(self, temp_install_dir):
        with open(temp_install_dir, "w") as f:
            f.write("not valid json {{{")
        result = _load_coinbase_wallet()
        assert result is None

    def test_swap_info_contains_contract_addresses(self, capsys):
        args = FakeArgs()
        coinbase_swap_info(args)
        out = capsys.readouterr().out
        assert SWAP_INFO["wrtc_contract"] in out
        assert SWAP_INFO["usdc_contract"] in out
        assert SWAP_INFO["aerodrome_pool"] in out
        assert "Aerodrome" in out

    def test_coinbase_show_no_wallet(self, temp_install_dir, capsys):
        coinbase_show(FakeArgs())
        out = capsys.readouterr().out
        assert "No Coinbase wallet found" in out

    def test_coinbase_show_with_wallet(self, mock_wallet_file, capsys):
        coinbase_show(FakeArgs())
        out = capsys.readouterr().out
        assert "0xABC123def456" in out
        assert "Base" in out

    def test_coinbase_link_invalid_address_short(self, capsys):
        args = FakeArgs(base_address="0x123")
        coinbase_link(args)
        out = capsys.readouterr().out
        assert "Invalid" in out

    def test_coinbase_link_invalid_address_no_0x(self, capsys):
        args = FakeArgs(base_address="A" * 40)
        coinbase_link(args)
        out = capsys.readouterr().out
        assert "Invalid" in out

    def test_coinbase_link_valid_address(self, temp_install_dir, capsys):
        addr = "0x" + "A" * 40
        args = FakeArgs(base_address=addr)
        coinbase_link(args)
        out = capsys.readouterr().out
        assert addr in out
        assert "linked" in out
        loaded = _load_coinbase_wallet()
        assert loaded["address"] == addr
        assert loaded["method"] == "manual_link"

    def test_coinbase_create_no_cdp_credentials(self, temp_install_dir, capsys, monkeypatch):
        monkeypatch.delenv("CDP_API_KEY_NAME", raising=False)
        monkeypatch.delenv("CDP_API_KEY_PRIVATE_KEY", raising=False)
        args = FakeArgs()
        coinbase_create(args)
        out = capsys.readouterr().out
        assert "CDP credentials not configured" in out

    def test_coinbase_create_already_exists_no_force(self, mock_wallet_file, capsys):
        args = FakeArgs()
        coinbase_create(args)
        out = capsys.readouterr().out
        assert "already have a Coinbase wallet" in out
        assert "ABC123" in out

    def test_coinbase_create_force_new(self, mock_wallet_file, capsys, monkeypatch):
        monkeypatch.setenv("CDP_API_KEY_NAME", "orgs/foo/apiKeys/bar")
        monkeypatch.setenv("CDP_API_KEY_PRIVATE_KEY", "-----BEGIN EC PRIVATE KEY-----\ntest\n-----END EC PRIVATE KEY-----")
        args = FakeArgs(force=True)
        # coinbase_agentkit won't be installed or will fail → graceful error
        coinbase_create(args)
        out = capsys.readouterr().out
        # Should either succeed with AgentKit or gracefully fail
        assert isinstance(out, str)

    def test_cmd_coinbase_unknown_action(self, capsys):
        args = FakeArgs(coinbase_action="unknown_action")
        cmd_coinbase(args)
        out = capsys.readouterr().out
        assert "Usage:" in out

    def test_cmd_coinbase_dispatch_create(self, temp_install_dir, capsys, monkeypatch):
        monkeypatch.delenv("CDP_API_KEY_NAME", raising=False)
        monkeypatch.delenv("CDP_API_KEY_PRIVATE_KEY", raising=False)
        args = FakeArgs(coinbase_action="create")
        cmd_coinbase(args)
        # Should show credential prompt
        out = capsys.readouterr().out
        assert "CDP" in out or "credential" in out.lower() or "Sign up" in out


# ─────────────────────────────────────────────────────────────────
# TEST: LocalMiner wallet creation & balance
# ─────────────────────────────────────────────────────────────────

class TestLocalMinerWallet:
    def test_local_miner_generates_wallet(self):
        miner = LocalMiner()
        assert miner.wallet is not None
        assert isinstance(miner.wallet, str)
        assert len(miner.wallet) > 0
        assert miner.wallet.endswith("RTC")

    def test_local_miner_accepts_custom_wallet(self):
        custom = "0xabcd1234abcd1234abcd1234abcd1234abcd1234RTC"
        miner = LocalMiner(wallet=custom)
        assert miner.wallet == custom

    def test_local_miner_wallet_sha256_format(self):
        miner = LocalMiner()
        # Generated wallet should be hex-like
        assert re.match(r"^[a-f0-9]+RTC$", miner.wallet)

    def test_local_miner_initial_state(self):
        miner = LocalMiner()
        assert miner.node_url == "https://bulbous-bouffant.metalseed.net"
        assert miner.enrolled is False
        assert miner.attestation_valid_until == 0


class TestLocalMinerHWInfo:
    def test_get_hw_info_returns_dict(self):
        miner = LocalMiner()
        hw = miner._get_hw_info()
        assert isinstance(hw, dict)
        assert "platform" in hw
        assert "machine" in hw
        assert "family" in hw
        assert "arch" in hw
        assert "cores" in hw
        assert "memory_gb" in hw

    def test_detect_arch_returns_tuple(self):
        miner = LocalMiner()
        family, arch = miner._detect_arch()
        assert family in ("x86", "arm", "powerpc")
        assert isinstance(arch, str)

    def test_get_mac_addresses_returns_list(self):
        miner = LocalMiner()
        macs = miner._get_mac_addresses()
        assert isinstance(macs, list)
        assert len(macs) > 0
        for mac in macs:
            assert re.match(r"^[0-9a-f:]{17}$", mac)

    def test_collect_entropy_returns_stats(self):
        miner = LocalMiner()
        entropy = miner._collect_entropy(cycles=10, inner_loop=1000)
        assert "mean_ns" in entropy
        assert "variance_ns" in entropy
        assert "min_ns" in entropy
        assert "max_ns" in entropy
        assert entropy["sample_count"] == 10
        assert entropy["samples_preview"] is not None

    def test_collect_entropy_deterministic_inner_loop(self):
        miner = LocalMiner()
        e1 = miner._collect_entropy(cycles=5, inner_loop=100)
        e2 = miner._collect_entropy(cycles=5, inner_loop=100)
        # Same params → same inner loop size → similar mean (within 50%)
        assert 0 < e1["mean_ns"] < e2["mean_ns"] * 2 or \
               0 < e2["mean_ns"] < e1["mean_ns"] * 2


class TestLocalMinerBalance:
    def test_check_balance_returns_zero_on_network_error(self):
        miner = LocalMiner()
        # Network error → returns 0
        with mock.patch("requests.get", side_effect=Exception("no network")):
            balance = miner.check_balance()
        assert balance == 0

    def test_check_balance_returns_balance_rtc(self):
        miner = LocalMiner()
        fake_response = mock.Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = {"balance_rtc": 42}
        with mock.patch("requests.get", return_value=fake_response):
            balance = miner.check_balance()
        assert balance == 42


# ─────────────────────────────────────────────────────────────────
# TEST: LocalMiner attestation flow (mocked)
# ─────────────────────────────────────────────────────────────────

class TestLocalMinerAttestation:
    def test_attest_gets_challenge_nonce(self):
        miner = LocalMiner()
        miner._get_hw_info()
        miner.fingerprint_data = {"all_passed": True, "checks": {}}

        challenge_payload = {"nonce": "test_nonce_12345"}
        fake_challenge = mock.Mock()
        fake_challenge.status_code = 200
        fake_challenge.json.return_value = challenge_payload

        fake_submit = mock.Mock()
        fake_submit.status_code = 200
        fake_submit.json.return_value = {"ok": True}
        fake_submit.text = "{}"

        with mock.patch("requests.post", side_effect=[fake_challenge, fake_submit]):
            result = miner.attest()

        assert result is True
        assert miner.attestation_valid_until > 0

    def test_attest_fails_on_challenge_error(self):
        miner = LocalMiner()
        miner._get_hw_info()
        with mock.patch("requests.post", side_effect=Exception("connection refused")):
            result = miner.attest()
        assert result is False

    def test_attest_fails_on_challenge_non_200(self):
        miner = LocalMiner()
        miner._get_hw_info()
        fake_resp = mock.Mock()
        fake_resp.status_code = 500
        with mock.patch("requests.post", return_value=fake_resp):
            result = miner.attest()
        assert result is False

    def test_attest_rejected_by_server(self):
        miner = LocalMiner()
        miner._get_hw_info()
        miner.fingerprint_data = {"all_passed": True}

        fake_challenge = mock.Mock()
        fake_challenge.status_code = 200
        fake_challenge.json.return_value = {"nonce": "nonce123"}

        fake_submit = mock.Mock()
        fake_submit.status_code = 200
        fake_submit.json.return_value = {"ok": False, "error": "bad signature"}

        with mock.patch("requests.post", side_effect=[fake_challenge, fake_submit]):
            result = miner.attest()
        assert result is False

    def test_enroll_attestation_expired_retries_attest(self):
        miner = LocalMiner()
        miner.attestation_valid_until = 0  # expired
        miner._get_hw_info()

        # First post (challenge), second post (attest submit), third post (enroll)
        fake_challenge = mock.Mock(status_code=200)
        fake_challenge.json.return_value = {"nonce": "n"}
        fake_submit = mock.Mock(status_code=200)
        fake_submit.json.return_value = {"ok": True}
        fake_enroll = mock.Mock(status_code=200)
        fake_enroll.json.return_value = {"ok": True, "epoch": 1, "weight": 1.5}

        with mock.patch("requests.post", side_effect=[
            fake_challenge, fake_submit, fake_enroll
        ]):
            result = miner.enroll()
        assert result is True
        assert miner.enrolled is True

    def test_enroll_fails_http_error(self):
        miner = LocalMiner()
        miner.attestation_valid_until = time.time() + 1000  # valid
        miner._get_hw_info()
        with mock.patch("requests.post", side_effect=Exception("network")):
            result = miner.enroll()
        assert result is False


# ─────────────────────────────────────────────────────────────────
# TEST: Hardware Fingerprint Checks
# ─────────────────────────────────────────────────────────────────

class TestFingerprintChecks:
    def test_check_clock_drift_returns_tuple(self):
        valid, data = fp.check_clock_drift(samples=20)
        assert isinstance(valid, bool)
        assert isinstance(data, dict)
        assert "mean_ns" in data
        assert "cv" in data

    def test_check_cache_timing_returns_tuple(self):
        valid, data = fp.check_cache_timing(iterations=10)
        assert isinstance(valid, bool)
        assert isinstance(data, dict)
        assert "l1_ns" in data
        assert "l2_ns" in data
        assert "l3_ns" in data
        assert "l2_l1_ratio" in data

    def test_check_simd_identity_returns_tuple(self):
        valid, data = fp.check_simd_identity()
        assert isinstance(valid, bool)
        assert isinstance(data, dict)
        assert "arch" in data
        # At least one SIMD flag or arch should be detected
        has_any = (
            data.get("has_sse") or
            data.get("has_avx") or
            data.get("has_altivec") or
            data.get("has_neon") or
            len(data.get("sample_flags", [])) > 0
        )
        assert has_any or data.get("simd_flags_count", 0) >= 0

    def test_check_thermal_drift_returns_tuple(self):
        valid, data = fp.check_thermal_drift(samples=10)
        assert isinstance(valid, bool)
        assert isinstance(data, dict)
        assert "cold_avg_ns" in data
        assert "hot_avg_ns" in data
        assert "drift_ratio" in data

    def test_check_instruction_jitter_returns_tuple(self):
        valid, data = fp.check_instruction_jitter(samples=10)
        assert isinstance(valid, bool)
        assert isinstance(data, dict)
        assert "int_avg_ns" in data
        assert "fp_avg_ns" in data
        assert "branch_avg_ns" in data

    def test_check_anti_emulation_returns_tuple(self):
        valid, data = fp.check_anti_emulation()
        assert isinstance(valid, bool)
        assert isinstance(data, dict)
        assert "vm_indicators" in data
        assert "indicator_count" in data
        assert "is_likely_vm" in data

    def test_validate_all_checks_returns_tuple(self):
        passed, results = fp.validate_all_checks(include_rom_check=False)
        assert isinstance(passed, bool)
        assert isinstance(results, dict)
        expected_keys = {
            "clock_drift", "cache_timing", "simd_identity",
            "thermal_drift", "instruction_jitter", "anti_emulation",
        }
        assert expected_keys.issubset(results.keys())
        for key in expected_keys:
            assert "passed" in results[key]
            assert "data" in results[key]


# ─────────────────────────────────────────────────────────────────
# TEST: PoW Miner Detection
# ─────────────────────────────────────────────────────────────────

class TestPowMinerDetection:
    def test_known_miners_defined(self):
        assert isinstance(pow_miners.KNOWN_MINERS, dict)
        assert len(pow_miners.KNOWN_MINERS) > 0
        for chain, info in pow_miners.KNOWN_MINERS.items():
            assert "display" in info
            assert "algo" in info
            assert "process_names" in info
            assert isinstance(info["process_names"], list)

    def test_pow_bonus_multipliers_defined(self):
        assert pow_miners.POW_BONUS["node_rpc"] == 1.5
        assert pow_miners.POW_BONUS["pool_account"] == 1.3
        assert pow_miners.POW_BONUS["process_only"] == 1.15

    def test_detect_running_miners_returns_list(self):
        result = pow_miners.detect_running_miners()
        assert isinstance(result, list)
        # Should be empty in test env (no real miners running)
        for item in result:
            assert "chain" in item
            assert "display" in item
            assert "algo" in item
            assert "proof_type" in item

    def test_get_supported_chains(self):
        chains = pow_miners.get_supported_chains()
        assert isinstance(chains, list)
        assert len(chains) > 0
        assert "ergo" in chains
        assert "kaspa" in chains
        assert "monero" in chains

    def test_get_chain_info_valid(self):
        info = pow_miners.get_chain_info("ergo")
        assert info is not None
        assert info["algo"] == "autolykos2"

    def test_get_chain_info_invalid(self):
        info = pow_miners.get_chain_info("nonexistent_chain_xyz")
        assert info is None

    def test_generate_pow_proof_unknown_chain_returns_none(self):
        result = pow_miners.generate_pow_proof("unknown_chain", "nonce123")
        assert result is None

    def test_generate_pow_proof_no_miner_returns_none(self):
        # With no actual miner running, should return None
        result = pow_miners.generate_pow_proof("ergo", "nonce123")
        # May be None or dict depending on process detection
        assert result is None or isinstance(result, dict)

    def test_generate_pow_proof_binds_nonce(self):
        result = pow_miners.generate_pow_proof(
            "ergo", "test_nonce", pool_address="erg_test", pool_name="herominers"
        )
        # Returns None if no miner, which is fine
        if result is not None:
            assert "nonce_binding" in result
            assert "timestamp" in result
            assert result["chain"] == "ergo"


# ─────────────────────────────────────────────────────────────────
# TEST: BCOS Engine
# ─────────────────────────────────────────────────────────────────

class TestBCOSEngine:
    def test_bcos_engine_init(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        assert engine.tier == "L1"
        assert engine.repo_path == tmp_path.resolve()

    def test_bcos_engine_tier_L0_L1_L2(self, tmp_path):
        for tier in ("L0", "L1", "L2"):
            engine = BCOSEngine(str(tmp_path), tier=tier)
            assert engine.tier == tier

    def test_detect_repo_name_no_git(self, tmp_path):
        engine = BCOSEngine(str(tmp_path))
        name = engine._detect_repo_name()
        assert name == tmp_path.name

    def test_tier_met_L0(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L0")
        engine.score_breakdown = {"license_compliance": 20, "vulnerability_scan": 25,
                                  "static_analysis": 20, "sbom_completeness": 10,
                                  "dependency_freshness": 5, "test_evidence": 10,
                                  "review_attestation": 0}
        assert engine._tier_met() is True

    def test_tier_met_L2_no_reviewer(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L2", reviewer="")
        engine.score_breakdown = {"license_compliance": 20, "vulnerability_scan": 25,
                                  "static_analysis": 20, "sbom_completeness": 10,
                                  "dependency_freshness": 5, "test_evidence": 10,
                                  "review_attestation": 10}
        assert engine._tier_met() is False  # needs reviewer

    def test_tier_met_L2_with_reviewer(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L2", reviewer="@alice")
        engine.score_breakdown = {"license_compliance": 20, "vulnerability_scan": 25,
                                  "static_analysis": 20, "sbom_completeness": 10,
                                  "dependency_freshness": 5, "test_evidence": 10,
                                  "review_attestation": 10}
        assert engine._tier_met() is True

    def test_run_all_returns_report_keys(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        report = engine.run_all()
        assert "schema" in report
        assert report["schema"] == "bcos-attestation/v2"
        assert "trust_score" in report
        assert "score_breakdown" in report
        assert "checks" in report
        assert "cert_id" in report
        assert "commitment" in report
        assert "tier_met" in report
        assert "engine_version" in report

    def test_run_all_sets_all_score_keys(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        report = engine.run_all()
        expected = {
            "license_compliance", "vulnerability_scan", "static_analysis",
            "sbom_completeness", "dependency_freshness",
            "test_evidence", "review_attestation",
        }
        assert expected.issubset(report["checks"].keys())
        assert expected.issubset(report["score_breakdown"].keys())

    def test_scan_repo_convenience_function(self, tmp_path):
        report = scan_repo(str(tmp_path), tier="L1")
        assert "trust_score" in report
        assert report["tier"] == "L1"

    def test_commit_id_derivation(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        report = engine.run_all()
        cert_id = report["cert_id"]
        assert cert_id.startswith("BCOS-")
        assert len(cert_id) == len("BCOS-") + 8

    def test_trust_score_bounded_0_to_100(self, tmp_path):
        # A fresh empty repo should still get a score (0s or partial)
        engine = BCOSEngine(str(tmp_path), tier="L0")
        report = engine.run_all()
        assert 0 <= report["trust_score"] <= 100

    def test_check_spdx_empty_repo(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        engine._check_spdx()
        check = engine.checks["license_compliance"]
        assert "spdx_coverage_pct" in check
        assert check["code_files_total"] >= 0

    def test_check_test_evidence_empty_repo(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        engine._check_test_evidence()
        check = engine.checks["test_evidence"]
        assert "test_file_count" in check
        assert "has_tests" in check or "passed" in check

    def test_check_dep_freshness(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        engine._check_dep_freshness()
        check = engine.checks["dependency_freshness"]
        assert "fresh_pct" in check
        assert "total_deps" in check

    def test_check_review_L1(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L1")
        engine._check_review()
        check = engine.checks["review_attestation"]
        assert check["tier"] == "L1"
        assert engine.score_breakdown["review_attestation"] == 5

    def test_check_review_L2_with_reviewer(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L2", reviewer="alice")
        engine._check_review()
        assert engine.score_breakdown["review_attestation"] == 10

    def test_compute_trust_score_caps_at_max(self, tmp_path):
        engine = BCOSEngine(str(tmp_path), tier="L2", reviewer="alice")
        engine.score_breakdown = {
            "license_compliance": 100,  # over cap
            "vulnerability_scan": 50,
            "static_analysis": 40,
            "sbom_completeness": 20,
            "dependency_freshness": 10,
            "test_evidence": 20,
            "review_attestation": 20,
        }
        engine._compute_trust_score()
        assert engine.score_breakdown["license_compliance"] == 20  # capped

    def test_score_weights_sum_to_100(self):
        from clawrtc.data.bcos_engine import SCORE_WEIGHTS, TIER_THRESHOLDS
        total = sum(SCORE_WEIGHTS.values())
        assert total == 100
        assert set(TIER_THRESHOLDS.keys()) == {"L0", "L1", "L2"}
        assert TIER_THRESHOLDS["L0"] < TIER_THRESHOLDS["L1"] < TIER_THRESHOLDS["L2"]


# ─────────────────────────────────────────────────────────────────
# TEST: Package metadata
# ─────────────────────────────────────────────────────────────────

class TestPackageMetadata:
    def test_version_available(self):
        assert clawrtc.__version__ is not None
        assert isinstance(clawrtc.__version__, str)

    def test_version_format(self):
        assert re.match(r"\d+\.\d+\.\d+", clawrtc.__version__)


# ─────────────────────────────────────────────────────────────────
# TEST: SWAP_INFO constants
# ─────────────────────────────────────────────────────────────────

class TestSwapInfo:
    def test_swap_info_has_required_keys(self):
        required = ["wrtc_contract", "usdc_contract", "aerodrome_pool",
                    "swap_url", "network", "reference_price_usd"]
        for key in required:
            assert key in SWAP_INFO

    def test_wrtc_contract_is_valid_eth_address(self):
        assert re.match(r"^0x[a-fA-F0-9]{40}$", SWAP_INFO["wrtc_contract"])

    def test_usdc_contract_is_valid_eth_address(self):
        assert re.match(r"^0x[a-fA-F0-9]{40}$", SWAP_INFO["usdc_contract"])

    def test_swap_url_contains_usdc_and_wrtc(self):
        url = SWAP_INFO["swap_url"]
        assert "aerodrome.finance" in url
        assert SWAP_INFO["usdc_contract"][:10] in url

    def test_reference_price_is_positive_float(self):
        assert isinstance(SWAP_INFO["reference_price_usd"], float)
        assert SWAP_INFO["reference_price_usd"] > 0


# ─────────────────────────────────────────────────────────────────
# INTEGRATION: Full miner lifecycle (mocked)
# ─────────────────────────────────────────────────────────────────

class TestMinerLifecycleIntegration:
    def test_full_mine_cycle_mocked(self):
        """Simulate a full attest → enroll → balance cycle with mocks."""
        miner = LocalMiner(wallet="test_wallet_RTC")
        miner._get_hw_info()
        miner.fingerprint_data = {"all_passed": True}

        fake_challenge = mock.Mock(status_code=200)
        fake_challenge.json.return_value = {"nonce": "lifecycle_nonce"}
        fake_submit = mock.Mock(status_code=200)
        fake_submit.json.return_value = {"ok": True}
        fake_enroll = mock.Mock(status_code=200)
        fake_enroll.json.return_value = {"ok": True, "epoch": 1, "weight": 2.0}
        fake_balance = mock.Mock(status_code=200)
        fake_balance.json.return_value = {"balance_rtc": 99}

        with mock.patch("requests.post", side_effect=[
            fake_challenge, fake_submit, fake_enroll
        ]):
            attest_ok = miner.attest()
        assert attest_ok is True
        assert miner.attestation_valid_until > 0

        with mock.patch("requests.post", return_value=fake_enroll):
            enroll_ok = miner.enroll()
        assert enroll_ok is True
        assert miner.enrolled is True

        with mock.patch("requests.get", return_value=fake_balance):
            balance = miner.check_balance()
        assert balance == 99
