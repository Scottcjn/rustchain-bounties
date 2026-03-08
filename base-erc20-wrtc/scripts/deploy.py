"""
Deploy wRTC ERC-20 Token to Base Testnet/Mainnet
"""

import os
import json
from web3 import Web3
from eth_account import Account
from pathlib import Path

# Configuration
BASE_TESTNET_RPC = "https://sepolia.base.org"
BASE_MAINNET_RPC = "https://mainnet.base.org"
EXPLORER_API = "https://api-sepolia.basescan.org/api"

# Load environment
PRIVATE_KEY = os.environ.get("DEPLOYER_PRIVATE_KEY", "")
CONTRACT_PATH = Path(__file__).parent / "artifacts" / "WrappedRTC.json"

# Token configuration
TOKEN_NAME = "Wrapped RTC"
TOKEN_SYMBOL = "wRTC"
TOKEN_DECIMALS = 6


def load_contract_abi():
    """Load compiled contract ABI"""
    artifacts_path = Path(__file__).parent / "contracts" / "artifacts" / "WrappedRTC.json"
    if artifacts_path.exists():
        with open(artifacts_path) as f:
            data = json.load(f)
            return data["abi"]
    
    # Fallback: return minimal ABI for verification
    return [
        "function name() view returns (string)",
        "function symbol() view returns (string)",
        "function decimals() view returns (uint8)",
        "function totalSupply() view returns (uint256)",
        "function balanceOf(address) view returns (uint256)",
        "function transfer(address, uint256) returns (bool)",
        "function mint(address, uint256)",
        "function burn(uint256)",
        "event Transfer(address indexed from, address indexed to, uint256 value)"
    ]


def deploy(network="testnet"):
    """Deploy wRTC to Base"""
    
    # Select network
    if network == "testnet":
        rpc = BASE_TESTNET_RPC
        explorer = "https://sepolia.basescan.org"
    else:
        rpc = BASE_MAINNET_RPC
        explorer = "https://basescan.org"
    
    # Connect to network
    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        print(f"Error: Cannot connect to {network}")
        return
    
    print(f"Connected to {network}")
    print(f"Chain ID: {w3.eth.chain_id}")
    
    # Load account
    if not PRIVATE_KEY:
        print("Error: DEPLOYER_PRIVATE_KEY not set")
        # Generate a test account for demo
        acct = Account.create()
        print(f"Generated test account: {acct.address}")
        print(f"WARNING: Use a funded account for real deployment!")
        return
    else:
        acct = Account.from_key(PRIVATE_KEY)
    
    print(f"Deployer: {acct.address}")
    
    # Check balance
    balance = w3.eth.get_balance(acct.address)
    print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
    
    if balance < w3.to_wei(0.01, 'ether'):
        print("Warning: Low balance!")
    
    # Load contract bytecode
    compiled_path = Path(__file__).parent / "contracts" / "artifacts" / "WrappedRTC.json"
    if not compiled_path.exists():
        print("\nContract not compiled. Please compile first:")
        print("  1. Install dependencies: npm install")
        print("  2. Compile: npx hardhat compile")
        print("\nFor now, showing deployment parameters:")
        print(f"  Token Name: {TOKEN_NAME}")
        print(f"  Token Symbol: {TOKEN_SYMBOL}")
        print(f"  Decimals: {TOKEN_DECIMALS}")
        print(f"  Initial Supply: 0 (minted via bridge)")
        print(f"  Network: {network}")
        return
    
    with open(compiled_path) as f:
        compiled = json.load(f)
    
    contract = w3.eth.contract(
        bytecode=compiled["bytecode"],
        abi=compiled["abi"]
    )
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(acct.address)
    gas_price = w3.eth.gas_price
    
    tx = contract.constructor(acct.address).build_transaction({
        'from': acct.address,
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': gas_price,
        'chainId': w3.eth.chain_id
    })
    
    # Sign and send
    signed_tx = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"\nTransaction sent: {tx_hash.hex()}")
    print(f"Waiting for receipt...")
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt.status == 1:
        print(f"\n✅ Contract deployed successfully!")
        print(f"   Address: {receipt.contractAddress}")
        print(f"   Block: {receipt.blockNumber}")
        print(f"   Gas used: {receipt.gasUsed}")
        print(f"\n   Explorer: {explorer}/address/{receipt.contractAddress}")
        print(f"\n   Verify on Basescan:")
        print(f"   {explorer}/verify-contracts")
        
        # Save deployment info
        deploy_info = {
            "network": network,
            "contractAddress": receipt.contractAddress,
            "txHash": tx_hash.hex(),
            "deployer": acct.address,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }
        
        deploy_path = Path(__file__).parent / "deployment.json"
        with open(deploy_path, 'w') as f:
            json.dump(deploy_info, f, indent=2)
        
        print(f"\n   Deployment info saved to: {deploy_path}")
    else:
        print(f"\n❌ Deployment failed!")
        print(f"   Transaction: {receipt.transactionHash.hex()}")


def verify_contract(contract_address, network="testnet"):
    """Verify contract on Basescan"""
    
    if network == "testnet":
        explorer = "https://sepolia.basescan.org"
    else:
        explorer = "https://basescan.org"
    
    print(f"\nVerification:")
    print(f"  Contract: {contract_address}")
    print(f"  Network: {network}")
    print(f"\nTo verify manually:")
    print(f"  1. Go to {explorer}/verify-contracts")
    print(f"  2. Enter contract address: {contract_address}")
    print(f"  3. Select 'Solidity (Single File)'")
    print(f"  4. Compiler version: ^0.8.20")
    print(f"  5. EVM Version: london")
    print(f"  6. Upload WrappedRTC.sol")


if __name__ == "__main__":
    import sys
    
    network = "testnet"
    if len(sys.argv) > 1:
        if sys.argv[1] == "mainnet":
            network = "mainnet"
    
    deploy(network)
