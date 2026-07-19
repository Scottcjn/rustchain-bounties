import argparse
import json
import requests
import time
from rustchain_crypto import sign_transaction  # Assuming this is the module for signing

# Constants
API_URL = "https://api.example.com"  # Replace with the actual API URL
FEVERDREAM_STUDIO = "feverdream_studio"
RTC_RATE = 0.0023  # Example rate, replace with the actual rate

def get_quote(prompt, seconds):
    url = f"{API_URL}/api/feverdream/info"
    params = {
        "prompt": prompt,
        "seconds": seconds
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def sign_transfer(wallet_file, amount, recipient):
    with open(wallet_file, 'r') as f:
        wallet = json.load(f)
    
    private_key = wallet['private_key']
    public_key = wallet['public_key']
    nonce = wallet.get('nonce', 0) + 1  # Increment nonce for each transaction
    
    payload = {
        "amount": amount,
        "recipient": recipient,
        "nonce": nonce
    }
    
    signature = sign_transaction(private_key, public_key, payload)
    return {
        "payload": payload,
        "signature": signature
    }

def post_order(quote, signed_transfer):
    url = f"{API_URL}/api/feverdream/order"
    data = {
        "quote_id": quote['id'],
        "signed_transfer": signed_transfer
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()

def poll_status(order_id):
    url = f"{API_URL}/api/feverdream/status/{order_id}"
    while True:
        response = requests.get(url)
        response.raise_for_status()
        status = response.json()
        if status['status'] == 'completed':
            print(f"Watch URL: {status['watch_url']}")
            break
        time.sleep(5)

def main():
    parser = argparse.ArgumentParser(description="Feverdream Order CLI")
    parser.add_argument("--prompt", required=True, help="The prompt for the order")
    parser.add_argument("--seconds", type=int, required=True, help="The duration in seconds")
    parser.add_argument("--wallet", required=True, help="Path to the wallet JSON file")
    args = parser.parse_args()

    # Step 1: Get the quote
    quote = get_quote(args.prompt, args.seconds)
    print(f"Quote: {quote}")

    # Step 2: Sign the transfer
    amount = quote['amount'] * RTC_RATE
    signed_transfer = sign_transfer(args.wallet, amount, FEVERDREAM_STUDIO)
    print(f"Signed Transfer: {signed_transfer}")

    # Step 3: Post the order
    order = post_order(quote, signed_transfer)
    print(f"Order: {order}")

    # Step 4: Poll the status
    poll_status(order['id'])

if __name__ == "__main__":
    main()