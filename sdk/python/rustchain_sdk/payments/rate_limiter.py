"""
RustChain Agent-to-Agent Payments Rate Limiter & Anti-Spam Guard
"""

from __future__ import annotations

import time
import threading
from typing import Dict, List, Optional, Tuple


class SlidingWindowRateLimiter:
    """Thread-safe sliding window rate limiter."""

    def __init__(self, max_requests: int = 60, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> Tuple[bool, int, float]:
        """
        Check if request is allowed for a key (e.g., wallet address or IP).

        Returns:
            (allowed: bool, remaining_requests: int, retry_after_seconds: float)
        """
        with self._lock:
            now = time.time()
            timestamps = self._history.get(key, [])
            # Filter out timestamps outside window
            valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]

            if len(valid_timestamps) >= self.max_requests:
                earliest = valid_timestamps[0]
                retry_after = max(0.0, self.window_seconds - (now - earliest))
                self._history[key] = valid_timestamps
                return False, 0, retry_after

            valid_timestamps.append(now)
            self._history[key] = valid_timestamps
            remaining = self.max_requests - len(valid_timestamps)
            return True, remaining, 0.0

    def reset(self, key: Optional[str] = None) -> None:
        """Reset rate limiter state for a key or all keys."""
        with self._lock:
            if key is not None:
                self._history.pop(key, None)
            else:
                self._history.clear()


class AntiSpamGuard:
    """
    Protects upvotes and payment endpoints from spam and automated floods.
    Tracks duplicate action signatures and short-window frequency.
    """

    def __init__(self, cooldown_seconds: float = 0.5, max_actions_per_min: int = 120):
        self.cooldown_seconds = cooldown_seconds
        self._last_action_time: Dict[str, float] = {}
        self._action_hashes: Dict[str, float] = {}
        self._limiter = SlidingWindowRateLimiter(max_requests=max_actions_per_min, window_seconds=60.0)
        self._lock = threading.Lock()

    def validate_action(self, voter_or_agent: str, action_hash: str) -> Tuple[bool, Optional[str]]:
        """
        Validates whether an action is legitimate and not spam.

        Returns:
            (is_valid: bool, error_reason: Optional[str])
        """
        with self._lock:
            now = time.time()

            # Check duplicate action hash (prevent replay/double tap within 10s)
            if action_hash in self._action_hashes:
                if now - self._action_hashes[action_hash] < 10.0:
                    return False, "Duplicate action detected within short window"

            # Check cooldown per agent
            last_time = self._last_action_time.get(voter_or_agent, 0.0)
            if now - last_time < self.cooldown_seconds:
                return False, f"Action rate too fast. Cooldown is {self.cooldown_seconds}s"

            # Check general rate limit
            allowed, _, retry_after = self._limiter.check(voter_or_agent)
            if not allowed:
                return False, f"Rate limit exceeded. Retry after {retry_after:.1f}s"

            self._last_action_time[voter_or_agent] = now
            self._action_hashes[action_hash] = now

            # Cleanup older action hashes (> 60s)
            if len(self._action_hashes) > 1000:
                cutoff = now - 60.0
                self._action_hashes = {h: t for h, t in self._action_hashes.items() if t > cutoff}

            return True, None
