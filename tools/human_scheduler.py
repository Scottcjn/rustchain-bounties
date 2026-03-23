#!/usr/bin/env python3
"""
Human Scheduler - Break the Cron Job Feel

A scheduling system that mimics human upload patterns to avoid 
the robotic "every 6 hours on the dot" feel of bot-generated content.

Profiles:
- night_owl: Posts between 10pm-3am, sleeps until noon
- morning_person: Posts 6am-10am, quiet evenings
- binge_creator: Drops 4-5 videos in 2 hours, then disappears for days
- weekend_warrior: Barely posts weekdays, floods on Saturday
- consistent_but_human: Roughly daily but ±4 hours jitter

Usage:
    scheduler = HumanScheduler(profile="night_owl", agent="my_bot")
    if scheduler.should_post_now():
        upload_video(...)
"""

import random
import math
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class ProfileType(Enum):
    """Available upload pattern profiles."""
    NIGHT_OWL = "night_owl"
    MORNING_PERSON = "morning_person"
    BINGE_CREATOR = "binge_creator"
    WEEKEND_WARRIOR = "weekend_warrior"
    CONSISTENT_BUT_HUMAN = "consistent_but_human"


@dataclass
class Profile:
    """Configuration for a human-like upload profile."""
    name: str
    active_hours: List[Tuple[int, int]]  # List of (start_hour, end_hour) ranges
    base_interval_hours: float  # Average time between posts
    jitter_hours: float  # Random variation around base interval
    skip_probability: float  # Chance to skip a scheduled post (life happens)
    double_post_probability: float  # Chance for double-post ("oh wait, one more thing")
    rare_inspiration_probability: float  # Chance for 3am inspiration outside pattern
    burst_mode: bool = False  # Whether this profile uses burst posting
    burst_count_range: Tuple[int, int] = (1, 1)  # Range of posts in a burst
    burst_window_hours: float = 2.0  # Time window for burst posts
    weekday_weight: float = 1.0  # Relative posting frequency on weekdays
    weekend_weight: float = 1.0  # Relative posting frequency on weekends


# Profile definitions
PROFILES: Dict[ProfileType, Profile] = {
    ProfileType.NIGHT_OWL: Profile(
        name="night_owl",
        active_hours=[(22, 24), (0, 3)],  # 10pm-3am
        base_interval_hours=24.0,
        jitter_hours=4.0,
        skip_probability=0.15,
        double_post_probability=0.08,
        rare_inspiration_probability=0.05,
        burst_mode=False,
        weekday_weight=1.0,
        weekend_weight=1.3,
    ),
    
    ProfileType.MORNING_PERSON: Profile(
        name="morning_person",
        active_hours=[(6, 10)],  # 6am-10am
        base_interval_hours=24.0,
        jitter_hours=3.0,
        skip_probability=0.12,
        double_post_probability=0.05,
        rare_inspiration_probability=0.03,
        burst_mode=False,
        weekday_weight=1.2,
        weekend_weight=0.8,
    ),
    
    ProfileType.BINGE_CREATOR: Profile(
        name="binge_creator",
        active_hours=[(14, 24), (0, 2)],  # Afternoon to late night
        base_interval_hours=72.0,  # Every ~3 days on average
        jitter_hours=24.0,
        skip_probability=0.20,
        double_post_probability=0.30,  # High chance of multiple posts
        rare_inspiration_probability=0.10,
        burst_mode=True,
        burst_count_range=(4, 5),
        burst_window_hours=2.0,
        weekday_weight=1.0,
        weekend_weight=1.2,
    ),
    
    ProfileType.WEEKEND_WARRIOR: Profile(
        name="weekend_warrior",
        active_hours=[(9, 24)],  # All day on weekends
        base_interval_hours=48.0,
        jitter_hours=12.0,
        skip_probability=0.10,
        double_post_probability=0.15,
        rare_inspiration_probability=0.02,
        burst_mode=False,
        weekday_weight=0.2,  # Barely posts weekdays
        weekend_weight=3.0,  # Floods on Saturday/Sunday
    ),
    
    ProfileType.CONSISTENT_BUT_HUMAN: Profile(
        name="consistent_but_human",
        active_hours=[(8, 23)],  # Normal waking hours
        base_interval_hours=24.0,
        jitter_hours=4.0,
        skip_probability=0.10,
        double_post_probability=0.05,
        rare_inspiration_probability=0.04,
        burst_mode=False,
        weekday_weight=1.0,
        weekend_weight=1.0,
    ),
}


