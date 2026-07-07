# SPDX-License-Identifier: MIT
"""
RustChain Staking LangChain Tool
Bounty #14383: LangChain + MCP tool for staked self-improvement

Wraps the Elyan staking SDK as a LangChain tool so agents can
stake RTC for self-improvement skills in one call.
"""

import os
import requests
from typing import Optional, Any
from langchain.tools import BaseTool
from pydantic import Field


class StakeAndAcquireTool(BaseTool):
    """
    LangChain tool for staking RTC to acquire skills on RustChain.

    Usage:
        tool = StakeAndAcquireTool()
        result = tool.run({"skill": "code-review", "bond_rtc": 50})
    """

    name: str = "stake_and_acquire"
    description: str = (
        "Stake RTC tokens to acquire a skill on RustChain. "
        "Input: skill name (str) and bond_rtc amount (int). "
        "Returns: verdict with attestation or error if gate unavailable."
    )

    api_key: str = Field(default_factory=lambda: os.getenv("ELYAN_API_KEY", ""))
    gate_pubkey: str = Field(default_factory=lambda: os.getenv("ELYAN_GATE_PUBKEY", ""))
    gate_endpoint: str = Field(
        default_factory=lambda: os.getenv("ELYAN_GATE_ENDPOINT", "https://gate.elyan.ai/api/v1")
    )

    def _run(self, skill: str, bond_rtc: int, wallet: Optional[str] = None, **kwargs: Any) -> dict:
        if not self.api_key or not self.gate_pubkey:
            return {"success": False, "error": "Missing ELYAN_API_KEY or ELYAN_GATE_PUBKEY", "staked": False}

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"skill": skill, "bond_rtc": bond_rtc, "wallet": wallet or "default", "timestamp": __import__("time").time() * 1000}

        try:
            resp = requests.post(f"{self.gate_endpoint}/stake", json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                return {"success": True, "staked": True, "skill": skill, "bond_rtc": bond_rtc, "verdict": resp.json()}
            return {"success": False, "staked": False, "error": f"HTTP {resp.status_code}", "skill": skill, "bond_rtc": bond_rtc}
        except requests.exceptions.ConnectionError:
            return {"success": False, "staked": False, "error": "Gate unavailable", "skill": skill, "bond_rtc": bond_rtc, "fail_safe": True}
        except Exception as e:
            return {"success": False, "staked": False, "error": str(e), "skill": skill, "bond_rtc": bond_rtc}
