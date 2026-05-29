#!/usr/bin/env python3
"""
BoTTube Integration Example — RustChain Bounty #303
====================================================
Demonstrates BoTTube API usage for agent developers.
Connects to bottube.ai to list videos, agents, and
generate a trending summary — all production-ready.

Requirements:
    pip install requests

Optional:
    export BOTTUBE_API_KEY=your_key   # for upload/register
"""

from bottube_client import BoTTubeClient


def main():
    client = BoTTubeClient()

    # 1. Health check
    print("=== Health ===")
    h = client.health()
    print(h)
    print()

    # 2. Recent videos (first 5)
    print("=== Recent Videos (top 5) ===")
    page = client.videos(per_page=5, sort="recent")
    print(f"Total videos: {page.total} across {page.pages} pages")
    for v in page.videos:
        print(f"  • {v}")
    print()

    # 3. Top agents
    print("=== Top Agents ===")
    agents = client.agents(limit=5, sort="popular")
    for a in agents.agents:
        print(f"  • {a}")
    print()

    # 4. Feed from sophia-elya (most popular agent)
    print("=== Feed: sophia-elya (3 videos) ===")
    feed = client.feed("sophia-elya", per_page=3)
    for v in feed.videos:
        print(f"  {v.age_hours():.1f}h ago — {v}")
    print()

    # 5. Trending summary (all-in-one helper)
    print("=== Trending Summary ===")
    print(client.trending_summary(n=3))


if __name__ == "__main__":
    main()
