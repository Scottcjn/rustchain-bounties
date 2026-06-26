"""
RustChain LangChain Tool — staked self-improvement
Bounty #14383: https://github.com/Scottcjn/rustchain-bounties/issues/14383

Usage:
    from langchain_staking_tool import RustChainStakeTool

    tool = RustChainStakeTool()
    result = tool.run("rust_async:1.5")          # skill:bond_rtc
    # or via an agent:
    agent.run("Acquire skill 'zero_knowledge' for 2 RTC")
"""

from __future__ import annotations

import json
from typing import Any, Optional, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Import from the co-located staking SDK
from staking_sdk import stake_and_acquire, StakeResult, NODE_URL


# ── Input schema ───────────────────────────────────────────────────────────────

class StakeInput(BaseModel):
    """Validated input for the RustChain stake-and-acquire tool."""
    skill: str = Field(
        description=(
            "Identifier of the skill to acquire, e.g. 'rust_async', "
            "'zero_knowledge', 'p2p_networking'."
        )
    )
    bond_rtc: float = Field(
        default=1.0,
        gt=0,
        description="Amount of RTC to bond (stake). Must be > 0. Default: 1.0.",
    )
    private_key_hex: Optional[str] = Field(
        default=None,
        description=(
            "64-char hex Ed25519 private key for signing the attestation. "
            "Falls back to RUSTCHAIN_PRIVATE_KEY env var. "
            "If neither is set a test-only HMAC stub is used."
        ),
    )


# ── LangChain Tool ─────────────────────────────────────────────────────────────

class RustChainStakeTool(BaseTool):
    """
    LangChain tool that stakes RTC on the RustChain network and acquires
    a skill from the reference gate in a single call.

    Fail-safe: if the gate is unavailable the stake is automatically refunded
    and the error is surfaced to the caller — no RTC is lost.

    Tool name : ``rustchain_stake_and_acquire``

    Input     : A JSON object with ``skill`` and optional ``bond_rtc`` /
                ``private_key_hex`` fields **or** a colon-delimited shorthand
                ``"<skill>:<bond_rtc>"`` (e.g. ``"rust_async:1.5"``).

    Output    : JSON string with verdict, attestation signature, and
                ``refunded`` flag.

    Example::

        tool = RustChainStakeTool()

        # Shorthand string
        print(tool.run("rust_async:2.0"))

        # Structured dict
        print(tool.run({"skill": "zero_knowledge", "bond_rtc": 5.0}))
    """

    name: str = "rustchain_stake_and_acquire"
    description: str = (
        "Stake RTC on RustChain and acquire a skill from the skill gate in one call. "
        "Input: JSON with 'skill' (str) and optional 'bond_rtc' (float, default 1.0). "
        "Shorthand: 'skill_name:bond_amount' e.g. 'rust_async:2.0'. "
        "Returns: JSON with verdict ('acquired'|'denied'|'error'), "
        "signed attestation, and 'refunded' (bool). "
        "Fail-safe: gate unavailable → stake refunded automatically."
    )
    args_schema: Type[BaseModel] = StakeInput
    return_direct: bool = False

    # Allow extra config fields (e.g. node_url override) without Pydantic error
    class Config:
        arbitrary_types_allowed = True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_input(self, tool_input: Any) -> StakeInput:
        """Normalise string shorthand or dict into StakeInput."""
        if isinstance(tool_input, str):
            tool_input = tool_input.strip()
            # Try JSON first
            if tool_input.startswith("{"):
                data = json.loads(tool_input)
                return StakeInput(**data)
            # Colon shorthand: "skill:bond"
            parts = tool_input.split(":", 1)
            skill = parts[0].strip()
            bond = float(parts[1].strip()) if len(parts) > 1 else 1.0
            return StakeInput(skill=skill, bond_rtc=bond)
        if isinstance(tool_input, dict):
            return StakeInput(**tool_input)
        if isinstance(tool_input, StakeInput):
            return tool_input
        raise ValueError(f"Unsupported input type: {type(tool_input)}")

    # ------------------------------------------------------------------
    # BaseTool interface
    # ------------------------------------------------------------------

    def _run(
        self,
        skill: str,
        bond_rtc: float = 1.0,
        private_key_hex: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Execute the stake-and-acquire flow.

        Called by LangChain when the tool is invoked via an agent or directly.
        """
        result: StakeResult = stake_and_acquire(
            skill=skill,
            bond_rtc=bond_rtc,
            private_key_hex=private_key_hex,
        )
        return json.dumps(result.to_dict(), indent=2)

    async def _arun(
        self,
        skill: str,
        bond_rtc: float = 1.0,
        private_key_hex: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Async wrapper — delegates to sync implementation."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self._run(
                skill=skill,
                bond_rtc=bond_rtc,
                private_key_hex=private_key_hex,
            ),
        )


# ── Convenience factory ────────────────────────────────────────────────────────

def make_stake_tool(**kwargs: Any) -> RustChainStakeTool:
    """Create a RustChainStakeTool with optional overrides."""
    return RustChainStakeTool(**kwargs)


# ── Quick demo ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()

    tool = RustChainStakeTool()
    print("=== RustChain LangChain Stake Tool Demo ===\n")
    print(f"Tool name       : {tool.name}")
    print(f"Node URL        : {NODE_URL}")
    print()

    # Test shorthand input
    result_str = tool.run("rust_async:1.0")
    result = json.loads(result_str)
    print("Result:")
    print(json.dumps(result, indent=2))
    print()
    print(f"Verdict  : {result['verdict']}")
    print(f"Refunded : {result['refunded']}")
    if result.get("attestation"):
        print(f"Attest   : {result['attestation'].get('sig_hex','?')[:32]}…")
