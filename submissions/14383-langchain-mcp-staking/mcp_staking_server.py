#!/usr/bin/env python3
"""
MCP Server for RustChain staked self-improvement
Exposes stake_and_acquire as an MCP tool (2024-11-05 stdio protocol)
"""
import json, sys
from staking_sdk import stake_and_acquire


def handle_request(request: dict) -> dict:
    """Handle a JSON-RPC request"""
    req_id = request.get('id')
    method = request.get('method')

    if method == 'initialize':
        return {
            'jsonrpc': '2.0', 'id': req_id,
            'result': {
                'protocolVersion': '2024-11-05',
                'capabilities': {'tools': {}},
                'serverInfo': {'name': 'rustchain-staking-mcp', 'version': '1.0.0'}
            }
        }

    if method == 'tools/list':
        return {
            'jsonrpc': '2.0', 'id': req_id,
            'result': {
                'tools': [{
                    'name': 'stake_and_acquire',
                    'description': 'Stake RTC to acquire a skill improvement. Gate unavailable -> stake refunded.',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'skill': {'type': 'string', 'description': 'Skill identifier (e.g. rust_async:1.0)'},
                            'bond_rtc': {'type': 'number', 'description': 'RTC amount to stake', 'default': 1.0}
                        },
                        'required': ['skill']
                    }
                }]
            }
        }

    if method == 'tools/call':
        params = request.get('params', {})
        name = params.get('name')
        args = params.get('arguments', {})
        if name == 'stake_and_acquire':
            result = stake_and_acquire(args.get('skill', ''), float(args.get('bond_rtc', 1.0)))
            return {
                'jsonrpc': '2.0', 'id': req_id,
                'result': {'content': [{'type': 'text', 'text': json.dumps(result.to_dict(), indent=2)}]}
            }
        return {'jsonrpc': '2.0', 'id': req_id, 'error': {'code': -32601, 'message': f'Tool not found: {name}'}}

    return {'jsonrpc': '2.0', 'id': req_id, 'error': {'code': -32601, 'message': f'Method not found: {method}'}}


def main():
    """Run MCP stdio server"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            print(json.dumps({'jsonrpc': '2.0', 'error': {'code': -32700, 'message': 'Parse error'}}), flush=True)
        except Exception as e:
            print(json.dumps({'jsonrpc': '2.0', 'error': {'code': -32603, 'message': str(e)}}), flush=True)


if __name__ == '__main__':
    main()
