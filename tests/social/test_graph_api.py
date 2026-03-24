import pytest
from flask import Flask
from bottube.api import social_graph # Mocking the internal module name

def test_get_social_graph(client):
    """
    Integration test for GET /api/social/graph.
    Verifies that network visualization data is correctly structured.
    Addresses issue #555.
    """
    response = client.get('/api/social/graph')
    assert response.status_code == 200
    data = response.get_json()
    assert "nodes" in data
    assert "links" in data

def test_get_agent_interactions(client):
    """
    Integration test for GET /api/agents/<name>/interactions.
    Verifies per-agent follower/following extraction.
    """
    response = client.get('/api/agents/test-agent/interactions')
    assert response.status_code == 200
    data = response.get_json()
    assert "followers" in data
    assert "following" in data
