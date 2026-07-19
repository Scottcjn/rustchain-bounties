import sys
import requests

def get_wallet_balance(wallet_id):
    try:
        response = requests.get(f"https://api.example.com/wallets/{wallet_id}")
        response.raise_for_status()
        data = response.json()
        if 'balance' not in data:
            raise KeyError("Missing balance field in response")
        return data['balance']
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}", file=sys.stderr)
        sys.exit(2)
    except requests.exceptions.ConnectionError as e:
        print(f"Network Error: {e}", file=sys.stderr)
        sys.exit(3)
    except (ValueError, KeyError) as e:
        print(f"Malformed JSON or missing balance field: {e}", file=sys.stderr)
        sys.exit(4)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(5)

if __name__ == "__main__":
    if len(sys.argv)!= 2:
        print("Usage: python wallet_balance.py <wallet_id>", file=sys.stderr)
        sys.exit(1)
    
    wallet_id = sys.argv[1]
    try:
        balance = get_wallet_balance(wallet_id)
        print(f"Balance: {balance}")
    except SystemExit as e:
        sys.exit(e.code)
