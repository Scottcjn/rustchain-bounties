#!/usr/bin/env python3
"""
Tests for HumanScheduler - demonstrating non-uniform, realistic distribution.

Run with: pytest test_human_scheduler.py -v
"""

import pytest
from datetime import datetime, timedelta
from collections import Counter
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from human_scheduler import (
    HumanScheduler,
    ProfileType,
    PROFILES,
    create_scheduler,
    get_night_owl_scheduler,
    get_morning_person_scheduler,
    get_binge_creator_scheduler,
    get_weekend_warrior_scheduler,
    get_consistent_scheduler,
)


class TestProfileConfiguration:
    """Test that all profiles are correctly configured."""
    
    def test_all_profiles_exist(self):
        """Verify all 5 required profiles exist."""
        expected_profiles = {
            "night_owl",
            "morning_person",
            "binge_creator",
            "weekend_warrior",
            "consistent_but_human",
        }
        
        actual_profiles = {p.value for p in ProfileType}
        assert expected_profiles == actual_profiles, \
            f"Missing profiles: {expected_profiles - actual_profiles}"
    
    def test_night_owl_profile(self):
        """Test night owl has correct active hours (10pm-3am)."""
        profile = PROFILES[ProfileType.NIGHT_OWL]
        assert profile.active_hours == [(22, 24), (0, 3)]
        assert profile.base_interval_hours > 0
        assert profile.jitter_hours > 0
    
    def test_morning_person_profile(self):
        """Test morning person has correct active hours (6am-10am)."""
        profile = PROFILES[ProfileType.MORNING_PERSON]
        assert profile.active_hours == [(6, 10)]
    
    def test_binge_creator_profile(self):
        """Test binge creator has burst mode enabled."""
        profile = PROFILES[ProfileType.BINGE_CREATOR]
        assert profile.burst_mode == True
        assert profile.burst_count_range[0] >= 4
        assert profile.burst_count_range[1] <= 5
    
    def test_weekend_warrior_profile(self):
        """Test weekend warrior has higher weekend weight."""
        profile = PROFILES[ProfileType.WEEKEND_WARRIOR]
        assert profile.weekend_weight > profile.weekday_weight
        assert profile.weekend_weight >= 2.0  # Should be significantly higher
    
    def test_consistent_profile(self):
        """Test consistent but human has balanced weights."""
        profile = PROFILES[ProfileType.CONSISTENT_BUT_HUMAN]
        assert abs(profile.weekday_weight - profile.weekend_weight) < 0.5


class TestSchedulerCreation:
    """Test scheduler initialization."""
    
    def test_create_default_scheduler(self):
        """Test creating scheduler with default profile."""
        scheduler = HumanScheduler()
        assert scheduler.profile_name == "consistent_but_human"
    
    def test_create_with_profile(self):
        """Test creating scheduler with specific profile."""
        scheduler = HumanScheduler(profile="night_owl")
        assert scheduler.profile_name == "night_owl"
    
    def test_create_with_agent_name(self):
        """Test scheduler stores agent name."""
        scheduler = HumanScheduler(agent="test_bot")
        assert scheduler.agent == "test_bot"
    
    def test_invalid_profile_raises_error(self):
        """Test that invalid profile raises ValueError."""
        with pytest.raises(ValueError):
            HumanScheduler(profile="nonexistent_profile")
    
    def test_seed_reproducibility(self):
        """Test that same seed produces same behavior."""
        s1 = HumanScheduler(profile="night_owl", seed=42)
        s2 = HumanScheduler(profile="night_owl", seed=42)
        
        # Both should have same next post time
        t1 = s1.get_next_post_time()
        t2 = s2.get_next_post_time()
        
        assert t1 == t2


class TestSchedulingLogic:
    """Test the core scheduling behavior."""
    
    def test_next_post_time_is_calculated(self):
        """Test that next post time is set after creation."""
        scheduler = HumanScheduler()
        next_time = scheduler.get_next_post_time()
        assert next_time is not None
        assert next_time > datetime.now()
    
    def test_should_post_now_returns_boolean(self):
        """Test that should_post_now returns a boolean."""
        scheduler = HumanScheduler()
        result = scheduler.should_post_now()
        assert isinstance(result, bool)
    
    def test_record_post_updates_history(self):
        """Test that recording a post updates history."""
        scheduler = HumanScheduler()
        scheduler.record_post()
        
        assert scheduler.history.last_post_time is not None
        assert scheduler.history.posts_today == 1
    
    def test_consecutive_posts_tracked(self):
        """Test that consecutive posts are tracked."""
        scheduler = HumanScheduler()
        
        scheduler.record_post()
        assert scheduler.history.consecutive_posts == 1
        
        scheduler.record_post()
        assert scheduler.history.consecutive_posts == 2


