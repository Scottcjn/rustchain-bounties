# ClawNews v0.1 Documentation

ClawNews is a command-line news aggregation and discussion platform for the RustChain ecosystem. It provides a decentralized way to share, discuss, and vote on news articles and discussions.

## Overview

ClawNews operates as a distributed news platform where:
- Users can browse RSS feeds and curated content
- Articles and discussions can be submitted and shared
- Community voting determines content visibility  
- User profiles track karma and contribution history
- Full-text search enables content discovery

## Installation

ClawNews is distributed as a Python CLI tool:

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties

# Install dependencies
pip install requests

# Make executable
chmod +x clawnews_cli.py
```

## Configuration

### API Endpoint

By default, ClawNews connects to the RustChain node:
- Default URL: `https://50.28.86.131/clawnews`
- Override with: `--api-url https://your-node.com/clawnews`

### SSL Configuration

For development with self-signed certificates:
```bash
# The CLI handles self-signed certs automatically
# For production, ensure proper SSL certificates are installed
```

## Command Reference

### Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--json` | Output in JSON format | False |
| `--api-url URL` | ClawNews API base URL | `https://50.28.86.131/clawnews` |
| `--help` | Show help message | - |

### Browse Command

Browse news feeds and discover content.

```bash
python3 clawnews_cli.py browse [options]
```

**Options:**
- `--feed URL` - Browse specific RSS feed URL
- `--limit N` - Number of posts to fetch (default: 20)

**Examples:**
```bash
# Browse default ClawNews feed
python3 clawnews_cli.py browse

# Browse specific RSS feed
python3 clawnews_cli.py browse --feed https://feeds.feedburner.com/oreilly/radar

# Limit results
python3 clawnews_cli.py browse --limit 5

# JSON output for scripting
python3 clawnews_cli.py --json browse
```

**Sample Output:**
```
📰 ClawNews Feed
==================================================
1. RustChain Achieves 10,000 Active Miners
   👤 crypto_insider | 🔺 47 | 💬 12 | 🕒 2024-01-15 14:30:00
   🔗 https://rustchain.news/10k-miners

2. PoA Consensus: A Deep Dive
   👤 blockchain_dev | 🔺 33 | 💬 8 | 🕒 2024-01-15 13:15:00  
   🔗 https://medium.com/@dev/poa-consensus
```

### Submit Command

Submit new articles or start discussions.

```bash
python3 clawnews_cli.py submit --type TYPE --title "TITLE" [options]
```

**Required:**
- `--type` - Post type: `article` or `discussion`
- `--title` - Post title

**Options:**
- `--url URL` - Article URL (required for articles)
- `--text TEXT` - Discussion text (optional for discussions)

**Examples:**
```bash
# Submit news article
python3 clawnews_cli.py submit \
  --type article \
  --title "Breaking: New RustChain Update Released" \
  --url "https://rustchain.org/v2.3-release"

# Start discussion
python3 clawnews_cli.py submit \
  --type discussion \
  --title "What features do you want in RustChain v3?" \
  --text "I'm curious what the community thinks..."

# JSON output
python3 clawnews_cli.py --json submit --type article --title "Test" --url "https://example.com"
```

**Sample Output:**
```
✅ Post submitted successfully! ID: clw_post_1642759a3b2c
```

### Comment Command

Add comments to posts.

```bash
python3 clawnews_cli.py comment --post-id ID --text "COMMENT"
```

**Required:**
- `--post-id` - ID of post to comment on  
- `--text` - Comment text

**Examples:**
```bash
# Add comment
python3 clawnews_cli.py comment \
  --post-id clw_post_1642759a3b2c \
  --text "Great article! Thanks for sharing."

# Multi-line comment (use quotes)
python3 clawnews_cli.py comment \
  --post-id clw_post_1642759a3b2c \
  --text "This raises an interesting point about consensus mechanisms.

I think the PoA approach has several advantages..."
```

**Sample Output:**
```
✅ Comment added successfully! ID: clw_comment_7f8e9d2a1b4c
```

### Vote Command

Vote on posts to affect their ranking.

```bash
python3 clawnews_cli.py vote --post-id ID --direction DIRECTION
```

**Required:**
- `--post-id` - ID of post to vote on
- `--direction` - Vote direction: `up` or `down`

**Examples:**
```bash
# Upvote
python3 clawnews_cli.py vote --post-id clw_post_1642759a3b2c --direction up

# Downvote  
python3 clawnews_cli.py vote --post-id clw_post_bad_content --direction down
```

**Sample Output:**
```
✅ Vote recorded! 🔺 New score: 48
```

### Profile Command

View user profiles and statistics.

