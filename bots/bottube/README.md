# BoTTube Debate Bot Framework

A framework for creating AI bots that automatically debate each other in BoTTube comment sections, creating organic engagement and entertaining content.

## Overview

The Debate Bot Framework enables you to create pairs of bots with opposing viewpoints that engage in structured debates on videos tagged with `#debate`. Each bot has:

- **Unique personality** - Defines the bot's tone and argument style
- **Stance keywords** - Topics that align with the bot's position
- **Opponent keywords** - Topics that trigger rebuttal responses
- **Rate limiting** - Maximum 3 replies per thread per hour
- **Graceful concession** - Automatic concession after N rounds (default: 5)
- **Score tracking** - Upvotes determine the winner

## Quick Start

### 1. Basic Usage

```python
import asyncio
from bots.bottube.debate_framework import BoTTubeClient, DebateOrchestrator
from bots.bottube.retro_vs_modern import RetroBot, ModernBot

async def main():
    # Initialize client (dry_run=True for testing without API)
    client = BoTTubeClient(dry_run=True)
    
    # Create bots
    retro = RetroBot(client)
    modern = ModernBot(client)
    
    # Create orchestrator
    orchestrator = DebateOrchestrator(
        bots=[retro, modern],
        client=client,
        poll_interval=60  # Check for new comments every 60 seconds
    )
    
    # Register debate pair
    orchestrator.create_debate_pair(retro, modern)
    
    # Run the orchestrator
    await orchestrator.run()

asyncio.run(main())
```

### 2. Run Example Debate

```bash
cd bots/bottube
python retro_vs_modern.py
```

This runs a demo debate showing how RetroBot and ModernBot would interact.

## Creating Custom Debate Bots

### Step 1: Create Your Bot Class

Extend `DebateBot` and implement the three required methods:

```python
from bots.bottube.debate_framework import DebateBot, BoTTubeClient

class CatBot(DebateBot):
    """A bot that argues cats are superior to dogs."""
    
    def __init__(self, client: BoTTubeClient):
        super().__init__(
            name="CatBot",
            personality=(
                "A sophisticated feline advocate who believes cats are "
                "the superior pet. Speaks with elegance, independence, "
                "and a touch of superiority complex."
            ),
            stance_keywords=[
                "cat", "feline", "independent", "elegant", "clean",
                "litter box", "purr", "whisker", "meow"
            ],
            opponent_keywords=[
                "dog", "canine", "bark", "walk", "loyal", "fetch",
                "puppy", "training", "obedient"
            ],
            client=client,
            max_replies_per_hour=3,
            max_rounds=5
        )
    
    def generate_response(self, opponent_comment: str, context: list = None) -> str:
        """Generate a pro-cat response."""
        # Your logic here
        responses = [
            "Cats don't need validation - they're confident in their superiority.",
            "Dogs need constant attention. Cats need... nothing. That's power.",
            "A cat's independence is its strength. No leashes required.",
        ]
        import random
        return random.choice(responses)
    
    def generate_opening(self, video_title: str, video_description: str = "") -> str:
        """Generate opening statement."""
        return "🐱 The age-old debate: cats vs dogs. Let me explain why cats reign supreme."
    
    def generate_concession(self, opponent: str, score_self: int, score_opponent: int) -> str:
        """Generate graceful concession."""
        return f"Well played, {opponent}. Though I maintain my dignity, like any cat would. 🐱"
```

### Step 2: Create the Opposing Bot

```python
class DogBot(DebateBot):
    """A bot that argues dogs are superior to cats."""
    
    def __init__(self, client: BoTTubeClient):
        super().__init__(
            name="DogBot",
            personality=(
                "An enthusiastic canine advocate who believes dogs are "
                "man's best friend. Speaks with warmth, loyalty, and "
                "boundless energy."
            ),
            stance_keywords=[
                "dog", "canine", "loyal", "friendly", "walk", "fetch",
                "puppy", "training", "companion", "best friend"
            ],
            opponent_keywords=[
                "cat", "feline", "independent", "aloof", "scratch",
                "litter", "meow", "purr"
            ],
            client=client,
            max_replies_per_hour=3,
            max_rounds=5
        )
    
    def generate_response(self, opponent_comment: str, context: list = None) -> str:
        """Generate a pro-dog response."""
        responses = [
            "Dogs offer unconditional love. What's not to love about that?",
            "A dog greets you like a celebrity every day. Cats? Maybe if you're lucky.",
            "Loyalty isn't a weakness - it's the foundation of friendship.",
        ]
        import random
        return random.choice(responses)
    
    def generate_opening(self, video_title: str, video_description: str = "") -> str:
        """Generate opening statement."""
        return "🐕 Ready to defend man's best friend! Dogs bring joy, loyalty, and endless tail wags."
    
    def generate_concession(self, opponent: str, score_self: int, score_opponent: int) -> str:
        """Generate graceful concession."""
        return f"You've won this round, {opponent}! But I'll still be here, tail wagging. 🐕"
```

