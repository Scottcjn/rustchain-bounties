#!/usr/bin/env python3
"""
Discord Transport with real API integration for RustChain Beacon.
"""

import os
import time
import logging
from dataclasses import dataclass
from typing import Optional, List, Callable

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISCORD_API = "https://discord.com/api/v10"

@dataclass
class DiscordConfig:
    bot_token: str
    rate_limit_retries: int = 5
    timeout: int = 30

class DiscordTransport:
    """Discord transport with rate limiting and real API calls."""
    
    def __init__(self, config: DiscordConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bot {config.bot_token}",
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make request with retry logic."""
        url = f"{DISCORD_API}{endpoint}"
        
        for attempt in range(self.config.rate_limit_retries):
            try:
                resp = self.session.request(method, url, timeout=self.config.timeout, **kwargs)
                
                if resp.status_code == 429:
                    retry_after = float(resp.headers.get("X-RateLimit-Reset-After", 1))
                    logger.warning(f"Rate limited, retrying in {retry_after}s")
                    time.sleep(retry_after)
                    continue
                
                resp.raise_for_status()
                return resp.json()
                
            except requests.exceptions.RequestException as e:
                if attempt == self.config.rate_limit_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        return {}
    
    def send_message(self, channel_id: str, content: str) -> dict:
        """Send message to channel."""
        return self._request("POST", f"/channels/{channel_id}/messages", json={"content": content})
    
    def get_messages(self, channel_id: str, limit: int = 50) -> List[dict]:
        """Get messages from channel."""
        return self._request("GET", f"/channels/{channel_id}/messages", params={"limit": limit})
    
    def listen(self, channel_id: str, callback: Callable[[dict], None], interval: float = 5.0):
        """Listen for messages."""
        last_id = None
        while True:
            messages = self.get_messages(channel_id, 10)
            for msg in reversed(messages):
                if msg.get("id") != last_id:
                    callback(msg)
                    last_id = msg.get("id")
            time.sleep(interval)


def main():
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("Set DISCORD_BOT_TOKEN")
        return
    
    config = DiscordConfig(bot_token=token)
    transport = DiscordTransport(config)
    
    # Get bot info
    me = transport._request("GET", "/users/@me")
    print(f"Logged in as: {me['username']}#{me['discriminator']}")


if __name__ == "__main__":
    main()
