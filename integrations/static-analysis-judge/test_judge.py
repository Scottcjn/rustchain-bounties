# SPDX-License-Identifier: MIT
"""Tests for the static-analysis Judge."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from judge import Judge, StaticAnalysisJudge  # noqa: E402


def _req(**files: str) -> dict:
    return {"files": files}


def test_clean_code_passes():
    j = StaticAnalysisJudge()
    passed, reasons = j.judge(_req(**{"a.py": "def add(x, y):\n    return x + y\n"}))
    assert passed is True
    assert reasons == []


def test_eval_call_fails():
    j = StaticAnalysisJudge()
    passed, reasons = j.judge(_req(**{"a.py": "x = eval('1+1')\n"}))
    assert passed is False
    assert any("eval" in r for r in reasons)


def test_banned_import_fails():
    j = StaticAnalysisJudge()
    passed, reasons = j.judge(_req(**{"a.py": "import subprocess\n"}))
    assert passed is False
    assert any("subprocess" in r for r in reasons)


def test_banned_import_from_fails():
    j = StaticAnalysisJudge()
    passed, reasons = j.judge(_req(**{"a.py": "from pickle import loads\n"}))
    assert passed is False
    assert any("pickle" in r for r in reasons)


def test_syntax_error_fails():
    j = StaticAnalysisJudge()
    passed, reasons = j.judge(_req(**{"a.py": "def bad(:\n"}))
    assert passed is False
    assert any("syntax error" in r for r in reasons)


def test_oversized_function_fails():
    j = StaticAnalysisJudge(max_function_lines=3)
    src = "def f():\n" + "    x = 1\n" * 10
    passed, reasons = j.judge(_req(**{"a.py": src}))
    assert passed is False
    assert any("too long" in r for r in reasons)


def test_oversized_file_fails():
    j = StaticAnalysisJudge(max_file_lines=5)
    src = "x = 1\n" * 20
    passed, reasons = j.judge(_req(**{"a.py": src}))
    assert passed is False
    assert any("file too large" in r for r in reasons)


def test_empty_request_fails():
    j = StaticAnalysisJudge()
    passed, reasons = j.judge({"files": {}})
    assert passed is False
    assert reasons


def test_implements_judge_interface():
    j = StaticAnalysisJudge()
    assert isinstance(j, Judge)
    # Contract: judge(request) -> (bool, list[str])
    passed, reasons = j.judge(_req(**{"a.py": "x = 1\n"}))
    assert isinstance(passed, bool)
    assert isinstance(reasons, list)


def test_sign_and_verify_roundtrip():
    j = StaticAnalysisJudge()
    env = j.sign_verdict(_req(**{"a.py": "x = 1\n"}))
    assert env["verdict"]["passed"] is True
    assert env["verdict"]["judge_id"] == "judge.static-analysis.v1"
    assert StaticAnalysisJudge.verify(env) is True


def test_signature_tamper_detected():
    j = StaticAnalysisJudge()
    env = j.sign_verdict(_req(**{"a.py": "x = 1\n"}))
    # Tamper with the verdict body — verification must fail.
    env["verdict"]["passed"] = False
    assert StaticAnalysisJudge.verify(env) is False


def test_signature_swap_detected():
    j = StaticAnalysisJudge()
    env = j.sign_verdict(_req(**{"a.py": "x = 1\n"}))
    # Replace signature with garbage of the right length.
    env["signature"] = base64.b64encode(b"\x00" * 64).decode("ascii")
    assert StaticAnalysisJudge.verify(env) is False


def test_public_key_is_32_bytes():
    j = StaticAnalysisJudge()
    assert len(j.public_key_bytes()) == 32
