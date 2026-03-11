#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Tests for the RustChain VS Code extension structure.

Validates that the extension package is well-formed, all declared files
exist, snippet JSON is valid, and SPDX headers are present on source
files.  These are pure-Python structural checks — no Node.js required.

Run: python -m pytest tests/test_vscode_extension.py -v
Bounty: #1619
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT_ROOT = os.path.join(REPO_ROOT, "vscode-extension")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _read_head(path: str, lines: int = 10) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return "".join(fh.readline() for _ in range(lines))


# ---------------------------------------------------------------------------
# package.json validation
# ---------------------------------------------------------------------------


class TestPackageJson:
    """Verify the VS Code extension manifest is correct."""

    def setup_method(self):
        self.pkg = _load_json(os.path.join(EXT_ROOT, "package.json"))

    def test_package_json_exists(self):
        assert os.path.isfile(os.path.join(EXT_ROOT, "package.json"))

    def test_has_required_fields(self):
        for field in ("name", "displayName", "version", "engines", "main", "contributes"):
            assert field in self.pkg, f"Missing required field: {field}"

    def test_engine_vscode_specified(self):
        assert "vscode" in self.pkg["engines"]

    def test_has_activation_events(self):
        assert "activationEvents" in self.pkg
        assert len(self.pkg["activationEvents"]) > 0

    def test_contributes_configuration(self):
        config = self.pkg["contributes"]["configuration"]
        props = config["properties"]
        assert "rustchain.nodeUrl" in props
        assert "rustchain.minerId" in props
        assert "rustchain.balanceRefreshInterval" in props
        assert "rustchain.showBalance" in props

    def test_contributes_commands(self):
        commands = self.pkg["contributes"]["commands"]
        cmd_ids = [c["command"] for c in commands]
        assert "rustchain.refreshBalance" in cmd_ids
        assert "rustchain.setMinerId" in cmd_ids
        assert "rustchain.checkNodeHealth" in cmd_ids

    def test_contributes_languages(self):
        langs = self.pkg["contributes"]["languages"]
        ids = [lang["id"] for lang in langs]
        assert "rustchain-config" in ids

    def test_contributes_grammars(self):
        grammars = self.pkg["contributes"]["grammars"]
        assert len(grammars) > 0
        assert grammars[0]["scopeName"] == "source.rustchain-config"

    def test_contributes_snippets(self):
        snippets = self.pkg["contributes"]["snippets"]
        assert len(snippets) >= 3, "Expected at least 3 snippet contributions"
        languages = [s["language"] for s in snippets]
        assert "python" in languages
        assert "shellscript" in languages
        assert "rustchain-config" in languages

    def test_default_node_url_matches_docs(self):
        """Default node URL must match the official node in docs/API_REFERENCE.md."""
        props = self.pkg["contributes"]["configuration"]["properties"]
        assert props["rustchain.nodeUrl"]["default"] == "https://50.28.86.131"

    def test_license_is_mit(self):
        assert self.pkg.get("license") == "MIT"


# ---------------------------------------------------------------------------
# File structure
# ---------------------------------------------------------------------------


class TestFileStructure:
    """Verify all declared files actually exist on disk."""

    def setup_method(self):
        self.pkg = _load_json(os.path.join(EXT_ROOT, "package.json"))

    def test_tsconfig_exists(self):
        assert os.path.isfile(os.path.join(EXT_ROOT, "tsconfig.json"))

    def test_language_configuration_exists(self):
        assert os.path.isfile(os.path.join(EXT_ROOT, "language-configuration.json"))

    def test_grammar_file_exists(self):
        for g in self.pkg["contributes"]["grammars"]:
            path = os.path.join(EXT_ROOT, g["path"])
            assert os.path.isfile(path), f"Grammar file missing: {g['path']}"

    def test_snippet_files_exist(self):
        for s in self.pkg["contributes"]["snippets"]:
            path = os.path.join(EXT_ROOT, s["path"])
            assert os.path.isfile(path), f"Snippet file missing: {s['path']}"

    def test_source_entry_point_exists(self):
        """src/extension.ts must exist (the main entry point before compilation)."""
        assert os.path.isfile(os.path.join(EXT_ROOT, "src", "extension.ts"))

    def test_source_files_exist(self):
        expected = [
            "src/extension.ts",
            "src/balanceStatusBar.ts",
            "src/rustchainApi.ts",
            "src/nodeHealth.ts",
        ]
        for rel in expected:
            assert os.path.isfile(os.path.join(EXT_ROOT, rel)), f"Missing: {rel}"