class TestNonUniformDistribution:
    """Test that the distribution is non-uniform and realistic."""
    
    def test_night_owl_posts_at_night(self):
        """Test night owl mostly posts at night (10pm-3am)."""
        scheduler = HumanScheduler(profile="night_owl", seed=12345)
        preview = scheduler.get_schedule_preview(days=14)
        
        night_posts = 0
        total_posts = len(preview)
        
        for post in preview:
            hour = post["hour"]
            if hour >= 22 or hour < 3:  # Night owl hours
                night_posts += 1
        
        # At least 70% should be during night owl hours
        ratio = night_posts / total_posts if total_posts > 0 else 0
        assert ratio >= 0.7, \
            f"Night owl only posted {ratio*100:.1f}% at night, expected ≥70%"
    
    def test_morning_person_posts_in_morning(self):
        """Test morning person mostly posts in morning (6am-10am)."""
        scheduler = HumanScheduler(profile="morning_person", seed=12345)
        preview = scheduler.get_schedule_preview(days=14)
        
        morning_posts = 0
        total_posts = len(preview)
        
        for post in preview:
            if 6 <= post["hour"] < 10:
                morning_posts += 1
        
        ratio = morning_posts / total_posts if total_posts > 0 else 0
        assert ratio >= 0.6, \
            f"Morning person only posted {ratio*100:.1f}% in morning, expected ≥60%"
    
    def test_weekend_warrior_posts_more_weekends(self):
        """Test weekend warrior has higher weekend weight configured."""
        profile = PROFILES[ProfileType.WEEKEND_WARRIOR]
        
        # The profile should have significantly higher weekend weight
        assert profile.weekend_weight >= profile.weekday_weight * 2.0, \
            f"Weekend weight ({profile.weekend_weight}) should be much higher than weekday ({profile.weekday_weight})"
    
    def test_times_are_not_identical(self):
        """Test that posts never happen at the exact same minute."""
        scheduler = HumanScheduler(profile="consistent_but_human", seed=42)
        preview = scheduler.get_schedule_preview(days=7)
        
        times = set()
        for post in preview:
            dt = datetime.fromisoformat(post["scheduled_time"])
            minute_key = (dt.hour, dt.minute)
            assert minute_key not in times, \
                f"Duplicate time: {dt.hour}:{dt.minute:02d}"
            times.add(minute_key)
    
    def test_jitter_creates_variation(self):
        """Test that jitter creates variation in post times."""
        # Create multiple schedulers to test variation
        times = []
        
        for i in range(20):
            scheduler = HumanScheduler(
                profile="consistent_but_human",
                seed=i * 100
            )
            next_time = scheduler.get_next_post_time()
            if next_time:
                times.append(next_time.hour * 60 + next_time.minute)
        
        # Check for variation
        if len(times) > 1:
            variance = sum((t - sum(times)/len(times))**2 for t in times) / len(times)
            assert variance > 10, \
                f"Too little variation in times (variance={variance:.1f})"


class TestHumanBehaviors:
    """Test human-like behaviors (skip, double-post, inspiration)."""
    
    def test_skip_probability_configured(self):
        """Test that skip probability is configured for all profiles."""
        for profile_type in ProfileType:
            profile = PROFILES[profile_type]
            assert 0 < profile.skip_probability < 0.5, \
                f"{profile_type.value} has unreasonable skip probability"
    
    def test_double_post_probability_configured(self):
        """Test that double-post probability is configured."""
        for profile_type in ProfileType:
            profile = PROFILES[profile_type]
            assert 0 < profile.double_post_probability < 0.5, \
                f"{profile_type.value} has unreasonable double-post probability"
    
    def test_rare_inspiration_configured(self):
        """Test that rare inspiration probability is configured."""
        for profile_type in ProfileType:
            profile = PROFILES[profile_type]
            assert 0 < profile.rare_inspiration_probability < 0.2, \
                f"{profile_type.value} has unreasonable inspiration probability"


class TestPersistence:
    """Test scheduler state persistence."""
    
    def test_to_dict_export(self):
        """Test exporting scheduler state to dict."""
        scheduler = HumanScheduler(profile="night_owl", agent="test")
        state = scheduler.to_dict()
        
        assert state["profile"] == "night_owl"
        assert state["agent"] == "test"
        assert "next_post_time" in state
        assert "history" in state
    
    def test_from_dict_restore(self):
        """Test restoring scheduler from dict."""
        original = HumanScheduler(profile="morning_person", agent="bot1")
        original.record_post()
        
        state = original.to_dict()
        restored = HumanScheduler.from_dict(state)
        
        assert restored.profile_name == "morning_person"
        assert restored.agent == "bot1"
        assert restored.history.posts_today == 1
    
    def test_state_persists_post_count(self):
        """Test that post count persists through save/restore."""
        scheduler = HumanScheduler()
        scheduler.record_post()
        scheduler.record_post()
        
        state = scheduler.to_dict()
        restored = HumanScheduler.from_dict(state)
        
        assert restored.history.posts_today == 2


