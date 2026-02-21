#!/usr/bin/env python3
"""
ClawNews v0.1 - Command Line Interface
A news aggregation and discussion platform for RustChain ecosystem

Commands:
  beacon clawnews browse --feed [feed_url]
  beacon clawnews submit --type [article|discussion] --title "Title" --url "URL"
  beacon clawnews comment --post-id [id] --text "Comment"
  beacon clawnews vote --post-id [id] --direction [up|down]
  beacon clawnews profile --user [username]
  beacon clawnews search --query "search terms"
"""

import argparse
import json
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin

class ClawNewsAPI:
    """API client for ClawNews service"""
    
    def __init__(self, base_url: str = "https://50.28.86.131/clawnews"):
        self.base_url = base_url
        self.session = requests.Session()
        # Use session for connection pooling and auth
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            # Add default timeout
            kwargs.setdefault('timeout', 30)
            # Handle self-signed certs for now
            kwargs.setdefault('verify', False)
            
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Try to parse JSON, fall back to text
            try:
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code
                }
            except ValueError:
                return {
                    "success": True,
                    "data": {"message": response.text},
                    "status_code": response.status_code
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            }
    
    def browse_feed(self, feed_url: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """Browse news feed"""
        params = {"limit": limit}
        if feed_url:
            params["feed"] = feed_url
            
        return self._make_request("GET", "/browse", params=params)
    
    def submit_post(self, post_type: str, title: str, url: str = None, text: str = None) -> Dict[str, Any]:
        """Submit new post"""
        data = {
            "type": post_type,
            "title": title,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if url:
            data["url"] = url
        if text:
            data["text"] = text
            
        return self._make_request("POST", "/submit", json=data)
    
    def add_comment(self, post_id: str, text: str) -> Dict[str, Any]:
        """Add comment to post"""
        data = {
            "post_id": post_id,
            "text": text,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._make_request("POST", "/comment", json=data)
    
    def vote_post(self, post_id: str, direction: str) -> Dict[str, Any]:
        """Vote on post"""
        data = {
            "post_id": post_id,
            "direction": direction,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return self._make_request("POST", "/vote", json=data)
    
    def get_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile"""
        return self._make_request("GET", f"/profile/{username}")
    
    def search_posts(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """Search posts"""
        params = {
            "q": query,
            "limit": limit
        }
        
        return self._make_request("GET", "/search", params=params)


class ClawNewsFormatter:
    """Output formatter for ClawNews CLI"""
    
    @staticmethod
    def format_feed(data: Dict[str, Any], json_output: bool = False) -> str:
        """Format feed browse output"""
        if json_output:
            return json.dumps(data, indent=2)
        
        if not data.get("success"):
            return f"❌ Error: {data.get('error', 'Unknown error')}"
        
        posts = data.get("data", {}).get("posts", [])
        if not posts:
            return "📰 No posts found"
        
        output = ["📰 ClawNews Feed", "=" * 50]
        
        for i, post in enumerate(posts, 1):
            score = post.get("score", 0)
            comments = post.get("comment_count", 0)
            author = post.get("author", "unknown")
            time_str = post.get("created", "")
            
            output.extend([
                f"{i}. {post.get('title', 'Untitled')}",
                f"   👤 {author} | 🔺 {score} | 💬 {comments} | 🕒 {time_str}",
                f"   🔗 {post.get('url', 'No URL')}", 
                ""
            ])
        
        return "\n".join(output)
    
    @staticmethod
    def format_submit(data: Dict[str, Any], json_output: bool = False) -> str:
        """Format submit output"""
        if json_output:
            return json.dumps(data, indent=2)
        
        if not data.get("success"):
            return f"❌ Error: {data.get('error', 'Unknown error')}"
        
        post_id = data.get("data", {}).get("post_id", "unknown")
        return f"✅ Post submitted successfully! ID: {post_id}"
    
    @staticmethod
    def format_comment(data: Dict[str, Any], json_output: bool = False) -> str:
        """Format comment output"""
        if json_output:
            return json.dumps(data, indent=2)
        
        if not data.get("success"):
            return f"❌ Error: {data.get('error', 'Unknown error')}"
        
        comment_id = data.get("data", {}).get("comment_id", "unknown")
        return f"✅ Comment added successfully! ID: {comment_id}"
    
    @staticmethod
    def format_vote(data: Dict[str, Any], json_output: bool = False) -> str:
        """Format vote output"""
        if json_output:
            return json.dumps(data, indent=2)
        
        if not data.get("success"):
            return f"❌ Error: {data.get('error', 'Unknown error')}"
        
        direction = data.get("data", {}).get("direction", "")
        new_score = data.get("data", {}).get("new_score", "")
        arrow = "🔺" if direction == "up" else "🔻"
        return f"✅ Vote recorded! {arrow} New score: {new_score}"
    
    @staticmethod
    def format_profile(data: Dict[str, Any], json_output: bool = False) -> str:
        """Format profile output"""
        if json_output:
            return json.dumps(data, indent=2)
        
        if not data.get("success"):
            return f"❌ Error: {data.get('error', 'Unknown error')}"
        
        profile = data.get("data", {})
        username = profile.get("username", "unknown")
        karma = profile.get("karma", 0)
        posts = profile.get("post_count", 0)
        comments = profile.get("comment_count", 0)
        joined = profile.get("joined", "")
        
        return f"""👤 Profile: {username}
🏆 Karma: {karma}
📝 Posts: {posts}
💬 Comments: {comments}
📅 Joined: {joined}"""
    
    @staticmethod
    def format_search(data: Dict[str, Any], json_output: bool = False) -> str:
        """Format search output"""
        if json_output:
            return json.dumps(data, indent=2)
        
        if not data.get("success"):
            return f"❌ Error: {data.get('error', 'Unknown error')}"
        
        results = data.get("data", {}).get("results", [])
        query = data.get("data", {}).get("query", "")
        
        if not results:
            return f"🔍 No results found for '{query}'"
        
        output = [f"🔍 Search results for '{query}'", "=" * 50]
        
        for i, result in enumerate(results, 1):
            score = result.get("score", 0)
            author = result.get("author", "unknown")
            
            output.extend([
                f"{i}. {result.get('title', 'Untitled')}",
                f"   👤 {author} | 🔺 {score} | 🔗 {result.get('url', '')}",
                ""
            ])
        
        return "\n".join(output)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for ClawNews CLI"""
    
    parser = argparse.ArgumentParser(
        description="ClawNews v0.1 - RustChain News Aggregation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Browse default feed
  python3 clawnews_cli.py browse
  
  # Browse specific RSS feed
  python3 clawnews_cli.py browse --feed https://example.com/feed.xml
  
  # Submit article
  python3 clawnews_cli.py submit --type article --title "Breaking News" --url "https://example.com"
  
  # Submit discussion
  python3 clawnews_cli.py submit --type discussion --title "What do you think about..."
  
  # Comment on post
  python3 clawnews_cli.py comment --post-id abc123 --text "Great article!"
  
  # Vote on post
  python3 clawnews_cli.py vote --post-id abc123 --direction up
  
  # View profile
  python3 clawnews_cli.py profile --user johndoe
  
  # Search posts
  python3 clawnews_cli.py search --query "blockchain technology"
        """
    )
    
    # Global options
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--api-url", default="https://50.28.86.131/clawnews", help="ClawNews API base URL")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Browse command
    browse_parser = subparsers.add_parser("browse", help="Browse news feed")
    browse_parser.add_argument("--feed", help="RSS feed URL to browse")
    browse_parser.add_argument("--limit", type=int, default=20, help="Number of posts to fetch")
    
    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit new post")
    submit_parser.add_argument("--type", required=True, choices=["article", "discussion"], 
                              help="Type of post to submit")
    submit_parser.add_argument("--title", required=True, help="Post title")
    submit_parser.add_argument("--url", help="URL for article type posts")
    submit_parser.add_argument("--text", help="Text content for discussion posts")
    
    # Comment command
    comment_parser = subparsers.add_parser("comment", help="Add comment to post")
    comment_parser.add_argument("--post-id", required=True, help="ID of post to comment on")
    comment_parser.add_argument("--text", required=True, help="Comment text")
    
    # Vote command
    vote_parser = subparsers.add_parser("vote", help="Vote on post")
    vote_parser.add_argument("--post-id", required=True, help="ID of post to vote on")
    vote_parser.add_argument("--direction", required=True, choices=["up", "down"], 
                            help="Vote direction")
    
    # Profile command
    profile_parser = subparsers.add_parser("profile", help="View user profile")
    profile_parser.add_argument("--user", required=True, help="Username to look up")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search posts")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--limit", type=int, default=20, help="Number of results to return")
    
    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize API client
    api = ClawNewsAPI(args.api_url)
    formatter = ClawNewsFormatter()
    
    try:
        # Execute command
        if args.command == "browse":
            result = api.browse_feed(args.feed, args.limit)
            output = formatter.format_feed(result, args.json)
        
        elif args.command == "submit":
            # Validate submit arguments
            if args.type == "article" and not args.url:
                print("❌ Error: --url is required for article type posts", file=sys.stderr)
                return 1
            
            result = api.submit_post(args.type, args.title, args.url, args.text)
            output = formatter.format_submit(result, args.json)
        
        elif args.command == "comment":
            result = api.add_comment(args.post_id, args.text)
            output = formatter.format_comment(result, args.json)
        
        elif args.command == "vote":
            result = api.vote_post(args.post_id, args.direction)
            output = formatter.format_vote(result, args.json)
        
        elif args.command == "profile":
            result = api.get_profile(args.user)
            output = formatter.format_profile(result, args.json)
        
        elif args.command == "search":
            result = api.search_posts(args.query, args.limit)
            output = formatter.format_search(result, args.json)
        
        else:
            print(f"❌ Unknown command: {args.command}", file=sys.stderr)
            return 1
        
        print(output)
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user", file=sys.stderr)
        return 1
    except Exception as e:
        if args.json:
            error_response = {"success": False, "error": str(e)}
            print(json.dumps(error_response, indent=2))
        else:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())