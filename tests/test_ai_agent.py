import pytest
from ai_agent import Darwin

def test_darwin_init():
    """Test that Darwin initializes correctly."""
    agent = Darwin()
    assert agent is not None
    assert hasattr(agent, 'name')
    assert agent.name == 'Darwin'

def test_darwin_process_input():
    """Test that Darwin can process input."""
    agent = Darwin()
    test_input = "Hello, Darwin!"
    response = agent.process_input(test_input)
    assert isinstance(response, str)
    assert len(response) > 0

def test_darwin_analyze_data():
    """Test that Darwin can analyze data."""
    agent = Darwin()
    test_data = [1, 2, 3, 4, 5]
    result = agent.analyze_data(test_data)
    assert isinstance(result, dict)
    assert 'mean' in result
    assert 'count' in result

def test_darwin_generate_report():
    """Test that Darwin can generate a report."""
    agent = Darwin()
    test_data = {'mean': 3.0, 'count': 5}
    report = agent.generate_report(test_data)
    assert isinstance(report, str)
    assert len(report) > 0