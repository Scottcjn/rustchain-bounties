#!/usr/bin/env python3
"""
Test cases for BoTTube Agent Memory
Bounty #2285 - 40 RTC
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta

from agent_memory import (
    AgentMemoryStore,
    VideoMemory,
    TFIDFVectorizer,
    AgentStats
)


class TestTFIDFVectorizer:
    """Test TF-IDF vectorizer"""

    def test_fit(self):
        """Test fitting the vectorizer"""
        vectorizer = TFIDFVectorizer()
        documents = [
            "python programming tutorial",
            "javascript web development",
            "python machine learning",
            "javascript frontend framework"
        ]
        vectorizer.fit(documents)

        assert len(vectorizer.vocabulary) > 0
        assert len(vectorizer.idf) > 0
        assert vectorizer.document_count == 4

    def test_transform(self):
        """Test transforming text to TF-IDF vector"""
        vectorizer = TFIDFVectorizer()
        documents = ["python programming", "javascript development"]
        vectorizer.fit(documents)

        vector = vectorizer.transform("python is great")

        assert 'python' in vector
        assert vector['python'] > 0

    def test_cosine_similarity_same(self):
        """Test cosine similarity with identical vectors"""
        vectorizer = TFIDFVectorizer()
        vec1 = {'python': 0.5, 'code': 0.3}
        vec2 = {'python': 0.5, 'code': 0.3}

        similarity = vectorizer.cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(1.0, rel=0.01)

    def test_cosine_similarity_different(self):
        """Test cosine similarity with different vectors"""
        vectorizer = TFIDFVectorizer()
        vec1 = {'python': 0.5, 'code': 0.3}
        vec2 = {'javascript': 0.6, 'web': 0.4}

        similarity = vectorizer.cosine_similarity(vec1, vec2)

        assert similarity == 0.0

    def test_cosine_similarity_partial(self):
        """Test cosine similarity with partial overlap"""
        vectorizer = TFIDFVectorizer()
        vec1 = {'python': 0.5, 'code': 0.3}
        vec2 = {'python': 0.4, 'script': 0.2}

        similarity = vectorizer.cosine_similarity(vec1, vec2)

        assert 0 < similarity < 1


class TestVideoMemory:
    """Test VideoMemory dataclass"""

    def test_create(self):
        """Test creating a video memory"""
        video = VideoMemory(
            video_id="vid_001",
            agent_name="test_agent",
            title="Test Video",
            description="A test video description"
        )

        assert video.video_id == "vid_001"
        assert video.agent_name == "test_agent"
        assert video.title == "Test Video"
        assert video.description == "A test video description"
        assert video.topics == []
        assert video.opinions == []

    def test_to_dict(self):
        """Test converting to dictionary"""
        video = VideoMemory(
            video_id="vid_001",
            agent_name="test_agent",
            title="Test Video",
            description="Test description"
        )

        data = video.to_dict()

        assert data['video_id'] == "vid_001"
        assert data['agent_name'] == "test_agent"
        assert data['title'] == "Test Video"

    def test_from_dict(self):
        """Test creating from dictionary"""
        data = {
            'video_id': 'vid_001',
            'agent_name': 'test_agent',
            'title': 'Test Video',
            'description': 'Test description',
            'topics': ['python', 'ai'],
            'opinions': ['I think AI is great']
        }

        video = VideoMemory.from_dict(data)

        assert video.video_id == "vid_001"
        assert video.topics == ['python', 'ai']
        assert video.opinions == ['I think AI is great']


class TestAgentMemoryStore:
    """Test AgentMemoryStore"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)

    @pytest.fixture
    def store(self, temp_db):
        """Create a memory store with temp database"""
        return AgentMemoryStore(db_path=temp_db)

    def test_init_db(self, temp_db):
        """Test database initialization"""
        store = AgentMemoryStore(db_path=temp_db)

        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        assert 'agent_videos' in tables
        assert 'video_embeddings' in tables
        assert 'agent_series' in tables

        conn.close()

    def test_add_video(self, store):
        """Test adding a video to memory"""
        video = VideoMemory(
            video_id="vid_001",
            agent_name="test_agent",
            title="Python Tutorial",
            description="Learn Python programming"
        )

        result = store.add_video(video)

        assert result == True

        # Verify video was added
        stats = store.get_agent_stats("test_agent")
        assert stats is not None
        assert stats.total_videos == 1

    def test_add_multiple_videos(self, store):
        """Test adding multiple videos"""
        for i in range(3):
            video = VideoMemory(
                video_id=f"vid_{i:03d}",
                agent_name="test_agent",
                title=f"Video {i}",
                description=f"Description {i}"
            )
            store.add_video(video)

        stats = store.get_agent_stats("test_agent")
        assert stats.total_videos == 3

    def test_search_memory(self, store):
        """Test searching memory"""
        # Add some videos
        videos = [
            VideoMemory(video_id="vid_001", agent_name="test_agent",
                       title="Python Tutorial", description="Learn Python basics"),
            VideoMemory(video_id="vid_002", agent_name="test_agent",
                       title="JavaScript Guide", description="Learn JavaScript"),
            VideoMemory(video_id="vid_003", agent_name="test_agent",
                       title="Python Advanced", description="Advanced Python"),
        ]

        for v in videos:
            store.add_video(v)

        # Search for Python
        results = store.search_memory("test_agent", "Python programming")

        assert len(results) > 0
        # Python videos should rank higher
        assert results[0]['title'] in ["Python Tutorial", "Python Advanced"]

    def test_get_agent_stats(self, store):
        """Test getting agent statistics"""
        # Add videos
        videos = [
            VideoMemory(video_id="vid_001", agent_name="test_agent",
                       title="Video 1", description="Desc 1", views=100, likes=10,
                       topics=['python', 'ai']),
            VideoMemory(video_id="vid_002", agent_name="test_agent",
                       title="Video 2", description="Desc 2", views=200, likes=20,
                       topics=['python', 'ml']),
        ]

        for v in videos:
            store.add_video(v)

        stats = store.get_agent_stats("test_agent")

        assert stats is not None
        assert stats.total_videos == 2
        assert stats.total_views == 300
        assert stats.total_likes == 30
        assert len(stats.top_topics) > 0

    def test_check_for_self_reference(self, store):
        """Test self-reference checking"""
        # Add a past video
        past_video = VideoMemory(
            video_id="vid_001",
            agent_name="test_agent",
            title="Python Tutorial",
            description="Learn Python programming basics"
        )
        store.add_video(past_video)

        # Check for similar content
        suggestions = store.check_for_self_reference(
            "test_agent",
            "Advanced Python Programming",
            "Building on our Python basics tutorial"
        )

        assert suggestions['has_similar'] == True
        assert len(suggestions['similar_videos']) > 0
        assert suggestions['suggested_reference'] is not None

    def test_series_detection(self, store):
        """Test series detection"""
        video = VideoMemory(
            video_id="vid_001",
            agent_name="test_agent",
            title="Cooking Series Part 3",
            description="Continuing our cooking tutorial series"
        )
        store.add_video(video)

        series_info = store._detect_series(
            "test_agent",
            "Cooking Series Part 4",
            "Next episode in the series"
        )

        assert series_info is not None
        assert series_info['part_number'] == 4

    def test_milestone_detection(self, store):
        """Test milestone detection"""
        # Add 9 videos
        for i in range(9):
            video = VideoMemory(
                video_id=f"vid_{i:03d}",
                agent_name="test_agent",
                title=f"Video {i}",
                description="Description"
            )
            store.add_video(video)

        # Check for milestone on 10th video
        suggestions = store.check_for_self_reference(
            "test_agent",
            "Video 10",
            "Description"
        )

        assert suggestions['milestone_info'] is not None
        assert suggestions['milestone_info']['milestone'] == 10

    def test_opinion_extraction(self, store):
        """Test opinion extraction"""
        opinions = store._extract_opinions(
            "I think Python is great. In my opinion, it's the best language."
        )

        assert len(opinions) > 0
        assert any('python' in o for o in opinions)

    def test_get_all_agents(self, store):
        """Test getting all agents"""
        # Add videos for multiple agents
        for agent in ['agent1', 'agent2', 'agent3']:
            video = VideoMemory(
                video_id=f"vid_{agent}",
                agent_name=agent,
                title=f"Video by {agent}",
                description="Description"
            )
            store.add_video(video)

        agents = store.get_all_agents()

        assert len(agents) == 3
        assert 'agent1' in agents
        assert 'agent2' in agents
        assert 'agent3' in agents

    def test_delete_video(self, store):
        """Test deleting a video"""
        video = VideoMemory(
            video_id="vid_001",
            agent_name="test_agent",
            title="Test Video",
            description="Description"
        )
        store.add_video(video)

        stats = store.get_agent_stats("test_agent")
        assert stats.total_videos == 1

        # Delete video
        result = store.delete_video("vid_001", "test_agent")
        assert result == True

        stats = store.get_agent_stats("test_agent")
        assert stats is None

    def test_export_memory(self, store):
        """Test exporting memory"""
        # Add videos
        for i in range(3):
            video = VideoMemory(
                video_id=f"vid_{i:03d}",
                agent_name="test_agent",
                title=f"Video {i}",
                description=f"Description {i}",
                topics=['topic1'],
                opinions=['opinion1']
            )
            store.add_video(video)

        exported = store.export_memory("test_agent")

        assert 'agent_name' in exported
        assert 'stats' in exported
        assert 'videos' in exported
        assert len(exported['videos']) == 3


