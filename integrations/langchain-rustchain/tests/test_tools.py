from unittest.mock import patch

from langchain_rustchain import RustChainAPI, RustChainTool


def test_balance_normalizes_amount_rtc():
    api = RustChainAPI()
    with patch.object(api, "_get", return_value={"amount_rtc": 12.5}):
        assert api.check_balance("wallet") == 12.5


def test_bounty_list_normalizes_items():
    api = RustChainAPI()
    sample = [{"number": 1, "title": "Bounty", "html_url": "https://example/1", "labels": []}]
    with patch.object(api, "_get_url", return_value=sample):
        assert api.list_bounties(1) == [
            {"number": 1, "title": "Bounty", "url": "https://example/1", "labels": []}
        ]


def test_tool_dispatches_health():
    tool = RustChainTool()
    with patch.object(RustChainAPI, "get_node_health", return_value={"ok": True}):
        assert tool.invoke({"action": "get_node_health"}) == {"ok": True}


def test_balance_requires_wallet():
    tool = RustChainTool()
    try:
        tool.invoke({"action": "check_balance"})
    except ValueError as exc:
        assert "wallet_id" in str(exc)
    else:
        raise AssertionError("missing wallet_id must fail")
