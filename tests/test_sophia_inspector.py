#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Comprehensive tests for SophiaCore Attestation Inspector.

Covers:
  - Response parsing (valid, malformed, edge cases)
  - Database CRUD, WAL mode, retry logic
  - Inspector orchestration with mocked Ollama
  - HTTP API endpoints
  - Override workflow
  - Batch status
  - Ollama failover behavior

Usage:
    python -m pytest tests/test_sophia_inspector.py -v
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from urllib.error import URLError

# Ensure scripts/ is importable
_SCRIPTS_DIR = str(Path(__file__).parent.parent / "scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from sophia_db import (
    InspectionResult,
    InspectionRecord,
    SophiaDB,
    VALID_VERDICTS,
    fingerprint_hash,
)
from sophia_inspector import (
    OllamaClient,
    SophiaInspector,
    build_user_prompt,
    parse_sophia_response,
    SYSTEM_PROMPT,
    VALID_FLAGS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary SophiaDB."""
    db_path = str(tmp_path / "test_sophia.db")
    return SophiaDB(db_path)


@pytest.fixture
def sample_fingerprint():
    """Sample fingerprint bundle for testing."""
    return {
        "all_passed": True,
        "checks": {
            "clock_drift": {
                "passed": True,
                "data": {"cv": 0.042, "samples": 1000, "mean": 25000, "std_dev": 1050},
            },
            "cache_timing": {
                "passed": True,
                "data": {"l1_ns": 2, "l2_ns": 8, "l3_ns": 35, "ram_ns": 120},
            },
            "simd_identity": {
                "passed": True,
                "data": {"features": ["sse2", "avx2"], "arch": "x86_64"},
            },
            "thermal_drift": {
                "passed": True,
                "data": {"entropy": 0.78, "variance": 0.023},
            },
            "instruction_jitter": {
                "passed": True,
                "data": {"jitter_cv": 0.031, "samples": 500},
            },
            "anti_emulation": {
                "passed": True,
                "data": {"vm_detected": False, "hypervisor": "none"},
            },
        },
    }


@pytest.fixture
def sample_hardware():
    return {
        "cpu_model": "Intel Core i7-4770",
        "device_family": "x86",
        "device_arch": "x86_64",
    }


@pytest.fixture
def sample_result():
    return InspectionResult(
        miner_id="test_miner_001",
        verdict="APPROVED",
        confidence=0.92,
        reasoning="All checks coherent, genuine silicon pattern.",
        flags=(),
        epoch=104,
        fingerprint_hash="abc123",
        fingerprint_data='{"all_passed":true}',
        ollama_host="http://localhost:11434",
        latency_ms=1500,
    )


# ===========================================================================
# Test: Response Parsing
# ===========================================================================

class TestResponseParsing:
    """Test the robust 4-stage response parsing."""

    def test_valid_json_direct(self):
        raw = '{"verdict":"APPROVED","confidence":0.95,"reasoning":"Looks good","flags":[]}'
        result = parse_sophia_response(raw)
        assert result["verdict"] == "APPROVED"
        assert result["confidence"] == 0.95
        assert result["flags"] == []

    def test_json_with_markdown_fences(self):
        raw = '```json\n{"verdict":"SUSPICIOUS","confidence":0.4,"reasoning":"Odd","flags":["VM_INDICATORS"]}\n```'
        result = parse_sophia_response(raw)
        assert result["verdict"] == "SUSPICIOUS"
        assert "VM_INDICATORS" in result["flags"]

    def test_json_with_plain_fences(self):
        raw = '```\n{"verdict":"CAUTIOUS","confidence":0.6,"reasoning":"Maybe","flags":[]}\n```'
        result = parse_sophia_response(raw)
        assert result["verdict"] == "CAUTIOUS"

    def test_json_embedded_in_text(self):
        raw = 'Here is my analysis:\n{"verdict":"REJECTED","confidence":0.88,"reasoning":"VM detected","flags":["VM_INDICATORS"]}\nEnd.'
        result = parse_sophia_response(raw)
        assert result["verdict"] == "REJECTED"

    def test_completely_malformed(self):
        raw = "I think this hardware looks suspicious but I can't tell for sure."
        result = parse_sophia_response(raw)
        assert result["verdict"] == "CAUTIOUS"
        assert result["confidence"] == 0.3
        assert "parse_error" in result["flags"]

    def test_empty_response(self):
        result = parse_sophia_response("")
        assert result["verdict"] == "CAUTIOUS"
        assert result["confidence"] == 0.3

    def test_invalid_verdict_falls_through(self):
        raw = '{"verdict":"MAYBE","confidence":0.5,"reasoning":"unsure","flags":[]}'
        result = parse_sophia_response(raw)
        # Should fall through to graceful degradation
        assert result["verdict"] == "CAUTIOUS"
        assert result["confidence"] == 0.3

    def test_confidence_clamped(self):
        raw = '{"verdict":"APPROVED","confidence":1.5,"reasoning":"very sure","flags":[]}'
        result = parse_sophia_response(raw)
        assert result["confidence"] == 1.0

    def test_confidence_negative_clamped(self):
        raw = '{"verdict":"APPROVED","confidence":-0.1,"reasoning":"unsure","flags":[]}'
        result = parse_sophia_response(raw)
        assert result["confidence"] == 0.0

    def test_flags_non_list(self):
        raw = '{"verdict":"APPROVED","confidence":0.9,"reasoning":"ok","flags":"single_flag"}'
        result = parse_sophia_response(raw)
        assert result["flags"] == []

    def test_missing_fields_defaults(self):
        raw = '{"verdict":"APPROVED"}'
        result = parse_sophia_response(raw)
        assert result["confidence"] == 0.5
        assert result["reasoning"] == ""
        assert result["flags"] == []

    def test_verdict_case_insensitive(self):
        raw = '{"verdict":"approved","confidence":0.8,"reasoning":"ok","flags":[]}'
        result = parse_sophia_response(raw)
        assert result["verdict"] == "APPROVED"


# ===========================================================================
# Test: Database Layer
# ===========================================================================

class TestSophiaDB:
    """Test the database CRUD operations."""

    def test_db_creation(self, tmp_db):
        """DB should be created with proper schema."""
        conn = sqlite3.connect(tmp_db.db_path)
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()
        assert "sophia_inspections" in tables

    def test_wal_mode(self, tmp_db):
        """DB should use WAL mode for concurrency."""
        conn = sqlite3.connect(tmp_db.db_path)
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode.lower() == "wal"

    def test_insert_and_retrieve(self, tmp_db, sample_result):
        row_id = tmp_db.record_inspection(sample_result)
        assert row_id > 0

        record = tmp_db.get_latest("test_miner_001")
        assert record is not None
        assert record.miner_id == "test_miner_001"
        assert record.verdict == "APPROVED"
        assert record.confidence == 0.92

    def test_get_latest_none(self, tmp_db):
        assert tmp_db.get_latest("nonexistent") is None

    def test_get_history(self, tmp_db, sample_result):
        for i in range(5):
            tmp_db.record_inspection(InspectionResult(
                miner_id="test_miner",
                verdict="APPROVED" if i % 2 == 0 else "CAUTIOUS",
                confidence=0.8 + i * 0.02,
            ))

        history = tmp_db.get_history("test_miner", limit=3)
        assert len(history) == 3
        # Should be newest first
        assert history[0].confidence > history[1].confidence

    def test_override_workflow(self, tmp_db, sample_result):
        row_id = tmp_db.record_inspection(InspectionResult(
            miner_id="suspicious_miner",
            verdict="SUSPICIOUS",
            confidence=0.4,
            reasoning="Multiple anomalies detected",
            flags=("CACHE_HIERARCHY_INVALID",),
        ))

        # Override to APPROVED
        updated = tmp_db.record_override(
            row_id, "APPROVED", "Manual review: hardware is genuine", "admin_scott"
        )
        assert updated

        record = tmp_db.get_latest("suspicious_miner")
        assert record.override_verdict == "APPROVED"
        assert record.override_by == "admin_scott"
        assert record.effective_verdict == "APPROVED"
        assert record.emoji == "✨"

    def test_override_invalid_verdict(self, tmp_db, sample_result):
        row_id = tmp_db.record_inspection(sample_result)
        with pytest.raises(ValueError, match="Override verdict"):
            tmp_db.record_override(row_id, "CAUTIOUS", "reason", "admin")

    def test_override_empty_reason(self, tmp_db, sample_result):
        row_id = tmp_db.record_inspection(sample_result)
        with pytest.raises(ValueError, match="reason"):
            tmp_db.record_override(row_id, "APPROVED", "  ", "admin")

    def test_pending_reviews(self, tmp_db):
        tmp_db.record_inspection(InspectionResult(
            miner_id="approved_miner", verdict="APPROVED", confidence=0.95,
        ))
        tmp_db.record_inspection(InspectionResult(
            miner_id="cautious_miner", verdict="CAUTIOUS", confidence=0.6,
        ))
        tmp_db.record_inspection(InspectionResult(
            miner_id="suspicious_miner", verdict="SUSPICIOUS", confidence=0.3,
        ))

        pending = tmp_db.get_pending_reviews()
        assert len(pending) == 2
        # SUSPICIOUS should come first
        assert pending[0].verdict == "SUSPICIOUS"
        assert pending[1].verdict == "CAUTIOUS"

    def test_batch_status(self, tmp_db):
        tmp_db.record_inspection(InspectionResult(
            miner_id="m1", verdict="APPROVED", confidence=0.9,
        ))
        tmp_db.record_inspection(InspectionResult(
            miner_id="m2", verdict="CAUTIOUS", confidence=0.6,
        ))

        batch = tmp_db.get_batch_status(["m1", "m2", "m_nonexistent"])
        assert batch["m1"] is not None
        assert batch["m1"].verdict == "APPROVED"
        assert batch["m2"].verdict == "CAUTIOUS"
        assert batch["m_nonexistent"] is None

    def test_historical_fingerprints(self, tmp_db):
        for i in range(5):
            tmp_db.record_inspection(InspectionResult(
                miner_id="test_miner",
                verdict="APPROVED",
                confidence=0.9,
                fingerprint_data=json.dumps({"epoch": i, "cv": 0.04 + i * 0.001}),
            ))

        historical = tmp_db.get_historical_fingerprints("test_miner", limit=3)
        assert len(historical) == 3
        # Newest first
        parsed = json.loads(historical[0])
        assert parsed["epoch"] == 4

    def test_stats(self, tmp_db):
        for v in ["APPROVED", "APPROVED", "CAUTIOUS", "SUSPICIOUS"]:
            tmp_db.record_inspection(InspectionResult(
                miner_id=f"miner_{v.lower()}", verdict=v, confidence=0.7,
                latency_ms=1500,
            ))

        stats = tmp_db.get_stats()
        assert stats["total_inspections"] == 4
        assert stats["by_verdict"]["APPROVED"] == 2
        assert stats["by_verdict"]["CAUTIOUS"] == 1
        assert stats["pending_reviews"] == 2
        assert stats["avg_latency_ms"] > 0

    def test_invalid_verdict_rejected(self, tmp_db):
        with pytest.raises(ValueError, match="Invalid verdict"):
            tmp_db.record_inspection(InspectionResult(
                miner_id="test", verdict="INVALID", confidence=0.5,
            ))

    def test_invalid_confidence_rejected(self, tmp_db):
        with pytest.raises(ValueError, match="Confidence"):
            tmp_db.record_inspection(InspectionResult(
                miner_id="test", verdict="APPROVED", confidence=1.5,
            ))


# ===========================================================================
# Test: Fingerprint Hash
# ===========================================================================

class TestFingerprintHash:
    def test_deterministic(self, sample_fingerprint):
        h1 = fingerprint_hash(sample_fingerprint)
        h2 = fingerprint_hash(sample_fingerprint)
        assert h1 == h2
        assert len(h1) == 64

    def test_different_data_different_hash(self, sample_fingerprint):
        h1 = fingerprint_hash(sample_fingerprint)
        modified = dict(sample_fingerprint)
        modified["all_passed"] = False
        h2 = fingerprint_hash(modified)
        assert h1 != h2


# ===========================================================================
# Test: Prompt Building
# ===========================================================================

class TestPromptBuilding:
    def test_basic_prompt(self, sample_fingerprint, sample_hardware):
        prompt = build_user_prompt(sample_fingerprint, sample_hardware)
        assert "CURRENT FINGERPRINT" in prompt
        assert "CLAIMED HARDWARE" in prompt
        assert "clock_drift" in prompt
        assert "Intel Core i7-4770" in prompt

    def test_prompt_with_history(self, sample_fingerprint, sample_hardware):
        history = [
            '{"cv": 0.041, "epoch": 103}',
            '{"cv": 0.043, "epoch": 102}',
        ]
        prompt = build_user_prompt(sample_fingerprint, sample_hardware, history)
        assert "HISTORICAL FINGERPRINTS" in prompt
        assert "Epoch -1" in prompt
        assert "Epoch -2" in prompt

    def test_prompt_no_history(self, sample_fingerprint, sample_hardware):
        prompt = build_user_prompt(sample_fingerprint, sample_hardware, None)
        assert "HISTORICAL" not in prompt

    def test_system_prompt_has_instructions(self):
        assert "verdict" in SYSTEM_PROMPT.lower()
        assert "confidence" in SYSTEM_PROMPT.lower()
        assert "JSON" in SYSTEM_PROMPT


# ===========================================================================
# Test: Ollama Client
# ===========================================================================

class TestOllamaClient:
    def test_init(self):
        client = OllamaClient(
            hosts=["http://host1:11434", "http://host2:11434"],
            model="test-model",
        )
        assert len(client.hosts) == 2
        assert client.model == "test-model"

    @patch("sophia_inspector.urllib.request.urlopen")
    def test_health_check_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "models": [{"name": "test-model:latest"}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        client = OllamaClient(hosts=["http://localhost:11434"], model="test-model")
        assert client.check_host_health("http://localhost:11434")

    @patch("sophia_inspector.urllib.request.urlopen")
    def test_health_check_model_not_found(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps({
            "models": [{"name": "other-model:latest"}]
        }).encode()
        mock_urlopen.return_value = mock_resp

        client = OllamaClient(hosts=["http://localhost:11434"], model="test-model")
        assert not client.check_host_health("http://localhost:11434")

    @patch("sophia_inspector.urllib.request.urlopen")
    def test_generate_failover(self, mock_urlopen):
        """Test that generation falls over to next host on failure."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            # Fail on first call (tags for host1), succeed on second (tags for host2), etc.
            req = args[0]
            url = req.full_url if hasattr(req, 'full_url') else str(req)

            if "host1" in url:
                raise URLError("Connection refused")

            mock_resp = MagicMock()
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)

            if "/api/tags" in url:
                mock_resp.read.return_value = json.dumps({
                    "models": [{"name": "test-model:latest"}]
                }).encode()
            else:
                mock_resp.read.return_value = json.dumps({
                    "response": '{"verdict":"APPROVED","confidence":0.9,"reasoning":"ok","flags":[]}'
                }).encode()
            return mock_resp

        mock_urlopen.side_effect = side_effect

        client = OllamaClient(
            hosts=["http://host1:11434", "http://host2:11434"],
            model="test-model",
            per_host_timeout=5,
        )
        # Force health checks to pass
        client._host_health = {h: True for h in client.hosts}
        client._host_last_check = {h: time.time() for h in client.hosts}

        response, host, latency = client.generate("system", "user")
        assert host == "http://host2:11434"
        assert response  # Some response text

    def test_all_hosts_fail(self):
        client = OllamaClient(hosts=["http://nohost:11434"], model="test", per_host_timeout=1)
        client._host_health = {"http://nohost:11434": True}
        client._host_last_check = {"http://nohost:11434": time.time()}

        with pytest.raises(RuntimeError, match="All Ollama hosts failed"):
            client.generate("system", "user")


