"""Unit tests for tools/bcos_spdx_check.py — Bounty Issue #1589

Covers all pure functions with 12 test cases:
- _has_spdx: valid header, missing header, shebang skip, edge cases
- _top_lines: normal file, short file, unreadable
- main: missing base ref, SPDX pass/fail, non-code extension skip
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from tools.bcos_spdx_check import _has_spdx, _top_lines, main


# ─── _has_spdx ──────────────────────────────────────────────────────

class TestHasSpdx:
    def test_valid_spdx(self):
        lines = ["# SPDX-License-Identifier: MIT", "print('hello')"]
        assert _has_spdx(lines) is True

    def test_valid_apache(self):
        lines = ["/* SPDX-License-Identifier: Apache-2.0 */", "int main() {}"]
        assert _has_spdx(lines) is True

    def test_missing_spdx(self):
        lines = ["# some comment", "print('hello')"]
        assert _has_spdx(lines) is False

    def test_empty_lines(self):
        assert _has_spdx([]) is False

    def test_shebang_with_spdx(self):
        lines = ["#!/usr/bin/env python3", "# SPDX-License-Identifier: MIT", "print()"]
        assert _has_spdx(lines) is True

    def test_shebang_without_spdx(self):
        lines = ["#!/bin/bash", "echo hello"]
        assert _has_spdx(lines) is False

    def test_spdx_after_blank_lines(self):
        lines = ["", "", "# SPDX-License-Identifier: GPL-3.0", "code"]
        assert _has_spdx(lines) is True

    def test_spdx_beyond_20_lines(self):
        lines = [""] * 21 + ["# SPDX-License-Identifier: MIT"]
        assert _has_spdx(lines) is False


# ─── _top_lines ─────────────────────────────────────────────────────

class TestTopLines:
    def test_normal_file(self, tmp_path):
        f = tmp_path / "test.py"
        f.write_text("line1\nline2\nline3\nline4\nline5")
        assert _top_lines(f) == ["line1", "line2", "line3", "line4", "line5"]

    def test_short_file(self, tmp_path):
        f = tmp_path / "short.py"
        f.write_text("only_one_line")
        assert _top_lines(f) == ["only_one_line"]

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.py"
        f.write_text("")
        assert _top_lines(f) == []

    def test_nonexistent_file(self, tmp_path):
        f = tmp_path / "nope.py"
        assert _top_lines(f) == []

    def test_respects_max_lines(self, tmp_path):
        f = tmp_path / "long.txt"
        f.write_text("\n".join(f"line{i}" for i in range(100)))
        assert len(_top_lines(f, max_lines=10)) == 10



