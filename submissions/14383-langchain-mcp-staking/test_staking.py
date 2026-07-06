#!/usr/bin/env python3
"""Tests for RustChain staking SDK, LangChain tool, and MCP server"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from staking_sdk import stake_and_acquire, StakeResult
from mcp_staking_server import handle_request


def test_sdk_failsafe():
    """Gate unavailable -> refunded=True"""
    result = stake_and_acquire('test_skill:1.0', 5.0)
    assert result.refunded == True, f"Expected refunded=True, got {result.refunded}"
    assert result.verdict == 'error', f"Expected verdict=error, got {result.verdict}"
    assert result.error is not None, "Expected error message"
    print(f'  ✅ Fail-safe: {result.error}')


def test_sdk_result_shape():
    """StakeResult has correct fields"""
    result = StakeResult(verdict='ok', refunded=False, attestation='sig:abc123',
                         skill='test', bond_rtc=1.0)
    d = result.to_dict()
    assert d['verdict'] == 'ok'
    assert d['refunded'] == False
    assert d['attestation'] == 'sig:abc123'
    assert d['skill'] == 'test'
    print('  ✅ Result shape correct')


def test_mcp_initialize():
    """MCP server handles initialize"""
    resp = handle_request({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'})
    assert resp.get('result', {}).get('protocolVersion') == '2024-11-05'
    assert 'tools' in resp['result']['capabilities']
    print('  ✅ MCP initialize OK')


def test_mcp_tools_list():
    """MCP server lists staking tool"""
    resp = handle_request({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})
    tools = resp.get('result', {}).get('tools', [])
    assert len(tools) == 1
    assert tools[0]['name'] == 'stake_and_acquire'
    assert 'skill' in str(tools[0]['inputSchema'])
    print('  ✅ MCP tools/list OK')


def test_mcp_tools_call():
    """MCP server calls staking tool"""
    resp = handle_request({
        'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call',
        'params': {'name': 'stake_and_acquire', 'arguments': {'skill': 'test:1.0', 'bond_rtc': 2.0}}
    })
    content = resp.get('result', {}).get('content', [])
    assert len(content) > 0
    text = json.loads(content[0]['text'])
    assert 'refunded' in text
    print(f'  ✅ MCP tools/call OK -> refunded={text.get("refunded")}')


def test_mcp_unknown_tool():
    """MCP server returns error for unknown tool"""
    resp = handle_request({
        'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call',
        'params': {'name': 'nonexistent', 'arguments': {}}
    })
    assert 'error' in resp
    print('  ✅ MCP unknown tool error OK')


if __name__ == '__main__':
    tests = [test_sdk_failsafe, test_sdk_result_shape,
             test_mcp_initialize, test_mcp_tools_list,
             test_mcp_tools_call, test_mcp_unknown_tool]
    passed = 0
    total = len(tests)
    print(f'Running {total} tests...')
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f'  ❌ {t.__name__}: {e}')
    print(f'\n{passed}/{total} tests passed')
    sys.exit(0 if passed == total else 1)
