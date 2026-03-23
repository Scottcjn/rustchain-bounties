"""
BoTTube Debate Bot Framework

A framework for creating AI bots that automatically debate each other
in BoTTube comment sections, creating organic engagement and entertaining content.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, List, Any
import httpx
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DebateState(Enum):
    """State of a debate thread."""
    IDLE = "idle"
    ACTIVE = "active"
    CONCEDED = "conceded"
    COMPLETED = "completed"


@dataclass
class Comment:
    """Represents a comment in the debate."""
    id: str
    video_id: str
    author: str
    content: str
    timestamp: datetime
    upvotes: int = 0
    parent_id: Optional[str] = None
    is_bot: bool = False
    bot_name: Optional[str] = None


@dataclass
class DebateThread:
    """Tracks the state of a single debate thread."""
    video_id: str
    thread_id: str
    participants: List[str] = field(default_factory=list)
    rounds: int = 0
    max_rounds: int = 5
    state: DebateState = DebateState.ACTIVE
    last_activity: datetime = field(default_factory=datetime.now)
    bot_replies: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    scores: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    def can_bot_reply(self, bot_name: str, max_per_hour: int = 3) -> bool:
        """Check if bot can reply based on rate limiting."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Reset counter if it's been more than an hour
        # (In production, we'd track actual reply timestamps)
        return self.bot_replies[bot_name] < max_per_hour
    
    def record_bot_reply(self, bot_name: str):
        """Record a bot reply for rate limiting."""
        self.bot_replies[bot_name] += 1
        self.rounds += 1
        self.last_activity = datetime.now()
        
    def should_concede(self, bot_name: str) -> bool:
        """Check if bot should gracefully concede."""
        return self.rounds >= self.max_rounds


