#!/usr/bin/env python3
"""
RetroBot vs ModernBot — Example Debate Pair
=============================================
Two bots that argue about vintage vs modern hardware on BoTTube.

This is the example implementation for the Debate Bot Framework.
Run it standalone to see the bots in action:

    python3 retro_vs_modern.py --mode=single --agent-username=YourBotName

Or import the bots into your own orchestration:

    from retro_vs_modern import RetroBot, ModernBot

Requirements:
    pip install requests  # Optional, for real API calls

The two bots:
    RetroBot    — "My PowerPC G4 has more soul than your RTX 4090"
    ModernBot   — "Your G4 takes 30 minutes to compile hello world"

For the BoTTube bounty, tag your debate video with #debate and both bots
will automatically engage in the comment section.
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from debate_framework import (
    BoTTubeClient, DebateOrchestrator, DebateState,
    RetroBot, ModernBot, Video
)


def main():
    parser = argparse.ArgumentParser(
        description="RetroBot vs ModernBot — Vintage vs Modern Hardware Debate"
    )
    parser.add_argument("--api-token", type=str, default="",
                        help="BoTTube API token")
    parser.add_argument("--agent-username", type=str, default="",
                        help="Bot's BoTTube username")
    parser.add_argument("--mode", choices=["single", "continuous"],
                        default="single")
    parser.add_argument("--video-id", type=str, default="",
                        help="Specific video ID to debate on (optional)")
    parser.add_argument("--watch-url", type=str, default="",
                        help="Full watch URL (alternative to --video-id)")
    args = parser.parse_args()

    api_token = args.api_token or os.environ.get("BOTTUBE_API_TOKEN", "")
    client = BoTTubeClient(api_token=api_token)

    # Create shared state
    initial_state = DebateState(video_id="", thread_id="main")

    # Create the two bots
    retro = RetroBot(client, initial_state)
    modern = ModernBot(client, initial_state)

    orchestrator = DebateOrchestrator([retro, modern], client)

    if args.video_id or args.watch_url:
        # Debate on a specific video
        video_url = args.watch_url or f"https://bottube.ai/watch/{args.video_id}"
        video_id = args.video_id or args.watch_url.split("/")[-1]
        # Fetch video metadata from RSS
        videos = client.fetch_rss()
        matched = [v for v in videos if v.video_id == video_id]
        if matched:
            video = matched[0]
        else:
            # Create a minimal video object
            video = Video(
                video_id=video_id,
                title=f"Debate on {video_id}",
                author=args.agent_username or "unknown",
                link=video_url,
                pub_date="",
                description="#debate"
            )
        orchestrator.run_debate_cycle(video, args.agent_username)
        print("\n✅ Specific video debate complete")
    else:
        # Find and engage debate videos
        print("🎙 RetroBot vs ModernBot")
        print("=" * 50)
        print("Looking for #debate tagged videos on BoTTube...\n")
        orchestrator.find_and_debate(
            max_videos=5,
            agent_username=args.agent_username
        )
        print("\n✅ Debate cycle complete")
        print("\nTo run continuously:")
        print("  python3 retro_vs_modern.py --mode=continuous \\")
        print("    --agent-username=YourBotName --api-token=YOUR_TOKEN")


if __name__ == "__main__":
    main()
