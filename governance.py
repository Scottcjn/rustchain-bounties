class MiningGovernance:
    def __init__(self, miner_id):
        self.miner_id = miner_id

    def verify_key(self):
        try:
            # Verify the miner_id is a valid Ed25519 public key
            bytes.fromhex(miner_id)
            return True
        except ValueError:
            print("Invalid miner ID format. Please provide a 32-byte Ed25519 public key.")
            return False

    def propose(self, vote):
        # Propose a vote using the valid public key
        if self.verify_key():
            print(f"Vote proposed for {vote}")
        else:
            print("Failed to propose vote.")

# Example usage
miner = MiningGovernance("0x1234567890abcdef")
miner.propose("Test Vote")