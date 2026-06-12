from unittest.mock import Mock

import pytest
import requests

from openai_agents_rustchain_tool import (
    RustChainClient,
    create_rustchain_agent,
    create_rustchain_tools,
)


def make_client(payload, *, status_error=None):
    response = Mock()
    response.json.return_value = payload
    if status_error is not None:
        response.raise_for_status.side_effect = status_error

    session = Mock()
    session.headers = {}
    session.get.return_value = response
    return RustChainClient(session=session), session


def test_check_balance_uses_documented_wallet_endpoint():
    client, session = make_client({"balance": 42})

    result = client.check_balance("alice")

    assert result == {
        "ok": True,
        "data": {"balance": 42},
        "wallet_id": "alice",
    }
    session.get.assert_called_once_with(
        "https://rustchain.org/wallet/balance",
        params={"miner_id": "alice"},
        timeout=10.0,
    )


def test_check_balance_rejects_empty_wallet_without_request():
    client, session = make_client({})

    assert client.check_balance("  ") == {
        "ok": False,
        "error": "wallet_id must not be empty",
    }
    session.get.assert_not_called()


def test_list_bounties_uses_github_api_and_excludes_pull_requests():
    client, session = make_client(
        [
            {"number": 1, "title": "A bounty"},
            {"number": 2, "pull_request": {"url": "example"}},
        ]
    )

    result = client.list_bounties(5)

    assert result == {
        "ok": True,
        "count": 1,
        "bounties": [{"number": 1, "title": "A bounty"}],
    }
    session.get.assert_called_once_with(
        "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues",
        params={
            "state": "open",
            "labels": "bounty",
            "per_page": 5,
        },
        timeout=10.0,
    )


@pytest.mark.parametrize("limit", [0, 101])
def test_list_bounties_rejects_invalid_limit(limit):
    client, session = make_client([])

    assert client.list_bounties(limit) == {
        "ok": False,
        "error": "limit must be between 1 and 100",
    }
    session.get.assert_not_called()


def test_node_errors_are_returned_without_raising():
    error = requests.HTTPError("503 Server Error")
    client, _ = make_client({}, status_error=error)

    assert client.get_node_health() == {
        "ok": False,
        "error": "RustChain request failed: 503 Server Error",
    }


def test_invalid_json_is_returned_without_raising():
    client, session = make_client({})
    session.get.return_value.json.side_effect = ValueError("bad JSON")

    assert client.get_current_epoch() == {
        "ok": False,
        "error": "RustChain returned invalid JSON: bad JSON",
    }


def test_creates_expected_native_tools_and_agent():
    client, _ = make_client({})

    tools = create_rustchain_tools(client)
    agent = create_rustchain_agent(client)

    expected_names = {
        "check_balance",
        "list_bounties",
        "get_node_health",
        "get_current_epoch",
    }
    assert {tool.name for tool in tools} == expected_names
    assert {tool.name for tool in agent.tools} == expected_names
