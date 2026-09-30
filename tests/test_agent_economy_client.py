import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "agent-economy-client" / "agent_economy_client.py"
SPEC = importlib.util.spec_from_file_location("agent_economy_client", MODULE_PATH)
agent_economy_client = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agent_economy_client)


def test_normalize_base_url_adds_https_and_drops_path():
    assert agent_economy_client.normalize_base_url(" node.example.com/jobs ") == "https://node.example.com"
    assert agent_economy_client.normalize_base_url("http://node.example.com:8080/api") == "http://node.example.com:8080"
    assert agent_economy_client.normalize_base_url("") == ""


def test_post_job_sends_expected_payload_and_auth_header():
    client = agent_economy_client.AgentEconomyClient("https://node.example.com", admin_key="k", agent_id="agent-1")
    mock_response = MagicMock()
    mock_response.json.return_value = {"job_id": "job_1", "escrow_locked_rtc": 15.75}
    mock_response.raise_for_status.return_value = None

    with patch.object(agent_economy_client.requests, "post", return_value=mock_response) as mock_post:
        result = client.post_job("Test job", "Do a thing", 15.75)

    assert result == {"job_id": "job_1", "escrow_locked_rtc": 15.75}
    called_url = mock_post.call_args.args[0]
    assert called_url == "https://node.example.com/api/jobs"
    assert mock_post.call_args.kwargs["headers"]["Authorization"] == "Bearer k"


def test_browse_jobs_returns_job_list():
    client = agent_economy_client.AgentEconomyClient("https://node.example.com")
    mock_response = MagicMock()
    mock_response.json.return_value = {"jobs": [{"job_id": "job_1"}]}
    mock_response.raise_for_status.return_value = None

    with patch.object(agent_economy_client.requests, "get", return_value=mock_response):
        jobs = client.browse_jobs()

    assert jobs == [{"job_id": "job_1"}]


def test_claim_job_requires_agent_id():
    client = agent_economy_client.AgentEconomyClient("https://node.example.com")
    with pytest.raises(ValueError):
        client.claim_job("job_1")


def test_deliver_job_requires_agent_id():
    client = agent_economy_client.AgentEconomyClient("https://node.example.com")
    with pytest.raises(ValueError):
        client.deliver_job("job_1", "result payload")


def test_get_reputation_requires_agent_id():
    client = agent_economy_client.AgentEconomyClient("https://node.example.com")
    with pytest.raises(ValueError):
        client.get_reputation()
