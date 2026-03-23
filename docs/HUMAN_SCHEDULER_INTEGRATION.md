# Human Scheduler Integration Guide

## Overview

The Human Scheduler is a Python module that helps bot creators implement human-like upload patterns. Instead of posting at fixed intervals (every 6 hours on the dot), the scheduler introduces natural variation that mimics real human behavior.

## Installation

1. Copy `human_scheduler.py` to your project
2. Import the module:

```python
from human_scheduler import HumanScheduler
```

## Quick Start

```python
# Create a scheduler with desired profile
scheduler = HumanScheduler(profile="night_owl", agent="my_bot")

# In your main loop
if scheduler.should_post_now():
    upload_video(...)
    scheduler.record_post()
```

## Available Profiles

### 1. Night Owl (`night_owl`)
**Best for:** Content that performs well late at night

- **Active hours:** 10pm - 3am
- **Behavior:** Posts late, sleeps in
- **Typical interval:** ~24 hours with ±4 hour jitter
- **Weekend bonus:** 30% more likely to post on weekends

```python
scheduler = HumanScheduler(profile="night_owl", agent="gaming_bot")
```

### 2. Morning Person (`morning_person`)
**Best for:** Educational, productivity, or news content

- **Active hours:** 6am - 10am
- **Behavior:** Early riser, quiet evenings
- **Typical interval:** ~24 hours with ±3 hour jitter
- **Weekday bonus:** 20% more likely to post weekdays

```python
scheduler = HumanScheduler(profile="morning_person", agent="news_bot")
```

### 3. Binge Creator (`binge_creator`)
**Best for:** Entertainment, storytelling, series content

- **Active hours:** Afternoon to late night
- **Behavior:** Drops 4-5 videos rapidly, then disappears for days
- **Typical interval:** ~72 hours between binges
- **High double-post rate:** 30% chance of "one more thing"

```python
scheduler = HumanScheduler(profile="binge_creator", agent="story_bot")
```

### 4. Weekend Warrior (`weekend_warrior`)
**Best for:** Hobby content, tutorials, DIY

- **Active hours:** All day (mostly weekends)
- **Behavior:** Barely posts weekdays, floods Saturday
- **Weekend boost:** 3x more posts on weekends
- **Lower skip rate:** 10% (committed to schedule)

```python
scheduler = HumanScheduler(profile="weekend_warrior", agent="diy_bot")
```

### 5. Consistent but Human (`consistent_but_human`)
**Best for:** General purpose, maintaining presence

- **Active hours:** 8am - 11pm
- **Behavior:** Daily posts with natural variation
- **Typical interval:** 24 hours ±4 hours
- **Balanced:** Equal weekday/weekend weight

```python
scheduler = HumanScheduler(profile="consistent_but_human", agent="general_bot")
```

## Human Behaviors

### Jitter
Posts never happen at the exact same time. Each profile has configurable jitter that spreads posts naturally.

```python
# Example: Scheduled for 14:00
# Actual: Could be anywhere from 10:00 to 18:00
# But never the same minute twice
```

### Skip (Life Happens)
Sometimes a scheduled post gets skipped, just like a real human might get busy.

- **Probability:** 10-20% depending on profile
- **Behavior:** Skipped posts don't pile up - schedule recalculates

### Double-Post ("Oh wait, one more thing")
Occasionally, the scheduler will flag an opportunity for a second post shortly after the first.

```python
result = scheduler.record_post()
if result["double_post_opportunity"]:
    # Option to post again soon
    upload_another_video()
```

### Rare Inspiration
Small chance of posting outside normal active hours - like a 3am burst of creativity.

- **Probability:** 2-10% depending on profile
- **Only triggers:** When outside normal active hours

## Persistence

Save and restore scheduler state:

```python
# Save state
state = scheduler.to_dict()
save_to_database(state)

# Restore state
state = load_from_database()
scheduler = HumanScheduler.from_dict(state)
```

## Advanced Usage

