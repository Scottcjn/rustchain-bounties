import asyncio
import os

# Add path to RustChain directory
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../rustchain-mcp-server')))

from lib import rustchain_health, rustchain_balance

async def main():
    try:
        health_response = await rustchain_health()
        print('Health Response:', health_response)
    except Exception as e:
        print('Health check failed:', e)

    wallet_address = 'test_wallet'
    try:
        balance_response = await rustchain_balance(wallet_address)
        print(f'Balance for {wallet_address}: {balance_response}')
    except Exception as e:
        print('Balance check failed:', e)

if __name__ == '__main__':
    asyncio.run(main())