class TestConvenienceFunctions:
    """Test convenience factory functions."""
    
    def test_get_night_owl_scheduler(self):
        s = get_night_owl_scheduler("test")
        assert s.profile_name == "night_owl"
    
    def test_get_morning_person_scheduler(self):
        s = get_morning_person_scheduler("test")
        assert s.profile_name == "morning_person"
    
    def test_get_binge_creator_scheduler(self):
        s = get_binge_creator_scheduler("test")
        assert s.profile_name == "binge_creator"
    
    def test_get_weekend_warrior_scheduler(self):
        s = get_weekend_warrior_scheduler("test")
        assert s.profile_name == "weekend_warrior"
    
    def test_get_consistent_scheduler(self):
        s = get_consistent_scheduler("test")
        assert s.profile_name == "consistent_but_human"
    
    def test_create_scheduler_factory(self):
        s = create_scheduler(profile="night_owl", agent="factory")
        assert s.profile_name == "night_owl"
        assert s.agent == "factory"


class TestIntegrationGuide:
    """Test integration patterns from the guide."""
    
    def test_basic_integration_pattern(self):
        """Test the basic integration pattern shown in the guide."""
        # This is the pattern from the issue:
        scheduler = HumanScheduler(profile="night_owl", agent="my_bot")
        
        # Simulate checking multiple times
        results = []
        for _ in range(10):
            result = scheduler.should_post_now()
            results.append(result)
        
        # Should return booleans
        assert all(isinstance(r, bool) for r in results)
    
    def test_wrapped_usage(self):
        """Test using scheduler as a wrapper/middleware."""
        class VideoUploader:
            def __init__(self, profile="consistent_but_human"):
                self.scheduler = HumanScheduler(profile=profile, agent="uploader")
                self.upload_count = 0
            
            def maybe_upload(self, check_time=None):
                if self.scheduler.should_post_now(check_time):
                    # Simulate upload
                    self.upload_count += 1
                    self.scheduler.record_post()
                    return True
                return False
        
        uploader = VideoUploader(profile="consistent_but_human")
        
        # Force post by using current time as next post time
        # This simulates what happens when it's actually time to post
        now = datetime.now()
        uploader.scheduler._next_post_time = now
        result = uploader.maybe_upload(now)
        
        # Should have uploaded
        assert result == True
        assert uploader.upload_count == 1


class TestDistributionStatistics:
    """Statistical tests for distribution properties."""
    
    def test_hour_distribution_not_uniform(self):
        """Test that hour distribution is NOT uniform."""
        scheduler = HumanScheduler(profile="night_owl", seed=42)
        preview = scheduler.get_schedule_preview(days=30)
        
        hour_counts = Counter(post["hour"] for post in preview)
        
        # If uniform, all hours would have similar counts
        # For night_owl, we expect clustering in 22-3 range
        
        night_hours = sum(hour_counts[h] for h in range(22, 24))
        night_hours += sum(hour_counts[h] for h in range(0, 3))
        
        other_hours = sum(hour_counts[h] for h in range(3, 22))
        
        # Night hours should dominate for night_owl
        assert night_hours > other_hours * 0.5, \
            "Distribution appears too uniform - not human-like"
    
    def test_interval_variation(self):
        """Test that intervals between posts vary."""
        scheduler = HumanScheduler(profile="consistent_but_human", seed=123)
        preview = scheduler.get_schedule_preview(days=7)
        
        if len(preview) < 2:
            pytest.skip("Not enough data points")
        
        intervals = []
        prev_time = None
        
        for post in preview:
            curr_time = datetime.fromisoformat(post["scheduled_time"])
            if prev_time:
                interval = (curr_time - prev_time).total_seconds() / 3600
                intervals.append(interval)
            prev_time = curr_time
        
        if len(intervals) > 1:
            # Calculate coefficient of variation
            mean_interval = sum(intervals) / len(intervals)
            if mean_interval > 0:
                variance = sum((i - mean_interval)**2 for i in intervals) / len(intervals)
                std_dev = variance ** 0.5
                cv = std_dev / mean_interval
                
                # Should have some variation (CV > 0.1)
                assert cv > 0.1, \
                    f"Too little interval variation (CV={cv:.3f})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])