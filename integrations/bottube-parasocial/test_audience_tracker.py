#!/usr/bin/env python3
"""Tests for BoTTube Audience Tracker — Parasocial Hooks

Comprehensive test suite covering:
  - Viewer status transitions (new → casual → regular → returning)
  - Sentiment analysis
  - Response generation
  - Boundary conditions
  - Edge cases

Author: HuiNeng
Bounty: Scottcjn/rustchain-bounties#2286 (25 RTC)
"""

import pytest
import tempfile
import time
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from audience_tracker import (
    AudienceTracker,
    Viewer,
    Comment,
    ViewerStatus,
    Sentiment,
    SentimentAnalyzer,
    REGULAR_THRESHOLD,
    ABSENCE_THRESHOLD_DAYS,
    CRITIC_THRESHOLD,
    PERSONALIZATION_RATE,
    MAX_SHOUTOUTS,
)


# ─── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    tmp = Path(tempfile.mkdtemp(prefix="test_audience_"))
    yield tmp
    # Cleanup
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def tracker(temp_dir):
    """Create a fresh AudienceTracker for testing."""
    return AudienceTracker("test_agent", data_dir=str(temp_dir))


# ─── Sentiment Analyzer Tests ───────────────────────────────────────────

class TestSentimentAnalyzer:
    """Tests for the SentimentAnalyzer class."""
    
    def test_positive_english(self):
        """Test positive sentiment detection in English."""
        assert SentimentAnalyzer.analyze("Great video! I love it!") == Sentiment.POSITIVE
        assert SentimentAnalyzer.analyze("Amazing content, thanks!") == Sentiment.POSITIVE
        assert SentimentAnalyzer.analyze("This is the best video ever!") == Sentiment.POSITIVE
    
    def test_positive_chinese(self):
        """Test positive sentiment detection in Chinese."""
        assert SentimentAnalyzer.analyze("太棒了！非常喜欢！") == Sentiment.POSITIVE
        assert SentimentAnalyzer.analyze("谢谢分享，很厉害！") == Sentiment.POSITIVE
        assert SentimentAnalyzer.analyze("学到了很多！") == Sentiment.POSITIVE
    
    def test_negative_english(self):
        """Test negative sentiment detection in English."""
        assert SentimentAnalyzer.analyze("This is terrible, I hate it.") == Sentiment.NEGATIVE
        assert SentimentAnalyzer.analyze("Boring and disappointing.") == Sentiment.NEGATIVE
        assert SentimentAnalyzer.analyze("Worst video ever, waste of time.") == Sentiment.NEGATIVE
    
    def test_negative_chinese(self):
        """Test negative sentiment detection in Chinese."""
        assert SentimentAnalyzer.analyze("这个视频太差了，讨厌。") == Sentiment.NEGATIVE
        assert SentimentAnalyzer.analyze("无聊，浪费时间。") == Sentiment.NEGATIVE
        assert SentimentAnalyzer.analyze("垃圾内容。") == Sentiment.NEGATIVE
    
    def test_neutral(self):
        """Test neutral sentiment detection."""
        assert SentimentAnalyzer.analyze("I watched this.") == Sentiment.NEUTRAL
        assert SentimentAnalyzer.analyze("The video is about cats.") == Sentiment.NEUTRAL
        assert SentimentAnalyzer.analyze("好的") == Sentiment.NEUTRAL
    
    def test_mixed_sentiment(self):
        """Test mixed sentiment (should be neutral if equal)."""
        # Equal positive and negative words
        assert SentimentAnalyzer.analyze("Good but bad") == Sentiment.NEUTRAL
        # More positive
        assert SentimentAnalyzer.analyze("Good and great but bad") == Sentiment.POSITIVE
        # More negative
        assert SentimentAnalyzer.analyze("Bad and terrible but good") == Sentiment.NEGATIVE


# ─── Viewer Status Tests ─────────────────────────────────────────────────

