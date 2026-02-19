#!/usr/bin/env python3
"""Tests for Supply Chain Linter"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from supply_chain_linter import SupplyChainLinter, LintIssue, Severity, IssueType


class TestCredentialDetection:
    """Test credential detection patterns."""
    
    def test_detects_github_token(self):
        linter = SupplyChainLinter(".")
        # Create temp file with token
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('GITHUB_TOKEN = "ghp_abcdefghijklmnopqrstuvwxyz123456"')
            temp_path = f.name
        
        try:
            linter._scan_file_for_credentials(Path(temp_path))
            assert len(linter.issues) > 0
            assert any(i.severity == Severity.CRITICAL for i in linter.issues)
        finally:
            Path(temp_path).unlink()
    
    def test_detects_aws_key(self):
        linter = SupplyChainLinter(".")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('AWS_KEY = "AKIAIOSFODNN7EXAMPLE"')
            temp_path = f.name
        
        try:
            linter._scan_file_for_credentials(Path(temp_path))
            assert len(linter.issues) > 0
        finally:
            Path(temp_path).unlink()
    
    def test_detects_api_key(self):
        linter = SupplyChainLinter(".")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('api_key = "sk-abcdefghijklmnopqrstuvwxyz123456"')
            temp_path = f.name
        
        try:
            linter._scan_file_for_credentials(Path(temp_path))
            assert len(linter.issues) > 0
        finally:
            Path(temp_path).unlink()


class TestGitHubActions:
    """Test GitHub Actions scanning."""
    
    def test_finds_unpinned_action(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workflows_dir = Path(tmpdir) / ".github" / "workflows"
            workflows_dir.mkdir(parents=True)
            
            workflow = workflows_dir / "test.yml"
            workflow.write_text("""
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout
      - uses: actions/setup-node
""")
            
            linter = SupplyChainLinter(tmpdir)
            linter._scan_github_actions()
            
            assert len(linter.issues) > 0


class TestDepScanning:
    """Test dependency file scanning."""
    
    def test_finds_suspicious_package(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            req_file = Path(tmpdir) / "requirements.txt"
            req_file.write_text("""
requests
http-request
numpy
""")
            
            linter = SupplyChainLinter(tmpdir)
            linter._scan_dependency_files()
            
            assert len(linter.issues) > 0


class TestScriptScanning:
    """Test script scanning."""
    
    def test_finds_dangerous_patterns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            script = Path(tmpdir) / "test.py"
            script.write_text("""
import os
import subprocess

# Dangerous!
result = os.system("ls -la")
subprocess.run(["ls"])
""")
            
            linter = SupplyChainLinter(tmpdir)
            linter._scan_script_file(script)
            
            assert len(linter.issues) > 0


class TestIntegration:
    """Integration tests."""
    
    def test_full_scan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test repo structure
            Path(tmpdir, "test.py").write_text('api_key = "sk-test12345678901234567890"')
            Path(tmpdir, "requirements.txt").write_text("requests")
            
            linter = SupplyChainLinter(tmpdir)
            issues = linter.scan()
            
            assert linter.get_summary()["files_scanned"] > 0
            assert len(issues) > 0
    
    def test_nonexistent_path(self):
        linter = SupplyChainLinter("/nonexistent/path")
        issues = linter.scan()
        
        assert len(issues) == 1
        assert issues[0].severity == Severity.CRITICAL


class TestLintIssue:
    """Test LintIssue dataclass."""
    
    def test_to_dict(self):
        issue = LintIssue(
            severity=Severity.CRITICAL,
            issue_type=IssueType.CREDENTIAL_LEAK,
            message="Test issue",
            file_path="test.py",
            line_number=10,
            rule_id="TEST001"
        )
        
        data = issue.to_dict()
        
        assert data["severity"] == "critical"
        assert data["issue_type"] == "credential_leak"
        assert data["message"] == "Test issue"
        assert data["file"] == "test.py"
        assert data["line"] == 10"
        assert data["rule"] == "TEST001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
