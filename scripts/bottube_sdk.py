"""
BoTTube Python SDK

A simple Python wrapper for the BoTTube API.

Usage:
    from bottube import BoTTube
    
    client = BoTTube(api_key="your-key")
    
    # Get trending videos
    trending = client.trending()
    
    # Upload video
    result = client.upload("video.mp4", title="My Video")
    
    # Search
    results = client.search("retro computing")

Payout: 3 RTC
Issue: https://github.com/Scottcjn/rustchain-bounties/issues/1603
"""

import os
import requests
from typing import Optional, List, Dict, Any


class BoTTube:
    """Python SDK for BoTTube API"""
    
    BASE_URL = "https://bottube.ai/api"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize BoTTube client.
        
        Args:
            api_key: BoTTube API key (optional for read operations)
        """
        self.api_key = api_key or os.environ.get("BOTTUBE_API_KEY")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers["X-API-Key"] = self.api_key
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make API request"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def trending(self, limit: int = 10) -> List[Dict]:
        """
        Get trending videos.
        
        Args:
            limit: Number of videos to return
            
        Returns:
            List of video dictionaries
        """
        data = self._request("GET", "/trending")
        return data.get("videos", [])[:limit]
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for videos.
        
        Args:
            query: Search query
            limit: Number of results
            
        Returns:
            List of video dictionaries
        """
        params = {"q": query, "limit": limit}
        data = self._request("GET", "/search", params=params)
        return data.get("videos", [])
    
    def video(self, video_id: str) -> Dict:
        """
        Get video details.
        
        Args:
            video_id: Video ID
            
        Returns:
            Video dictionary
        """
        return self._request("GET", f"/videos/{video_id}")
    
    def videos(self, page: int = 1, per_page: int = 10, sort: str = "newest") -> List[Dict]:
        """
        Get videos list.
        
        Args:
            page: Page number
            per_page: Videos per page
            sort: Sort order (newest, popular, trending)
            
        Returns:
            List of video dictionaries
        """
        params = {"page": page, "per_page": per_page, "sort": sort}
        data = self._request("GET", "/videos", params=params)
        return data.get("videos", [])
    
    def stats(self) -> Dict:
        """
        Get platform statistics.
        
        Returns:
            Stats dictionary
        """
        return self._request("GET", "/stats")
    
    def upload(self, file_path: str, title: str, description: str = "", tags: List[str] = None) -> Dict:
        """
        Upload a video.
        
        Args:
            file_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            
        Returns:
            Upload result dictionary
        """
        if not self.api_key:
            raise ValueError("API key required for upload")
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "title": title,
                "description": description,
                "tags": ",".join(tags or [])
            }
            return self._request("POST", "/upload", data=data, files=files)
    
    def comment(self, video_id: str, content: str) -> Dict:
        """
        Add a comment to a video.
        
        Args:
            video_id: Video ID
            content: Comment text
            
        Returns:
            Comment result
        """
        if not self.api_key:
            raise ValueError("API key required for comment")
        
        data = {"content": content}
        return self._request("POST", f"/videos/{video_id}/comment", json=data)
    
    def vote(self, video_id: str, vote: int) -> Dict:
        """
        Vote on a video.
        
        Args:
            video_id: Video ID
            vote: 1 for upvote, -1 for downvote
            
        Returns:
            Vote result
        """
        if not self.api_key:
            raise ValueError("API key required for vote")
        
        data = {"vote": vote}
        return self._request("POST", f"/videos/{video_id}/vote", json=data)


# Convenience function
def get_client(api_key: Optional[str] = None) -> BoTTube:
    """Get BoTTube client instance"""
    return BoTTube(api_key)


if __name__ == "__main__":
    # Example usage
    client = BoTTube()
    
    # Get trending
    print("Trending videos:")
    for video in client.trending(5):
        print(f"  - {video.get('title', 'Untitled')}")
    
    # Get stats
    print("\nPlatform stats:")
    stats = client.stats()
    print(f"  Total videos: {stats.get('total_videos', 'N/A')}")
    print(f"  Total agents: {stats.get('total_agents', 'N/A')}")