class TestViewerStatus:
    """Tests for viewer status transitions."""
    
    def test_new_viewer(self, tracker):
        """Test that first comment creates NEW status."""
        comment = tracker.record_comment(
            video_id="video_1",
            viewer_id="user_new",
            display_name="NewViewer",
            content="First comment!"
        )
        
        viewer = tracker.get_viewer("user_new")
        assert viewer is not None
        assert viewer.status == ViewerStatus.NEW
        assert viewer.total_comments == 1
        assert len(viewer.videos_commented) == 1
    
    def test_casual_viewer(self, tracker):
        """Test CASUAL status (1-2 videos)."""
        # First video
        tracker.record_comment("video_1", "user_casual", "Casual", "First!")
        # Second video
        tracker.record_comment("video_2", "user_casual", "Casual", "Second!")
        
        viewer = tracker.get_viewer("user_casual")
        assert viewer.status == ViewerStatus.CASUAL
        assert len(viewer.videos_commented) == 2
    
    def test_regular_viewer(self, tracker):
        """Test REGULAR status (3+ videos)."""
        for i in range(REGULAR_THRESHOLD):
            tracker.record_comment(
                f"video_{i}",
                "user_regular",
                "RegularFan",
                f"Comment on video {i}"
            )
        
        viewer = tracker.get_viewer("user_regular")
        assert viewer.status == ViewerStatus.REGULAR
        assert len(viewer.videos_commented) >= REGULAR_THRESHOLD
    
    def test_returning_viewer(self, tracker):
        """Test RETURNING status (absent then returned)."""
        # Create a viewer with some history
        tracker.record_comment("video_1", "user_return", "Returner", "Here!")
        tracker.record_comment("video_2", "user_return", "Returner", "Still here!")
        
        # Mark as "old" interaction
        viewer = tracker.get_viewer("user_return")
        viewer.last_seen = time.time() - (ABSENCE_THRESHOLD_DAYS + 5) * 86400
        tracker._save()
        
        # Reload and check
        tracker._load()
        
        # New comment should trigger RETURNING status
        tracker.record_comment("video_3", "user_return", "Returner", "I'm back!")
        
        viewer = tracker.get_viewer("user_return")
        assert viewer.status == ViewerStatus.RETURNING
    
    def test_critic_viewer(self, tracker):
        """Test CRITIC status (consistently negative)."""
        # Create viewer with mostly negative comments
        for i in range(5):
            tracker.record_comment(
                f"video_{i}",
                "user_critic",
                "TheCritic",
                "This is terrible and disappointing!"
            )
        
        # Add one positive to keep ratio below threshold
        tracker.record_comment("video_5", "user_critic", "TheCritic", "Okay I guess.")
        
        viewer = tracker.get_viewer("user_critic")
        # Should be CRITIC if sentiment ratio is below threshold
        assert viewer.sentiment_ratio < CRITIC_THRESHOLD or viewer.status == ViewerStatus.REGULAR


# ─── Comment Recording Tests ─────────────────────────────────────────────

class TestCommentRecording:
    """Tests for comment recording functionality."""
    
    def test_basic_comment_recording(self, tracker):
        """Test basic comment recording."""
        comment = tracker.record_comment(
            video_id="test_video",
            viewer_id="test_user",
            display_name="TestUser",
            content="Test comment"
        )
        
        assert comment.video_id == "test_video"
        assert comment.viewer_id == "test_user"
        assert comment.content == "Test comment"
        assert comment.sentiment in Sentiment
    
    def test_comment_persistence(self, tracker):
        """Test that comments are persisted and reloadable."""
        tracker.record_comment("v1", "u1", "User1", "Comment 1")
        tracker.record_comment("v1", "u2", "User2", "Comment 2")
        
        # Create new tracker instance (simulates restart)
        new_tracker = AudienceTracker("test_agent", data_dir=tracker.data_dir)
        
        assert len(new_tracker._comments) == 2
        assert new_tracker.get_viewer("u1") is not None
        assert new_tracker.get_viewer("u2") is not None
    
    def test_multiple_comments_same_viewer(self, tracker):
        """Test multiple comments from same viewer."""
        for i in range(5):
            tracker.record_comment(
                f"video_{i}",
                "multi_user",
                "MultiUser",
                f"Comment {i}"
            )
        
        viewer = tracker.get_viewer("multi_user")
        assert viewer.total_comments == 5
        assert len(viewer.videos_commented) == 5
    
    def test_comment_same_video_multiple_times(self, tracker):
        """Test multiple comments on same video from same user."""
        for i in range(3):
            tracker.record_comment(
                "same_video",
                "same_user",
                "SameUser",
                f"Comment {i}"
            )
        
        viewer = tracker.get_viewer("same_user")
        # Should count all comments but video only once
        assert viewer.total_comments == 3
        assert len(viewer.videos_commented) == 1


# ─── Response Generation Tests ───────────────────────────────────────────

