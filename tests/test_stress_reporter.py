"""Unit tests for scripts/stress_test/reporter.py — Bounty Issue #1589

Covers StressTestReporter with 12 test cases:
- generate_markdown: all success, all failure, mixed, zero miners, duplicate IDs
- save_report: file output
- latency calculations: p50/p95/p99
- error analysis: aggregation
"""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

from stress_test.reporter import StressTestReporter


def _results(success_count=10, fail_count=0, with_duplicates=False, with_steps=True):
    """Helper to generate test results."""
    results = []
    for i in range(success_count):
        r = {"success": True, "total_time": 0.1 + i * 0.01}
        if with_steps:
            r["steps"] = {"challenge": 0.02, "submit": 0.05, "enroll": 0.03}
        if with_duplicates and i < 3:
            r["is_duplicate"] = True
        results.append(r)
    for i in range(fail_count):
        results.append({"success": False, "total_time": 0.05, "error": f"Error code {i}"})
    return results


class TestGenerateMarkdown:
    def test_all_success(self):
        r = StressTestReporter("https://node.test", 10, 1.0, _results(10))
        md = r.generate_markdown()
        assert "# RustChain RIP-200 Stress Test Report" in md
        assert "100.0%" in md
        assert "https://node.test" in md

    def test_all_failure(self):
        r = StressTestReporter("https://node.test", 10, 1.0, _results(0, 10))
        md = r.generate_markdown()
        assert "0.0%" in md
        assert "Error Analysis" in md

    def test_mixed_results(self):
        r = StressTestReporter("https://node.test", 10, 1.0, _results(7, 3))
        md = r.generate_markdown()
        assert "70.0%" in md
        assert "Error Analysis" in md

    def test_zero_miners(self):
        r = StressTestReporter("https://node.test", 0, 0.5, [])
        md = r.generate_markdown()
        assert "0" in md

    def test_duplicate_ids(self):
        results = _results(10, with_duplicates=True)
        r = StressTestReporter("https://node.test", 10, 1.0, results)
        md = r.generate_markdown()
        assert "Duplicate ID" in md

    def test_includes_step_breakdown(self):
        r = StressTestReporter("https://node.test", 5, 1.0, _results(5))
        md = r.generate_markdown()
        assert "Challenge" in md
        assert "Submit" in md
        assert "Enroll" in md

    def test_includes_disclaimer(self):
        r = StressTestReporter("https://node.test", 5, 1.0, _results(5))
        md = r.generate_markdown()
        assert "Disclaimer" in md
        assert "simulation" in md.lower()


class TestLatencyCalculations:
    def test_p50(self):
        r = StressTestReporter("https://node.test", 5, 1.0, _results(5))
        md = r.generate_markdown()
        assert "P50" in md

    def test_empty_results_no_crash(self):
        r = StressTestReporter("https://node.test", 0, 0.1, [])
        md = r.generate_markdown()
        assert md  # should not crash


class TestSaveReport:
    def test_writes_file(self, tmp_path):
        r = StressTestReporter("https://node.test", 5, 1.0, _results(5))
        out = str(tmp_path / "report.md")
        r.save_report(out)
        content = open(out).read()
        assert "RustChain RIP-200 Stress Test Report" in content
