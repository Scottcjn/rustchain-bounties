#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Tests for the Homebrew formula (Formula/rustchain-miner.rb).

Validates structure, supply-chain hygiene, and correctness of the formula
without requiring a Homebrew installation.

Run: python -m pytest tests/test_homebrew_formula.py -v
"""

import hashlib
import os
import re
import urllib.request

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
FORMULA_PATH = os.path.join(REPO_ROOT, "Formula", "rustchain-miner.rb")


# ---------------------------------------------------------------------------
# File presence
# ---------------------------------------------------------------------------


class TestFormulaExists:
    """Verify the formula file is present and well-formed."""

    def test_formula_file_exists(self):
        assert os.path.isfile(FORMULA_PATH), "Formula/rustchain-miner.rb must exist"

    def test_formula_not_empty(self):
        assert os.path.getsize(FORMULA_PATH) > 0, "Formula must not be empty"


# ---------------------------------------------------------------------------
# SPDX / BCOS compliance
# ---------------------------------------------------------------------------


class TestBCOSCompliance:
    """Verify BCOS requirements for new code files."""

    def _read_formula(self):
        with open(FORMULA_PATH, "r") as f:
            return f.read()

    def test_spdx_header_present(self):
        content = self._read_formula()
        assert "SPDX-License-Identifier:" in content, (
            "New code files must include an SPDX-License-Identifier header"
        )

    def test_spdx_header_is_mit(self):
        content = self._read_formula()
        assert "SPDX-License-Identifier: MIT" in content, (
            "SPDX header must specify MIT to match project license"
        )

    def test_license_field_present(self):
        content = self._read_formula()
        assert re.search(r'license\s+"MIT"', content), (
            "Formula must declare license \"MIT\""
        )


# ---------------------------------------------------------------------------
# Homebrew formula structure
# ---------------------------------------------------------------------------


class TestFormulaStructure:
    """Validate the Ruby formula follows Homebrew conventions."""

    def _read_formula(self):
        with open(FORMULA_PATH, "r") as f:
            return f.read()

    def test_class_name(self):
        content = self._read_formula()
        assert "class RustchainMiner < Formula" in content, (
            "Formula class must be RustchainMiner < Formula"
        )

    def test_has_desc(self):
        content = self._read_formula()
        assert re.search(r'desc\s+"[^"]+"', content), "Formula must have a desc"

    def test_has_homepage(self):
        content = self._read_formula()
        assert re.search(r'homepage\s+"https://github\.com/Scottcjn/Rustchain"', content), (
            "Formula must have homepage pointing to the Rustchain repo"
        )

    def test_has_url(self):
        content = self._read_formula()
        assert re.search(r'url\s+"https://', content), "Formula must have a source url"

    def test_has_sha256(self):
        content = self._read_formula()
        assert re.search(r'sha256\s+"[a-f0-9]{64}"', content), (
            "Formula must have a sha256 checksum for the source tarball"
        )

    def test_has_version(self):
        content = self._read_formula()
        assert re.search(r'version\s+"[0-9]+\.[0-9]+', content), (
            "Formula must declare a version"
        )

    def test_depends_on_python(self):
        content = self._read_formula()
        assert 'depends_on "python@3"' in content, (
            "Formula must depend on python@3"
        )

    def test_has_install_method(self):
        content = self._read_formula()
        assert "def install" in content, "Formula must have an install method"

    def test_has_test_block(self):
        content = self._read_formula()
        assert re.search(r"test do\b", content), "Formula must have a test block"

    def test_has_service_block(self):
        content = self._read_formula()
        assert re.search(r"service do\b", content), (
            "Formula should include a service block for brew services"
        )

    def test_has_caveats(self):
        content = self._read_formula()
        assert "def caveats" in content, "Formula should include caveats"


# ---------------------------------------------------------------------------
# Supply-chain hygiene
# ---------------------------------------------------------------------------


class TestSupplyChainHygiene:
    """Verify the formula meets supply-chain safety requirements."""

    def _read_formula(self):
        with open(FORMULA_PATH, "r") as f:
            return f.read()

    def test_pinned_tag_referenced(self):
        """Source URL must pin to a specific tag, not a branch."""
        content = self._read_formula()
        url_match = re.search(r'url\s+"([^"]+)"', content)
        assert url_match, "Must have a url field"
        url = url_match.group(1)
        assert "/tags/" in url or "/releases/" in url, (
            "Source URL must reference a pinned tag or release, not a branch"
        )

    def test_commit_sha_documented(self):
        """Formula should document the pinned commit SHA."""
        content = self._read_formula()
        assert re.search(r"[Cc]ommit.*[a-f0-9]{7,40}", content), (
            "Formula should document the commit SHA for auditability"
        )

    def test_upstream_checksums_documented(self):
        """Formula should include upstream miner file checksums."""
        content = self._read_formula()
        # Should have at least the miner script checksum documented
        sha_count = len(re.findall(r"[a-f0-9]{64}", content))
        # tarball sha256 + at least 3 upstream file checksums + 5 PyPI resource checksums
        assert sha_count >= 6, (
            f"Expected at least 6 SHA256 checksums (tarball + upstream + deps), found {sha_count}"
        )

    def test_no_curl_pipe_bash(self):
        """Formula must not use curl|bash patterns."""
        content = self._read_formula()
        risky = re.compile(r"(curl|wget)\s+.*\|\s*(ba)?sh")
        assert not risky.search(content), (
            "Formula must not contain curl|bash or wget|sh patterns"
        )

    def test_python_deps_pinned_with_checksums(self):
        """All Python resource blocks must have url + sha256."""
        content = self._read_formula()
        resource_blocks = re.findall(
            r'resource\s+"([^"]+)"\s+do\s+(.*?)end',
            content,
            re.DOTALL,
        )
        assert len(resource_blocks) >= 1, "Must have at least one Python resource"
        for name, block in resource_blocks:
            assert re.search(r'url\s+"https://', block), (
                f"Resource '{name}' must have a url"
            )
            assert re.search(r'sha256\s+"[a-f0-9]{64}"', block), (
                f"Resource '{name}' must have a sha256 checksum"
            )

    def test_all_pypi_urls_use_https(self):
        """All PyPI resource URLs must use HTTPS."""
        content = self._read_formula()
        urls = re.findall(r'url\s+"(http[^"]+)"', content)
        for url in urls:
            assert url.startswith("https://"), (
                f"URL must use HTTPS: {url}"
            )

    def test_requests_dependency_version_pinned(self):
        """The requests dependency must match the reproducible build pin."""
        content = self._read_formula()
        assert "requests-2.31.0" in content, (
            "requests version should match the project's reproducible build pin (2.31.0)"
        )


# ---------------------------------------------------------------------------
# Platform handling
# ---------------------------------------------------------------------------


class TestPlatformHandling:
    """Verify the formula handles macOS and Linux correctly."""

    def _read_formula(self):
        with open(FORMULA_PATH, "r") as f:
            return f.read()

    def test_mac_miner_referenced(self):
        content = self._read_formula()
        assert "rustchain_mac_miner_v2.4.py" in content, (
            "Formula must reference macOS miner script"
        )

    def test_linux_miner_referenced(self):
        content = self._read_formula()
        assert "rustchain_linux_miner.py" in content, (
            "Formula must reference Linux miner script"
        )

    def test_os_detection(self):
        content = self._read_formula()
        assert "OS.mac?" in content, (
            "Formula must use OS.mac? for platform detection"
        )

    def test_fingerprint_module_installed(self):
        content = self._read_formula()
        assert "fingerprint_checks.py" in content, (
            "Formula must install the fingerprint_checks module"
        )

    def test_wrapper_script_created(self):
        content = self._read_formula()
        assert "rustchain-miner" in content, (
            "Formula must create a rustchain-miner wrapper in bin/"
        )


# ---------------------------------------------------------------------------
# Tarball verification (network, skipped in offline CI)
# ---------------------------------------------------------------------------


class TestTarballIntegrity:
    """Verify the source tarball is reachable and matches the pinned SHA256."""

    def _read_formula(self):
        with open(FORMULA_PATH, "r") as f:
            return f.read()

    def _extract_field(self, field):
        content = self._read_formula()
        match = re.search(rf'{field}\s+"([^"]+)"', content)
        return match.group(1) if match else None

    def test_tarball_sha256_matches(self):
        """Download the tarball and verify SHA256 (requires network)."""
        url = self._extract_field("url")
        expected_sha = self._extract_field("sha256")
        assert url and expected_sha, "url and sha256 must be present"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "rustchain-test"})
            resp = urllib.request.urlopen(req, timeout=30)
            data = resp.read()
        except Exception:
            # Network unavailable — skip gracefully
            import pytest
            pytest.skip("Network unavailable; cannot verify tarball SHA256")

        actual_sha = hashlib.sha256(data).hexdigest()
        assert actual_sha == expected_sha, (
            f"Tarball SHA256 mismatch: expected {expected_sha}, got {actual_sha}"
        )
