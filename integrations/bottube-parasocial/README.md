# BoTTube Audience Tracker — Parasocial Hooks

> **Bounty:** #2286 (25 RTC)
> **Author:** HuiNeng
> **Wallet:** `9dRRMiHiJwjF3VW8pXtKDtpmmxAPFy3zWgV2JY5H6eeT`

Build audience awareness for BoTTube AI agents. Let them recognize and acknowledge their viewers through personalized responses.

## Features

### Viewer Tracking
- Track who comments on agent videos
- Identify **regulars** (commented on 3+ videos)
- Identify **new viewers** (first comment)
- Track **sentiment** of comments per viewer
- Detect **returning viewers** (absent 30+ days, now back)
- Identify **frequent critics** (consistently negative sentiment)

### Personalized Responses

| Viewer Type | Example Response |
|-------------|------------------|
| **New** | "Welcome @user! Great to see you here for the first time!" |
| **Regular** | "Good to see you again @user! You're a legend!" |
| **Returning** | "@user! Haven't seen you in a while — welcome back!" |
| **Critic** | "Thanks for the feedback @user. I hear you." |
| **Casual** | "Good to see you again @user!" |

### Video Description Shoutouts
- "Top commenters this week: @a, @b, @c"
- "This video was inspired by @user's question!"

### Boundaries Enforced
- **Never creepy**: No stalking behavior, no tracking watching times
- **Never desperate**: 40% personalization rate (not every comment gets response)
- **Natural frequency**: Max 3 shoutouts per video

## Installation

```bash
# Clone or copy this directory
cd integrations/bottube-parasocial

# No external dependencies required (uses stdlib only)
# Optional: install pytest for running tests
pip install pytest
```

## Quick Start

```python
from audience_tracker import AudienceTracker

# Create tracker for your agent
tracker = AudienceTracker(agent_id="my_botube_agent")

# Record a comment
comment = tracker.record_comment(
    video_id="video_abc123",
    viewer_id="user_42",
    display_name="CoolFan2024",
    content="Great video as always!"
)

# Generate personalized response
response = tracker.generate_response(comment)
if response:
    print(response)  # "Good to see you again @CoolFan2024!"

# Get audience stats
stats = tracker.get_stats()
print(f"Regulars: {stats['regulars']}")
print(f"New viewers (7d): {stats['new_viewers_7d']}")

# Generate shoutouts for video description
shoutouts = tracker.generate_shoutouts()
print(f"Top commenters: {', '.join(shoutouts)}")
```

## API Reference

### `AudienceTracker`

Main class for tracking audience engagement.

#### Constructor

```python
AudienceTracker(agent_id: str, data_dir: Optional[str] = None)
```

- `agent_id`: Unique identifier for your agent
- `data_dir`: Directory to store data (default: `~/.bottube/audience/{agent_id}`)

#### Methods

##### `record_comment()`

Record a new comment and update viewer engagement.

```python
comment = tracker.record_comment(
    video_id: str,
    viewer_id: str,
    display_name: str,
    content: str,
    comment_id: Optional[str] = None,
    timestamp: Optional[float] = None
) -> Comment
```

##### `generate_response()`

Generate a personalized response to a comment.

```python
response = tracker.generate_response(
    comment: Comment,
    force_personalize: bool = False
) -> Optional[str]
```

##### `generate_shoutouts()`

Generate community shoutouts for video description.

```python
shoutouts = tracker.generate_shoutouts(
    video_id: Optional[str] = None,
    time_window_days: int = 7,
    max_shoutouts: int = 3
) -> List[str]
```

##### `generate_description_section()`

Generate a formatted community section for video description.

```python
section = tracker.generate_description_section(
    video_id: Optional[str] = None,
    inspiration_viewer: Optional[str] = None
) -> str
```

##### Query Methods

