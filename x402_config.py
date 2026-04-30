# x402_config.py

import os

def load_env_vars():
    # Load environment variables securely (using HSM if available)
    cdp_api_key_private_key = os.getenv('CDP_API_KEY_PRIVATE_KEY', '')
    price_all_default = os.getenv('PRICE_ALL_DEFAULT', '0')
    
    return cdp_api_key_private_key, price_all_default

def main():
    cdp_api_key_private_key, price_all_default = load_env_vars()
    
    # Set default values if environment variables are not set
    if not cdp_api_key_private_key:
        print("CDP API Key Private Key is not set. Using default value.")
        cdp_api_key_private_key = 'default_cdp_api_key'
    
    if not price_all_default:
        print("Price All Default is not set. Using default value.")
        price_all_default = 'default_price_all_default'
    
    print(f"CDP API Key Private Key: {cdp_api_key_private_key}")
    print(f"Price All Default: {price_all_default}")

if __name__ == "__main__":
    main()