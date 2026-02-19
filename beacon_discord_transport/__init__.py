#!/usr/bin/env python3
"""
Beacon Discord Transport - Error handling, rate limiting, and listener mode.

A robust Discord transport for Beacon with:
- Exponential backoff for rate limits
- Error handling and retry logic
- Listener mode for incoming messages
- Connection resilience
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Any
from enum import Enum

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limit handling strategies."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"


@dataclass
class RateLimitConfig:
    """Configuration for rate limit handling."""
    max_retries: int = 5
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    strategy: RateLimitStrategy = RateLimitStrategy.EXPONENTIAL_BACKOFF
    retry_on_status: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])


@dataclass
class DiscordMessage:
    """Represents a Discord message."""
    id: str
    channel_id: str
    author: str
    content: str
    timestamp: str
    guild_id: Optional[str] = None
    attachments: List[Dict] = field(default_factory=list)
    embeds: List[Dict] = field(default_factory=list)


class DiscordTransportError(Exception):
    """Base exception for Discord transport errors."""
    pass


class RateLimitError(DiscordTransportError):
    """Raised when rate limited."""
    def __init__(self, message: str, retry_after: float = 0):
        super().__init__(message)
        self.retry_after = retry_after


class DiscordTransport:
    """Discord transport with error handling and rate limit retries."""

    def __init__(
        self,
        bot_token: str,
        rate_limit_config: Optional[RateLimitConfig] = None,
    ):
        """
        Initialize Discord transport.
        
        Args:
            bot_token: Discord bot token
            rate_limit_config: Configuration for rate limit handling
        """
        self.bot_token = bot_token
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.base_url = "https://discord.com/api/v10"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bot {bot_token}",
            "Content-Type": "application/json",
        })
        
        # Track rate limits per endpoint
        self._rate_limits: Dict[str, Dict] = {}
        
        # Message listeners
        self._listeners: List[Callable[[DiscordMessage], None]] = []
        
        # Connection state
        self._connected = False
        self._last_heartbeat = None

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on strategy."""
        config = self.rate_limit_config
        
        if config.strategy == RateLimitStrategy.EXPONENTIAL_BACKOFF:
            delay = config.base_delay * (2 ** attempt)
        elif config.strategy == RateLimitStrategy.LINEAR_BACKOFF:
            delay = config.base_delay * attempt
        else:  # FIXED_DELAY
            delay = config.base_delay
        
        # Add jitter (random 0-1 second)
        import random
        delay += random.random()
        
        # Cap at max delay
        return min(delay, config.max_delay)

    def _should_retry(self, status_code: int) -> bool:
        """Check if we should retry based on status code."""
        return status_code in self.rate_limit_config.retry_on_status

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Handle rate limit response."""
        if response.status_code == 429:
            # Check for retry_after header
            retry_after = float(response.headers.get("X-RateLimit-Reset-After", 0))
            if retry_after == 0:
                # Fallback to body parsing
                try:
                    data = response.json()
                    retry_after = float(data.get("retry_after", 1))
                except (json.JSONDecodeError, ValueError):
                    retry_after = self.rate_limit_config.base_delay
            
            raise RateLimitError(
                f"Rate limited. Retry after {retry_after}s",
                retry_after=retry_after
            )

    def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            DiscordTransportError: If all retries exhausted
        """
        url = f"{self.base_url}{endpoint}"
        last_error = None
        
        for attempt in range(self.rate_limit_config.max_retries):
            try:
                response = self.session.request(method, url, **kwargs)
                
                # Handle success
                if response.status_code < 400:
                    return response
                
                # Handle rate limit
                if response.status_code == 429:
                    self._handle_rate_limit(response)
                
                # Check if we should retry
                if self._should_retry(response.status_code):
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Request failed (status {response.status_code}), "
                        f"retrying in {delay:.1f}s (attempt {attempt + 1})"
                    )
                    time.sleep(delay)
                    last_error = DiscordTransportError(
                        f"Request failed with status {response.status_code}"
                    )
                    continue
                
                # Non-retryable error
                response.raise_for_status()
                
            except RateLimitError:
                # Re-raise rate limit errors
                raise
            except requests.exceptions.RequestException as e:
                last_error = DiscordTransportError(f"Request failed: {e}")
                delay = self._calculate_delay(attempt)
                logger.warning(f"Request error: {e}, retrying in {delay:.1f}s")
                time.sleep(delay)
        
        raise last_error or DiscordTransportError("Max retries exhausted")

    # ===== Public API =====

    def send_message(
        self,
        channel_id: str,
        content: str,
        **kwargs
    ) -> Dict:
        """
        Send a message to a Discord channel.
        
        Args:
            channel_id: Discord channel ID
            content: Message content
            **kwargs: Additional message options
            
        Returns:
            Message data from Discord API
        """
        payload = {"content": content, **kwargs}
        
        response = self._request_with_retry(
            "POST",
            f"/channels/{channel_id}/messages",
            json=payload
        )
        
        return response.json()

    def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50,
        before: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get messages from a channel.
        
        Args:
            channel_id: Discord channel ID
            limit: Number of messages to fetch
            before: Message ID to get messages before
            
        Returns:
            List of message objects
        """
        params = {"limit": limit}
        if before:
            params["before"] = before
        
        response = self._request_with_retry(
            "GET",
            f"/channels/{channel_id}/messages",
            params=params
        )
        
        return response.json()

    def add_listener(self, callback: Callable[[DiscordMessage], None]) -> None:
        """
        Add a message listener.
        
        Args:
            callback: Function to call when message received
        """
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[DiscordMessage], None]) -> None:
        """
        Remove a message listener.
        
        Args:
            callback: Listener to remove
        """
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self, message: DiscordMessage) -> None:
        """Notify all listeners of a new message."""
        for listener in self._listeners:
            try:
                listener(message)
            except Exception as e:
                logger.error(f"Listener error: {e}")

    def listen(
        self,
        channel_id: str,
        poll_interval: float = 5.0,
        max_messages: Optional[int] = None,
    ) -> List[DiscordMessage]:
        """
        Listen for new messages in a channel.
        
        This is a simple polling-based listener. For production use,
        consider using Discord's Gateway (WebSocket) API.
        
        Args:
            channel_id: Channel to listen on
            poll_interval: Seconds between polls
            max_messages: Maximum messages to collect (None = infinite)
            
        Returns:
            List of collected messages
        """
        collected = []
        last_message_id = None
        
        logger.info(f"Starting listener on channel {channel_id}")
        
        while max_messages is None or len(collected) < max_messages:
            try:
                # Get recent messages
                messages = self.get_channel_messages(
                    channel_id,
                    limit=10,
                    before=last_message_id
                )
                
                if not messages:
                    time.sleep(poll_interval)
                    continue
                
                # Process new messages (Discord returns newest first)
                for msg_data in reversed(messages):
                    if last_message_id and msg_data["id"] == last_message_id:
                        continue
                    
                    message = DiscordMessage(
                        id=msg_data["id"],
                        channel_id=msg_data["channel_id"],
                        author=msg_data["author"]["username"],
                        content=msg_data["content"],
                        timestamp=msg_data["timestamp"],
                        guild_id=msg_data.get("guild_id"),
                        attachments=msg_data.get("attachments", []),
                        embeds=msg_data.get("embeds", []),
                    )
                    
                    collected.append(message)
                    self._notify_listeners(message)
                    
                    if max_messages and len(collected) >= max_messages:
                        break
                
                last_message_id = messages[0]["id"] if messages else last_message_id
                
                # Sleep before next poll
                time.sleep(poll_interval)
                
            except KeyboardInterrupt:
                logger.info("Listener stopped by user")
                break
            except Exception as e:
                logger.error(f"Listener error: {e}")
                time.sleep(poll_interval * 2)  # Back off on error
        
        logger.info(f"Listener collected {len(collected)} messages")
        return collected

    def get_guild_channels(self, guild_id: str) -> List[Dict]:
        """
        Get all channels in a guild.
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            List of channel objects
        """
        response = self._request_with_retry(
            "GET",
            f"/guilds/{guild_id}/channels"
        )
        return response.json()

    def get_bot_info(self) -> Dict:
        """
        Get bot user information.
        
        Returns:
            Bot user object
        """
        response = self._request_with_retry("GET", "/users/@me")
        return response.json()

    def close(self) -> None:
        """Close the transport and cleanup resources."""
        self._connected = False
        self.session.close()
        logger.info("Discord transport closed")


# ===== Convenience Functions =====

def create_transport(
    bot_token: str,
    max_retries: int = 5,
    base_delay: float = 1.0,
) -> DiscordTransport:
    """
    Create a configured Discord transport.
    
    Args:
        bot_token: Discord bot token
        max_retries: Maximum retry attempts
        base_delay: Base delay for backoff
        
    Returns:
        Configured DiscordTransport instance
    """
    config = RateLimitConfig(
        max_retries=max_retries,
        base_delay=base_delay,
    )
    return DiscordTransport(bot_token, config)


# ===== Main (for testing) =====

if __name__ == "__main__":
    import os
    
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("Set DISCORD_BOT_TOKEN environment variable to test")
        exit(1)
    
    transport = create_transport(token)
    
    # Get bot info
    bot_info = transport.get_bot_info()
    print(f"Logged in as: {bot_info['username']}#{bot_info['discriminator']}")
    
    transport.close()