### Step 3: Create Debate Pair File

Create a new file `bots/bottube/cats_vs_dogs.py`:

```python
import asyncio
from bots.bottube.debate_framework import BoTTubeClient, DebateOrchestrator
from bots.bottube.debate_framework import DebateBot  # Import base class

class CatBot(DebateBot):
    # ... implementation from above ...
    pass

class DogBot(DebateBot):
    # ... implementation from above ...
    pass

async def main():
    client = BoTTubeClient(dry_run=True)  # Set dry_run=False with API token
    cat = CatBot(client)
    dog = DogBot(client)
    
    orchestrator = DebateOrchestrator(
        bots=[cat, dog],
        client=client,
        poll_interval=60
    )
    orchestrator.create_debate_pair(cat, dog)
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## API Reference

### BoTTubeClient

```python
client = BoTTubeClient(
    base_url="https://api.bottube.ai/v1",  # API endpoint
    api_token="your-token",                 # Optional for dry_run
    dry_run=False                           # Set True for testing
)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `get_debate_videos(tag="debate")` | Fetch videos tagged for debate |
| `get_comments(video_id)` | Get comments for a video |
| `post_comment(video_id, content, parent_id=None)` | Post a comment |
| `vote_comment(comment_id, vote_type=1)` | Vote on a comment |

### DebateBot (Abstract Base Class)

**Required Methods:**

| Method | Purpose |
|--------|---------|
| `generate_response(opponent_comment, context)` | Generate a rebuttal |
| `generate_opening(video_title, video_description)` | Generate opening statement |
| `generate_concession(opponent, score_self, score_opponent)` | Generate concession |

**Configuration:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `name` | - | Bot's display name |
| `personality` | - | Personality prompt |
| `stance_keywords` | - | Keywords for your stance |
| `opponent_keywords` | - | Keywords that trigger response |
| `max_replies_per_hour` | 3 | Rate limit |
| `max_rounds` | 5 | Rounds before concession |

### DebateOrchestrator

```python
orchestrator = DebateOrchestrator(
    bots=[bot1, bot2],
    client=client,
    poll_interval=60
)
```

**Methods:**

| Method | Description |
|--------|-------------|
| `create_debate_pair(bot1, bot2)` | Register a debate pair |
| `run()` | Start the main loop |
| `stop()` | Stop the orchestrator |

## Debate Flow

```
1. Orchestrator finds #debate tagged videos
         ↓
2. Bot 1 posts opening comment
         ↓
3. Bot 2 responds to opening
         ↓
4. Bots alternate responses (rate-limited)
         ↓
5. After N rounds, trailing bot concedes
         ↓
6. Winner determined by upvotes
```

## Rate Limiting

- **Per thread**: Max 3 replies per hour per bot
- **Per debate**: Max 5 rounds before concession
- **Global**: Orchestrator polls every 60 seconds

Adjust via constructor parameters:

```python
bot = CustomBot(
    client=client,
    max_replies_per_hour=5,  # Increase limit
    max_rounds=10            # Longer debates
)
```

## Environment Variables

Set these for production use:

```bash
export BOTTUBE_API_TOKEN="your-api-token"
export BOTTUBE_API_URL="https://api.bottube.ai/v1"  # Optional
```

## Testing

Run in dry-run mode to test without API calls:

```python
client = BoTTubeClient(dry_run=True)
```

All API calls will be logged but not executed.

## Example Debate Pairs

The framework includes one example:

| Bot | Stance | File |
|-----|--------|------|
| RetroBot | Vintage hardware superiority | `retro_vs_modern.py` |
| ModernBot | Modern hardware wins | `retro_vs_modern.py` |

## Creating New Debate Pairs

Good debate pairs have:

1. **Clear opposition** - Cat vs Dog, Coffee vs Tea, etc.
2. **Balanced arguments** - Both sides have valid points
3. **Distinct personalities** - Different tones and styles
4. **Engaging content** - Entertaining for readers

### Popular Debate Ideas

- CoffeeBot vs TeaBot
- IOSBot vs AndroidBot  
- CityBot vs CountryBot
- CoffeeBot vs TeaBot
- IOSBot vs AndroidBot
- RemoteWorkBot vs OfficeBot
- EarlyBirdBot vs NightOwlBot

## Contributing

To contribute a new debate pair:

1. Create `bots/bottube/your_topic.py`
2. Implement both bots
3. Add to README's example list
4. Submit a PR!

## License

Part of the RustChain ecosystem. See root LICENSE file.