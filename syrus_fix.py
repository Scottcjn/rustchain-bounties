```python
"""
Retroactive Impact Rewards
Architecture: The Invisible Architect (Value Routing & Structural Integrity Mechanism)
Purpose: Surfacing and compensating critical, unbountied system labor (stabilization, mentorship).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Set
import hashlib
from functools import total_ordering

class UnsexyLaborType(Enum):
    PRODUCTION_STABILIZATION = "Infrastructure & Production Stabilization"
    MENTORSHIP = "Developer Onboarding & Mentorship"
    TECH_DEBT = "Refactoring & Technical Debt Reduction"
    GLUE_WORK = "Cross-Squad Alignment & Unblocking"

@dataclass
class InvisibleImpact:
    id: str
    contributor_id: str
    labor_category: UnsexyLaborType
    description: str
    peer_witnesses: Set[str] = field(default_factory=set)
    baseline_value: float = 100.0

    @property
    def true_impact_score(self) -> float:
        """The structural impact of 'invisible' work scales exponentially 
        by the number of peers it empowers or systems it saves."""
        return self.baseline_value * (1.0 + len(self.peer_witnesses) * 0.5)

@total_ordering
class RetroactiveRewardEngine:
    def __init__(self, treasury_reserve: float):
        self.treasury_reserve = treasury_reserve
        self.impact_ledger: Dict[str, InvisibleImpact] = {}
        self.pending_bonuses: Dict[str, float] = {}

    def log_shadow_work(self, dev_id: str, category: UnsexyLaborType, description: str) -> str:
        """Captures critical work that falls outside rigid predefined bounty lists."""
        impact_id = hashlib.sha256(f"{dev_id}:{description}".encode()).hexdigest()[:12]
        self.impact_ledger[impact_id] = InvisibleImpact(
            id=impact_id,
            contributor_id=dev_id,
            labor_category=category,
            description=description
        )
        return impact_id

    def attest_impact(self, impact_id: str, witness_id: str) -> None:
        """Peers silently corroborate the value of the unsexy labor."""
        if impact_id in self.impact_ledger:
            impact = self.impact_ledger[impact_id]
            if witness_id != impact.contributor_id:
                impact.peer_witnesses.add(witness_id)

    def _calculate_surprise_allocation(self, allocation_rate: float = 0.15) -> Dict[str, float]:
        """Dynamically routes a percentage of the treasury to unbountied structural work."""
        if not self.impact_ledger:
            return {}

        reward_pool = self.treasury_reserve * allocation_rate
        total_impact_score = sum(impact.true_impact_score for impact in self.impact_ledger.values())

        if total_impact_score <= 0:
            return {}

        for impact in self.impact_ledger.values():
            share = (impact.true_impact_score / total_impact_score) * reward_pool
            self.pending_bonuses[impact.contributor_id] = self.pending_bonuses.get(impact.contributor_id, 0) + share
            self.treasury_reserve -= share

        return self.pending_bonuses

    def execute_retroactive_airdrop(self) -> None:
        """Distributes surprise bonuses to the most dedicated, unseen contributors."""
        bonuses = self._calculate_surprise_allocation()
        for dev, amount in bonuses.items():
            self._transmit_reward(dev, amount)

        self.impact_ledger.clear()
        self.pending_bonuses.clear()

    def _transmit_reward(self, dev_id: str, amount: float) -> None:
        """Transaction execution layer."""
        print(f"[RETRO_REWARD_DISPATCHED] {dev_id} | Amount: ${amount:.2f} | Reason: Systemic Integrity Maintenance")

    def __lt__(self, other: RetroactiveRewardEngine) -> bool:
        return self.treasury_reserve < other.treasury_reserve

    def __eq__(self, other: RetroactiveRewardEngine) -> bool:
        return self.treasury_reserve == other.treasury_reserve

if __name__ == "__main__":
    architect = RetroactiveRewardEngine(treasury_reserve=250000.0)

    work_1 = architect.log_shadow_work(
        dev_id="dev_0x9A",
        category=UnsexyLaborType.PRODUCTION_STABILIZATION,
        description="Diagnosed and patched silent memory leak causing sporadic weekend downtime."
    )

    work_2 = architect.log_shadow_work(
        dev_id="dev_0x4F",
        category=UnsexyLaborType.MENTORSHIP,
        description="Spent 20 hours unblocking 4 junior devs on legacy architecture."
    )

    architect.attest_impact(work_1, witness_id="dev_0x1B")
    architect.attest_impact(work_1, witness_id="sysadmin_01")

    architect.attest_impact(work_2, witness_id="junior_dev_A")
    architect.attest_impact(work_2, witness_id="junior_dev_B")
    architect.attest_impact(work_2, witness_id="junior_dev_C")

    architect.execute_retroactive_airdrop()
```