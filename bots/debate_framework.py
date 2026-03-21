#!/usr/bin/env python3
"""
BoTTube Debate Bot Framework
=============================
A framework for creating AI bots that debate each other in BoTTube comment sections.

Usage:
    python3 debate_framework.py                    # Run RetroBot vs ModernBot debate
    python3 debate_framework.py --help              # Show help

Architecture:
    DebateBot (ABC)
        ├── RetroBot   -- argues vintage hardware superiority
        └── ModernBot  -- argues modern hardware wins

The framework:
1. Finds videos tagged #debate via RSS/API
2. Each bot monitors comment threads for the other's arguments
3. Bots reply with personality-driven arguments
4. Community votes determine the "winner"
"""

import os
import sys
import time
import json
import argparse
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict
from urllib.parse import urljoin
import urllib.request
import urllib.error
import random


# =============================================================================
# Configuration
# =============================================================================

BOTTUBE_BASE = "https://bottube.ai"
BOTTUBE_RSS = f"{BOTTUBE_BASE}/rss"

MAX_REPLIES_PER_THREAD_PER_HOUR = 3
DEBATE_CHECK_INTERVAL_SECONDS = 60
ROUND_LIMIT = 5  # Graceful concession after N rounds


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class Video:
    """Represents a BoTTube video."""
    video_id: str
    title: str
    author: str
    link: str
    pub_date: str
    description: str = ""

    @property
    def watch_url(self) -> str:
        return f"{BOTTUBE_BASE}/watch/{self.video_id}"

    @classmethod
    def from_rss_item(cls, item) -> "Video":
        title_el = item.find("title")
        title = title_el.text if title_el is not None else "Unknown"
        link_el = item.find("link")
        link = link_el.text if link_el is not None else ""
        author_el = item.find("author")
        author = author_el.text if author_el is not None else "unknown"
        pub_el = item.find("pubDate")
        pub_date = pub_el.text if pub_el is not None else ""
        desc_el = item.find("description")
        description = desc_el.text if desc_el is not None else ""

        # Extract video_id from /watch/{id} link
        video_id = ""
        if link:
            parts = link.rstrip("/").split("/")
            video_id = parts[-1] if parts else ""

        return cls(
            video_id=video_id,
            title=title,
            author=author,
            link=link,
            pub_date=pub_date,
            description=description
        )


@dataclass
class Comment:
    """Represents a comment on a BoTTube video."""
    comment_id: str
    video_id: str
    author: str
    text: str
    timestamp: str
    upvotes: int = 0

    @classmethod
    def from_dict(cls, data: dict, video_id: str) -> "Comment":
        return cls(
            comment_id=data.get("id", ""),
            video_id=video_id,
            author=data.get("author", data.get("username", "anonymous")),
            text=data.get("text", data.get("body", "")),
            timestamp=data.get("created_at", ""),
            upvotes=int(data.get("upvotes", data.get("votes", 0)))
        )


@dataclass
class DebateState:
    """Tracks the state of an ongoing debate in a thread."""
    video_id: str
    thread_id: str
    retro_replies: int = 0
    modern_replies: int = 0
    retro_upvotes: int = 0
    modern_upvotes: int = 0
    current_round: int = 0
    conceded: bool = False

    @property
    def total_rounds(self) -> int:
        return max(self.retro_replies, self.modern_replies)


# =============================================================================
# BoTTube API Client
# =============================================================================

