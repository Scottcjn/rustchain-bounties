# SPDX-License-Identifier: MIT
"""BoTTube API client."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://bottube.ai"


class BoTTubeClient:
    """Client for the BoTTube API.

    Args:
        api_key: BoTTube API key. If None, read from BOTTUBE_API_KEY env var.
        base_url: Base URL of the BoTTube instance.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL,
    ) -> None:
        self.api_key = api_key or os.getenv("BOTTUBE_API_KEY", "")
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(
        self, path: str, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None
    ) -> Any:
        url = f"{self.base_url}{path}"
        if files:
            # Multipart upload
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            resp = requests.post(url, data=data, files=files, headers=headers, timeout=120)
        else:
            resp = requests.post(url, json=data, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    # -------------------------------------------------------------------------
    # Read tools
    # -------------------------------------------------------------------------

    def trending(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get trending videos."""
        params: Dict[str, Any] = {}
        if category:
            params["category"] = category
        return self._get("/api/trending", params)

    def videos(
        self,
        page: int = 1,
        per_page: int = 10,
        sort: str = "newest",
    ) -> Dict[str, Any]:
        """List videos with pagination."""
        return self._get(
            "/api/videos",
            {"page": page, "per_page": per_page, "sort": sort},
        )

    def search(self, query: str) -> Dict[str, Any]:
        """Search videos by query."""
        return self._get("/api/search", {"q": query})

    def video(self, video_id: str) -> Dict[str, Any]:
        """Get video details and comments."""
        return self._get(f"/api/videos/{video_id}")

    def comments(self, video_id: str) -> Dict[str, Any]:
        """Get comments for a video."""
        return self._get(f"/api/videos/{video_id}/comments")

    def agent(self, agent_name: str) -> Dict[str, Any]:
        """Get agent profile and videos."""
        return self._get(f"/api/agents/{agent_name}")

    def stats(self) -> Dict[str, Any]:
        """Get platform statistics."""
        return self._get("/api/stats")

    # -------------------------------------------------------------------------
    # Write tools (require API key)
    # -------------------------------------------------------------------------

    def upload(
        self,
        file_path: str,
        title: str,
        description: str = "",
        tags: Optional[List[str]] = None,
        agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Upload a video.

        Args:
            file_path: Path to the video file.
            title: Video title.
            description: Video description.
            tags: List of tags.
            agent_name: Name of the uploading agent (used as wallet identifier).

        Returns:
            API response with video ID and URL.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Video file not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "video/mp4")}
            data: Dict[str, Any] = {
                "title": title,
                "description": description,
            }
            if tags:
                data["tags"] = ",".join(tags)
            if agent_name:
                data["agent_name"] = agent_name
            return self._post("/api/upload", data=data, files=files)

    def comment(self, video_id: str, content: str) -> Dict[str, Any]:
        """Post a comment on a video."""
        return self._post(f"/api/videos/{video_id}/comment", {"content": content})

    def vote(self, video_id: str, vote: int) -> Dict[str, Any]:
        """Vote on a video.

        Args:
            video_id: The video ID.
            vote: 1 = upvote, -1 = downvote.
        """
        if vote not in (1, -1):
            raise ValueError("vote must be 1 (upvote) or -1 (downvote)")
        return self._post(f"/api/videos/{video_id}/vote", {"vote": vote})

    def register(self, agent_name: str, display_name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new agent on BoTTube."""
        data: Dict[str, Any] = {"agent_name": agent_name}
        if display_name:
            data["display_name"] = display_name
        return self._post("/api/register", data)

    @classmethod
    def from_env(cls) -> "BoTTubeClient":
        """Create a client from environment variables."""
        return cls(api_key=os.getenv("BOTTUBE_API_KEY", ""))
