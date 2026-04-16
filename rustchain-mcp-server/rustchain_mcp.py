#!/usr/bin/env python3
"""
RustChain MCP Server v1.0
Connect any AI agent (Claude Code, Cursor, Windsurf) to RustChain blockchain.
Install: pip install rustchain-mcp
Usage:   uvx rustchain-mcp
Issue:   https://github.com/Scottcjn/rustchain-bounties/issues/2859
"""
import asyncio, json, os, sys
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

DEFAULT_NODE_URL = os.environ.get('RUSTCHAIN_NODE_URL', 'https://50.28.86.131')
app = Server('rustchain-mcp')

async def node_get(endpoint, params=None):
    url = f'{DEFAULT_NODE_URL}{endpoint}'
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        return {'error': str(e)}

@app.list_tools()
async def list_tools():
    return [
        Tool(name='rustchain_health', description='Check node health status', inputSchema={'type':'object','properties':{}}),
        Tool(name='rustchain_balance', description='Query wallet RTC balance', inputSchema={'type':'object','properties':{'wallet':{'type':'string','description':'Wallet address'}},'required':['wallet']}),
        Tool(name='rustchain_miners', description='List active miners', inputSchema={'type':'object','properties':{'limit':{'type':'integer','default':20}}} ),
        Tool(name='rustchain_epoch', description='Get current epoch info', inputSchema={'type':'object','properties':{}}),
        Tool(name='rustchain_bounties', description='List open bounties', inputSchema={'type':'object','properties':{'limit':{'type':'integer','default':10}}} ),
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == 'rustchain_health':
        result = await node_get('/health')
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    elif name == 'rustchain_balance':
        wallet = arguments.get('wallet', '')
        result = await node_get(f'/balance/{wallet}')
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    elif name == 'rustchain_miners':
        limit = arguments.get('limit', 20)
        result = await node_get('/api/miners', params={'limit': limit})
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    elif name == 'rustchain_epoch':
        result = await node_get('/epoch')
        return [TextContent(type='text', text=json.dumps(result, indent=2))]
    elif name == 'rustchain_bounties':
        limit = arguments.get('limit', 10)
        query = 'label:bounty+state:open+repo:Scottcjn/rustchain-bounties'
        url = f'https://api.github.com/search/issues?q={query}&per_page={limit}'
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            data = resp.json()
            bounties = [{'title':i['title'],'url':i['html_url'],'updated':i['updated_at'][:10]} for i in data.get('items',[])]
        return [TextContent(type='text', text=json.dumps({'bounties':bounties,'total':data.get('total_count',0)}, indent=2))]
    return [TextContent(type='text', text=f'Unknown tool: {name}')]

async def main():
    print(f'[rustchain-mcp] Starting... Node: {DEFAULT_NODE_URL}', file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == '__main__':
    asyncio.run(main())
