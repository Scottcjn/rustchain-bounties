import os
import sys
import json
import time
import requests
from rustchain_sdk.wallet import RustChainWallet

def payout_rtc(recipient_address, amount_rtc):
    seed_phrase_str = os.getenv("REWARD_WALLET_SEED")
    if not seed_phrase_str:
        print("❌ Error: REWARD_WALLET_SEED environment variable not set")
        sys.exit(1)

    # Convert seed phrase string back to list
    seed_phrase = seed_phrase_str.split(",")
    
    try:
        wallet = RustChainWallet.from_seed_phrase(seed_phrase)
        print(f"Using Reward Wallet: {wallet.address}")
        
        # Convert RTC to smallest units (assuming 10^8 as in many chains, 
        # but need to check RustChain spec. Using a placeholder here).
        # Based on the issue #13519, they use "amount_rtc": 1
        # So we'll send it as is.
        
        payload = wallet.sign_transfer(recipient_address, amount_rtc)
        
        print(f"Sending {amount_rtc} RTC to {recipient_address}...")
        
        # Use the official endpoint from issue #13519
        response = requests.post(
            "https://rustchain.org/wallet/transfer/signed",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            print(f"✅ Success! Transaction Hash: {response.json().get('tx_hash', 'unknown')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Critical error during payout: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python payout.py <recipient_address> <amount>")
        sys.exit(1)
        
    recipient = sys.argv[1]
    amount = float(sys.argv[2])
    
    if payout_rtc(recipient, amount):
        sys.exit(0)
    else:
        sys.exit(1)
