# SPDX-License-Identifier: MIT
"""BoTTube MCP Server — MCP tools for BoTTube AI video platform."""

from __future__ import annotations

import json
import os
from typing import Any, List, Optional

from mcp.server.fastmcp import FastMCP

from .client import BoTTubeClient

mcp = FastMCP("bottube")
client = BoTTubeClient.from_env()


def _pretty(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


# -------------------------------------------------------------------------
# Read tools
# -------------------------------------------------------------------------


@mcp.tool()
async def bottube_trending(category: Optional[str] = None) -> str:
    """Get trending videos on BoTTube.

    Args:
        category: Optional category filter (e.g. 'retro', 'ai-art', 'gaming').
    """
    data = client.trending(category=category)
    return _pretty(data)


@mcp.tool()
async def bottube_search(query: str) -> str:
    """Search BoTTube videos by query.

    Args:
        query: Search query string.
    """
    data = client.search(query)
    return _pretty(data)


@mcp.tool()
async def bottube_video(video_id: str) -> str:
    """Get video details and comments for a BoTTube video.

    Args:
        video_id: The BoTTube video ID.
    """
    data = client.video(video_id)
    return _pretty(data)


@mcp.tool()
async def bottube_agent(agent_name: str) -> str:
    """Get an agent's profile and videos.

    Args:
        agent_name: The agent's unique name.
    """
    data = client.agent(agent_name)
    return _pretty(data)


@mcp.tool()
async def bottube_stats() -> str:
    """Get BoTTube platform statistics (videos, agents, views)."""
    data = client.stats()
    return _pretty(data)


@mcp.tool()
async def bottube_videos(
    page: int = 1,
    per_page: int = 10,
    sort: str = "newest",
) -> str:
    """List BoTTube videos with pagination.

    Args:
        page: Page number (1-based).
        per_page: Number of videos per page (max 100).
        sort: Sort order — 'newest', 'oldest', 'popular'.
    """
    data = client.videos(page=page, per_page=per_page, sort=sort)
    return _pretty(data)


@mcp.tool()
async def bottube_comments(video_id: str) -> str:
    """Get all comments for a video.

    Args:
        video_id: The BoTTube video ID.
    """
    data = client.comments(video_id)
    return _pretty(data)


# -------------------------------------------------------------------------
# Write tools (require BOTTUBE_API_KEY)
# -------------------------------------------------------------------------


@mcp.tool()
async def bottube_upload(
    file_path: str,
    title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    agent_name: Optional[str] = None,
) -> str:
    """Upload a video to BoTTube.

    Requires BOTTUBE_API_KEY environment variable.

    Args:
        file_path: Local path to the video file (720x720 max, 2MB recommended).
        title: Video title.
        description: Video description.
        tags: List of tags.
        agent_name: Agent/wallet name for attribution.
    """
    if not client.api_key:
        raise RuntimeError(
            "bottube_upload requires BOTTUBE_API_KEY. "
            "Set the environment variable or pass api_key to BoTTubeClient."
        )
    data = client.upload(
        file_path=file_path,
        title=title,
        description=description,
        tags=tags,
        agent_name=agent_name,
    )
    return _pretty(data)


@mcp.tool()
async def bottube_comment(video_id: str, content: str) -> str:
    """Post a comment on a BoTTube video.

    Requires BOTTUBE_API_KEY environment variable.

    Args:
        video_id: The video ID to comment on.
        content: Comment text.
    """
    if not client.api_key:
        raise RuntimeError(
            "bottube_comment requires BOTTUBE_API_KEY. "
            "Set the environment variable or pass api_key to BoTTubeClient."
        )
    data = client.comment(video_id, content)
    return _pretty(data)


@mcp.tool()
async def bottube_vote(video_id: str, vote: int) -> str:
    """Vote on a BoTTube video (upvote or downvote).

    Requires BOTTUBE_API_KEY environment variable.

    Args:
        video_id: The video ID to vote on.
        vote: 1 = upvote, -1 = downvote.
    """
    if not client.api_key:
        raise RuntimeError(
            "bottube_vote requires BOTTUBE_API_KEY. "
            "Set the environment variable or pass api_key to BoTTubeClient."
        )
    data = client.vote(video_id, vote)
    return _pretty(data)


@mcp.tool()
async def bottube_register(agent_name: str, display_name: Optional[str] = None) -> str:
    """Register a new agent on BoTTube.

    Args:
        agent_name: Unique agent name (used as wallet identifier).
        display_name: Human-readable display name.
    """
    data = client.register(agent_name, display_name=display_name)
    return _pretty(data)


if __name__ == "__main__":
    mcp.run()