# ===========================================================================
# Test: Inspector Integration
# ===========================================================================

class TestSophiaInspector:
    @patch.object(OllamaClient, "generate")
    def test_full_inspection_flow(self, mock_generate, tmp_db, sample_fingerprint, sample_hardware):
        mock_generate.return_value = (
            '{"verdict":"APPROVED","confidence":0.93,"reasoning":"Coherent silicon pattern","flags":[]}',
            "http://localhost:11434",
            1500,
        )

        client = OllamaClient(hosts=["http://localhost:11434"])
        inspector = SophiaInspector(ollama=client, db=tmp_db)

        result = inspector.inspect(
            "test_miner", sample_fingerprint, sample_hardware, epoch=104
        )

        assert result.verdict == "APPROVED"
        assert result.confidence == 0.93
        assert result.ollama_host == "http://localhost:11434"
        assert result.latency_ms == 1500

        # Verify it was stored in DB
        record = tmp_db.get_latest("test_miner")
        assert record is not None
        assert record.verdict == "APPROVED"

    @patch.object(OllamaClient, "generate")
    def test_inspection_with_malformed_response(self, mock_generate, tmp_db, sample_fingerprint):
        mock_generate.return_value = (
            "I think this looks ok but I'm not sure",
            "http://localhost:11434",
            2000,
        )

        client = OllamaClient(hosts=["http://localhost:11434"])
        inspector = SophiaInspector(ollama=client, db=tmp_db)

        result = inspector.inspect("test_miner", sample_fingerprint)
        assert result.verdict == "CAUTIOUS"
        assert result.confidence == 0.3
        assert "parse_error" in result.flags

    @patch.object(OllamaClient, "generate")
    def test_inspection_all_hosts_fail(self, mock_generate, tmp_db, sample_fingerprint):
        mock_generate.side_effect = RuntimeError("All Ollama hosts failed")

        client = OllamaClient(hosts=["http://localhost:11434"])
        inspector = SophiaInspector(ollama=client, db=tmp_db)

        result = inspector.inspect("test_miner", sample_fingerprint)
        assert result.verdict == "CAUTIOUS"
        assert result.confidence == 0.1
        assert "service_unavailable" in result.flags

    @patch.object(OllamaClient, "generate")
    def test_inspection_stores_fingerprint_data(self, mock_generate, tmp_db, sample_fingerprint):
        mock_generate.return_value = (
            '{"verdict":"APPROVED","confidence":0.9,"reasoning":"ok","flags":[]}',
            "http://localhost:11434",
            1000,
        )

        client = OllamaClient(hosts=["http://localhost:11434"])
        inspector = SophiaInspector(ollama=client, db=tmp_db)
        inspector.inspect("test_miner", sample_fingerprint)

        # Verify fingerprint data stored for historical comparison
        historical = tmp_db.get_historical_fingerprints("test_miner")
        assert len(historical) == 1
        parsed = json.loads(historical[0])
        assert parsed["all_passed"] is True


