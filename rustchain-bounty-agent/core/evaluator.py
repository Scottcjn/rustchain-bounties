"""
Bounty Evaluator - Assesses and selects the best bounties to pursue
"""

from typing import List, Dict
from dataclasses import dataclass
import json


@dataclass
class EvaluationScore:
    """Score breakdown for a bounty"""
    amount_score: float      # 40% - Higher payout = better
    complexity_score: float  # 30% - Lower complexity = better
    competition_score: float # 20% - Less competition = better
    time_score: float        # 10% - Faster completion = better
    total: float
    
    def __repr__(self):
        return f"Score({self.total:.2f}: amount={self.amount_score:.2f}, complexity={self.complexity_score:.2f})"


class BountyEvaluator:
    """Evaluates bounties and selects the best ones to pursue"""
    
    def __init__(self):
        self.weights = {
            'amount': 0.40,
            'complexity': 0.30,
            'competition': 0.20,
            'time': 0.10
        }
    
    def evaluate(self, bounty) -> EvaluationScore:
        """Evaluate a single bounty"""
        # Amount score (normalized to 0-100)
        max_amount = 500  # Assume $500 is max reasonable bounty
        amount_score = min(bounty.amount / max_amount * 100, 100)
        
        # Complexity score (inverse - easier is better)
        difficulty_map = {'easy': 100, 'medium': 60, 'hard': 30}
        complexity_score = difficulty_map.get(bounty.difficulty, 50)
        
        # Competition score (placeholder - would need PR count)
        competition_score = 70  # Assume moderate competition
        
        # Time score (placeholder - would need time estimate)
        time_score = 70  # Assume reasonable time
        
        # Calculate weighted total
        total = (
            amount_score * self.weights['amount'] +
            complexity_score * self.weights['complexity'] +
            competition_score * self.weights['competition'] +
            time_score * self.weights['time']
        )
        
        return EvaluationScore(
            amount_score=amount_score,
            complexity_score=complexity_score,
            competition_score=competition_score,
            time_score=time_score,
            total=total
        )
    
    def select_best(self, bounties: List, top_n: int = 3) -> List[Dict]:
        """Select the top N best bounties"""
        scored_bounties = []
        
        for bounty in bounties:
            score = self.evaluate(bounty)
            scored_bounties.append({
                'bounty': bounty,
                'score': score
            })
        
        # Sort by total score (descending)
        scored_bounties.sort(key=lambda x: x['score'].total, reverse=True)
        
        return scored_bounties[:top_n]
    
    def print_evaluation(self, scored_bounties: List[Dict]):
        """Print evaluation results"""
        print("\n" + "="*60)
        print("🎯 BOUNTY EVALUATION RESULTS")
        print("="*60)
        
        for i, item in enumerate(scored_bounties, 1):
            bounty = item['bounty']
            score = item['score']
            
            print(f"\n{i}. {bounty.title[:60]}")
            print(f"   💰 Amount: ${bounty.amount}")
            print(f"   📊 Difficulty: {bounty.difficulty}")
            print(f"   ⭐ Total Score: {score.total:.1f}/100")
            print(f"      - Amount: {score.amount_score:.1f}")
            print(f"      - Complexity: {score.complexity_score:.1f}")
            print(f"   🔗 {bounty.url}")


if __name__ == "__main__":
    # Example usage
    from scanner import BountyScanner
    
    scanner = BountyScanner()
    repos = ["Scottcjn/rustchain-bounties"]
    bounties = scanner.scan_multiple(repos)
    
    evaluator = BountyEvaluator()
    best = evaluator.select_best(bounties, top_n=5)
    evaluator.print_evaluation(best)