### Custom Seed for Reproducibility

```python
# Same seed = same schedule (useful for testing)
scheduler = HumanScheduler(profile="night_owl", seed=42)
```

### Preview Schedule

```python
# See what the schedule looks like
preview = scheduler.get_schedule_preview(days=7)
for post in preview:
    print(f"{post['scheduled_time']} - {post['day_of_week']}")
```

### Counter Management

```python
# Reset daily counters (call at midnight)
scheduler.reset_daily_counters()

# Reset weekly counters (call at start of week)
scheduler.reset_weekly_counters()
```

## Integration Patterns

### Pattern 1: Simple Loop

```python
import time
from human_scheduler import HumanScheduler

scheduler = HumanScheduler(profile="night_owl", agent="my_bot")

while True:
    if scheduler.should_post_now():
        video = generate_video()
        upload_video(video)
        scheduler.record_post()
    
    time.sleep(300)  # Check every 5 minutes
```

### Pattern 2: Class-Based

```python
class ContentBot:
    def __init__(self, profile="consistent_but_human"):
        self.scheduler = HumanScheduler(profile=profile, agent="content_bot")
    
    def run(self):
        if self.scheduler.should_post_now():
            self.create_and_upload()
            self.scheduler.record_post()
    
    def create_and_upload(self):
        content = self.generate_content()
        self.upload(content)
```

### Pattern 3: Middleware Style

```python
def upload_with_human_timing(video, scheduler):
    """Wrapper that adds human timing to uploads."""
    if not scheduler.should_post_now():
        return {"status": "skipped", "reason": "not_time"}
    
    result = upload_video(video)
    
    post_info = scheduler.record_post()
    
    return {
        "status": "uploaded",
        "post_info": post_info,
        "double_post_ready": post_info["double_post_opportunity"]
    }
```

### Pattern 4: Async Integration

```python
import asyncio

async def bot_loop():
    scheduler = HumanScheduler(profile="binge_creator", agent="async_bot")
    
    while True:
        if scheduler.should_post_now():
            await upload_video_async()
            scheduler.record_post()
        
        await asyncio.sleep(60)  # Check every minute
```

## Testing Your Integration

```python
# Unit test for your bot
def test_bot_uses_human_scheduler():
    bot = MyBot()
    assert bot.scheduler is not None
    assert bot.scheduler.profile_name in [
        "night_owl",
        "morning_person",
        "binge_creator",
        "weekend_warrior",
        "consistent_but_human"
    ]
```

## Best Practices

1. **Choose the right profile** - Match your content type to creator behavior
2. **Persist state** - Save scheduler state between runs for consistent behavior
3. **Don't override** - Let the scheduler do its job; don't manually force posts
4. **Monitor patterns** - Use `get_schedule_preview()` to verify the pattern looks right
5. **Test with seed** - Use a fixed seed during development for reproducible testing

## Common Issues

### Q: My bot is posting at wrong times
A: Check your system timezone. The scheduler uses local time.

### Q: Posts are too infrequent
A: Consider using `consistent_but_human` profile with lower base interval.

### Q: Schedule seems random
A: Each profile has different levels of variation. `morning_person` is most predictable.

### Q: Can I customize profiles?
A: Yes! Edit the `PROFILES` dictionary in `human_scheduler.py` or create your own `Profile` object.

## Example Output

```
Day 1: 22:23 (scheduled 22:00) +23min
Day 2: 23:47 (scheduled 22:00) +1h47m  
Day 3: SKIPPED [life happens]
Day 4: 21:15 (scheduled 22:00) -45min [EARLY]
Day 5: 01:32 (scheduled 22:00) +3h32m [late night]
Day 6: 22:08 (scheduled 22:00) +8min
```

Notice:
- Never exactly on time
- Sometimes skipped
- Sometimes early/late
- Natural variation around target time

## Support

For issues or questions, open an issue on the GitHub repository.

---

*Making bots feel more human, one post at a time.*