"""
BountyEvaluator — uses Claude API to score each bounty on feasibility and value.
Falls back to a heuristic score if ANTHROPIC_API_KEY is not set.
"""
import os
import json
import re
from typing import Optional
from scanner import Bounty


def _heuristic_score(bounty: Bounty) -> float:
    """Simple score when no LLM available: reward_rtc / complexity proxy."""
    rtc = bounty.reward_rtc or 1.0
    is_easy = any(l in bounty.labels for l in ["easy", "good first issue"])
    is_hard = any(l in bounty.labels for l in ["critical", "red-team", "major"])
    multiplier = 1.5 if is_easy else (0.5 if is_hard else 1.0)
    return min(10.0, (rtc / 10.0) * multiplier)


def _claude_score(bounty: Bounty, api_key: str) -> float:
    """Ask Claude to evaluate feasibility and return score 0-10."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        prompt = f"""You are evaluating a GitHub bounty for an autonomous AI coding agent.

Bounty #{bounty.number}: {bounty.title}
Reward: {bounty.reward_rtc} RTC
Labels: {', '.join(bounty.labels)}

Description (first 800 chars):
{bounty.body[:800]}

Rate this bounty 0-10 for an autonomous AI agent considering:
- Can the agent complete it without human input? (weight: 40%)
- Reward-to-effort ratio (weight: 35%)
- Is the deliverable concrete/verifiable? (weight: 25%)

Reply with ONLY a JSON object: {{"score": <float 0-10>, "reason": "<15 words max>"}}"""

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        data = json.loads(re.search(r'\{.*\}', text, re.DOTALL).group())
        return float(data["score"])
    except Exception:
        return _heuristic_score(bounty)


def score_bounties(bounties: list[Bounty]) -> list[tuple[float, Bounty]]:
    """Return (score, bounty) pairs, sorted best-first."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    scored = []
    for bounty in bounties:
        if api_key:
            s = _claude_score(bounty, api_key)
        else:
            s = _heuristic_score(bounty)
        scored.append((s, bounty))
    return sorted(scored, key=lambda x: x[0], reverse=True)