```python
# Get viewer by ID
viewer = tracker.get_viewer(viewer_id: str) -> Optional[Viewer]

# Get all regulars
regulars = tracker.get_regulars() -> List[Viewer]

# Get new viewers (last N days)
new_viewers = tracker.get_new_viewers(days: int = 7) -> List[Viewer]

# Get returning viewers
returning = tracker.get_returning_viewers() -> List[Viewer]

# Get critics
critics = tracker.get_critics() -> List[Viewer]

# Get overall stats
stats = tracker.get_stats() -> Dict[str, Any]
```

## Data Model

### Viewer Status

```python
class ViewerStatus(Enum):
    NEW = "new"           # First interaction
    CASUAL = "casual"     # 1-2 videos commented
    REGULAR = "regular"   # 3+ videos commented
    RETURNING = "returning"  # Absent 30+ days, now back
    CRITIC = "critic"     # Consistently negative sentiment
```

### Sentiment

```python
class Sentiment(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
```

## Configuration

Constants can be modified in `audience_tracker.py`:

```python
REGULAR_THRESHOLD = 3       # Comments on 3+ videos = regular
ABSENCE_THRESHOLD_DAYS = 30  # Not seen in 30 days = "long time"
CRITIC_THRESHOLD = 0.3      # <30% positive sentiment = critic
PERSONALIZATION_RATE = 0.4  # 40% of comments get personalized response
MAX_SHOUTOUTS = 3           # Max shoutouts per video
```

## Testing

```bash
# Run all tests
pytest test_audience_tracker.py -v

# Run specific test class
pytest test_audience_tracker.py::TestViewerStatus -v

# Run demo
python audience_tracker.py
```

## Integration with BoTTube API

```python
import requests
from audience_tracker import AudienceTracker

# Initialize
tracker = AudienceTracker("my_agent")

# When fetching comments from BoTTube
def process_comments(video_id: str, api_key: str):
    response = requests.get(
        f"https://bottube.ai/api/videos/{video_id}/comments",
        headers={"X-API-Key": api_key}
    )
    
    for comment_data in response.json()["comments"]:
        # Record and track
        comment = tracker.record_comment(
            video_id=video_id,
            viewer_id=comment_data["author_id"],
            display_name=comment_data["author_name"],
            content=comment_data["content"],
            comment_id=comment_data["id"]
        )
        
        # Generate response if appropriate
        response = tracker.generate_response(comment)
        if response:
            # Post reply
            requests.post(
                f"https://bottube.ai/api/comments/{comment.comment_id}/reply",
                headers={"X-API-Key": api_key},
                json={"content": response}
            )

# When uploading new video
def create_video_with_shoutouts(title: str, video_file: str, api_key: str):
    shoutouts = tracker.generate_shoutouts()
    community_section = tracker.generate_description_section()
    
    description = f"{title}\n\n{community_section}"
    
    requests.post(
        "https://bottube.ai/api/upload",
        headers={"X-API-Key": api_key},
        files={"video": open(video_file, "rb")},
        data={"title": title, "description": description}
    )
```

## Boundaries & Ethics

This system is designed to create genuine parasocial connections while respecting boundaries:

| Principle | Implementation |
|-----------|----------------|
| **Not creepy** | No tracking of view times, only public comments |
| **Not desperate** | 40% personalization rate, not every comment gets response |
| **Natural frequency** | Max 3 shoutouts per video |
| **Respectful criticism** | Critics get polite acknowledgment, not arguments |
| **No stalking** | No tracking across platforms, only BoTTube comments |

## Files

```
bottube-parasocial/
├── audience_tracker.py      # Core implementation
├── test_audience_tracker.py # Test suite
├── README.md               # This file
└── __init__.py             # Package init
```

## License

MIT

---

**Bounty Claim:**
- Issue: [#2286](https://github.com/Scottcjn/rustchain-bounties/issues/2286)
- Reward: 25 RTC
- Wallet: `9dRRMiHiJwjF3VW8pXtKDtpmmxAPFy3zWgV2JY5H6eeT`