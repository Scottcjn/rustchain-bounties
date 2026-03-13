"""
Tests for BoTTube Python SDK
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from bottube import BoTTube, BoTTubeError, Video, Comment


class TestBoTTubeInit:
    """Test BoTTube client initialization."""
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        client = BoTTube(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == "https://api.bottube.ai"
    
    def test_init_with_env_var(self):
        """Test initialization with environment variable."""
        with patch.dict("os.environ", {"BOTTUBE_API_KEY": "env_key"}):
            client = BoTTube()
            assert client.api_key == "env_key"
    
    def test_init_custom_base_url(self):
        """Test initialization with custom base URL."""
        client = BoTTube(api_key="key", base_url="https://custom.api.com/")
        assert client.base_url == "https://custom.api.com"


class TestVideoUpload:
    """Test video upload functionality."""
    
    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_upload_file_not_found(self, mock_getsize, mock_exists):
        """Test upload with non-existent file."""
        mock_exists.return_value = False
        
        client = BoTTube(api_key="test_key")
        
        with pytest.raises(BoTTubeError) as exc_info:
            client.upload("/nonexistent/video.mp4", "Title")
        
        assert exc_info.value.code == "FILE_NOT_FOUND"
    
    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_upload_file_too_large(self, mock_getsize, mock_exists):
        """Test upload with file exceeding 2MB limit."""
        mock_exists.return_value = True
        mock_getsize.return_value = 3 * 1024 * 1024  # 3MB
        
        client = BoTTube(api_key="test_key")
        
        with pytest.raises(BoTTubeError) as exc_info:
            client.upload("/large/video.mp4", "Title")
        
        assert exc_info.value.code == "FILE_TOO_LARGE"


class TestSearch:
    """Test video search functionality."""
    
    @patch("requests.Session.request")
    def test_search_basic(self, mock_request):
        """Test basic search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "videos": [
                {
                    "id": "vid1",
                    "title": "Test Video",
                    "description": "Test desc",
                    "url": "https://bottube.ai/v/vid1",
                    "thumbnail_url": "https://bottube.ai/t/vid1.jpg",
                    "duration": 60,
                    "views": 100,
                    "upvotes": 10,
                    "downvotes": 2,
                    "tags": ["test", "demo"],
                    "created_at": "2026-03-13T12:00:00",
                    "updated_at": "2026-03-13T12:00:00"
                }
            ]
        }
        mock_request.return_value = mock_response
        
        client = BoTTube(api_key="test_key")
        results = client.search("test query", limit=10)
        
        assert len(results) == 1
        assert results[0].id == "vid1"
        assert results[0].title == "Test Video"
        mock_request.assert_called_once()


class TestComments:
    """Test comment functionality."""
    
    @patch("requests.Session.request")
    def test_comment_create(self, mock_request):
        """Test creating a comment."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "comment1",
            "video_id": "vid1",
            "text": "Great video!",
            "author": "user123",
            "created_at": "2026-03-13T12:00:00",
            "upvotes": 0
        }
        mock_request.return_value = mock_response
        
        client = BoTTube(api_key="test_key")
        comment = client.comment("vid1", "Great video!")
        
        assert comment.id == "comment1"
        assert comment.text == "Great video!"


class TestVoting:
    """Test voting functionality."""
    
    @patch("requests.Session.request")
    def test_upvote(self, mock_request):
        """Test upvoting a video."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_request.return_value = mock_response
        
        client = BoTTube(api_key="test_key")
        result = client.upvote("vid1")
        
        assert result is True
        mock_request.assert_called_once_with(
            "POST",
            "https://api.bottube.ai/videos/vid1/upvote",
            data=None,
            params=None,
            json=None,
            files=None,
            headers=None,
            timeout=None
        )
    
    @patch("requests.Session.request")
    def test_downvote(self, mock_request):
        """Test downvoting a video."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        client = BoTTube(api_key="test_key")
        result = client.downvote("vid1")
        
        assert result is True


class TestVideoModel:
    """Test Video data model."""
    
    def test_video_creation(self):
        """Test creating a Video object."""
        video = Video(
            id="vid1",
            title="Test",
            description="Desc",
            url="https://bottube.ai/v/vid1",
            thumbnail_url="https://bottube.ai/t/vid1.jpg",
            duration=60,
            views=100,
            upvotes=10,
            downvotes=2,
            tags=["test"],
            created_at=datetime(2026, 3, 13, 12, 0, 0),
            updated_at=datetime(2026, 3, 13, 12, 0, 0)
        )
        
        assert video.id == "vid1"
        assert video.title == "Test"
        assert len(video.tags) == 1


class TestCommentModel:
    """Test Comment data model."""
    
    def test_comment_creation(self):
        """Test creating a Comment object."""
        comment = Comment(
            id="comment1",
            video_id="vid1",
            text="Great!",
            author="user123",
            created_at=datetime(2026, 3, 13, 12, 0, 0),
            upvotes=5
        )
        
        assert comment.id == "comment1"
        assert comment.text == "Great!"
        assert comment.upvotes == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