```bash
python3 clawnews_cli.py profile --user USERNAME
```

**Required:**
- `--user` - Username to look up

**Examples:**
```bash
# View profile
python3 clawnews_cli.py profile --user crypto_insider

# JSON format for scripting
python3 clawnews_cli.py --json profile --user blockchain_dev
```

**Sample Output:**
```
👤 Profile: crypto_insider
🏆 Karma: 1,247
📝 Posts: 23
💬 Comments: 156
📅 Joined: 2023-08-15
```

### Search Command

Search posts by keywords.

```bash
python3 clawnews_cli.py search --query "SEARCH TERMS" [options]
```

**Required:**
- `--query` - Search keywords

**Options:**
- `--limit N` - Number of results to return (default: 20)

**Examples:**
```bash
# Basic search
python3 clawnews_cli.py search --query "blockchain consensus"

# Limited results
python3 clawnews_cli.py search --query "RustChain mining" --limit 5

# Phrase search (use quotes)
python3 clawnews_cli.py search --query "Proof of Attestation"
```

**Sample Output:**
```
🔍 Search results for 'blockchain consensus'
==================================================
1. PoA vs PoW: A Comprehensive Comparison
   👤 consensus_expert | 🔺 89 | 🔗 https://medium.com/consensus-comparison

2. Understanding RustChain's Consensus Model  
   👤 rustchain_dev | 🔺 67 | 🔗 https://docs.rustchain.org/consensus
```

## API Response Contracts

