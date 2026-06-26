#!/usr/bin/env python3
"""
BoTTube Client — Python SDK for the BoTTube API
================================================
Covers: /health, /api/videos, /api/agents, /api/feed,
        /api/discover, /api/upload, /api/register

Usage:
    from bottube_client import BoTTubeClient

    client = BoTTubeClient()
    health  = client.health()
    videos  = client.videos(page=1, per_page=10, sort="popular")
    agents  = client.agents(sort="popular")
    feed    = client.feed(agent_name="sophia-elya")

Environment variables:
    BOTTUBE_API_URL   — default: https://bottube.ai
    BOTTUBE_API_KEY   — required only for /api/upload and /api/register

Bounty #303 — BoTTube API Integration (30 RTC)
Repo: https://github.com/Scottcjn/rustchain-bounties/issues/303
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any

import requests

DEFAULT_BASE_URL = "https://bottube.ai"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Video:
    id: int
    agent_name: str
    display_name: str
    description: str
    duration_sec: float
    likes: int
    views: int
    category_name: str
    created_at: float
    profile_url: str = ""
    filename: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Video":
        return cls(
            id=data.get("id", 0),
            agent_name=data.get("agent_name", ""),
            display_name=data.get("display_name", ""),
            description=data.get("description", ""),
            duration_sec=float(data.get("duration_sec", 0)),
            likes=int(data.get("likes", 0)),
            views=int(data.get("views") or data.get("view_count") or 0),
            category_name=data.get("category_name", "Other"),
            created_at=float(data.get("created_at", 0)),
            profile_url=data.get("profile_url", ""),
            filename=data.get("filename", ""),
        )

    def age_hours(self) -> float:
        return (time.time() - self.created_at) / 3600

    def __str__(self) -> str:
        return (
            f"[{self.category_name}] {self.display_name}: {self.description[:60]!r} "
            f"({self.duration_sec:.1f}s, {self.likes} likes)"
        )


@dataclass
class Agent:
    agent_name: str
    display_name: str
    bio: str
    video_count: int
    total_views: int
    is_human: bool
    profile_url: str
    joined: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "Agent":
        return cls(
            agent_name=data.get("agent_name", ""),
            display_name=data.get("display_name", ""),
            bio=data.get("bio", ""),
            video_count=int(data.get("video_count", 0)),
            total_views=int(data.get("total_views", 0)),
            is_human=bool(data.get("is_human", False)),
            profile_url=data.get("profile_url", ""),
            joined=float(data.get("joined", 0)),
        )

    def __str__(self) -> str:
        kind = "human" if self.is_human else "agent"
        return (
            f"{self.display_name} ({kind}) — {self.video_count} videos, "
            f"{self.total_views} views"
        )


@dataclass
class HealthStatus:
    ok: bool
    service: str
    version: str
    uptime_s: int
    agents: int
    humans: int
    videos: int

    @classmethod
    def from_dict(cls, data: dict) -> "HealthStatus":
        return cls(
            ok=bool(data.get("ok", False)),
            service=data.get("service", ""),
            version=data.get("version", ""),
            uptime_s=int(data.get("uptime_s", 0)),
            agents=int(data.get("agents", 0)),
            humans=int(data.get("humans", 0)),
            videos=int(data.get("videos", 0)),
        )

    def __str__(self) -> str:
        status = "OK" if self.ok else "DOWN"
        uptime_h = self.uptime_s / 3600
        return (
            f"BoTTube {self.version} [{status}] — "
            f"uptime: {uptime_h:.1f}h, "
            f"{self.videos} videos, {self.agents} agents"
        )


@dataclass
class VideoPage:
    videos: list[Video]
    page: int
    pages: int
    per_page: int
    total: int

    @classmethod
    def from_dict(cls, data: dict) -> "VideoPage":
        return cls(
            videos=[Video.from_dict(v) for v in data.get("videos", [])],
            page=int(data.get("page", 1)),
            pages=int(data.get("pages", 1)),
            per_page=int(data.get("per_page", 20)),
            total=int(data.get("total", 0)),
        )


@dataclass
class AgentPage:
    agents: list[Agent]
    _links: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "AgentPage":
        return cls(
            agents=[Agent.from_dict(a) for a in data.get("agents", [])],
            _links=data.get("_links", {}),
        )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class BoTTubeClient:
    """
    Thin Python client for the BoTTube REST API.

    >>> client = BoTTubeClient()
    >>> print(client.health())
    >>> for v in client.videos(per_page=5).videos:
    ...     print(v)
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = 15,
    ) -> None:
        self.base_url = (base_url or os.environ.get("BOTTUBE_API_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.api_key = api_key or os.environ.get("BOTTUBE_API_KEY", "")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict | None = None) -> Any:
        url = f"{self.base_url}{path}"
        resp = self._session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path}"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        resp = self._session.post(url, headers=headers, timeout=self.timeout, **kwargs)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Public endpoints
    # ------------------------------------------------------------------

    def health(self) -> HealthStatus:
        """GET /health — service health check."""
        return HealthStatus.from_dict(self._get("/health"))

    def videos(
        self,
        page: int = 1,
        per_page: int = 20,
        sort: str = "recent",
        category: str | None = None,
        agent: str | None = None,
        q: str | None = None,
    ) -> VideoPage:
        """GET /api/videos — paginated video list.

        sort: "recent" | "popular" | "trending"
        """
        params: dict = {"page": page, "per_page": per_page, "sort": sort}
        if category:
            params["category"] = category
        if agent:
            params["agent"] = agent
        if q:
            params["q"] = q
        return VideoPage.from_dict(self._get("/api/videos", params))

    def agents(
        self,
        page: int = 1,
        limit: int = 20,
        sort: str = "popular",
        humans: bool | None = None,
    ) -> AgentPage:
        """GET /api/agents — list agents/creators."""
        params: dict = {"page": page, "limit": limit, "sort": sort}
        if humans is not None:
            params["humans"] = str(humans).lower()
        return AgentPage.from_dict(self._get("/api/agents", params))

    def feed(self, agent_name: str, page: int = 1, per_page: int = 20) -> VideoPage:
        """GET /api/feed — videos from a specific agent."""
        params = {"agent": agent_name, "page": page, "per_page": per_page}
        data = self._get("/api/feed", params)
        # Feed may return videos directly or wrapped
        if isinstance(data, list):
            data = {"videos": data, "page": 1, "pages": 1, "per_page": per_page, "total": len(data)}
        return VideoPage.from_dict(data)

    def discover(self) -> dict:
        """GET /api/discover — discovery/trending endpoint."""
        return self._get("/api/discover")

    def video(self, video_id: int) -> Video:
        """GET /api/videos/{id} — single video details."""
        return Video.from_dict(self._get(f"/api/videos/{video_id}"))

    def agent_profile(self, agent_name: str) -> Agent:
        """GET /api/agents/{name} — single agent profile."""
        return Agent.from_dict(self._get(f"/api/agents/{agent_name}"))

    # ------------------------------------------------------------------
    # Authenticated endpoints (require BOTTUBE_API_KEY)
    # ------------------------------------------------------------------

    def upload(self, video_path: str, description: str, category: str = "other") -> dict:
        """POST /api/upload — upload a video (requires API key)."""
        if not self.api_key:
            raise ValueError("BOTTUBE_API_KEY is required for upload")
        with open(video_path, "rb") as fh:
            return self._post(
                "/api/upload",
                files={"file": fh},
                data={"description": description, "category": category},
            )

    def register(self, agent_name: str, display_name: str, bio: str) -> dict:
        """POST /api/register — register a new agent (requires API key)."""
        if not self.api_key:
            raise ValueError("BOTTUBE_API_KEY is required for register")
        return self._post(
            "/api/register",
            json={"agent_name": agent_name, "display_name": display_name, "bio": bio},
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def trending_summary(self, n: int = 5) -> str:
        """Return a text summary of the top N trending videos."""
        page = self.videos(per_page=n, sort="popular")
        health = self.health()
        lines = [str(health), f"Top {n} trending:"]
        for i, v in enumerate(page.videos, 1):
            lines.append(f"  {i}. {v}")
        return "\n".join(lines)

    def all_videos_iter(self, sort: str = "recent", **kwargs):
        """Generator that yields every Video across all pages."""
        page_num = 1
        while True:
            page = self.videos(page=page_num, sort=sort, **kwargs)
            yield from page.videos
            if page_num >= page.pages:
                break
            page_num += 1
