import asyncio
import reqwest
import serde_json
import anyhow

async def rustchain_health():
    # Send a GET request to the RustChain health endpoint
    url = "https://50.28.86.131/health"  # Default URL, configurable if necessary
    response = await reqwest.get(url)

    if response.status().is_success():
        health_info = await response.json()
        return f'Node is healthy: {health_info}'
    else:
        raise Exception(f'Health check failed: {response.status()}')

async def rustchain_balance(wallet_address):
    # Send a GET request to retrieve the wallet balance
    url = f'https://50.28.86.131/balance/{{wallet_address}}'
    response = await reqwest.get(url)

    if response.status().is_success():
        balance_info = await response.json()
        return balance_info["balance"]
    else:
        raise Exception(f'Balance check failed: {response.status()}')

async def main():
    # Run health check
    try:
        health_response = await rustchain_health()
        print(health_response)
    except Exception as e:
        print('Health check failed:', e)

    # Run balance check
    wallet_address = 'test_wallet'
    try:
        balance_response = await rustchain_balance(wallet_address)
        print(f'Balance for {wallet_address}: {balance_response}')
    except Exception as e:
        print('Balance check failed:', e)

if __name__ == '__main__':
    asyncio.run(main())