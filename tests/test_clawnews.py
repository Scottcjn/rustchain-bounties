#!/usr/bin/env python3
"""
Tests for ClawNews v0.1 CLI
Comprehensive test coverage for all command paths and payload formation
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from clawnews_cli import ClawNewsAPI, ClawNewsFormatter, create_parser, main


class TestClawNewsAPI:
    """Test ClawNews API client"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.api = ClawNewsAPI("https://test.example.com")
    
    @patch('clawnews_cli.requests.Session')
    def test_api_initialization(self, mock_session):
        """Test API client initialization"""
        api = ClawNewsAPI("https://custom.url.com")
        assert api.base_url == "https://custom.url.com"
        mock_session.assert_called_once()
    
    def test_make_request_success(self):
        """Test successful API request"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_response.raise_for_status.return_value = None
        
        # Mock the session's request method directly
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api._make_request("GET", "/test")
        
        assert result["success"] is True
        assert result["data"] == {"test": "data"}
        assert result["status_code"] == 200
    
    @patch('clawnews_cli.requests.Session')
    def test_make_request_http_error(self, mock_session):
        """Test API request with HTTP error"""
        import requests
        
        # Mock HTTP error
        mock_response = Mock()
        mock_response.status_code = 404
        
        mock_session.return_value.request.side_effect = requests.exceptions.HTTPError()
        
        result = self.api._make_request("GET", "/notfound")
        
        assert result["success"] is False
        assert "error" in result
    
    def test_browse_feed_default(self):
        """Test browse feed with default parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"posts": []}
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.browse_feed()
        
        # Verify request was made with correct parameters
        self.api.session.request.assert_called_once()
        call_args = self.api.session.request.call_args
        assert call_args[0][0] == "GET"  # method
        assert "/browse" in call_args[0][1]  # URL contains endpoint
        assert call_args[1]["params"]["limit"] == 20
    
    def test_browse_feed_with_url(self):
        """Test browse feed with custom feed URL"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"posts": []}
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.browse_feed("https://example.com/feed.xml", 10)
        
        call_args = self.api.session.request.call_args
        assert call_args[1]["params"]["feed"] == "https://example.com/feed.xml"
        assert call_args[1]["params"]["limit"] == 10
    
    def test_submit_post_article(self):
        """Test submit article post"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"post_id": "abc123"}
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.submit_post("article", "Test Title", "https://example.com")
        
        call_args = self.api.session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/submit" in call_args[0][1]
        
        payload = call_args[1]["json"]
        assert payload["type"] == "article"
        assert payload["title"] == "Test Title"
        assert payload["url"] == "https://example.com"
        assert "timestamp" in payload
    
    def test_submit_post_discussion(self):
        """Test submit discussion post"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"post_id": "def456"}
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.submit_post("discussion", "Discussion Title", text="Discussion text")
        
        call_args = self.api.session.request.call_args
        payload = call_args[1]["json"]
        assert payload["type"] == "discussion"
        assert payload["title"] == "Discussion Title"
        assert payload["text"] == "Discussion text"
        assert "url" not in payload or payload["url"] is None
    
    def test_add_comment(self):
        """Test add comment"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"comment_id": "comment123"}
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.add_comment("post123", "Great article!")
        
        call_args = self.api.session.request.call_args
        payload = call_args[1]["json"]
        assert payload["post_id"] == "post123"
        assert payload["text"] == "Great article!"
        assert "timestamp" in payload
    
    def test_vote_post(self):
        """Test vote on post"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"new_score": 15, "direction": "up"}
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.vote_post("post123", "up")
        
        call_args = self.api.session.request.call_args
        payload = call_args[1]["json"]
        assert payload["post_id"] == "post123"
        assert payload["direction"] == "up"
        assert "timestamp" in payload
    
    def test_get_profile(self):
        """Test get user profile"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "username": "testuser",
            "karma": 42,
            "post_count": 10,
            "comment_count": 25
        }
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.get_profile("testuser")
        
        call_args = self.api.session.request.call_args
        assert call_args[0][0] == "GET"
        assert "/profile/testuser" in call_args[0][1]
    
    def test_search_posts(self):
        """Test search posts"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"title": "Test Result", "score": 10}],
            "query": "test search"
        }
        mock_response.raise_for_status.return_value = None
        
        self.api.session.request = Mock(return_value=mock_response)
        
        result = self.api.search_posts("test search", 15)
        
        call_args = self.api.session.request.call_args
        assert call_args[1]["params"]["q"] == "test search"
        assert call_args[1]["params"]["limit"] == 15


class TestClawNewsFormatter:
    """Test ClawNews output formatter"""
    
    def test_format_feed_success(self):
        """Test format feed with successful data"""
        data = {
            "success": True,
            "data": {
                "posts": [
                    {
                        "title": "Test Article",
                        "author": "testuser",
                        "score": 15,
                        "comment_count": 5,
                        "created": "2024-01-15 10:30:00",
                        "url": "https://example.com/article"
                    }
                ]
            }
        }
        
        result = ClawNewsFormatter.format_feed(data)
        
        assert "📰 ClawNews Feed" in result
        assert "Test Article" in result
        assert "testuser" in result
        assert "🔺 15" in result
        assert "💬 5" in result
    
    def test_format_feed_json(self):
        """Test format feed with JSON output"""
        data = {"success": True, "data": {"posts": []}}
        
        result = ClawNewsFormatter.format_feed(data, json_output=True)
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["success"] is True
    
    def test_format_feed_error(self):
        """Test format feed with error"""
        data = {"success": False, "error": "API not available"}
        
        result = ClawNewsFormatter.format_feed(data)
        
        assert "❌ Error: API not available" in result
    
    def test_format_feed_empty(self):
        """Test format feed with no posts"""
        data = {"success": True, "data": {"posts": []}}
        
        result = ClawNewsFormatter.format_feed(data)
        
        assert "📰 No posts found" in result
    
    def test_format_submit_success(self):
        """Test format submit success"""
        data = {"success": True, "data": {"post_id": "abc123"}}
        
        result = ClawNewsFormatter.format_submit(data)
        
        assert "✅ Post submitted successfully" in result
        assert "abc123" in result
    
    def test_format_comment_success(self):
        """Test format comment success"""
        data = {"success": True, "data": {"comment_id": "comment456"}}
        
        result = ClawNewsFormatter.format_comment(data)
        
        assert "✅ Comment added successfully" in result
        assert "comment456" in result
    
    def test_format_vote_up(self):
        """Test format vote up"""
        data = {
            "success": True,
            "data": {"direction": "up", "new_score": 16}
        }
        
        result = ClawNewsFormatter.format_vote(data)
        
        assert "✅ Vote recorded" in result
        assert "🔺" in result
        assert "16" in result
    
    def test_format_vote_down(self):
        """Test format vote down"""
        data = {
            "success": True,
            "data": {"direction": "down", "new_score": 14}
        }
        
        result = ClawNewsFormatter.format_vote(data)
        
        assert "✅ Vote recorded" in result
        assert "🔻" in result
        assert "14" in result
    
    def test_format_profile_success(self):
        """Test format profile success"""
        data = {
            "success": True,
            "data": {
                "username": "johndoe",
                "karma": 150,
                "post_count": 25,
                "comment_count": 80,
                "joined": "2023-06-15"
            }
        }
        
        result = ClawNewsFormatter.format_profile(data)
        
        assert "👤 Profile: johndoe" in result
        assert "🏆 Karma: 150" in result
        assert "📝 Posts: 25" in result
        assert "💬 Comments: 80" in result
    
    def test_format_search_success(self):
        """Test format search success"""
        data = {
            "success": True,
            "data": {
                "query": "blockchain",
                "results": [
                    {
                        "title": "Blockchain Basics",
                        "author": "crypto_expert",
                        "score": 25,
                        "url": "https://example.com/blockchain"
                    }
                ]
            }
        }
        
        result = ClawNewsFormatter.format_search(data)
        
        assert "🔍 Search results for 'blockchain'" in result
        assert "Blockchain Basics" in result
        assert "crypto_expert" in result
    
    def test_format_search_no_results(self):
        """Test format search with no results"""
        data = {
            "success": True,
            "data": {"query": "nonexistent", "results": []}
        }
        
        result = ClawNewsFormatter.format_search(data)
        
        assert "🔍 No results found for 'nonexistent'" in result


class TestClawNewsCLI:
    """Test ClawNews CLI argument parsing and command execution"""
    
    def test_parser_creation(self):
        """Test argument parser creation"""
        parser = create_parser()
        
        # Test help doesn't raise exception
        with pytest.raises(SystemExit):
            parser.parse_args(['--help'])
    
    def test_browse_command_parsing(self):
        """Test browse command argument parsing"""
        parser = create_parser()
        
        # Test default browse
        args = parser.parse_args(['browse'])
        assert args.command == 'browse'
        assert args.limit == 20
        assert args.feed is None
        
        # Test browse with options
        args = parser.parse_args(['browse', '--feed', 'https://example.com/feed.xml', '--limit', '10'])
        assert args.command == 'browse'
        assert args.feed == 'https://example.com/feed.xml'
        assert args.limit == 10
    
    def test_submit_command_parsing(self):
        """Test submit command argument parsing"""
        parser = create_parser()
        
        # Test article submission
        args = parser.parse_args(['submit', '--type', 'article', '--title', 'Test Title', '--url', 'https://example.com'])
        assert args.command == 'submit'
        assert args.type == 'article'
        assert args.title == 'Test Title'
        assert args.url == 'https://example.com'
        
        # Test discussion submission
        args = parser.parse_args(['submit', '--type', 'discussion', '--title', 'Discussion', '--text', 'Discussion text'])
        assert args.command == 'submit'
        assert args.type == 'discussion'
        assert args.title == 'Discussion'
        assert args.text == 'Discussion text'
    
    def test_comment_command_parsing(self):
        """Test comment command argument parsing"""
        parser = create_parser()
        
        args = parser.parse_args(['comment', '--post-id', 'abc123', '--text', 'Great post!'])
        assert args.command == 'comment'
        assert args.post_id == 'abc123'
        assert args.text == 'Great post!'
    
    def test_vote_command_parsing(self):
        """Test vote command argument parsing"""
        parser = create_parser()
        
        # Test upvote
        args = parser.parse_args(['vote', '--post-id', 'abc123', '--direction', 'up'])
        assert args.command == 'vote'
        assert args.post_id == 'abc123'
        assert args.direction == 'up'
        
        # Test downvote
        args = parser.parse_args(['vote', '--post-id', 'def456', '--direction', 'down'])
        assert args.direction == 'down'
    
    def test_profile_command_parsing(self):
        """Test profile command argument parsing"""
        parser = create_parser()
        
        args = parser.parse_args(['profile', '--user', 'johndoe'])
        assert args.command == 'profile'
        assert args.user == 'johndoe'
    
    def test_search_command_parsing(self):
        """Test search command argument parsing"""
        parser = create_parser()
        
        args = parser.parse_args(['search', '--query', 'blockchain technology'])
        assert args.command == 'search'
        assert args.query == 'blockchain technology'
        assert args.limit == 20
        
        # Test with custom limit
        args = parser.parse_args(['search', '--query', 'test', '--limit', '5'])
        assert args.limit == 5
    
    def test_global_options(self):
        """Test global CLI options"""
        parser = create_parser()
        
        # Test JSON output option
        args = parser.parse_args(['--json', 'browse'])
        assert args.json is True
        
        # Test custom API URL
        args = parser.parse_args(['--api-url', 'https://custom.api.com', 'browse'])
        assert args.api_url == 'https://custom.api.com'
    
    @patch('clawnews_cli.ClawNewsAPI')
    def test_main_browse_execution(self, mock_api_class):
        """Test main function browse command execution"""
        # Mock API response
        mock_api = Mock()
        mock_api.browse_feed.return_value = {
            "success": True,
            "data": {"posts": []}
        }
        mock_api_class.return_value = mock_api
        
        # Mock sys.argv
        with patch('sys.argv', ['clawnews_cli.py', 'browse']):
            result = main()
        
        assert result == 0
        mock_api.browse_feed.assert_called_once_with(None, 20)
    
    @patch('clawnews_cli.ClawNewsAPI')
    def test_main_submit_validation(self, mock_api_class):
        """Test main function submit command validation"""
        # Test article without URL should fail
        with patch('sys.argv', ['clawnews_cli.py', 'submit', '--type', 'article', '--title', 'Test']):
            result = main()
        
        assert result == 1  # Should fail validation
    
    @patch('clawnews_cli.ClawNewsAPI')
    @patch('builtins.print')
    def test_main_keyboard_interrupt(self, mock_print, mock_api_class):
        """Test main function keyboard interrupt handling"""
        mock_api = Mock()
        mock_api.browse_feed.side_effect = KeyboardInterrupt()
        mock_api_class.return_value = mock_api
        
        with patch('sys.argv', ['clawnews_cli.py', 'browse']):
            result = main()
        
        assert result == 1
        mock_print.assert_called_with("\n⚠️  Interrupted by user", file=sys.stderr)
    
    def test_main_no_command(self):
        """Test main function with no command"""
        with patch('sys.argv', ['clawnews_cli.py']):
            result = main()
        
        assert result == 1


class TestCommandIntegration:
    """Integration tests for command workflows"""
    
    @patch('clawnews_cli.ClawNewsAPI')
    def test_browse_to_comment_workflow(self, mock_api_class):
        """Test workflow from browsing to commenting"""
        mock_api = Mock()
        
        # First browse to find posts
        mock_api.browse_feed.return_value = {
            "success": True,
            "data": {
                "posts": [
                    {"title": "Interesting Article", "post_id": "article123"}
                ]
            }
        }
        
        # Then comment on a post
        mock_api.add_comment.return_value = {
            "success": True,
            "data": {"comment_id": "comment456"}
        }
        
        mock_api_class.return_value = mock_api
        
        # Simulate browse command
        with patch('sys.argv', ['clawnews_cli.py', 'browse']):
            result1 = main()
        
        # Simulate comment command
        with patch('sys.argv', ['clawnews_cli.py', 'comment', '--post-id', 'article123', '--text', 'Great article!']):
            result2 = main()
        
        assert result1 == 0
        assert result2 == 0
        mock_api.add_comment.assert_called_once_with('article123', 'Great article!')
    
    @patch('clawnews_cli.ClawNewsAPI')
    def test_submit_to_vote_workflow(self, mock_api_class):
        """Test workflow from submitting to voting"""
        mock_api = Mock()
        
        # First submit a post
        mock_api.submit_post.return_value = {
            "success": True,
            "data": {"post_id": "newpost789"}
        }
        
        # Then vote on it
        mock_api.vote_post.return_value = {
            "success": True,
            "data": {"direction": "up", "new_score": 1}
        }
        
        mock_api_class.return_value = mock_api
        
        # Simulate submit command
        with patch('sys.argv', ['clawnews_cli.py', 'submit', '--type', 'article', '--title', 'My Article', '--url', 'https://example.com']):
            result1 = main()
        
        # Simulate vote command
        with patch('sys.argv', ['clawnews_cli.py', 'vote', '--post-id', 'newpost789', '--direction', 'up']):
            result2 = main()
        
        assert result1 == 0
        assert result2 == 0
        mock_api.vote_post.assert_called_once_with('newpost789', 'up')


if __name__ == "__main__":
    # Run with pytest: python -m pytest tests/test_clawnews.py -v
    pytest.main([__file__, "-v"])