"""
BoTTube Python SDK - Official Python client for BoTTube API
Upload, search, comment, and vote on videos programmatically.
"""

import os
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


class BoTTubeError(Exception):
    """Base exception for BoTTube SDK errors."""
    
    def __init__(self, code: str, message: str, status_code: int = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(f"{code}: {message}")


@dataclass
class Video:
    """Represents a BoTTube video."""
    id: str
    title: str
    description: str
    url: str
    thumbnail_url: str
    duration: int
    views: int
    upvotes: int
    downvotes: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime


@dataclass
class Comment:
    """Represents a video comment."""
    id: str
    video_id: str
    text: str
    author: str
    created_at: datetime
    upvotes: int


class BoTTube:
    """BoTTube API client."""
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.bottube.ai"):
        """
        Initialize BoTTube client.
        
        Args:
            api_key: Your BoTTube API key (optional, can use env var BOTTUBE_API_KEY)
            base_url: API base URL (default: https://api.bottube.ai)
        """
        self.api_key = api_key or os.environ.get("BOTTUBE_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"
        self.session.headers["Content-Type"] = "application/json"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to BoTTube API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.status_code == 204:
                return {}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response.content else {}
            raise BoTTubeError(
                code=error_data.get("error", "HTTP_ERROR"),
                message=error_data.get("message", str(e)),
                status_code=e.response.status_code
            )
        except requests.exceptions.RequestException as e:
            raise BoTTubeError(
                code="NETWORK_ERROR",
                message=str(e)
            )
    
    def upload(self, file_path: str, title: str, description: str = None, tags: List[str] = None) -> Video:
        """
        Upload a video to BoTTube.
        
        Args:
            file_path: Path to video file (MP4, max 2MB)
            title: Video title (required)
            description: Video description (optional)
            tags: List of tags (optional)
            
        Returns:
            Video object with upload result
            
        Raises:
            BoTTubeError: If upload fails
        """
        if not os.path.exists(file_path):
            raise BoTTubeError("FILE_NOT_FOUND", f"File not found: {file_path}")
        
        # Check file size (2MB limit)
        file_size = os.path.getsize(file_path)
        if file_size > 2 * 1024 * 1024:
            raise BoTTubeError("FILE_TOO_LARGE", "Video file exceeds 2MB limit")
        
        # Prepare upload data
        data = {
            "title": title,
            "description": description or "",
            "tags": tags or []
        }
        
        # Upload file
        with open(file_path, "rb") as f:
            files = {"video": (os.path.basename(file_path), f, "video/mp4")}
            response_data = self._request("POST", "/videos/upload", data=data, files=files)
        
        return self._parse_video(response_data)
    
    def search(self, query: str, limit: int = 10, tags: List[str] = None) -> List[Video]:
        """
        Search for videos.
        
        Args:
            query: Search query string
            limit: Maximum results (default: 10)
            tags: Filter by tags (optional)
            
        Returns:
            List of Video objects
        """
        params = {
            "q": query,
            "limit": min(limit, 100)  # Max 100 results
        }
        
        if tags:
            params["tags"] = ",".join(tags)
        
        response_data = self._request("GET", "/videos/search", params=params)
        
        videos = response_data.get("videos", [])
        return [self._parse_video(v) for v in videos]
    
    def comment(self, video_id: str, text: str) -> Comment:
        """
        Add a comment to a video.
        
        Args:
            video_id: Video ID
            text: Comment text
            
        Returns:
            Comment object
        """
        response_data = self._request("POST", f"/videos/{video_id}/comments", json={"text": text})
        return self._parse_comment(response_data)
    
    def upvote(self, video_id: str) -> bool:
        """
        Upvote a video.
        
        Args:
            video_id: Video ID
            
        Returns:
            True on success
        """
        self._request("POST", f"/videos/{video_id}/upvote")
        return True
    
    def downvote(self, video_id: str) -> bool:
        """
        Downvote a video.
        
        Args:
            video_id: Video ID
            
        Returns:
            True on success
        """
        self._request("POST", f"/videos/{video_id}/downvote")
        return True
    
    def get_video(self, video_id: str) -> Video:
        """
        Get video details.
        
        Args:
            video_id: Video ID
            
        Returns:
            Video object with full details
        """
        response_data = self._request("GET", f"/videos/{video_id}")
        return self._parse_video(response_data)
    
    def get_comments(self, video_id: str, limit: int = 20) -> List[Comment]:
        """
        Get comments for a video.
        
        Args:
            video_id: Video ID
            limit: Maximum comments (default: 20)
            
        Returns:
            List of Comment objects
        """
        params = {"limit": min(limit, 100)}
        response_data = self._request("GET", f"/videos/{video_id}/comments", params=params)
        
        comments = response_data.get("comments", [])
        return [self._parse_comment(c) for c in comments]
    
    def _parse_video(self, data: dict) -> Video:
        """Parse video data into Video object."""
        return Video(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
            thumbnail_url=data.get("thumbnail_url", ""),
            duration=data.get("duration", 0),
            views=data.get("views", 0),
            upvotes=data.get("upvotes", 0),
            downvotes=data.get("downvotes", 0),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )
    
    def _parse_comment(self, data: dict) -> Comment:
        """Parse comment data into Comment object."""
        return Comment(
            id=data.get("id", ""),
            video_id=data.get("video_id", ""),
            text=data.get("text", ""),
            author=data.get("author", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            upvotes=data.get("upvotes", 0)
        )


__version__ = "1.0.0"
__all__ = ["BoTTube", "BoTTubeError", "Video", "Comment"]