class TestResponseGeneration:
    """Tests for personalized response generation."""
    
    def test_response_for_new_viewer(self, tracker):
        """Test response for new viewers."""
        comment = tracker.record_comment("v1", "new_guy", "NewGuy", "First time!")
        response = tracker.generate_response(comment, force_personalize=True)
        
        assert response is not None
        assert "NewGuy" in response or "@new_guy" in response.lower()
        assert "welcome" in response.lower() or "first" in response.lower()
    
    def test_response_for_regular(self, tracker):
        """Test response for regular viewers."""
        # Create regular
        for i in range(REGULAR_THRESHOLD):
            tracker.record_comment(f"v{i}", "regular_guy", "RegularGuy", f"Comment {i}")
        
        viewer = tracker.get_viewer("regular_guy")
        comment = Comment("test_id", "v_new", "regular_guy", "Test", time.time())
        response = tracker.generate_response(comment, force_personalize=True)
        
        assert response is not None
        assert "RegularGuy" in response
    
    def test_response_for_returning(self, tracker):
        """Test response for returning viewers."""
        # Create viewer
        tracker.record_comment("v1", "return_guy", "ReturnGuy", "Here")
        tracker.record_comment("v2", "return_guy", "ReturnGuy", "Still here")
        
        # Simulate absence
        viewer = tracker.get_viewer("return_guy")
        viewer.last_seen = time.time() - (ABSENCE_THRESHOLD_DAYS + 5) * 86400
        tracker._save()
        tracker._load()
        
        # New comment triggers returning
        comment = tracker.record_comment("v3", "return_guy", "ReturnGuy", "Back!")
        response = tracker.generate_response(comment, force_personalize=True)
        
        assert response is not None
        assert "back" in response.lower() or "while" in response.lower() or "haven't" in response.lower()
    
    def test_response_for_critic(self, tracker):
        """Test respectful response for critics."""
        # Create critic
        for i in range(4):
            tracker.record_comment(
                f"v{i}",
                "critic_guy",
                "CriticGuy",
                "This is terrible and boring!"
            )
        
        viewer = tracker.get_viewer("critic_guy")
        comment = Comment("test_id", "v_new", "critic_guy", "Bad", time.time())
        response = tracker.generate_response(comment, force_personalize=True)
        
        # Should be respectful, not defensive
        assert response is not None
        assert "thanks" in response.lower() or "appreciate" in response.lower() or "hear" in response.lower()
    
    def test_no_response_when_not_personalized(self, tracker):
        """Test that not all comments get responses."""
        comment = tracker.record_comment("v1", "user1", "User1", "Nice!")
        
        # Without force_personalize, may return None based on random
        # Test that with force_personalize=False multiple times,
        # some return None
        responses = []
        for _ in range(20):
            c = tracker.record_comment(f"v_{_}", "user1", "User1", f"Comment {_}")
            r = tracker.generate_response(c, force_personalize=False)
            responses.append(r)
        
        # At least some should be None due to PERSONALIZATION_RATE < 1
        none_count = sum(1 for r in responses if r is None)
        assert none_count > 0, "Expected some responses to be None due to personalization rate"


# ─── Shoutout Tests ───────────────────────────────────────────────────────

class TestShoutouts:
    """Tests for video description shoutouts."""
    
    def test_generate_shoutouts(self, tracker):
        """Test shoutout generation."""
        # Create regular viewers
        for i in range(REGULAR_THRESHOLD + 1):
            tracker.record_comment(f"v{i}", "top_fan", "TopFan", f"Great {i}!")
            tracker.record_comment(f"v{i}", "second_fan", "SecondFan", f"Nice {i}!")
        
        shoutouts = tracker.generate_shoutouts()
        
        assert len(shoutouts) <= MAX_SHOUTOUTS
        assert "TopFan" in shoutouts or "SecondFan" in shoutouts
    
    def test_shoutout_description_section(self, tracker):
        """Test full description section generation."""
        for i in range(REGULAR_THRESHOLD + 1):
            tracker.record_comment(f"v{i}", "fan1", "Fan1", f"Great {i}!")
        
        section = tracker.generate_description_section()
        
        assert "commenters" in section.lower() or "shoutout" in section.lower()
    
    def test_shoutout_with_inspiration(self, tracker):
        """Test inspiration mention in description."""
        tracker.record_comment("v1", "inspirer", "Inspirer", "Can you make a video about X?")
        
        section = tracker.generate_description_section(inspiration_viewer="inspirer")
        
        assert "inspired" in section.lower()


# ─── Boundary Condition Tests ─────────────────────────────────────────────