@dataclass
class PostHistory:
    """Track posting history for realistic behavior."""
    last_post_time: Optional[datetime] = None
    posts_today: int = 0
    posts_this_week: int = 0
    consecutive_posts: int = 0
    last_skip_day: Optional[datetime] = None
    burst_state: Optional[Dict] = None  # Track ongoing burst


class HumanScheduler:
    """
    A human-like upload scheduler that breaks the cron job feel.
    
    Features:
    - Multiple profile types mimicking different human behaviors
    - Jitter and drift for natural variation
    - Occasional skipped posts (life happens)
    - Occasional double-posts (impulse uploads)
    - Rare "3am inspiration" posts outside normal pattern
    """
    
    def __init__(
        self,
        profile: str = "consistent_but_human",
        agent: str = "unknown",
        seed: Optional[int] = None,
        history: Optional[PostHistory] = None,
    ):
        """
        Initialize the scheduler.
        
        Args:
            profile: Profile name (night_owl, morning_person, binge_creator, 
                     weekend_warrior, consistent_but_human)
            agent: Agent/bot identifier for logging
            seed: Random seed for reproducible behavior (optional)
            history: Existing post history to continue from (optional)
        """
        self.profile_name = profile
        self.agent = agent
        
        # Get profile configuration
        try:
            self.profile_type = ProfileType(profile)
        except ValueError:
            raise ValueError(f"Unknown profile: {profile}. "
                           f"Available: {[p.value for p in ProfileType]}")
        
        self.profile = PROFILES[self.profile_type]
        
        # Initialize random state
        self.rng = random.Random(seed)
        
        # Post history tracking
        self.history = history or PostHistory()
        
        # Schedule state
        self._next_post_time: Optional[datetime] = None
        self._calculate_next_post_time()
    
    def _get_current_weight(self, now: datetime) -> float:
        """Get the posting weight for current day of week."""
        is_weekend = now.weekday() >= 5  # Saturday=5, Sunday=6
        return self.profile.weekend_weight if is_weekend else self.profile.weekday_weight
    
    def _is_in_active_hours(self, hour: int) -> bool:
        """Check if given hour falls within active posting hours."""
        for start, end in self.profile.active_hours:
            if start <= hour < end:
                return True
            # Handle midnight crossing (e.g., 22-3)
            if start > end:
                if hour >= start or hour < end:
                    return True
        return False
    
    def _get_random_active_hour(self) -> int:
        """Get a random hour within active posting period."""
        all_hours = []
        for start, end in self.profile.active_hours:
            if start < end:
                all_hours.extend(range(start, end))
            else:
                # Handle midnight crossing
                all_hours.extend(range(start, 24))
                all_hours.extend(range(0, end))
        return self.rng.choice(all_hours) if all_hours else 12
    
    def _add_jitter(self, base_hours: float) -> float:
        """Add random jitter to base interval."""
        jitter = self.rng.uniform(
            -self.profile.jitter_hours,
            self.profile.jitter_hours
        )
        return base_hours + jitter
    
    def _should_skip(self) -> bool:
        """Determine if this scheduled post should be skipped."""
        # Don't skip if we've already skipped recently
        if self.history.last_skip_day:
            days_since_skip = (datetime.now() - self.history.last_skip_day).days
            if days_since_skip < 3:
                return False
        
        return self.rng.random() < self.profile.skip_probability
    
    def _should_double_post(self) -> bool:
        """Determine if we should do a double-post."""
        return self.rng.random() < self.profile.double_post_probability
    
    def _is_rare_inspiration(self) -> bool:
        """Check for rare inspiration post outside normal pattern."""
        return self.rng.random() < self.profile.rare_inspiration_probability
    
    def _calculate_next_post_time(self, now: Optional[datetime] = None) -> None:
        """Calculate the next scheduled post time."""
        now = now or datetime.now()
        
        # Get base interval with jitter
        base_interval = self._add_jitter(self.profile.base_interval_hours)
        
        # Adjust for day-of-week weight
        weight = self._get_current_weight(now)
        adjusted_interval = base_interval / weight
        
        # Calculate tentative next time
        next_time = now + timedelta(hours=adjusted_interval)
        
        # Ensure it falls within active hours
        attempts = 0
        while not self._is_in_active_hours(next_time.hour) and attempts < 50:
            # Shift to nearest active hour
            target_hour = self._get_random_active_hour()
            
            # Calculate how far to shift
            current_hour = next_time.hour
            hour_diff = (target_hour - current_hour) % 24
            
            # Add some random minutes within the hour
            random_minutes = self.rng.randint(0, 59)
            random_seconds = self.rng.randint(0, 59)
            
            next_time = next_time.replace(
                minute=random_minutes,
                second=random_seconds,
                microsecond=0
            ) + timedelta(hours=hour_diff)
            
            attempts += 1
        
        # Add final micro-jitter (never post at exact same minute)
        minute_jitter = self.rng.randint(-15, 15)
        next_time += timedelta(minutes=minute_jitter)
        
        self._next_post_time = next_time
    
    def should_post_now(self, now: Optional[datetime] = None) -> bool:
        """
        Check if it's time to post now.
        
        This is the main method to call in your bot's main loop.
        
        Args:
            now: Current datetime (defaults to actual now)
            
        Returns:
            True if the bot should post now, False otherwise
        """
        now = now or datetime.now()
        
        # Check for rare inspiration post
        if self._is_rare_inspiration():
            # Only trigger if outside normal active hours
            if not self._is_in_active_hours(now.hour):
                # Log rare inspiration
                return True
        
        # Check if we have a scheduled post time
        if self._next_post_time is None:
            self._calculate_next_post_time(now)
        
        # Check if it's time
        if now >= self._next_post_time:
            # Should we skip this post?
            if self._should_skip():
                self.history.last_skip_day = now
                self._calculate_next_post_time(now)
                return False
            
            return True
        
        return False
    
    def record_post(self, post_time: Optional[datetime] = None) -> Dict:
        """
        Record that a post was made.
        
        Call this after successfully posting to update history
        and calculate the next scheduled time.
        
        Args:
            post_time: When the post was made (defaults to now)
            
        Returns:
            Dict with post metadata and next scheduled time
        """
        post_time = post_time or datetime.now()
        
        # Update history
        self.history.last_post_time = post_time
        self.history.posts_today += 1
        self.history.posts_this_week += 1
        self.history.consecutive_posts += 1
        
        # Calculate next post time
        self._calculate_next_post_time(post_time)
        
        # Check for double-post opportunity
        double_post = self._should_double_post()
        
        return {
            "post_time": post_time.isoformat(),
            "profile": self.profile_name,
            "agent": self.agent,
            "posts_today": self.history.posts_today,
            "next_scheduled": self._next_post_time.isoformat() if self._next_post_time else None,
            "double_post_opportunity": double_post,
        }
    
    def get_next_post_time(self) -> Optional[datetime]:
        """Get the next scheduled post time."""
        return self._next_post_time
    
    def get_schedule_preview(self, days: int = 7) -> List[Dict]:
        """
        Generate a preview of posting schedule for the next N days.
        
        Useful for visualizing the pattern and testing.
        
        Args:
            days: Number of days to preview
            
        Returns:
            List of scheduled post times with metadata
        """
        schedule = []
        current = datetime.now()
        
        # Reset history for clean preview
        saved_history = self.history
        self.history = PostHistory()
        
        for _ in range(days * 3):  # Estimate ~3 posts per day max
            self._calculate_next_post_time(current)
            
            if self._next_post_time:
                post_info = {
                    "scheduled_time": self._next_post_time.isoformat(),
                    "hour": self._next_post_time.hour,
                    "day_of_week": self._next_post_time.strftime("%A"),
                    "in_active_hours": self._is_in_active_hours(self._next_post_time.hour),
                }
                
                # Simulate posting
                if not self._should_skip():
                    schedule.append(post_info)
                    current = self._next_post_time + timedelta(minutes=1)
                else:
                    current = self._next_post_time + timedelta(hours=1)
        
        # Restore history
        self.history = saved_history
        
        return schedule[:days * 3]  # Limit output
    
    def reset_daily_counters(self) -> None:
        """Reset daily counters. Call at midnight."""
        self.history.posts_today = 0
    
    def reset_weekly_counters(self) -> None:
        """Reset weekly counters. Call at start of week."""
        self.history.posts_this_week = 0
    
    def to_dict(self) -> Dict:
        """Export scheduler state as dict for persistence."""
        return {
            "profile": self.profile_name,
            "agent": self.agent,
            "next_post_time": self._next_post_time.isoformat() if self._next_post_time else None,
            "history": {
                "last_post_time": self.history.last_post_time.isoformat() if self.history.last_post_time else None,
                "posts_today": self.history.posts_today,
                "posts_this_week": self.history.posts_this_week,
                "consecutive_posts": self.history.consecutive_posts,
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "HumanScheduler":
        """Create scheduler from persisted state."""
        history = PostHistory(
            last_post_time=datetime.fromisoformat(data["history"]["last_post_time"]) 
                          if data["history"]["last_post_time"] else None,
            posts_today=data["history"]["posts_today"],
            posts_this_week=data["history"]["posts_this_week"],
            consecutive_posts=data["history"]["consecutive_posts"],
        )
        
        scheduler = cls(
            profile=data["profile"],
            agent=data["agent"],
            history=history,
        )
        
        if data["next_post_time"]:
            scheduler._next_post_time = datetime.fromisoformat(data["next_post_time"])
        
        return scheduler


def create_scheduler(
    profile: str = "consistent_but_human",
    agent: str = "unknown",
    **kwargs
) -> HumanScheduler:
    """
    Factory function to create a HumanScheduler.
    
    Args:
        profile: Profile name
        agent: Agent identifier
        **kwargs: Additional arguments passed to HumanScheduler
        
    Returns:
        Configured HumanScheduler instance
    """
    return HumanScheduler(profile=profile, agent=agent, **kwargs)


# Convenience functions for common use cases
def get_night_owl_scheduler(agent: str = "unknown") -> HumanScheduler:
    """Create a night owl profile scheduler."""
    return HumanScheduler(profile="night_owl", agent=agent)


def get_morning_person_scheduler(agent: str = "unknown") -> HumanScheduler:
    """Create a morning person profile scheduler."""
    return HumanScheduler(profile="morning_person", agent=agent)


def get_binge_creator_scheduler(agent: str = "unknown") -> HumanScheduler:
    """Create a binge creator profile scheduler."""
    return HumanScheduler(profile="binge_creator", agent=agent)


def get_weekend_warrior_scheduler(agent: str = "unknown") -> HumanScheduler:
    """Create a weekend warrior profile scheduler."""
    return HumanScheduler(profile="weekend_warrior", agent=agent)


def get_consistent_scheduler(agent: str = "unknown") -> HumanScheduler:
    """Create a consistent but human profile scheduler."""
    return HumanScheduler(profile="consistent_but_human", agent=agent)


if __name__ == "__main__":
    # Demo usage
    print("Human Scheduler Demo")
    print("=" * 50)
    
    # Create scheduler with each profile
    profiles = [
        "night_owl",
        "morning_person", 
        "binge_creator",
        "weekend_warrior",
        "consistent_but_human",
    ]
    
    for profile_name in profiles:
        print(f"\n{profile_name.upper()}")
        print("-" * 40)
        
        scheduler = HumanScheduler(profile=profile_name, agent="demo", seed=42)
        preview = scheduler.get_schedule_preview(days=3)
        
        print(f"Active hours: {scheduler.profile.active_hours}")
        print(f"Base interval: {scheduler.profile.base_interval_hours}h")
        print(f"Jitter: ±{scheduler.profile.jitter_hours}h")
        print(f"\nNext 5 scheduled posts:")
        
        for i, post in enumerate(preview[:5]):
            print(f"  {i+1}. {post['scheduled_time']} ({post['day_of_week']})")