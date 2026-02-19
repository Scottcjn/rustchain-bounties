#!/usr/bin/env python3
"""Tests for generate_dynamic_badges.py V2

Run with: python -m pytest test_generate_dynamic_badges_v2.py -v
"""

import pytest
import json
import tempfile
from pathlib import Path
import sys

# Add the scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".github" / "scripts"))

# Import functions from the V2 script
from generate_dynamic_badges_v2 import (
    parse_rows,
    slugify_hunter,
    color_for_level,
    parse_int,
    validate_badge_json,
    calculate_weekly_growth,
    parse_category_stats,
    generate_top_3_badge,
    generate_weekly_growth_badge,
    generate_category_badge,
)


class TestSlugifyHunterV2:
    """Test collision-safe slugification."""

    def test_basic_slug(self):
        """Basic slug without collision."""
        assert slugify_hunter("@TestUser") == "testuser"

    def test_collision_detection(self):
        """Same name should get different slugs."""
        existing = set()
        slug1 = slugify_hunter("@testuser", existing)
        existing.add(slug1)
        slug2 = slugify_hunter("@testuser", existing)
        
        assert slug1 == "testuser"
        assert slug2 == "testuser-1"
        assert slug1 != slug2

    def test_multiple_collisions(self):
        """Multiple collisions should increment."""
        existing = set()
        slugs = []
        for i in range(5):
            slug = slugify_hunter("@user", existing)
            existing.add(slug)
            slugs.append(slug)
        
        assert slugs == ["user", "user-1", "user-2", "user-3", "user-4"]

    def test_no_collision_without_existing(self):
        """Without existing set, should return base slug."""
        assert slugify_hunter("@user", None) == "user"


class TestValidateBadgeJson:
    """Test badge JSON schema validation."""

    def test_valid_badge(self):
        """Valid badge should pass."""
        badge = {
            "schemaVersion": 1,
            "label": "Test",
            "message": "Hello",
            "color": "blue",
            "namedLogo": "github",
            "logoColor": "white",
        }
        is_valid, errors = validate_badge_json(badge)
        assert is_valid
        assert errors == []

    def test_missing_schema_version(self):
        """Missing schemaVersion should fail."""
        badge = {
            "label": "Test",
            "message": "Hello",
            "color": "blue",
        }
        is_valid, errors = validate_badge_json(badge)
        assert not is_valid
        assert any("schemaVersion" in e for e in errors)

    def test_invalid_schema_version(self):
        """Invalid schemaVersion should fail."""
        badge = {
            "schemaVersion": 2,
            "label": "Test",
            "message": "Hello",
            "color": "blue",
        }
        is_valid, errors = validate_badge_json(badge)
        assert not is_valid

    def test_missing_required_fields(self):
        """Missing required fields should fail."""
        badge = {"schemaVersion": 1}
        is_valid, errors = validate_badge_json(badge)
        assert not is_valid
        assert len(errors) >= 3  # label, message, color

    def test_wrong_types(self):
        """Wrong field types should fail."""
        badge = {
            "schemaVersion": 1,
            "label": 123,  # Should be string
            "message": "Hello",
            "color": "blue",
        }
        is_valid, errors = validate_badge_json(badge)
        assert not is_valid
        assert any("label" in e for e in errors)


class TestWeeklyGrowth:
    """Test weekly growth calculation."""

    def test_no_history(self):
        """No history file should return total as growth."""
        rows = [{"xp": 1000}, {"xp": 500}]
        growth = calculate_weekly_growth(rows, None)
        assert growth == 1500

    def test_empty_rows(self):
        """Empty rows should return 0."""
        growth = calculate_weekly_growth([], None)
        assert growth == 0


class TestCategoryStats:
    """Test category statistics parsing."""

    def test_no_ledger(self):
        """No ledger should return zeros."""
        stats = parse_category_stats(None)
        assert stats == {"docs": 0, "outreach": 0, "bug": 0}

    def test_nonexistent_ledger(self):
        """Nonexistent ledger file should return zeros."""
        stats = parse_category_stats(Path("/nonexistent"))
        assert stats == {"docs": 0, "outreach": 0, "bug": 0}


class TestTop3Badge:
    """Test top 3 hunters badge generation."""

    def test_empty_rows(self):
        """Empty rows should return placeholder."""
        label, msg, color = generate_top_3_badge([])
        assert label == "Top 3"
        assert "No hunters" in msg
        assert color == "lightgrey"

    def test_single_hunter(self):
        """Single hunter should show just their name."""
        rows = [{"hunter": "@user1", "level": 5, "xp": 1000}]
        label, msg, color = generate_top_3_badge(rows)
        assert label == "Top 3 Hunters"
        assert msg == "user1"
        assert color == "yellow"  # Level 5 color

    def test_three_hunters(self):
        """Three hunters should show all names."""
        rows = [
            {"hunter": "@alice", "level": 10, "xp": 2000},
            {"hunter": "@bob", "level": 8, "xp": 1500},
            {"hunter": "@charlie", "level": 6, "xp": 1000},
        ]
        label, msg, color = generate_top_3_badge(rows)
        assert label == "Top 3 Hunters"
        assert "alice" in msg
        assert "bob" in msg
        assert "charlie" in msg
        assert color == "gold"  # Top level 10 color


class TestWeeklyGrowthBadge:
    """Test weekly growth badge generation."""

    def test_no_growth(self):
        """Zero growth should show no change."""
        label, msg, color = generate_weekly_growth_badge(0)
        assert "No change" in msg
        assert color == "lightgrey"

    def test_small_growth(self):
        """Small growth should be blue."""
        label, msg, color = generate_weekly_growth_badge(50)
        assert "+50 XP" in msg
        assert color == "blue"

    def test_large_growth(self):
        """Large growth should be brightgreen."""
        label, msg, color = generate_weekly_growth_badge(1500)
        assert "+1500 XP" in msg
        assert color == "brightgreen"


class TestCategoryBadge:
    """Test category badge generation."""

    def test_docs_category(self):
        """Docs category should be blue."""
        label, msg, color = generate_category_badge("docs", 5)
        assert label == "Docs Bounties"
        assert msg == "5"
        assert color == "blue"

    def test_outreach_category(self):
        """Outreach category should be teal."""
        label, msg, color = generate_category_badge("outreach", 3)
        assert label == "Outreach Bounties"
        assert color == "teal"

    def test_bug_category(self):
        """Bug category should be red."""
        label, msg, color = generate_category_badge("bug", 10)
        assert label == "Bug Bounties"
        assert color == "red"


class TestDeterministicOutput:
    """Test that output is deterministic."""

    def test_json_sorting(self):
        """JSON output should have sorted keys."""
        import tempfile
        import os
        
        # Create a temporary file to test write_badge
        from generate_dynamic_badges_v2 import write_badge
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            write_badge(path, "Test", "Message", "blue", validate=False)
            
            content = path.read_text()
            # Should be sorted alphabetically
            assert '"color"' in content
            assert content.index('"color"') < content.index('"label"')
            assert content.index('"label"') < content.index('"message"')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
