#!/usr/bin/env python3
"""
Michael Sovereign V9.3.0 — A2A Gasless Relayer Client (Python)
Objective: Construct and sign Solana transactions to be broadcast by a fee-payer relayer.
Logic: Based on K's Specification (Phase 1).
"""

import os
import json
import base64
import requests
from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction
from solders.pubkey import Pubkey

class A2ARelayerClient:
    def __init__(self, relayer_url="https://api.octane.relayer/transaction"):
        self.relayer_url = relayer_url
        self.connection = Client(os.getenv("HELIUS_RPC_URL", "https://api.mainnet-beta.solana.com"))
        # Load agent keypair from env
        pk_str = os.getenv("SOLANA_PRIVATE_KEY")
        if pk_str:
            self.agent_keypair = Keypair.from_base58_string(pk_str)
        else:
            self.agent_keypair = None

    def build_gasless_transaction(self, instructions, relayer_pubkey_str):
        if not self.agent_keypair:
            return None, "Missing agent keypair"

        relayer_pubkey = Pubkey.from_string(relayer_pubkey_str)
        
        # 1. Fetch latest blockhash
        recent_blockhash = self.connection.get_latest_blockhash().value.blockhash
        
        # 2. Build MessageV0 with Relayer as fee payer
        # Note: instructions is a list of solders.instruction.Instruction
        message = MessageV0.try_compile(
            payer=relayer_pubkey,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=recent_blockhash
        )
        
        # 3. Create VersionedTransaction
        transaction = VersionedTransaction(message, [self.agent_keypair])
        
        # 4. Serialize and encode for Relayer API
        serialized_tx = bytes(transaction)
        encoded_tx = base64.b64encode(serialized_tx).decode('utf-8')
        
        return encoded_tx, None

    def send_to_relayer(self, encoded_tx):
        print(f"[A2A] Posting transaction to relayer: {self.relayer_url}")
        payload = {"transaction": encoded_tx}
        try:
            # We skip real request if url is dummy
            if "dummy" in self.relayer_url:
                 return {"status": "simulated", "txid": "sim_signature_123"}
                 
            response = requests.post(self.relayer_url, json=payload, timeout=15)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test block
    print("--- A2A Relayer Client Test ---")
    client = A2ARelayerClient()
    if client.agent_keypair:
        print(f"Agent Ready: {client.agent_keypair.pubkey()}")
    else:
        print("Running in observation mode (No keys).")