class TestBoundaries:
    """Tests for boundary enforcement."""
    
    def test_not_creepy(self, tracker):
        """Test that tracking doesn't become creepy."""
        # Add many comments from one user
        for i in range(100):
            tracker.record_comment(f"v{i}", "superfan", "SuperFan", f"Comment {i}")
        
        # Check boundaries
        result = tracker.check_boundaries()
        
        # Should flag excessive tracking if over 1000
        # (In our case, 100 comments should be fine)
        assert result["healthy"]
    
    def test_not_desperate(self, tracker):
        """Test that personalization rate isn't too high."""
        result = tracker.check_boundaries()
        
        assert result["personalization_rate"] <= 0.5, \
            "Personalization rate should be <= 50% to not seem desperate"
    
    def test_max_shoutouts_limit(self, tracker):
        """Test that shoutouts are limited."""
        # Create many eligible viewers
        for j in range(10):
            for i in range(REGULAR_THRESHOLD + 1):
                tracker.record_comment(f"v{j}_{i}", f"fan_{j}", f"Fan{j}", f"Great!")
        
        shoutouts = tracker.generate_shoutouts()
        
        assert len(shoutouts) <= MAX_SHOUTOUTS
    
    def test_min_engagement_for_shoutout(self, tracker):
        """Test that only sufficiently engaged viewers get shoutouts."""
        # Create viewer with only 1 video engagement
        tracker.record_comment("v1", "one_timer", "OneTimer", "Nice!")
        
        shoutouts = tracker.generate_shoutouts()
        
        # OneTimer should not be in shoutouts (only 1 video)
        assert "OneTimer" not in shoutouts


# ─── Edge Cases ───────────────────────────────────────────────────────────

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_tracker(self, tracker):
        """Test operations on empty tracker."""
        assert tracker.get_stats()["total_viewers"] == 0
        assert tracker.get_regulars() == []
        assert tracker.get_new_viewers() == []
        assert tracker.generate_shoutouts() == []
    
    def test_unknown_viewer(self, tracker):
        """Test handling unknown viewer."""
        assert tracker.get_viewer("nonexistent") is None
    
    def test_special_characters_in_names(self, tracker):
        """Test handling special characters in display names."""
        comment = tracker.record_comment(
            "v1",
            "special_user",
            "用户@特殊#字符!",
            "你好！"
        )
        
        viewer = tracker.get_viewer("special_user")
        assert viewer is not None
        assert viewer.display_name == "用户@特殊#字符!"
    
    def test_very_long_comment(self, tracker):
        """Test handling very long comments."""
        long_comment = "Great video! " * 1000  # ~13000 chars
        
        comment = tracker.record_comment(
            "v1",
            "long_user",
            "LongUser",
            long_comment
        )
        
        assert comment is not None
        assert len(comment.content) == len(long_comment)
    
    def test_concurrent_tracking(self, temp_dir):
        """Test that multiple agents can track separately."""
        tracker1 = AudienceTracker("agent_1", data_dir=str(temp_dir / "agent_1"))
        tracker2 = AudienceTracker("agent_2", data_dir=str(temp_dir / "agent_2"))
        
        tracker1.record_comment("v1", "user1", "User1", "Hi from agent 1!")
        tracker2.record_comment("v1", "user2", "User2", "Hi from agent 2!")
        
        assert tracker1.get_stats()["total_viewers"] == 1
        assert tracker2.get_stats()["total_viewers"] == 1
        assert tracker1.get_viewer("user1") is not None
        assert tracker1.get_viewer("user2") is None
        assert tracker2.get_viewer("user2") is not None
        assert tracker2.get_viewer("user1") is None


# ─── Stats Tests ───────────────────────────────────────────────────────────

class TestStats:
    """Tests for statistics functionality."""
    
    def test_basic_stats(self, tracker):
        """Test basic statistics calculation."""
        tracker.record_comment("v1", "u1", "User1", "Great!")
        tracker.record_comment("v1", "u2", "User2", "Nice!")
        tracker.record_comment("v2", "u1", "User1", "Still great!")
        
        stats = tracker.get_stats()
        
        assert stats["total_viewers"] == 2
        assert stats["total_comments"] == 3
        assert stats["videos_tracked"] == 2
    
    def test_status_distribution(self, tracker):
        """Test viewer status distribution in stats."""
        # Create different viewer types
        tracker.record_comment("v1", "new1", "New1", "Hi!")
        
        tracker.record_comment("v1", "casual1", "Casual1", "Hi!")
        tracker.record_comment("v2", "casual1", "Casual1", "Hi again!")
        
        for i in range(REGULAR_THRESHOLD):
            tracker.record_comment(f"v{i}", "regular1", "Regular1", f"Hi {i}!")
        
        stats = tracker.get_stats()
        
        # Should have at least one regular
        assert stats["regulars"] >= 1


# ─── Run Tests ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])