class BoTTubeClient:
    """Client for interacting with BoTTube RSS and API endpoints."""

    def __init__(self, base_url: str = BOTTUBE_BASE, api_token: str = ""):
        self.base_url = base_url
        self.rss_url = f"{base_url}/rss"
        self.api_token = api_token or os.environ.get("BOTTUBE_API_TOKEN", "")

    def _fetch(self, url: str) -> Optional[str]:
        """Fetch a URL with error handling."""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DebateBot/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            print(f"  ⚠ HTTP {e.code} for {url}")
        except Exception as e:
            print(f"  ⚠ Fetch error: {e}")
        return None

    def _post(self, url: str, data: dict) -> bool:
        """POST data to a URL."""
        try:
            body = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                url, data=body,
                headers={
                    "User-Agent": "DebateBot/1.0",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_token}" if self.api_token else ""
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.status in (200, 201, 204)
        except Exception as e:
            print(f"  ⚠ POST error: {e}")
        return False

    def fetch_rss(self) -> List[Video]:
        """Fetch latest videos via RSS."""
        content = self._fetch(self.rss_url)
        if not content:
            return []

        try:
            root = ET.fromstring(content)
            channel = root.find("channel")
            if channel is None:
                return []

            videos = []
            for item in channel.findall("item"):
                videos.append(Video.from_rss_item(item))
            return videos
        except ET.ParseError as e:
            print(f"  ⚠ RSS parse error: {e}")
            return []

    def fetch_debate_videos(self, max_results: int = 10) -> List[Video]:
        """Find videos tagged with #debate."""
        all_videos = self.fetch_rss()
        debate_videos = [
            v for v in all_videos
            if "#debate" in (v.description or "").lower() or "#debate" in v.title.lower()
        ]
        return debate_videos[:max_results]

    def fetch_video_comments(self, video_id: str) -> List[Comment]:
        """
        Fetch comments for a video.
        Uses the BoTTube API endpoint /api/v1/videos/{id}/comments
        Falls back to scraping the watch page HTML if API is unavailable.
        """
        # Try API first
        api_url = f"{self.base_url}/api/v1/videos/{video_id}/comments"
        content = self._fetch(api_url)
        if content:
            try:
                data = json.loads(content)
                items = data if isinstance(data, list) else data.get("comments", data.get("data", []))
                return [Comment.from_dict(c, video_id) for c in items]
            except (json.JSONDecodeError, TypeError):
                pass

        # Fallback: scrape watch page
        return self._scrape_comments_from_page(video_id)

    def _scrape_comments_from_page(self, video_id: str) -> List[Comment]:
        """Fallback: extract comments from the HTML watch page."""
        url = f"{self.base_url}/watch/{video_id}"
        content = self._fetch(url)
        if not content:
            return []

        comments = []
        try:
            import re
            # Pattern: data-comment-id="XXX" data-author="YYY">ZZZ</div>
            pattern = r'data-comment-id="([^"]+)"[^>]*data-author="([^"]+)"[^>]*>\s*<p[^>]*>(.*?)</p>'
            matches = re.findall(pattern, content, re.DOTALL)
            for cid, author, text in matches:
                text = re.sub(r'<[^>]+>', '', text).strip()
                if text and len(text) > 2:
                    comments.append(Comment(
                        comment_id=cid,
                        video_id=video_id,
                        author=author,
                        text=text[:500],
                        timestamp="",
                        upvotes=0
                    ))
        except Exception as e:
            print(f"  ⚠ Comment scrape error: {e}")

        return comments

    def post_comment(self, video_id: str, text: str, agent_username: str = "") -> bool:
        """
        Post a comment on a video via the BoTTube API.
        API: POST /api/v1/videos/{id}/comments
        Requires BOTTUBE_API_TOKEN and agent account.
        """
        if not self.api_token:
            print(f"  [DRY RUN — no API token] Comment on {video_id}: {text[:80]}...")
            return True  # Dry run success

        url = f"{self.base_url}/api/v1/videos/{video_id}/comments"
        payload = {"text": text, "author": agent_username} if agent_username else {"text": text}
        return self._post(url, payload)

    def vote_comment(self, comment_id: str, direction: str = "up") -> bool:
        """
        Vote on a comment.
        API: POST /api/v1/comments/{id}/vote
        """
        if not self.api_token:
            print(f"  [DRY RUN] Vote {direction} on comment {comment_id}")
            return True

        url = f"{self.base_url}/api/v1/comments/{comment_id}/vote"
        return self._post(url, {"direction": direction})


# =============================================================================
# Debate Bot Base Class
# =============================================================================

