import requests

# Simple health check implementation
def test_health():
    try:
        response = requests.get('https://50.28.86.131/health')
        if response.status_code == 200:
            print(f'Health Check: Node is healthy - {response.json()}')
        else:
            print(f'Health Check Failed: {response.status_code}')
    except Exception as e:
        print(f'Health Check Exception: {e}')

# Simple balance check implementation
def test_balance(wallet_address):
    try:
        response = requests.get(f'https://50.28.86.131/balance/{wallet_address}')
        if response.status_code == 200:
            print(f'Balance Check: {response.json()}')
        else:
            print(f'Balance Check Failed: {response.status_code}')
    except Exception as e:
        print(f'Balance Check Exception: {e}')

if __name__ == '__main__':
    test_health()
    test_balance('test_wallet')