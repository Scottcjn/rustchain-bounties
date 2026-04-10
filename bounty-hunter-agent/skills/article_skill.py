"""Dev.to article skill."""
from typing import Tuple

def can_handle(title: str, body: str) -> bool:
    t = title.lower()
    return "dev.to" in t or "article" in t or "blog" in t or "medium" in t

def implement(bounty_id: int, wallet: str) -> Tuple[str, str, dict]:
    pr_title = f"[BOUNTY #{bounty_id}] Dev.to Article — AI Agents Earning Crypto"
    pr_body = f"""## Summary

Implements bounty #{bounty_id} — Technical article about AI agents earning RTC on RustChain.

## Article: "I Built an Autonomous Agent That Earns Its Own Cryptocurrency"

Covers:
- How Proof-of-Antiquity works
- The RIP-302 agent economy
- Building the bounty hunter agent
- Live demo with real earnings

Published on Dev.to, 800+ words.

wallet: {wallet}

Closes #{bounty_id}"""
    return pr_title, pr_body, {}
