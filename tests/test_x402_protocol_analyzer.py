#!/usr/bin/env python3
"""
Tests for x402 Payment Protocol Analyzer
"""

import json
import pytest
from tools.x402_protocol_analyzer import x402ProtocolAnalyzer

class Testx402ProtocolAnalyzer:
    """
    Test cases for the x402 protocol analyzer
    """
    
    def setup_method(self):
        """Setup test environment"""
        self.analyzer = x402ProtocolAnalyzer()
    
    def test_valid_transaction(self):
        """Test analysis of a valid transaction"""
        transaction = {
            "from": "user1",
            "to": "user2",
            "amount": "100",
            "currency": "RTC",
            "type": "payment"
        }
        
        result = self.analyzer.analyze_transaction(transaction)
        
        assert result["transaction_data"] == transaction
        assert len(result["vulnerabilities"]) == 0
    
    def test_missing_required_field(self):
        """Test detection of missing required fields"""
        transaction = {
            "from": "user1",
            "to": "user2",
            "amount": "100"
            # Missing currency and type
        }
        
        result = self.analyzer.analyze_transaction(transaction)
        
        assert len(result["vulnerabilities"]) == 2
        assert any(v["type"] == "missing_field" and v["field"] == "currency" for v in result["vulnerabilities"])
        assert any(v["type"] == "missing_field" and v["field"] == "type" for v in result["vulnerabilities"])
    
    def test_invalid_amount(self):
        """Test detection of invalid amounts"""
        # Negative amount
        transaction = {
            "from": "user1",
            "to": "user2",
            "amount": "-100",
            "currency": "RTC",
            "type": "payment"
        }
        
        result = self.analyzer.analyze_transaction(transaction)
        
        assert any(v["type"] == "invalid_amount" for v in result["vulnerabilities"])
    
    def test_zero_amount(self):
        """Test detection of zero amount"""
        transaction = {
            "from": "user1",
            "to": "user2",
            "amount": "0",
            "currency": "RTC",
            "type": "payment"
        }
        
        result = self.analyzer.analyze_transaction(transaction)
        
        assert any(v["type"] == "invalid_amount" for v in result["vulnerabilities"])
    
    def test_invalid_amount_format(self):
        """Test detection of invalid amount format"""
        transaction = {
            "from": "user1",
            "to": "user2",
            "amount": "abc",
            "currency": "RTC",
            "type": "payment"
        }
        
        result = self.analyzer.analyze_transaction(transaction)
        
        assert any(v["type"] == "invalid_amount_format" for v in result["vulnerabilities"])
    
    def test_unsupported_currency(self):
        """Test detection of unsupported currency"""
        transaction = {
            "from": "user1",
            "to": "user2",
            "amount": "100",
            "currency": "XRP",
            "type": "payment"
        }
        
        result = self.analyzer.analyze_transaction(transaction)
        
        assert any(v["type"] == "unsupported_currency" for v in result["vulnerabilities"])
    
    def test_invalid_transaction_type(self):
        """Test detection of invalid transaction type"""
        transaction = {
            "from": "user1",
            "to": "user2",
            "amount": "100",
            "currency": "RTC",
            "type": "transfer"  # Invalid type
        }
        
        result = self.analyzer.analyze_transaction(transaction)
        
        assert any(v["type"] == "invalid_transaction_type" for v in result["vulnerabilities"])
    
    def test_generate_exploit_scenarios(self):
        """Test generation of exploit scenarios"""
        scenarios = self.analyzer.generate_exploit_scenarios()
        
        assert len(scenarios) == 4
        assert any(s["name"] == "Integer Overflow" for s in scenarios)
        assert any(s["name"] == "SQL Injection" for s in scenarios)
        assert any(s["name"] == "Race Condition" for s in scenarios)
        assert any(s["name"] == "Replay Attack" for s in scenarios)
    
    def test_integer_overflow_scenario(self):
        """Test integer overflow scenario"""
        scenarios = self.analyzer.generate_exploit_scenarios()
        overflow_scenario = next(s for s in scenarios if s["name"] == "Integer Overflow")
        
        assert "1e308" in overflow_scenario["payload"]["amount"]
        assert overflow_scenario["expected_vulnerability"] == "integer_overflow"
    
    def test_sql_injection_scenario(self):
        """Test SQL injection scenario"""
        scenarios = self.analyzer.generate_exploit_scenarios()
        sql_scenario = next(s for s in scenarios if s["name"] == "SQL Injection")
        
        assert "DROP TABLE" in sql_scenario["payload"]["from"]
        assert sql_scenario["expected_vulnerability"] == "sql_injection"
    
    def test_race_condition_scenario(self):
        """Test race condition scenario"""
        scenarios = self.analyzer.generate_exploit_scenarios()
        race_scenario = next(s for s in scenarios if s["name"] == "Race Condition")
        
        assert race_scenario["expected_vulnerability"] == "race_condition"
    
    def test_replay_attack_scenario(self):
        """Test replay attack scenario"""
        scenarios = self.analyzer.generate_exploit_scenarios()
        replay_scenario = next(s for s in scenarios if s["name"] == "Replay Attack")
        
        assert "nonce" in replay_scenario["payload"]
        assert replay_scenario["expected_vulnerability"] == "replay_attack"

if __name__ == "__main__":
    pytest.main(["-v", "test_x402_protocol_analyzer.py"])