# ---------------------------------------------------------------------------
# Snippet JSON validation
# ---------------------------------------------------------------------------


class TestSnippetFiles:
    """Each snippet file must be valid JSON with proper VS Code snippet structure."""

    def _snippet_paths(self):
        pkg = _load_json(os.path.join(EXT_ROOT, "package.json"))
        return [os.path.join(EXT_ROOT, s["path"]) for s in pkg["contributes"]["snippets"]]

    def test_all_snippets_valid_json(self):
        for path in self._snippet_paths():
            data = _load_json(path)
            assert isinstance(data, dict), f"{path} is not a JSON object"

    def test_snippets_have_required_keys(self):
        for path in self._snippet_paths():
            data = _load_json(path)
            for name, snippet in data.items():
                assert "prefix" in snippet, f"Snippet '{name}' in {path} missing 'prefix'"
                assert "body" in snippet, f"Snippet '{name}' in {path} missing 'body'"
                assert "description" in snippet, f"Snippet '{name}' in {path} missing 'description'"

    def test_snippet_body_is_list_of_strings(self):
        for path in self._snippet_paths():
            data = _load_json(path)
            for name, snippet in data.items():
                body = snippet["body"]
                assert isinstance(body, list), (
                    f"Snippet '{name}' in {path}: body must be a list"
                )
                for i, line in enumerate(body):
                    assert isinstance(line, str), (
                        f"Snippet '{name}' in {path}: body[{i}] is not a string"
                    )


# ---------------------------------------------------------------------------
# TextMate grammar validation
# ---------------------------------------------------------------------------


class TestGrammar:
    """Validate the TextMate grammar JSON structure."""

    def setup_method(self):
        path = os.path.join(EXT_ROOT, "syntaxes", "rustchain-config.tmLanguage.json")
        self.grammar = _load_json(path)

    def test_has_scope_name(self):
        assert self.grammar["scopeName"] == "source.rustchain-config"

    def test_has_patterns(self):
        assert "patterns" in self.grammar
        assert len(self.grammar["patterns"]) > 0

    def test_has_repository(self):
        assert "repository" in self.grammar

    def test_rustchain_keywords_present(self):
        """Grammar should highlight RustChain-specific identifiers."""
        repo = self.grammar["repository"]
        assert "rustchain-keywords" in repo
        patterns = repo["rustchain-keywords"]["patterns"]
        all_matches = " ".join(p.get("match", "") for p in patterns)
        for kw in ("miner_id", "wallet", "epoch", "attestation", "RTC", "RIP-200"):
            assert kw in all_matches, f"Keyword '{kw}' not in grammar"


# ---------------------------------------------------------------------------
# SPDX header enforcement
# ---------------------------------------------------------------------------


class TestSPDXHeaders:
    """All new TypeScript source files must have SPDX headers (BCOS policy)."""

    SPDX_RE = re.compile(r"SPDX-License-Identifier:\s*[A-Za-z0-9.\-+]+")

    def _ts_files(self):
        for dirpath, _dirs, files in os.walk(EXT_ROOT):
            for f in files:
                if f.endswith(".ts"):
                    yield os.path.join(dirpath, f)

    def test_all_ts_files_have_spdx(self):
        for path in self._ts_files():
            head = _read_head(path, 10)
            assert self.SPDX_RE.search(head), (
                f"Missing SPDX header in {os.path.relpath(path, REPO_ROOT)}"
            )
