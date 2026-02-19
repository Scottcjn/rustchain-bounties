#!/usr/bin/env python3
"""Tests for ClawNews CLI"""

import pytest
import sys
import json
import tempfile
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clawnews.cli import (
    ClawNewsConfig,
    ContentType,
    VoteDirection,
    FeedItem,
    SubmissionResult,
    cmd_browse,
    cmd_submit,
    cmd_comment,
    cmd_vote,
    cmd_profile,
    cmd_search,
    build_parser,
)


class TestClawNewsConfig:
    """Test ClawNewsConfig dataclass"""

    def test_default_config(self):
        config = ClawNewsConfig()
        assert config.api_url == "https://api.clawnews.example.com/v1"
        assert config.api_key is None
        assert config.timeout == 30

    def test_custom_config(self):
        config = ClawNewsConfig(
            api_url="https://custom.api.com",
            api_key="secret123",
            timeout=60
        )
        assert config.api_url == "https://custom.api.com"
        assert config.api_key == "secret123"
        assert config.timeout == 60


class TestContentType:
    """Test ContentType enum"""

    def test_values(self):
        assert ContentType.ARTICLE.value == "article"
        assert ContentType.LINK.value == "link"
        assert ContentType.DISCUSSION.value == "discussion"


class TestFeedItem:
    """Test FeedItem dataclass"""

    def test_create_item(self):
        item = FeedItem(
            id="123",
            title="Test Title",
            author="testuser",
            content_type="article",
            url="https://example.com",
            score=100,
            comment_count=50,
            created_at="2026-02-19T00:00:00Z"
        )
        assert item.id == "123"
        assert item.title == "Test Title"
        assert item.score == 100


class TestSubmissionResult:
    """Test SubmissionResult dataclass"""

    def test_success_result(self):
        result = SubmissionResult(
            success=True,
            post_id="item_123",
            message="Success",
            errors=[]
        )
        assert result.success is True
        assert result.post_id == "item_123"

    def test_error_result(self):
        result = SubmissionResult(
            success=False,
            post_id=None,
            message="Failed",
            errors=["Invalid title"]
        )
        assert result.success is False
        assert "Invalid title" in result.errors


class TestCmdBrowse:
    """Test browse command"""

    def test_browse_latest(self):
        args = type('Namespace', (), {
            'feed': 'latest',
            'limit': 5,
            'json': False,
            'verbose': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_browse(args, config)
        assert result == 0

    def test_browse_top(self):
        args = type('Namespace', (), {
            'feed': 'top',
            'limit': 10,
            'json': False,
            'verbose': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_browse(args, config)
        assert result == 0

    def test_browse_invalid_feed(self):
        args = type('Namespace', (), {
            'feed': 'invalid',
            'limit': 10,
            'json': False,
            'verbose': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_browse(args, config)
        assert result == 1

    def test_browse_json_output(self):
        args = type('Namespace', (), {
            'feed': 'latest',
            'limit': 5,
            'json': True,
            'verbose': False
        })()
        config = ClawNewsConfig()
        
        # Capture stdout
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = cmd_browse(args, config)
            output = mock_stdout.getvalue()
            
            # Should be valid JSON
            data = json.loads(output)
            assert isinstance(data, list)
            assert len(data) > 0


class TestCmdSubmit:
    """Test submit command"""

    def test_submit_article(self):
        args = type('Namespace', (), {
            'type': 'article',
            'title': 'Test Article',
            'url': 'https://example.com/article',
            'content': None,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_submit(args, config)
        assert result == 0

    def test_submit_link(self):
        args = type('Namespace', (), {
            'type': 'link',
            'title': 'Test Link',
            'url': 'https://example.com',
            'content': None,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_submit(args, config)
        assert result == 0

    def test_submit_discussion(self):
        args = type('Namespace', (), {
            'type': 'discussion',
            'title': 'Test Discussion',
            'url': None,
            'content': 'This is a discussion',
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_submit(args, config)
        assert result == 0

    def test_submit_missing_title(self):
        args = type('Namespace', (), {
            'type': 'article',
            'title': None,
            'url': 'https://example.com',
            'content': None,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_submit(args, config)
        assert result == 1

    def test_submit_missing_url(self):
        args = type('Namespace', (), {
            'type': 'article',
            'title': 'Test',
            'url': None,
            'content': None,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_submit(args, config)
        assert result == 1


class TestCmdComment:
    """Test comment command"""

    def test_comment_success(self):
        args = type('Namespace', (), {
            'post_id': 'item_123',
            'content': 'Great post!',
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_comment(args, config)
        assert result == 0

    def test_comment_missing_post_id(self):
        args = type('Namespace', (), {
            'post_id': None,
            'content': 'Great post!',
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_comment(args, config)
        assert result == 1

    def test_comment_missing_content(self):
        args = type('Namespace', (), {
            'post_id': 'item_123',
            'content': None,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_comment(args, config)
        assert result == 1


class TestCmdVote:
    """Test vote command"""

    def test_vote_up(self):
        args = type('Namespace', (), {
            'post_id': 'item_123',
            'direction': 'up',
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_vote(args, config)
        assert result == 0

    def test_vote_down(self):
        args = type('Namespace', (), {
            'post_id': 'item_123',
            'direction': 'down',
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_vote(args, config)
        assert result == 0

    def test_vote_invalid_direction(self):
        args = type('Namespace', (), {
            'post_id': 'item_123',
            'direction': 'invalid',
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_vote(args, config)
        assert result == 1


class TestCmdProfile:
    """Test profile command"""

    def test_profile_success(self):
        args = type('Namespace', (), {
            'user': 'testuser',
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_profile(args, config)
        assert result == 0

    def test_profile_missing_user(self):
        args = type('Namespace', (), {
            'user': None,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_profile(args, config)
        assert result == 1


class TestCmdSearch:
    """Test search command"""

    def test_search_success(self):
        args = type('Namespace', (), {
            'query': 'bitcoin',
            'limit': 10,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_search(args, config)
        assert result == 0

    def test_search_missing_query(self):
        args = type('Namespace', (), {
            'query': None,
            'limit': 10,
            'json': False
        })()
        config = ClawNewsConfig()
        
        result = cmd_search(args, config)
        assert result == 1


class TestArgParser:
    """Test argument parser"""

    def test_parser_browse(self):
        parser = build_parser()
        args = parser.parse_args(['browse', '--feed', 'top', '--limit', '5'])
        
        assert args.command == 'browse'
        assert args.feed == 'top'
        assert args.limit == 5

    def test_parser_submit(self):
        parser = build_parser()
        args = parser.parse_args([
            'submit',
            '--type', 'article',
            '--title', 'Test',
            '--url', 'https://example.com'
        ])
        
        assert args.command == 'submit'
        assert args.type == 'article'
        assert args.title == 'Test'

    def test_parser_all_commands(self):
        parser = build_parser()
        commands = ['browse', 'submit', 'comment', 'vote', 'profile', 'search']
        
        for cmd in commands:
            args = parser.parse_args([cmd, '--help'])
            # If we get here without error, the command exists
            assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