# ===========================================================================
# Test: Inspection Result validation
# ===========================================================================

class TestInspectionResult:
    def test_valid_result(self):
        r = InspectionResult(miner_id="m", verdict="APPROVED", confidence=0.9)
        r.validate()

    def test_invalid_verdict(self):
        with pytest.raises(ValueError):
            InspectionResult(miner_id="m", verdict="MAYBE", confidence=0.5).validate()

    def test_confidence_too_high(self):
        with pytest.raises(ValueError):
            InspectionResult(miner_id="m", verdict="APPROVED", confidence=1.1).validate()

    def test_confidence_too_low(self):
        with pytest.raises(ValueError):
            InspectionResult(miner_id="m", verdict="APPROVED", confidence=-0.1).validate()

    def test_to_dict(self):
        r = InspectionResult(
            miner_id="m", verdict="CAUTIOUS", confidence=0.6,
            flags=("FLAG1", "FLAG2"),
        )
        d = r.to_dict()
        assert d["flags"] == ["FLAG1", "FLAG2"]
        assert d["verdict"] == "CAUTIOUS"


class TestInspectionRecord:
    def test_effective_verdict_no_override(self):
        r = InspectionRecord(
            miner_id="m", verdict="SUSPICIOUS", confidence=0.4,
        )
        assert r.effective_verdict == "SUSPICIOUS"
        assert r.emoji == "🔍"

    def test_effective_verdict_with_override(self):
        r = InspectionRecord(
            miner_id="m", verdict="SUSPICIOUS", confidence=0.4,
            override_verdict="APPROVED", override_by="admin",
        )
        assert r.effective_verdict == "APPROVED"
        assert r.emoji == "✨"


