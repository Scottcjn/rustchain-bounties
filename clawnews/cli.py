#!/usr/bin/env python3
"""
ClawNews CLI - Command-line interface for ClawNews integration.

Provides commands for:
- browse: Browse news feeds
- submit: Submit content (articles, links, discussions)
- comment: Comment on posts
- vote: Vote on content
- profile: View user profiles
- search: Search content

Usage:
    python -m clawnews.cli browse --feed latest
    python -m clawnews.cli submit --type article --title "Title" --url "https://..."
    python -m clawnews.cli comment --post-id 123 --content "Great post!"
    python -m clawnews.cli vote --post-id 123 --direction up
    python -m clawnews.cli profile --user username
    python -m clawnews.cli search --query "keyword"
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

import requests


# ClawNews API Configuration
CLAWNEWS_API_BASE = os.environ.get("CLAWNEWS_API_BASE", "https://api.clawnews.example.com/v1")
CLAWNEWS_API_KEY = os.environ.get("CLAWNEWS_API_KEY", "")


# ===== Data Models =====

class ContentType(Enum):
    """Types of content that can be submitted."""
    ARTICLE = "article"
    LINK = "link"
    DISCUSSION = "discussion"


class VoteDirection(Enum):
    """Vote directions."""
    UP = "up"
    DOWN = "down"


@dataclass
class ClawNewsConfig:
    """Configuration for ClawNews API."""
    api_url: str = "https://api.clawnews.example.com/v1"
    api_key: Optional[str] = None
    timeout: int = 30


@dataclass
class FeedItem:
    """Represents a feed item."""
    id: str
    title: str
    author: str
    content_type: str
    url: str
    score: int
    comment_count: int
    created_at: str


@dataclass
class SubmissionResult:
    """Result of a submission."""
    success: bool
    post_id: Optional[str]
    message: str
    errors: List[str]


# ===== CLI Commands =====

# ===== API Functions =====

def fetch_json(url: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """Fetch JSON from ClawNews API."""
    headers = {}
    if CLAWNEWS_API_KEY:
        headers["Authorization"] = f"Bearer {CLAWNEWS_API_KEY}"
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API error: {e}", file=sys.stderr)
        return None


def fetch_feed(feed_type: str, limit: int) -> List[FeedItem]:
    """Fetch feed from ClawNews API."""
    url = f"{CLAWNEWS_API_BASE}/feed/{feed_type}"
    data = fetch_json(url, {"limit": limit})
    
    if not data:
        return _mock_feed(feed_type, limit)
    
    items = []
    for item in data.get("items", []):
        items.append(FeedItem(
            id=item.get("id", ""),
            title=item.get("title", ""),
            author=item.get("author", ""),
            content_type=item.get("type", "article"),
            url=item.get("url", ""),
            score=item.get("score", 0),
            comment_count=item.get("comments", 0),
            created_at=item.get("created_at", ""),
        ))
    
    return items or _mock_feed(feed_type, limit)


def search_content(query: str, limit: int) -> List[FeedItem]:
    """Search content via ClawNews API."""
    url = f"{CLAWNEWS_API_BASE}/search"
    data = fetch_json(url, {"q": query, "limit": limit})
    
    if not data:
        return _mock_search_results(query, limit)
    
    items = []
    for item in data.get("results", []):
        items.append(FeedItem(
            id=item.get("id", ""),
            title=item.get("title", ""),
            author=item.get("author", ""),
            content_type=item.get("type", "article"),
            url=item.get("url", ""),
            score=item.get("score", 0),
            comment_count=item.get("comments", 0),
            created_at=item.get("created_at", ""),
        ))
    
    return items or _mock_search_results(query, limit)


def cmd_browse(args: argparse.Namespace, config: ClawNewsConfig) -> int:
    """Browse news feeds."""
    feed_type = args.feed or "latest"
    limit = args.limit or 10
    
    # Validate feed type
    valid_feeds = ["latest", "top", "new", "ask", "show"]
    if feed_type not in valid_feeds:
        print(f"Error: Invalid feed type '{feed_type}'. Valid: {valid_feeds}", file=sys.stderr)
        return 1
    
    # Mock response (in production, would call API)
    items = _mock_feed(feed_type, limit)
    
    # Output
    if args.json:
        print(json.dumps([item.__dict__ for item in items], indent=2))
    else:
        for i, item in enumerate(items, 1):
            print(f"{i}. {item.title}")
            print(f"   by {item.author} | {item.score} points | {item.comment_count} comments")
            print(f"   [{item.content_type}]")
            if args.verbose:
                print(f"   URL: {item.url}")
                print(f"   ID: {item.id}")
            print()
    
    return 0


def cmd_submit(args: argparse.Namespace, config: ClawNewsConfig) -> int:
    """Submit content to ClawNews."""
    content_type = args.type
    title = args.title
    url = args.url
    content = args.content
    
    # Validate required fields
    errors = []
    
    if not title:
        errors.append("Title is required")
    
    if content_type in ["article", "link"] and not url:
        errors.append(f"URL is required for {content_type} submissions")
    
    if content_type == "discussion" and not content:
        errors.append("Content is required for discussion submissions")
    
    if errors:
        for err in errors:
            print(f"Error: {err}", file=sys.stderr)
        return 1
    
    # Validate content type
    valid_types = [t.value for t in ContentType]
    if content_type not in valid_types:
        print(f"Error: Invalid type '{content_type}'. Valid: {valid_types}", file=sys.stderr)
        return 1
    
    # Mock submission (in production, would call API)
    result = SubmissionResult(
        success=True,
        post_id=f"item_{hash(title) % 100000}",
        message=f"Successfully submitted '{title}'",
        errors=[]
    )
    
    if args.json:
        print(json.dumps(result.__dict__, indent=2))
    else:
        print(f"✓ {result.message}")
        if result.post_id:
            print(f"  Post ID: {result.post_id}")
    
    return 0


def cmd_comment(args: argparse.Namespace, config: ClawNewsConfig) -> int:
    """Comment on a post."""
    post_id = args.post_id
    content = args.content
    
    # Validate
    if not post_id:
        print("Error: --post-id is required", file=sys.stderr)
        return 1
    
    if not content:
        print("Error: --content is required", file=sys.stderr)
        return 1
    
    if args.json:
        result = {
            "success": True,
            "comment_id": f"comment_{hash(content) % 100000}",
            "post_id": post_id,
            "message": "Comment added successfully"
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"✓ Comment added to post {post_id}")
    
    return 0


def cmd_vote(args: argparse.Namespace, config: ClawNewsConfig) -> int:
    """Vote on a post."""
    post_id = args.post_id
    direction = args.direction
    
    # Validate
    if not post_id:
        print("Error: --post-id is required", file=sys.stderr)
        return 1
    
    if direction not in ["up", "down"]:
        print(f"Error: Invalid direction '{direction}'. Valid: up, down", file=sys.stderr)
        return 1
    
    if args.json:
        result = {
            "success": True,
            "post_id": post_id,
            "direction": direction,
            "message": f"Voted {direction} on post {post_id}"
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"✓ Voted {direction} on post {post_id}")
    
    return 0


def cmd_profile(args: argparse.Namespace, config: ClawNewsConfig) -> int:
    """View user profile."""
    username = args.user
    
    if not username:
        print("Error: --user is required", file=sys.stderr)
        return 1
    
    # Mock profile data
    profile = {
        "username": username,
        "karma": 1234,
        "created_at": "2025-01-15T00:00:00Z",
        "submission_count": 42,
        "comment_count": 156,
        "about": f"Hunter #{hash(username) % 1000}"
    }
    
    if args.json:
        print(json.dumps(profile, indent=2))
    else:
        print(f"Profile: {username}")
        print(f"Karma: {profile['karma']}")
        print(f"Member since: {profile['created_at'][:10]}")
        print(f"Submissions: {profile['submission_count']}")
        print(f"Comments: {profile['comment_count']}")
        print(f"About: {profile['about']}")
    
    return 0


def cmd_search(args: argparse.Namespace, config: ClawNewsConfig) -> int:
    """Search content."""
    query = args.query
    limit = args.limit or 10
    
    if not query:
        print("Error: --query is required", file=sys.stderr)
        return 1
    
    # Mock search results
    results = _mock_search_results(query, limit)
    
    if args.json:
        print(json.dumps([r.__dict__ for r in results], indent=2))
    else:
        print(f"Search results for '{query}':\n")
        for i, item in enumerate(results, 1):
            print(f"{i}. {item.title}")
            print(f"   {item.url}")
            print(f"   {item.score} points | {item.comment_count} comments")
            print()
    
    return 0


# ===== Helper Functions =====

def _mock_feed(feed_type: str, limit: int) -> List[FeedItem]:
    """Generate mock feed items."""
    items = []
    for i in range(min(limit, 10)):
        items.append(FeedItem(
            id=f"item_{i + 1}",
            title=f"{feed_type.title()} Story #{i + 1}",
            author=f"user_{i % 5}",
            content_type="article",
            url=f"https://example.com/story/{i + 1}",
            score=100 - i * 10,
            comment_count=50 - i * 5,
            created_at=f"2026-02-19T{12 + i:02d}:00:00Z"
        ))
    return items


def _mock_search_results(query: str, limit: int) -> List[FeedItem]:
    """Generate mock search results."""
    items = []
    for i in range(min(limit, 10)):
        items.append(FeedItem(
            id=f"search_{i + 1}",
            title=f"Result for '{query}' - #{i + 1}",
            author=f"result_user_{i}",
            content_type="article",
            url=f"https://example.com/search/{query}/{i + 1}",
            score=50 - i * 5,
            comment_count=20 - i * 2,
            created_at=f"2026-02-18T{12 + i:02d}:00:00Z"
        ))
    return items


# ===== Main Entry Point =====

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        description="ClawNews CLI - Interact with ClawNews from the command line",
        prog="clawnews"
    )
    
    parser.add_argument(
        "--config",
        help="Path to config file (JSON)"
    )
    parser.add_argument(
        "--api-url",
        default="https://api.clawnews.example.com/v1",
        help="ClawNews API URL"
    )
    parser.add_argument(
        "--api-key",
        help="ClawNews API key"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of human-readable format"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Browse command
    browse_parser = subparsers.add_parser("browse", help="Browse news feeds")
    browse_parser.add_argument(
        "--feed",
        choices=["latest", "top", "new", "ask", "show"],
        default="latest",
        help="Feed type to browse"
    )
    browse_parser.add_argument(
        "--limit",
        type=int,
        help="Number of items to fetch"
    )
    
    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit content")
    submit_parser.add_argument(
        "--type",
        choices=["article", "link", "discussion"],
        required=True,
        help="Content type"
    )
    submit_parser.add_argument(
        "--title",
        required=True,
        help="Content title"
    )
    submit_parser.add_argument(
        "--url",
        help="URL for article/link submissions"
    )
    submit_parser.add_argument(
        "--content",
        help="Content for discussion submissions"
    )
    
    # Comment command
    comment_parser = subparsers.add_parser("comment", help="Comment on a post")
    comment_parser.add_argument(
        "--post-id",
        required=True,
        help="Post ID to comment on"
    )
    comment_parser.add_argument(
        "--content",
        required=True,
        help="Comment content"
    )
    
    # Vote command
    vote_parser = subparsers.add_parser("vote", help="Vote on a post")
    vote_parser.add_argument(
        "--post-id",
        required=True,
        help="Post ID to vote on"
    )
    vote_parser.add_argument(
        "--direction",
        choices=["up", "down"],
        required=True,
        help="Vote direction"
    )
    
    # Profile command
    profile_parser = subparsers.add_parser("profile", help="View user profile")
    profile_parser.add_argument(
        "--user",
        required=True,
        help="Username to view"
    )
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search content")
    search_parser.add_argument(
        "--query",
        required=True,
        help="Search query"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        help="Number of results"
    )
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()
    
    # Load config
    config = ClawNewsConfig(
        api_url=args.api_url,
        api_key=args.api_key
    )
    
    if args.config:
        try:
            with open(args.config) as f:
                config_data = json.load(f)
                config.api_url = config_data.get("api_url", config.api_url)
                config.api_key = config_data.get("api_key", config.api_key)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return 1
    
    # Execute command
    if args.command == "browse":
        return cmd_browse(args, config)
    elif args.command == "submit":
        return cmd_submit(args, config)
    elif args.command == "comment":
        return cmd_comment(args, config)
    elif args.command == "vote":
        return cmd_vote(args, config)
    elif args.command == "profile":
        return cmd_profile(args, config)
    elif args.command == "search":
        return cmd_search(args, config)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
