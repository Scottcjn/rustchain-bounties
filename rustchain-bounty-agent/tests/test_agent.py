# Bounty Agent Test Suite

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.scanner import Bounty, BountyScanner
from core.evaluator import BountyEvaluator


class TestBounty(unittest.TestCase):
    """Test Bounty class"""
    
    def test_parse_amount_rtc(self):
        """Test parsing RTC amounts"""
        issue = {
            'title': '[BOUNTY: 50 RTC] Test bounty',
            'body': 'Description',
            'html_url': 'https://github.com/test/test/issues/1',
            'number': 1,
            'repository': {'full_name': 'test/test'},
            'created_at': '2024-01-01'
        }
        bounty = Bounty(issue)
        self.assertEqual(bounty.amount, 50)
    
    def test_parse_amount_dollar(self):
        """Test parsing dollar amounts"""
        issue = {
            'title': 'Fix bug $100',
            'body': 'Description',
            'html_url': 'https://github.com/test/test/issues/1',
            'number': 1,
            'repository': {'full_name': 'test/test'},
            'created_at': '2024-01-01'
        }
        bounty = Bounty(issue)
        self.assertEqual(bounty.amount, 100)
    
    def test_difficulty_easy(self):
        """Test easy difficulty detection"""
        issue = {
            'title': 'Simple easy task',
            'body': 'Description',
            'html_url': 'https://github.com/test/test/issues/1',
            'number': 1,
            'repository': {'full_name': 'test/test'},
            'created_at': '2024-01-01'
        }
        bounty = Bounty(issue)
        self.assertEqual(bounty.difficulty, 'easy')


class TestEvaluator(unittest.TestCase):
    """Test BountyEvaluator class"""
    
    def test_evaluate_high_amount(self):
        """Test evaluation of high-value bounty"""
        mock_bounty = Mock()
        mock_bounty.amount = 200
        mock_bounty.difficulty = 'hard'
        
        evaluator = BountyEvaluator()
        score = evaluator.evaluate(mock_bounty)
        
        # High amount should give high score
        self.assertGreater(score.total, 50)
    
    def test_select_best(self):
        """Test selecting best bounties"""
        bounties = []
        for i, amount in enumerate([50, 100, 25, 200, 75]):
            mock = Mock()
            mock.amount = amount
            mock.difficulty = 'medium'
            bounties.append(mock)
        
        evaluator = BountyEvaluator()
        best = evaluator.select_best(bounties, top_n=3)
        
        # Should return top 3
        self.assertEqual(len(best), 3)
        # Highest amount should be first
        self.assertEqual(best[0]['bounty'].amount, 200)


if __name__ == '__main__':
    unittest.main()