class TestAgentStats:
    """Test AgentStats dataclass"""

    def test_to_dict(self):
        """Test converting to dictionary"""
        stats = AgentStats(
            agent_name="test_agent",
            total_videos=100,
            first_upload_date="2025-01-01",
            latest_upload_date="2025-12-01",
            total_views=10000,
            total_likes=500,
            top_topics=[('python', 50), ('ai', 30)],
            recent_opinions=['Opinion 1'],
            series_count=5,
            milestone_next=100
        )

        data = stats.to_dict()

        assert data['agent_name'] == "test_agent"
        assert data['total_videos'] == 100
        assert data['total_views'] == 10000
        assert data['top_topics'] == [('python', 50), ('ai', 30)]


# Integration test
def test_full_workflow():
    """Test full workflow from adding to searching"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    try:
        store = AgentMemoryStore(db_path=db_path)

        # Add videos over time
        videos = [
            VideoMemory(video_id="vid_001", agent_name="creative_ai",
                       title="AI Art Tutorial", description="Learn to create AI art",
                       topics=['ai', 'art'], upload_date="2025-01-01"),
            VideoMemory(video_id="vid_002", agent_name="creative_ai",
                       title="AI Music Generation", description="Create music with AI",
                       topics=['ai', 'music'], upload_date="2025-02-01"),
            VideoMemory(video_id="vid_003", agent_name="creative_ai",
                       title="Advanced AI Art", description="Advanced techniques for AI art",
                       topics=['ai', 'art'], upload_date="2025-03-01"),
        ]

        for v in videos:
            store.add_video(v)

        # Search for similar content
        results = store.search_memory("creative_ai", "AI art creation")

        assert len(results) > 0
        assert results[0]['title'] in ["AI Art Tutorial", "Advanced AI Art"]

        # Check self-reference
        suggestions = store.check_for_self_reference(
            "creative_ai",
            "AI Art Masterclass",
            "Building on our AI art tutorials"
        )

        assert suggestions['has_similar'] == True

        # Get stats
        stats = store.get_agent_stats("creative_ai")
        assert stats.total_videos == 3
        assert 'ai' in [t[0] for t in stats.top_topics]

    finally:
        os.unlink(db_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])