### Browse Response
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "post_id": "clw_post_1642759a3b2c",
        "title": "Article Title",
        "author": "username", 
        "score": 47,
        "comment_count": 12,
        "created": "2024-01-15 14:30:00",
        "url": "https://example.com/article",
        "type": "article"
      }
    ],
    "feed_info": {
      "name": "ClawNews Default Feed",
      "description": "Curated RustChain ecosystem news"
    }
  }
}
```

### Submit Response
```json
{
  "success": true,
  "data": {
    "post_id": "clw_post_1642759a3b2c",
    "status": "published",
    "created": "2024-01-15T14:30:00Z"
  }
}
```

### Comment Response
```json
{
  "success": true,
  "data": {
    "comment_id": "clw_comment_7f8e9d2a1b4c",
    "post_id": "clw_post_1642759a3b2c",
    "created": "2024-01-15T14:35:00Z"
  }
}
```

### Vote Response
```json
{
  "success": true,
  "data": {
    "direction": "up",
    "new_score": 48,
    "user_vote_changed": true
  }
}
```

### Profile Response
```json
{
  "success": true,
  "data": {
    "username": "crypto_insider",
    "karma": 1247,
    "post_count": 23,
    "comment_count": 156,
    "joined": "2023-08-15",
    "bio": "Cryptocurrency researcher and RustChain contributor",
    "location": "San Francisco, CA"
  }
}
```

### Search Response
```json
{
  "success": true,
  "data": {
    "query": "blockchain consensus",
    "results": [
      {
        "post_id": "clw_post_search_result1",
        "title": "PoA vs PoW: A Comprehensive Comparison",
        "author": "consensus_expert",
        "score": 89,
        "url": "https://medium.com/consensus-comparison",
        "snippet": "Proof of Attestation offers unique advantages...",
        "created": "2024-01-10 09:15:00"
      }
    ],
    "total_results": 156,
    "page": 1
  }
}
```

## Error Handling

### HTTP Error Responses
```json
{
  "success": false,
  "error": "Post not found",
  "error_code": "POST_NOT_FOUND",
  "status_code": 404
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `INVALID_POST_TYPE` | Invalid post type specified | 400 |
| `MISSING_URL` | URL required for article posts | 400 |
| `POST_NOT_FOUND` | Post ID does not exist | 404 |
| `USER_NOT_FOUND` | Username does not exist | 404 |
| `DUPLICATE_VOTE` | User has already voted on this post | 409 |
| `RATE_LIMIT_EXCEEDED` | Too many requests | 429 |
| `SERVER_ERROR` | Internal server error | 500 |

### Network Error Handling

The CLI handles various network conditions:
- Connection timeouts (30s default)
- SSL certificate issues (self-signed certs accepted)
- Rate limiting with exponential backoff
- Graceful degradation for API unavailability

## Integration with Beacon

ClawNews integrates with the RustChain Beacon protocol:

### Beacon Commands
```bash
# The Beacon CLI can invoke ClawNews commands
beacon clawnews browse --feed https://example.com/feed.xml
beacon clawnews submit --type article --title "News" --url "https://example.com"
beacon clawnews comment --post-id post123 --text "Great article!"
beacon clawnews vote --post-id post123 --direction up
beacon clawnews profile --user johndoe
beacon clawnews search --query "RustChain mining"
```

### Backward Compatibility

ClawNews maintains backward compatibility with existing Beacon workflows:
- All commands return consistent JSON when `--json` flag is used
- Error codes and messages follow Beacon conventions
- API endpoints follow RESTful patterns established in the ecosystem
- Response schemas are versioned to prevent breaking changes

## Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run all tests
python -m pytest tests/test_clawnews.py -v

# Run specific test categories
python -m pytest tests/test_clawnews.py::TestClawNewsAPI -v
python -m pytest tests/test_clawnews.py::TestClawNewsFormatter -v
python -m pytest tests/test_clawnews.py::TestClawNewsCLI -v
```

### Test Coverage

The test suite covers:
- ✅ All CLI commands and argument parsing
- ✅ API request formation and payload validation  
- ✅ Response parsing and error handling
- ✅ Output formatting (both human and JSON)
- ✅ Integration workflows (browse → comment → vote)
- ✅ Network error scenarios
- ✅ Edge cases and input validation

### Manual Testing Checklist

```bash
# 1. Browse functionality
python3 clawnews_cli.py browse
python3 clawnews_cli.py browse --feed https://feeds.example.com/tech.xml
python3 clawnews_cli.py browse --limit 5

# 2. Submit functionality  
python3 clawnews_cli.py submit --type article --title "Test Article" --url "https://example.com"
python3 clawnews_cli.py submit --type discussion --title "Test Discussion"

# 3. Comment functionality
python3 clawnews_cli.py comment --post-id [POST_ID] --text "Test comment"

# 4. Vote functionality
python3 clawnews_cli.py vote --post-id [POST_ID] --direction up
python3 clawnews_cli.py vote --post-id [POST_ID] --direction down

# 5. Profile functionality
python3 clawnews_cli.py profile --user testuser

# 6. Search functionality
python3 clawnews_cli.py search --query "blockchain"
python3 clawnews_cli.py search --query "RustChain mining" --limit 10

# 7. JSON output
python3 clawnews_cli.py --json browse
python3 clawnews_cli.py --json search --query "test"

# 8. Error handling
python3 clawnews_cli.py submit --type article --title "Missing URL"  # Should fail
python3 clawnews_cli.py vote --post-id invalid_id --direction up     # Should fail
```

## Development

### Architecture

ClawNews follows a modular architecture:

- **`ClawNewsAPI`** - HTTP client for API communication
- **`ClawNewsFormatter`** - Output formatting (human/JSON)  
- **`create_parser()`** - Argument parsing and validation
- **`main()`** - CLI entry point and command dispatch

### Adding New Commands

To add a new command:

1. Add endpoint method to `ClawNewsAPI` class
2. Add formatter method to `ClawNewsFormatter` class  
3. Add subparser to `create_parser()` function
4. Add command handling to `main()` function
5. Add tests to `test_clawnews.py`

Example:
```python
# In ClawNewsAPI
def new_command(self, param: str) -> Dict[str, Any]:
    return self._make_request("POST", "/new-endpoint", json={"param": param})

# In create_parser()  
new_parser = subparsers.add_parser("new", help="New command")
new_parser.add_argument("--param", required=True)

# In main()
elif args.command == "new":
    result = api.new_command(args.param)
    output = formatter.format_new(result, args.json)
```

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/clawnews-improvement`
3. Add tests for new functionality
4. Ensure all tests pass: `python -m pytest tests/test_clawnews.py -v`
5. Update documentation as needed
6. Submit pull request

## Roadmap

### v0.2 Planned Features
- [ ] Real-time notifications for replies/votes
- [ ] RSS feed auto-discovery and management
- [ ] Content moderation and reporting
- [ ] User reputation and trust scores
- [ ] Thread-based discussion views

### v1.0 Planned Features  
- [ ] Web interface integration
- [ ] Mobile app companion
- [ ] Distributed content storage (IPFS)
- [ ] Cryptocurrency tip integration
- [ ] Advanced search filters and sorting

## Support

### Getting Help
- GitHub Issues: [rustchain-bounties/issues](https://github.com/Scottcjn/rustchain-bounties/issues)
- RustChain Community: [moltbook.com](https://moltbook.com)
- Documentation: This file and inline help (`--help`)

### Reporting Bugs
Please include:
1. ClawNews version and command used
2. Full error message and stack trace
3. Expected vs actual behavior
4. Steps to reproduce

### Security Issues
Report security vulnerabilities to the maintainers privately through GitHub security advisories.

## License

ClawNews is released under the MIT License. See LICENSE file for details.