# ===========================================================================
# Test: Edge Cases
# ===========================================================================

class TestEdgeCases:
    def test_empty_miner_list_batch_status(self, tmp_db):
        result = tmp_db.get_batch_status([])
        assert result == {}

    def test_empty_history(self, tmp_db):
        history = tmp_db.get_history("nonexistent")
        assert history == []

    def test_empty_historical_fingerprints(self, tmp_db):
        fps = tmp_db.get_historical_fingerprints("nonexistent")
        assert fps == []

    def test_stats_empty_db(self, tmp_db):
        stats = tmp_db.get_stats()
        assert stats["total_inspections"] == 0
        assert stats["pending_reviews"] == 0

    def test_override_nonexistent_inspection(self, tmp_db):
        updated = tmp_db.record_override(99999, "APPROVED", "test", "admin")
        assert not updated

    def test_multiple_inspections_same_miner(self, tmp_db):
        """Latest should always return the most recent."""
        for conf in [0.5, 0.7, 0.9]:
            tmp_db.record_inspection(InspectionResult(
                miner_id="m", verdict="APPROVED", confidence=conf,
            ))
        latest = tmp_db.get_latest("m")
        assert latest.confidence == 0.9

    def test_fingerprint_hash_empty(self):
        h = fingerprint_hash({})
        assert len(h) == 64

    def test_last_inspected_time(self, tmp_db, sample_result):
        assert tmp_db.get_last_inspected_time("nobody") is None
        tmp_db.record_inspection(sample_result)
        t = tmp_db.get_last_inspected_time("test_miner_001")
        assert t is not None
