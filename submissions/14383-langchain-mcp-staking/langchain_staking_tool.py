#!/usr/bin/env python3
"""
LangChain Tool for RustChain staked self-improvement
Exposes stake_and_acquire(skill, bond_rtc) as a LangChain BaseTool
"""
try:
    from langchain.tools import BaseTool
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from typing import Optional, Type, Any
from staking_sdk import stake_and_acquire, StakeResult


class StakeInput(BaseModel):
    skill: str = Field(description="Skill identifier to acquire (e.g. 'rust_async:1.0')")
    bond_rtc: float = Field(default=1.0, description="Amount of RTC to stake")


class RustChainStakeTool(BaseTool):
    """LangChain tool for staking RTC to acquire skills"""
    name: str = "stake_and_acquire"
    description: str = (
        "Stake RTC tokens to acquire a skill improvement through the RustChain staking gate. "
        "Returns a verdict with signed attestation. If the gate is unavailable, the stake is refunded."
    )
    args_schema: Type[BaseModel] = StakeInput

    def _run(self, skill: str, bond_rtc: float = 1.0) -> dict:
        result = stake_and_acquire(skill, bond_rtc)
        return result.to_dict()

    async def _arun(self, skill: str, bond_rtc: float = 1.0) -> dict:
        return self._run(skill, bond_rtc)


# Standalone function for direct use
def create_stake_tool():
    """Create a configured RustChainStakeTool instance"""
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("langchain is required. Install with: pip install langchain")
    return RustChainStakeTool()