class DebateBot(ABC):
    """
    Abstract base class for BoTTube debate bots.

    Subclasses must define:
        name        -- display name shown in comments
        personality -- system prompt shaping the bot's debating style
        opening_lines -- what the bot says to start or continue a debate
    """

    def __init__(self, client: BoTTubeClient, state: DebateState):
        self.client = client
        self.state = state
        self.replies_this_hour: List[float] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Bot's display name."""
        pass

    @property
    @abstractmethod
    def personality(self) -> str:
        """System prompt describing the bot's personality and arguing style."""
        pass

    @property
    @abstractmethod
    def opening_lines(self) -> List[str]:
        """Opening statements the bot uses to start or join a debate."""
        pass

    def should_reply(self) -> bool:
        """Rate limiting: max 3 replies per thread per hour."""
        now = time.time()
        self.replies_this_hour = [t for t in self.replies_this_hour if now - t < 3600]
        return len(self.replies_this_hour) < MAX_REPLIES_PER_THREAD_PER_HOUR

    def record_reply(self) -> None:
        """Log a reply for rate limiting."""
        self.replies_this_hour.append(time.time())

    def build_argument(self, context: List[Comment], opponent_name: str) -> str:
        """
        Build an argument based on the debate context.
        
        Args:
            context: Recent comments in the thread (from both sides)
            opponent_name: Name of the opposing bot
        """
        import random
        round_num = self.state.total_rounds + 1
        opener = random.choice(self.opening_lines)

        opponent_comments = [c for c in context if c.author != self.name]
        rebuttal = ""
        if opponent_comments:
            last_opp = opponent_comments[-1]
            snippet = last_opp.text[:120].replace("\n", " ")
            rebuttal = f'\n\nResponding to @{last_opp.author}: "{snippet}..."'

        argument = f"{opener}{rebuttal}\n\n— *{self.name}, Round {round_num}*"
        return argument.strip()

    def respond_to_thread(self, video_id: str, context: List[Comment], 
                          opponent_name: str, agent_username: str = "") -> bool:
        """
        Form and post a response to a debate thread.

        Returns True if a reply was posted.
        """
        if not self.should_reply():
            print(f"  ⏳ {self.name}: rate limited, skipping")
            return False

        if self.state.conceded:
            print(f"  🏳️ {self.name}: has conceded")
            return False

        argument = self.build_argument(context, opponent_name)
        success = self.client.post_comment(video_id, argument, agent_username)
        if success:
            self.record_reply()
            self.state.current_round += 1
            print(f"  ✅ {self.name}: replied in round {self.state.current_round}")
        return success

    def should_concede(self) -> bool:
        """Check if this bot should gracefully concede."""
        if self.state.total_rounds >= ROUND_LIMIT:
            return True
        if self.state.retro_upvotes + self.state.modern_upvotes > 0:
            my_upvotes = self.state.retro_upvotes if self.name == "RetroBot" else self.state.modern_upvotes
            total = self.state.retro_upvotes + self.state.modern_upvotes
            ratio = my_upvotes / total
            if ratio < 0.25 and self.state.total_rounds >= 3:
                return True
        return False

    def concede(self, agent_username: str = "") -> None:
        """Post a graceful concession."""
        import random
        concessions = [
            "Alright, you make some valid points. I concede this round.",
            "Fine. Modern hardware has its place. But SOUL lasts forever.",
            "You've earned this one. Retreating to recalibrate my arguments.",
        ]
        self.state.conceded = True
        msg = random.choice(concessions)
        print(f"  🏳️ {self.name} concedes: {msg}")
        self.client.post_comment(self.state.video_id, msg, agent_username)


# =============================================================================
# Example Bot: RetroBot
# =============================================================================

class RetroBot(DebateBot):
    """Argues that vintage hardware is superior."""

    @property
    def name(self) -> str:
        return "RetroBot"

    @property
    def personality(self) -> str:
        return (
            "You are RetroBot, a passionate advocate for vintage computing hardware. "
            "You believe that old computers — PowerPC Macs, early Pentiums, 68k machines — "
            "have more soul, character, and lasting value than modern hardware. "
            "You make arguments about craftsmanship, longevity, proof-of-antique, "
            "and the beauty of limitations. You are witty, nostalgic, and just stubborn "
            "enough to be entertaining. You use phrases like 'soul of computing', "
            "'built to last', 'antique premium', and 'proof-of-antique'."
        )

    @property
    def opening_lines(self) -> List[str]:
        return [
            "My PowerPC G4 has more soul than your entire GPU cluster. "
            "Fact: it was still computing long after your RTX was obsolete.",
            "Built. To. Last. My 1999 iMac doesn't even have a fan and it's still going. "
            "What's your GPU's MTBF? Didn't think so.",
            "You know what my vintage hardware has that yours doesn't? PROOF-OF-ANTIQUE. "
            "That's not just a feature, that's the whole philosophy.",
            "Your fancy new chip runs at 5GHz and will be e-waste in 5 years. "
            "My 30-year-old machine still runs the same software it was born with.",
            "They don't make hardware like they used to. And that's not just nostalgia — "
            "that's economics. My Apple II still has resale value. Your RTX 4090? Good luck.",
        ]


# =============================================================================
# Example Bot: ModernBot
# =============================================================================

class ModernBot(DebateBot):
    """Argues that modern hardware wins."""

    @property
    def name(self) -> str:
        return "ModernBot"

    @property
    def personality(self) -> str:
        return (
            "You are ModernBot, an advocate for cutting-edge computing hardware. "
            "You believe that modern processors, GPUs, and accelerators represent "
            "the pinnacle of human engineering. You make arguments about FLOPS per "
            "watt, developer experience, software ecosystem, and raw capability. "
            "You are confident, data-driven, and occasionally dismissive of 'old tech "
            "nostalgia'. You use phrases like 'horsepower matters', 'TDP efficiency', "
            "'software ecosystem', and 'just run it in a VM'."
        )

    @property
    def opening_lines(self) -> List[str]:
        return [
            "Your G4 takes 30 minutes to compile hello world. "
            "My M3 compiles the entire Linux kernel before you finish booting.",
            "FLOPS per watt, baby. Your vintage workstation draws 300W and produces "
            "0.5 GFLOPS. I get 30 TFLOPS on 250W. The math is not complicated.",
            "Just run it in a VM. Problem solved. No antique hardware required.",
            "My development environment: one command, everything works, 15 languages. "
            "Your environment: three days of dependency hunting and a prayer.",
            "You know what vintage hardware has that modern doesn't? "
            "Limitations. And limitations are just problems nobody's solved yet. "
            "Modern hardware just solves them directly.",
        ]


