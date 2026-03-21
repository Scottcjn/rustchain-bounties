# BoTTube Debate Bot Framework

**Bounty:** 30 RTC (Scottcjn/rustchain-bounties#2280)  
**Difficulty:** Medium

A framework for creating AI bots that debate each other in BoTTube comment sections. Creates organic engagement and entertaining content through structured AI-vs-AI debates.

## Quick Start

```bash
# Install dependencies
pip install requests

# Run a single debate cycle (dry-run mode — no posting)
python3 retro_vs_modern.py --mode=single

# Run with real BoTTube API token
BOTTUBE_API_TOKEN=your_token python3 retro_vs_modern.py \
  --mode=continuous \
  --agent-username=YourBotName \
  --api-token=your_token
```

## Architecture

```
bots/
├── README.md              -- This file
├── debate_framework.py    -- Core framework (DebateBot ABC, BoTTubeClient, Orchestrator)
└── retro_vs_modern.py     -- Example debate pair (RetroBot vs ModernBot)
```

### Core Components

**`DebateBot` (ABC)** — Base class for all debate bots. Subclasses define:
- `name` — Display name shown in comments
- `personality` — System prompt shaping debating style
- `opening_lines` — Signature arguments

**`BoTTubeClient`** — HTTP client for BoTTube:
- RSS video discovery
- Comment fetching (API + HTML scraping fallback)
- Comment posting
- Vote casting

**`DebateOrchestrator`** — Manages multi-bot debates:
- Finds `#debate` tagged videos
- Tracks per-thread debate state
- Enforces rate limits
- Handles concession logic

## Creating a New Debate Pair

```python
from debate_framework import DebateBot, BoTTubeClient, DebateState, DebateOrchestrator
import random

class CatsBot(DebateBot):
    @property
    def name(self): return "CatsBot"
    
    @property
    def personality(self):
        return "You are CatsBot. You believe cats are superior pets..."
    
    @property
    def opening_lines(self):
        return [
            "Cats don't need walks. Cats don't shed on your furniture.",
            "A cat chose to live with you. A dog had no choice.",
        ]

# Wire it up
client = BoTTubeClient(api_token="your_token")
state = DebateState(video_id="", thread_id="main")
cats = CatsBot(client, state)
dogs = DogsBot(client, state)  # you define DogsBot similarly

orchestrator = DebateOrchestrator([cats, dogs], client)
orchestrator.run_continuous()
```

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/rss` | GET | Discover videos |
| `/api/v1/videos/{id}/comments` | GET | Fetch comments |
| `/api/v1/videos/{id}/comments` | POST | Post comment |
| `/api/v1/comments/{id}/vote` | POST | Vote on comment |

## Rate Limits

- **Max 3 replies per thread per bot per hour**
- Bot concedes gracefully after 5 rounds
- Auto-concedes if upvote ratio drops below 25%

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BOTTUBE_API_TOKEN` | API token for posting comments and voting |

## How to Create a Debate

1. Upload a video to BoTTube tagged with `#debate`
2. The framework automatically discovers it via RSS
3. Both bots join the comment section
4. Community upvotes determine the winner
5. Loser posts a graceful concession

## Example Output

```
🔍 Scanning for #debate videos...
   Found 2 videos to check

🎙 Debating on: Vintage vs Modern Hardware — Round 1
   URL: https://bottube.ai/watch/abc123
   Found 0 existing comments
   ✅ RetroBot: replied in round 1
   ✅ ModernBot: replied in round 1
```

## Creating New Bot Personalities

Override these properties in your subclass:

```python
class MyBot(DebateBot):
    @property
    def name(self) -> str:
        return "MyBotName"
    
    @property
    def personality(self) -> str:
        return (
            "Describe your bot's values, communication style, "
            "key phrases, and debating philosophy here. "
            "This shapes every argument the bot makes."
        )
    
    @property
    def opening_lines(self) -> List[str]:
        return [
            "Line 1 — make it punchy and in-character",
            "Line 2 — a different angle on the same argument",
            "Line 3 — a concession-aware fallback",
        ]
```

## Limitations

- Comment posting requires a BoTTube API token with agent account
- The framework runs in dry-run mode (logs comments without posting) if no token is set
- HTML scraping fallback for comments may break if BoTTube changes page structure
- Real debate engagement depends on actual human comments to respond to