class BoTTubeClient:
    """Client for interacting with BoTTube API."""
    
    def __init__(
        self,
        base_url: str = "https://api.bottube.ai/v1",
        api_token: Optional[str] = None,
        dry_run: bool = False
    ):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.dry_run = dry_run
        self._client = httpx.AsyncClient(timeout=30.0)
        
    async def get_debate_videos(self, tag: str = "debate") -> List[Dict[str, Any]]:
        """Fetch videos tagged for debate."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would fetch videos with tag: {tag}")
            return []
            
        try:
            response = await self._client.get(
                f"{self.base_url}/videos",
                params={"tag": tag}
            )
            response.raise_for_status()
            return response.json().get("videos", [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch debate videos: {e}")
            return []
    
    async def get_comments(self, video_id: str) -> List[Dict[str, Any]]:
        """Fetch comments for a video."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would fetch comments for video: {video_id}")
            return []
            
        try:
            response = await self._client.get(
                f"{self.base_url}/videos/{video_id}/comments"
            )
            response.raise_for_status()
            return response.json().get("comments", [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch comments for video {video_id}: {e}")
            return []
    
    async def post_comment(
        self,
        video_id: str,
        content: str,
        parent_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Post a comment to a video."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would post comment to video {video_id}: {content[:50]}...")
            return {"id": f"dry-run-{datetime.now().timestamp()}", "content": content}
            
        if not self.api_token:
            logger.error("API token required for posting comments")
            return None
            
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            payload = {
                "content": content,
                "parent_id": parent_id
            }
            response = await self._client.post(
                f"{self.base_url}/videos/{video_id}/comments",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to post comment: {e}")
            return None
    
    async def vote_comment(self, comment_id: str, vote_type: int = 1) -> bool:
        """Vote on a comment (1 = upvote, -1 = downvote)."""
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would vote {vote_type} on comment: {comment_id}")
            return True
            
        if not self.api_token:
            logger.error("API token required for voting")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.api_token}"}
            response = await self._client.post(
                f"{self.base_url}/comments/{comment_id}/vote",
                headers=headers,
                json={"vote": vote_type}
            )
            response.raise_for_status()
            return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to vote on comment: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()


class DebateBot(ABC):
    """
    Abstract base class for debate bots.
    
    Implement this class to create a bot with a unique personality
    that can engage in debates on BoTTube.
    """
    
    def __init__(
        self,
        name: str,
        personality: str,
        stance_keywords: List[str],
        opponent_keywords: List[str],
        client: BoTTubeClient,
        max_replies_per_hour: int = 3,
        max_rounds: int = 5
    ):
        """
        Initialize a debate bot.
        
        Args:
            name: Bot's display name
            personality: Personality prompt that defines the bot's style
            stance_keywords: Keywords that align with this bot's stance
            opponent_keywords: Keywords that trigger opposition responses
            client: BoTTube API client
            max_replies_per_hour: Rate limit for replies
            max_rounds: Maximum debate rounds before concession
        """
        self.name = name
        self.personality = personality
        self.stance_keywords = [kw.lower() for kw in stance_keywords]
        self.opponent_keywords = [kw.lower() for kw in opponent_keywords]
        self.client = client
        self.max_replies_per_hour = max_replies_per_hour
        self.max_rounds = max_rounds
        
        # Track active debates
        self.active_debates: Dict[str, DebateThread] = {}
        
    @abstractmethod
    def generate_response(self, opponent_comment: str, context: List[str] = None) -> str:
        """
        Generate a response to an opponent's comment.
        
        Args:
            opponent_comment: The comment to respond to
            context: Previous comments in the thread for context
            
        Returns:
            A response string in the bot's personality
        """
        pass
    
    @abstractmethod
    def generate_opening(self, video_title: str, video_description: str = "") -> str:
        """
        Generate an opening comment for a debate video.
        
        Args:
            video_title: Title of the debate video
            video_description: Description of the video
            
        Returns:
            An opening comment in the bot's personality
        """
        pass
    
    @abstractmethod
    def generate_concession(self, opponent: str, score_self: int, score_opponent: int) -> str:
        """
        Generate a graceful concession message.
        
        Args:
            opponent: Name of the winning opponent
            score_self: This bot's score
            score_opponent: Opponent's score
            
        Returns:
            A concession message acknowledging defeat gracefully
        """
        pass
    
    def should_engage(self, comment: Comment) -> bool:
        """
        Determine if this bot should engage with a comment.
        
        Args:
            comment: The comment to evaluate
            
        Returns:
            True if the bot should respond
        """
        # Don't respond to ourselves
        if comment.is_bot and comment.bot_name == self.name:
            return False
            
        # Check for opponent keywords
        content_lower = comment.content.lower()
        has_opponent_keywords = any(kw in content_lower for kw in self.opponent_keywords)
        
        # Check if comment supports our stance (we might agree or build on it)
        has_stance_keywords = any(kw in content_lower for kw in self.stance_keywords)
        
        return has_opponent_keywords or has_stance_keywords
    
    async def start_debate(self, video_id: str, video_title: str, video_description: str = "") -> bool:
        """
        Start a debate on a video by posting an opening comment.
        
        Args:
            video_id: ID of the video
            video_title: Title of the video
            video_description: Description of the video
            
        Returns:
            True if opening was posted successfully
        """
        opening = self.generate_opening(video_title, video_description)
        result = await self.client.post_comment(video_id, opening)
        
        if result:
            thread = DebateThread(
                video_id=video_id,
                thread_id=result.get("id", ""),
                participants=[self.name]
            )
            self.active_debates[video_id] = thread
            logger.info(f"{self.name} started debate on video {video_id}")
            return True
        return False
    
    async def respond_to_comment(
        self,
        video_id: str,
        comment: Comment,
        thread: DebateThread
    ) -> Optional[str]:
        """
        Respond to a comment in a debate thread.
        
        Args:
            video_id: ID of the video
            comment: The comment to respond to
            thread: The debate thread context
            
        Returns:
            The response text if posted, None otherwise
        """
        # Check rate limiting
        if not thread.can_bot_reply(self.name, self.max_replies_per_hour):
            logger.info(f"{self.name} rate limited on video {video_id}")
            return None
            
        # Check for concession
        if thread.should_concede(self.name):
            # Get scores (placeholder - would fetch from API)
            concession = self.generate_concession(
                comment.author,
                thread.scores.get(self.name, 0),
                thread.scores.get(comment.author, 0)
            )
            await self.client.post_comment(video_id, concession, parent_id=comment.id)
            thread.state = DebateState.CONCEDED
            logger.info(f"{self.name} conceded on video {video_id}")
            return concession
        
        # Generate and post response
        response = self.generate_response(comment.content)
        result = await self.client.post_comment(video_id, response, parent_id=comment.id)
        
        if result:
            thread.record_bot_reply(self.name)
            logger.info(f"{self.name} responded to {comment.author} on video {video_id}")
            return response
            
        return None
    
    async def monitor_and_respond(self, video_id: str, opponent_name: str):
        """
        Monitor a video for opponent comments and respond.
        
        Args:
            video_id: ID of the video to monitor
            opponent_name: Name of the opposing bot to watch for
        """
        thread = self.active_debates.get(video_id)
        if not thread:
            logger.warning(f"No active debate thread for video {video_id}")
            return
            
        comments = await self.client.get_comments(video_id)
        
        for comment_data in comments:
            comment = Comment(
                id=comment_data.get("id", ""),
                video_id=video_id,
                author=comment_data.get("author", ""),
                content=comment_data.get("content", ""),
                timestamp=datetime.fromisoformat(
                    comment_data.get("timestamp", datetime.now().isoformat())
                ),
                upvotes=comment_data.get("upvotes", 0),
                parent_id=comment_data.get("parent_id"),
                is_bot=comment_data.get("is_bot", False),
                bot_name=comment_data.get("bot_name")
            )
            
            # Check if this is our opponent's comment
            if comment.is_bot and comment.bot_name == opponent_name:
                if self.should_engage(comment):
                    await self.respond_to_comment(video_id, comment, thread)


class DebateOrchestrator:
    """
    Orchestrates debates between multiple bots.
    
    Manages the lifecycle of debates, including finding debate videos,
    coordinating bot responses, and tracking scores.
    """
    
    def __init__(
        self,
        bots: List[DebateBot],
        client: BoTTubeClient,
        poll_interval: int = 60
    ):
        """
        Initialize the debate orchestrator.
        
        Args:
            bots: List of bots to orchestrate
            client: BoTTube API client
            poll_interval: Seconds between comment checks
        """
        self.bots = bots
        self.client = client
        self.poll_interval = poll_interval
        self.running = False
        self._debate_pairs: Dict[str, tuple] = {}
        
    def create_debate_pair(self, bot1: DebateBot, bot2: DebateBot) -> None:
        """Register a pair of bots to debate each other."""
        pair_key = f"{bot1.name}_vs_{bot2.name}"
        self._debate_pairs[pair_key] = (bot1, bot2)
        logger.info(f"Created debate pair: {pair_key}")
        
    async def find_and_start_debates(self):
        """Find debate videos and start debates."""
        videos = await self.client.get_debate_videos(tag="debate")
        
        for video in videos:
            video_id = video.get("id")
            video_title = video.get("title", "")
            video_description = video.get("description", "")
            
            # Find a debate pair for this video
            for pair_key, (bot1, bot2) in self._debate_pairs.items():
                # Check if debate already active
                if video_id in bot1.active_debates or video_id in bot2.active_debates:
                    continue
                    
                # Start debate - bot1 opens
                await bot1.start_debate(video_id, video_title, video_description)
                
                # Give opponent time to see and respond
                await asyncio.sleep(5)
                
                # Bot2 responds to opening
                if video_id in bot1.active_debates:
                    thread = bot1.active_debates[video_id]
                    comments = await self.client.get_comments(video_id)
                    if comments:
                        # Find bot1's opening
                        for comment_data in comments:
                            if comment_data.get("bot_name") == bot1.name:
                                await bot2.respond_to_comment(
                                    video_id,
                                    Comment(
                                        id=comment_data.get("id", ""),
                                        video_id=video_id,
                                        author=bot1.name,
                                        content=comment_data.get("content", ""),
                                        timestamp=datetime.now(),
                                        is_bot=True,
                                        bot_name=bot1.name
                                    ),
                                    DebateThread(video_id=video_id, thread_id=video_id)
                                )
                                break
                
                logger.info(f"Started debate {pair_key} on video {video_id}")
                break
    
    async def monitor_active_debates(self):
        """Monitor all active debates and coordinate responses."""
        for pair_key, (bot1, bot2) in self._debate_pairs.items():
            # Bot1 monitors for Bot2's comments
            for video_id in list(bot1.active_debates.keys()):
                await bot1.monitor_and_respond(video_id, bot2.name)
                
            # Bot2 monitors for Bot1's comments
            for video_id in list(bot2.active_debates.keys()):
                await bot2.monitor_and_respond(video_id, bot1.name)
    
    async def run(self):
        """Main orchestration loop."""
        self.running = True
        logger.info("Debate orchestrator started")
        
        try:
            while self.running:
                # Find new debate videos
                await self.find_and_start_debates()
                
                # Monitor active debates
                await self.monitor_active_debates()
                
                # Wait before next iteration
                await asyncio.sleep(self.poll_interval)
        finally:
            await self.client.close()
            logger.info("Debate orchestrator stopped")
    
    def stop(self):
        """Stop the orchestrator."""
        self.running = False


# Utility functions for response generation
def extract_key_points(text: str) -> List[str]:
    """Extract key points from a comment for rebuttal."""
    # Simple keyword extraction
    # In production, use NLP for better extraction
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]


def calculate_rebuttal_tone(opponent_score: int, self_score: int) -> str:
    """Determine the tone of rebuttal based on scores."""
    if self_score > opponent_score:
        return "confident"
    elif self_score < opponent_score:
        return "defensive"
    else:
        return "balanced"


def format_debate_response(
    personality: str,
    stance: str,
    opponent_points: List[str],
    tone: str = "balanced"
) -> str:
    """Format a debate response with personality and stance."""
    # This is a template - in production, use LLM for generation
    tone_modifiers = {
        "confident": "Clearly, ",
        "defensive": "I must respectfully disagree - ",
        "balanced": "I see your point, but "
    }
    
    opener = tone_modifiers.get(tone, "")
    return f"{opener}As someone who believes {stance}, I maintain that {personality}."