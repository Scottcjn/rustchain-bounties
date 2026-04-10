import sys
import asyncio
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rustchain-mcp-server')))

from lib import rustchain_health, rustchain_balance

async def test_rustchain_health():
    try:
        response = await rustchain_health()
        print(response)
    except Exception as e:
        print(f'Health check failed: {e}')

async def test_rustchain_balance():
    wallet_address = 'test_wallet'
    try:
        balance = await rustchain_balance(wallet_address)
        print(f'Balance for {wallet_address}: {balance}')
    except Exception as e:
        print(f'Balance check failed: {e}')

async def run_tests():
    await test_rustchain_health()
    await test_rustchain_balance()

if __name__ == '__main__':
    asyncio.run(run_tests())