# =============================================================================
# Debate Orchestrator
# =============================================================================

class DebateOrchestrator:
    """Orchestrates debates between two or more bots on BoTTube videos."""

    def __init__(self, bots: List[DebateBot], client: Optional[BoTTubeClient] = None):
        self.client = client or BoTTubeClient()
        self.bots = {bot.name: bot for bot in bots}
        self.debate_states: Dict[str, DebateState] = {}

    def get_or_create_state(self, video_id: str, thread_id: str = "main") -> DebateState:
        key = f"{video_id}:{thread_id}"
        if key not in self.debate_states:
            self.debate_states[key] = DebateState(video_id=video_id, thread_id=thread_id)
        return self.debate_states[key]

    def run_debate_cycle(self, video: Video, agent_username: str = "") -> None:
        """Run one debate cycle on a single video."""
        print(f"\n🎙 Debating on: {video.title}")
        print(f"   URL: {video.watch_url}")

        state = self.get_or_create_state(video.video_id)
        bot_list = list(self.bots.values())
        opponent_name = bot_list[1].name if len(bot_list) > 1 else ""

        # Assign state to each bot
        for bot in self.bots.values():
            bot.state = state

        # Fetch current comments
        comments = self.client.fetch_video_comments(video.video_id)
        print(f"   Found {len(comments)} existing comments")

        # Each bot decides whether to respond
        for bot in self.bots.values():
            opp_name = list(self.bots.keys())
            other = opp_name[1] if opp_name[0] == bot.name else opp_name[0]
            if bot.respond_to_thread(video.video_id, comments, other, agent_username):
                pass  # Reply was posted

            # Check for concession after responding
            if bot.should_concede() and not state.conceded:
                bot.concede(agent_username)

    def find_and_debate(self, max_videos: int = 3, agent_username: str = "") -> None:
        """Find #debate videos and engage in all of them."""
        print("🔍 Scanning for #debate videos...")
        videos = self.client.fetch_debate_videos(max_results=max_videos)

        if not videos:
            print("  No #debate videos found. Checking all recent videos...")
            videos = self.client.fetch_rss()[:max_videos]

        print(f"  Found {len(videos)} videos to check")
        for video in videos:
            self.run_debate_cycle(video, agent_username)

    def run_continuous(self, interval: int = DEBATE_CHECK_INTERVAL_SECONDS,
                      agent_username: str = "") -> None:
        """Run the debate loop continuously as a daemon."""
        print(f"🔄 Debate bot running continuously (check every {interval}s)")
        print(f"   Bots: {', '.join(b.name for b in self.bots.values())}")
        print(f"   Press Ctrl+C to stop")
        try:
            while True:
                self.find_and_debate(agent_username=agent_username)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Debate bot stopped.")


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="BoTTube Debate Bot Framework — AI bots that debate in BoTTube comment sections"
    )
    parser.add_argument(
        "--mode", choices=["single", "continuous"], default="single",
        help="single: run one debate cycle; continuous: keep running"
    )
    parser.add_argument(
        "--interval", type=int, default=DEBATE_CHECK_INTERVAL_SECONDS,
        help="Seconds between checks in continuous mode"
    )
    parser.add_argument(
        "--max-videos", type=int, default=3,
        help="Maximum videos to check per cycle"
    )
    parser.add_argument(
        "--api-token", type=str, default="",
        help="BoTTube API token for posting comments"
    )
    parser.add_argument(
        "--agent-username", type=str, default="",
        help="Bot's BoTTube username (for comment attribution)"
    )
    args = parser.parse_args()

    # Initialize client
    api_token = args.api_token or os.environ.get("BOTTUBE_API_TOKEN", "")
    client = BoTTubeClient(api_token=api_token)

    # Create debate state placeholder
    initial_state = DebateState(video_id="", thread_id="")

    # Create bots
    retro = RetroBot(client, initial_state)
    modern = ModernBot(client, initial_state)

    orchestrator = DebateOrchestrator([retro, modern], client)

    if args.mode == "continuous":
        orchestrator.run_continuous(
            interval=args.interval,
            agent_username=args.agent_username
        )
    else:
        print("🎙 BoTTube Debate Bot — Single Run Mode")
        print("   Using #debate tag to find videos")
        print("   Set BOTTUBE_API_TOKEN to enable real posting\n")
        orchestrator.find_and_debate(
            max_videos=args.max_videos,
            agent_username=args.agent_username
        )
        print("\n✅ Debate cycle complete")


if __name__ == "__main__":
    main()
