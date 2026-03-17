"""Unit tests for scripts/sybil_risk_scorer.py — Bounty Issue #1589

Covers 6 pure functions with 16 test cases:
- extract_links: URLs, duplicates, punctuation cleanup, empty
- _normalize_text: lowercase, URL removal, mention removal
- _text_similarity: identical, different, empty
- _repo_from_issue_ref: standard, no slash, repo only
- _bucket: high, medium, low, boundary
- RiskPolicy: defaults, thresholds
"""

import pytest
from scripts.sybil_risk_scorer import (
    extract_links,
    _normalize_text,
    _text_similarity,
    _repo_from_issue_ref,
    _bucket,
    RiskPolicy,
)


# ─── extract_links ──────────────────────────────────────────────────

class TestExtractLinks:
    def test_single_url(self):
        result = extract_links("Check https://github.com/foo/bar for details")
        assert "https://github.com/foo/bar" in result

    def test_multiple_urls(self):
        result = extract_links("See https://a.com and https://b.org/path")
        assert "https://a.com/" in result
        assert "https://b.org/path" in result

    def test_deduplicates(self):
        text = "https://example.com https://example.com https://example.com/"
        result = extract_links(text)
        assert len(result) == 1

    def test_strips_trailing_punctuation(self):
        result = extract_links("Visit https://example.com), ok?")
        assert "https://example.com)" not in str(result)

    def test_empty_string(self):
        assert extract_links("") == ()
        assert extract_links(None) == ()

    def test_normalizes_case(self):
        result = extract_links("https://GITHUB.com/foo")
        assert "https://github.com/foo" in result


# ─── _normalize_text ────────────────────────────────────────────────

class TestNormalizeText:
    def test_lowercases(self):
        assert _normalize_text("Hello WORLD") == "hello world"

    def test_removes_urls(self):
        result = _normalize_text("Visit https://example.com now")
        assert "https" not in result

    def test_removes_mentions(self):
        result = _normalize_text("@user1 and @user2 did it")
        assert "@user1" not in result

    def test_empty_string(self):
        assert _normalize_text("") == ""
        assert _normalize_text(None) == ""


# ─── _text_similarity ──────────────────────────────────────────────

class TestTextSimilarity:
    def test_identical(self):
        assert _text_similarity("hello world", "hello world") == 1.0

    def test_different(self):
        assert _text_similarity("hello", "goodbye") < 0.5

    def test_empty(self):
        assert _text_similarity("", "hello") == 0.0
        assert _text_similarity("hello", "") == 0.0
        assert _text_similarity("", "") == 0.0

    def test_similar(self):
        score = _text_similarity("the quick brown fox", "the quick brown cat")
        assert 0.5 < score < 1.0


# ─── _repo_from_issue_ref ──────────────────────────────────────────

class TestRepoFromIssueRef:
    def test_standard(self):
        assert _repo_from_issue_ref("Scottcjn/rustchain-bounties#123") == "rustchain-bounties"

    def test_no_slash(self):
        assert _repo_from_issue_ref("rustchain-bounties#456") == "rustchain-bounties"

    def test_no_hash(self):
        assert _repo_from_issue_ref("foo/bar") == "bar"


# ─── _bucket ───────────────────────────────────────────────────────

class TestBucket:
    def test_high(self):
        p = RiskPolicy(name="test", medium_threshold=30, high_threshold=60)
        assert _bucket(100, p) == "high"

    def test_medium(self):
        p = RiskPolicy(name="test", medium_threshold=30, high_threshold=60)
        assert _bucket(30, p) == "medium"

    def test_low(self):
        p = RiskPolicy(name="test", medium_threshold=30, high_threshold=60)
        assert _bucket(0, p) == "low"

    def test_boundary(self):
        p = RiskPolicy(name="test", medium_threshold=30, high_threshold=60)
        assert _bucket(59, p) == "medium"
        assert _bucket(29, p) == "low"


# ─── RiskPolicy ────────────────────────────────────────────────────

class TestRiskPolicy:
    def test_has_thresholds(self):
        p = RiskPolicy(name="test", medium_threshold=30, high_threshold=60)
        assert p.medium_threshold == 30
        assert p.high_threshold > p.medium_threshold
