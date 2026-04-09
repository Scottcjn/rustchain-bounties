#!/usr/bin/env python3
"""
Bounty Evaluator — assesses difficulty, time, and feasibility of bounties.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from agent import LLMClient


# ── Skill taxonomy ────────────────────────────────────────────────────────

SKILL_KEYWORDS = {
    "rust": ["rust", "cargo", "wasm", "solana", "substrate", "no_std"],
    "python": ["python", "pip", "django", "flask", "fastapi"],
    "solidity": ["solidity", "smart contract", "evm", "ethereum", "erc20", "erc721"],
    "go": ["golang", "go ", "cosmos", "tendermint"],
    "frontend": ["react", "vue", "frontend", "ui", "css", "html", "javascript", "typescript"],
    "devops": ["docker", "kubernetes", "ci/cd", "github actions", "terraform"],
    "cryptography": ["encryption", "hash", "signature", "zero-knowledge", "zkp", "merkle"],
    "blockchain": ["blockchain", "defi", "nft", "bridge", "swap", "staking", "validator"],
}


@dataclass
class BountyAssessment:
    difficulty: str          # easy / medium / hard / expert
    time_estimate: str       # human-readable estimate
    time_hours: float        # numeric hours
    skills_required: List[str] = field(default_factory=list)
    feasible: bool = True
    confidence: float = 0.5  # 0-1
    reasoning: str = ""
    risk_factors: List[str] = field(default_factory=list)


class BountyEvaluator:
    """Evaluates bounties for difficulty, time, and skill requirements."""

    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm

    def evaluate(self, bounty: Dict) -> Dict:
        """Evaluate a bounty and return an assessment dict."""
        # Rule-based pre-assessment
        assessment = self._rule_based_evaluate(bounty)

        # Enhance with LLM if available
        if self.llm:
            try:
                llm_assessment = self._llm_evaluate(bounty, assessment)
                # Merge LLM results, preferring them when confidence is higher
                if llm_assessment.get("confidence", 0) > assessment.confidence:
                    assessment = BountyAssessment(
                        difficulty=llm_assessment.get("difficulty", assessment.difficulty),
                        time_estimate=llm_assessment.get("time_estimate", assessment.time_estimate),
                        time_hours=llm_assessment.get("time_hours", assessment.time_hours),
                        skills_required=llm_assessment.get("skills_required", assessment.skills_required),
                        feasible=llm_assessment.get("feasible", assessment.feasible),
                        confidence=llm_assessment.get("confidence", assessment.confidence),
                        reasoning=llm_assessment.get("reasoning", assessment.reasoning),
                        risk_factors=llm_assessment.get("risk_factors", assessment.risk_factors),
                    )
            except Exception:
                pass  # Fall back to rule-based

        return {
            "difficulty": assessment.difficulty,
            "time_estimate": assessment.time_estimate,
            "time_hours": assessment.time_hours,
            "skills_required": assessment.skills_required,
            "feasible": assessment.feasible,
            "confidence": assessment.confidence,
            "reasoning": assessment.reasoning,
            "risk_factors": assessment.risk_factors,
        }

    def _rule_based_evaluate(self, bounty: Dict) -> BountyAssessment:
        """Quick rule-based assessment from title/body heuristics."""
        text = f"{bounty.get('title', '')} {bounty.get('body', '')}".lower()
        reward = bounty.get("reward", 0)

        # Skill matching
        skills = []
        for skill, keywords in SKILL_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                skills.append(skill)

        # Difficulty from reward tiers
        if reward >= 500:
            difficulty = "expert"
            time_hours = 40.0
        elif reward >= 100:
            difficulty = "hard"
            time_hours = 20.0
        elif reward >= 50:
            difficulty = "medium"
            time_hours = 8.0
        elif reward >= 10:
            difficulty = "easy"
            time_hours = 3.0
        else:
            difficulty = "easy"
            time_hours = 1.0

        # Adjust for complexity keywords
        complexity_signals = ["rewrite", "migrate", "architecture", "design", "integrate"]
        if any(s in text for s in complexity_signals):
            difficulty = _bump_difficulty(difficulty)
            time_hours *= 1.5

        # Risk factors
        risk_factors = []
        if "breaking change" in text:
            risk_factors.append("breaking_change")
        if any(w in text for w in ["security", "audit", "vulnerability"]):
            risk_factors.append("security_sensitive")

        time_estimate = _hours_to_human(time_hours)

        return BountyAssessment(
            difficulty=difficulty,
            time_estimate=time_estimate,
            time_hours=time_hours,
            skills_required=skills or ["general"],
            feasible=True,
            confidence=0.6,
            reasoning="Rule-based heuristic assessment",
            risk_factors=risk_factors,
        )

    def _llm_evaluate(self, bounty: Dict, base: BountyAssessment) -> Dict:
        """Use LLM for deeper evaluation."""
        system = (
            "You are a bounty evaluation agent. Assess the following GitHub bounty issue. "
            "Return a JSON object with keys: difficulty (easy/medium/hard/expert), "
            "time_estimate (human-readable), time_hours (float), skills_required (list), "
            "feasible (bool), confidence (0-1), reasoning (str), risk_factors (list of str)."
        )
        prompt = (
            f"Title: {bounty.get('title', '')}\n"
            f"Body:\n{bounty.get('body', '')[:2000]}\n"
            f"Reward: {bounty.get('reward', 0)} RTC\n"
            f"Labels: {bounty.get('labels', [])}\n"
            f"Preliminary assessment: difficulty={base.difficulty}, "
            f"skills={base.skills_required}\n\n"
            "Provide your JSON assessment:"
        )
        raw = self.llm.complete(system, prompt, max_tokens=512, temperature=0.2)
        # Extract JSON from response
        try:
            # Try to find JSON in the response
            start = raw.index("{")
            end = raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError):
            return {}


# ── Helpers ───────────────────────────────────────────────────────────────

def _bump_difficulty(d: str) -> str:
    order = ["easy", "medium", "hard", "expert"]
    idx = order.index(d) if d in order else 0
    return order[min(idx + 1, len(order) - 1)]


def _hours_to_human(h: float) -> str:
    if h < 1:
        return f"{int(h * 60)} minutes"
    if h < 8:
        return f"{h:.0f} hours"
    days = h / 8
    if days < 5:
        return f"{days:.1f} days"
    weeks = days / 5
    return f"{weeks:.1f} weeks"


import json
