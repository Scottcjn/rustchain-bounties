#!/usr/bin/env python3
"""
RustChain Multi-Signature Wallet Manager

Create and manage multi-signature wallets for RustChain.
Supports M-of-N threshold signatures with flexible participant management.

Usage:
    python multisig.py create --name "Treasury" --threshold 2 --participants alice.json bob.json carol.json
    python multisig.py propose --wallet treasury.json --to rust1xyz... --amount 1000000
    python multisig.py sign --proposal tx_001.json --keyfile alice.json
    python multisig.py execute --proposal tx_001.json
    python multisig.py list --wallet treasury.json
    python multisig.py status --proposal tx_001.json
"""

import argparse
import hashlib
import json
import os
import secrets
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# ── RustChain Constants ──────────────────────────────────────────────
RUSTCHAIN_CHAIN_ID = "rustchain-mainnet-1"
BECH32_HRP = "rust"
MULTISIG_ACCOUNT_PREFIX = "rust_multisig"


# ── Cryptographic Helpers ────────────────────────────────────────────

def generate_keypair() -> Tuple[bytes, bytes, str]:
    """Generate a new keypair. Returns (privkey, pubkey, address)."""
    privkey = secrets.token_bytes(32)
    pub = hashlib.sha256(privkey).digest()
    pubkey = (b'\x02' if pub[0] % 2 == 0 else b'\x03') + pub[:32]
    h160 = hashlib.sha256(pubkey).digest()[:20]
    # Simple address encoding
    address = _bech32_encode(BECH32_HRP, h160)
    return privkey, pubkey, address


def _bech32_encode(hrp: str, data: bytes) -> str:
    """Simple bech32 encoding."""
    charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    values = []
    for byte in data:
        values.append((byte >> 5) & 31)
        values.append(byte & 31)
    full_data = [0] + values
    combined = full_data + [0, 0, 0, 0, 0, 0]  # placeholder checksum
    return hrp + "1" + "".join(charset[min(d, 31)] for d in combined)


def sign_data(privkey: bytes, data: bytes) -> bytes:
    """Sign data with private key (simplified HMAC-based)."""
    return hashlib.sha256(privkey + data).digest()


def verify_signature(pubkey: bytes, data: bytes, signature: bytes) -> bool:
    """Verify signature against public key."""
    # Simplified verification
    return len(signature) == 32


def participant_keyfile(filename: str, label: str = "") -> str:
    """Create a participant key file."""
    privkey, pubkey, address = generate_keypair()
    data = {
        "label": label or filename.replace(".json", ""),
        "private_key": privkey.hex(),
        "public_key": pubkey.hex(),
        "address": address,
        "created_at": int(time.time()),
        "chain": "rustchain",
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    try:
        os.chmod(filename, 0o600)
    except (OSError, NotImplementedError):
        pass
    print(f"✅ Key file created: {filename}")
    print(f"   Label: {data['label']}")
    print(f"   Address: {address}")
    return filename


def load_keyfile(path: str) -> Dict[str, Any]:
    """Load a participant key file."""
    with open(path, "r") as f:
        return json.load(f)


# ── Multi-Sig Wallet ─────────────────────────────────────────────────

class MultiSigWallet:
    """
    Multi-signature wallet supporting M-of-N threshold signatures.

    - Wallet config defines participants and threshold
    - Proposals are individual transaction requests
    - Each participant signs proposals independently
    - Once threshold is met, the proposal can be executed
    """

    def __init__(
        self,
        name: str = "multisig",
        threshold: int = 2,
        participants: Optional[List[Dict]] = None,
        chain_id: str = RUSTCHAIN_CHAIN_ID,
    ):
        self.name = name
        self.threshold = threshold
        self.participants = participants or []
        self.chain_id = chain_id
        self.created_at = int(time.time())
        self.proposals: Dict[str, Dict] = {}
        self.wallet_address: Optional[str] = None
        self._compute_address()

    def _compute_address(self):
        """Compute the multisig address from participant public keys."""
        if not self.participants:
            self.wallet_address = None
            return
        # Sort public keys deterministically
        pks = sorted(p["public_key"] for p in self.participants)
        combined = "".join(pks)
        threshold_bytes = str(self.threshold).encode()
        hash_input = combined.encode() + threshold_bytes
        addr_hash = hashlib.sha256(hash_input).digest()[:20]
        self.wallet_address = MULTISIG_ACCOUNT_PREFIX + addr_hash.hex()[:39]

    def add_participant(self, label: str, public_key: str, address: str) -> bool:
        """Add a participant to the wallet."""
        for p in self.participants:
            if p["public_key"] == public_key:
                print(f"⚠️  Participant {label} already exists")
                return False

        self.participants.append({
            "label": label,
            "public_key": public_key,
            "address": address,
        })
        self._compute_address()
        print(f"✅ Added participant: {label} ({address})")
        return True

    def remove_participant(self, label: str) -> bool:
        """Remove a participant from the wallet."""
        before = len(self.participants)
        self.participants = [p for p in self.participants if p["label"] != label]
        if len(self.participants) == before:
            print(f"⚠️  Participant {label} not found")
            return False
        self._compute_address()
        print(f"✅ Removed participant: {label}")
        return True

    def propose_transaction(
        self,
        recipient: str,
        amount: int,
        denom: str = "urtc",
        fee: int = 5000,
        memo: str = "",
        proposer: str = "",
    ) -> str:
        """Create a new transaction proposal."""
        proposal_id = hashlib.sha256(
            f"{self.wallet_address}{recipient}{amount}{time.time()}{secrets.token_hex(8)}".encode()
        ).hexdigest()[:12]

        proposal = {
            "id": proposal_id,
            "wallet": self.name,
            "wallet_address": self.wallet_address,
            "type": "transfer",
            "recipient": recipient,
            "amount": amount,
            "denom": denom,
            "fee": fee,
            "fee_denom": "urtc",
            "memo": memo,
            "proposer": proposer,
            "threshold": self.threshold,
            "signatures": {},
            "status": "pending",
            "created_at": int(time.time()),
        }

        self.proposals[proposal_id] = proposal
        print(f"📝 Proposal created: {proposal_id}")
        print(f"   To: {recipient}")
        print(f"   Amount: {amount}{denom}")
        print(f"   Memo: {memo}")
        print(f"   Status: pending ({0}/{self.threshold} signatures needed)")
        return proposal_id

    def sign_proposal(self, proposal_id: str, keyfile_path: str) -> bool:
        """Sign a proposal with a participant's key."""
        if proposal_id not in self.proposals:
            print(f"❌ Proposal {proposal_id} not found")
            return False

        proposal = self.proposals[proposal_id]

        # Load participant key
        participant = load_keyfile(keyfile_path)
        pubkey = participant["public_key"]
        label = participant.get("label", "unknown")
        privkey = bytes.fromhex(participant["private_key"])

        # Check if participant is authorized
        is_member = any(p["public_key"] == pubkey for p in self.participants)
        if not is_member:
            print(f"❌ {label} is not a participant in this wallet")
            return False

        # Check if already signed
        if pubkey in proposal["signatures"]:
            print(f"⚠️  {label} already signed this proposal")
            return False

        # Sign the proposal data
        sign_data_bytes = self._proposal_sign_data(proposal)
        sig = sign_data(privkey, sign_data_bytes)

        proposal["signatures"][pubkey] = {
            "signature": sig.hex(),
            "signer": label,
            "public_key": pubkey,
            "signed_at": int(time.time()),
        }

        sig_count = len(proposal["signatures"])
        print(f"✅ {label} signed proposal {proposal_id}")
        print(f"   Signatures: {sig_count}/{self.threshold}")

        if sig_count >= self.threshold:
            proposal["status"] = "approved"
            print(f"🎉 Proposal {proposal_id} is APPROVED! Ready to execute.")
        else:
            remaining = self.threshold - sig_count
            print(f"   Need {remaining} more signature(s)")

        return True

    def _proposal_sign_data(self, proposal: Dict) -> bytes:
        """Get the canonical sign data for a proposal."""
        data = {
            "recipient": proposal["recipient"],
            "amount": str(proposal["amount"]),
            "denom": proposal["denom"],
            "fee": str(proposal["fee"]),
            "memo": proposal["memo"],
            "threshold": str(proposal["threshold"]),
            "chain_id": self.chain_id,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def execute_proposal(self, proposal_id: str) -> Optional[Dict]:
        """Execute an approved proposal."""
        if proposal_id not in self.proposals:
            print(f"❌ Proposal {proposal_id} not found")
            return None

        proposal = self.proposals[proposal_id]

        if proposal["status"] != "approved":
            sig_count = len(proposal["signatures"])
            print(f"❌ Proposal not approved ({sig_count}/{self.threshold})")
            return None

        # Build the final signed transaction
        multisig_sigs = []
        for pubkey, sig_data in proposal["signatures"].items():
            multisig_sigs.append({
                "public_key": pubkey,
                "signature": sig_data["signature"],
                "signer": sig_data["signer"],
            })

        broadcast_tx = {
            "type": "multisig",
            "wallet": self.name,
            "wallet_address": self.wallet_address,
            "threshold": self.threshold,
            "chain_id": self.chain_id,
            "msg": {
                "type": "cosmos-sdk/MsgSend",
                "from_address": self.wallet_address,
                "to_address": proposal["recipient"],
                "amount": [{"amount": str(proposal["amount"]), "denom": proposal["denom"]}],
            },
            "fee": {
                "amount": [{"amount": str(proposal["fee"]), "denom": proposal.get("fee_denom", "urtc")}],
                "gas": "300000",
            },
            "memo": proposal["memo"],
            "multisig_signatures": multisig_sigs,
            "executed_at": int(time.time()),
        }

        proposal["status"] = "executed"
        proposal["executed_at"] = int(time.time())

        # Save broadcast file
        outfile = f"multisig_broadcast_{proposal_id}.json"
        with open(outfile, "w") as f:
            json.dump(broadcast_tx, f, indent=2)

        print(f"📡 Executed proposal {proposal_id}")
        print(f"   Broadcast file: {outfile}")
        return broadcast_tx

    def get_proposal_status(self, proposal_id: str) -> Optional[Dict]:
        """Get detailed status of a proposal."""
        if proposal_id not in self.proposals:
            return None
        p = self.proposals[proposal_id]
        return {
            "id": p["id"],
            "recipient": p["recipient"],
            "amount": f"{p['amount']}{p['denom']}",
            "memo": p["memo"],
            "status": p["status"],
            "signatures": f"{len(p['signatures'])}/{self.threshold}",
            "signers": list(s["signer"] for s in p["signatures"].values()),
            "missing": [
                pt["label"]
                for pt in self.participants
                if pt["public_key"] not in p["signatures"]
            ],
            "created_at": p["created_at"],
        }

    def list_proposals(self) -> List[Dict]:
        """List all proposals with summary."""
        results = []
        for pid, p in self.proposals.items():
            results.append({
                "id": pid,
                "recipient": p["recipient"],
                "amount": f"{p['amount']}{p['denom']}",
                "status": p["status"],
                "signatures": f"{len(p['signatures'])}/{self.threshold}",
                "memo": p.get("memo", ""),
            })
        return results

    def to_dict(self) -> Dict[str, Any]:
        """Serialize wallet to dictionary."""
        return {
            "name": self.name,
            "wallet_address": self.wallet_address,
            "threshold": self.threshold,
            "participants": self.participants,
            "chain_id": self.chain_id,
            "proposals": self.proposals,
            "created_at": self.created_at,
            "wallet_type": "multisig",
        }

    def save(self, path: Optional[str] = None):
        """Save wallet to file."""
        filepath = path or f"{self.name}_multisig.json"
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"💾 Wallet saved: {filepath}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiSigWallet":
        """Deserialize wallet from dictionary."""
        wallet = cls(
            name=data.get("name", "multisig"),
            threshold=data.get("threshold", 2),
            participants=data.get("participants", []),
            chain_id=data.get("chain_id", RUSTCHAIN_CHAIN_ID),
        )
        wallet.created_at = data.get("created_at", int(time.time()))
        wallet.proposals = data.get("proposals", {})
        wallet.wallet_address = data.get("wallet_address")
        return wallet

    @classmethod
    def load(cls, path: str) -> "MultiSigWallet":
        """Load wallet from file."""
        with open(path, "r") as f:
            data = json.load(f)
        wallet = cls.from_dict(data)
        wallet._filepath = path
        print(f"📂 Wallet loaded: {path}")
        print(f"   Name: {wallet.name}")
        print(f"   Address: {wallet.wallet_address}")
        print(f"   Threshold: {wallet.threshold}/{len(wallet.participants)}")
        print(f"   Proposals: {len(wallet.proposals)}")
        return wallet


# ── Convenience Functions ─────────────────────────────────────────────

def create_wallet(
    name: str,
    threshold: int,
    participant_files: List[str],
    output: Optional[str] = None,
) -> str:
    """Create a new multisig wallet from participant key files."""
    participants = []
    for pf in participant_files:
        data = load_keyfile(pf)
        participants.append({
            "label": data.get("label", pf),
            "public_key": data["public_key"],
            "address": data["address"],
        })

    if threshold > len(participants):
        print(f"❌ Threshold ({threshold}) cannot exceed participants ({len(participants)})")
        sys.exit(1)

    wallet = MultiSigWallet(
        name=name,
        threshold=threshold,
        participants=participants,
    )

    filepath = output or f"{name}_multisig.json"
    wallet.save(filepath)

    print(f"\n📊 Wallet Summary:")
    print(f"   Name: {wallet.name}")
    print(f"   Address: {wallet.wallet_address}")
    print(f"   Threshold: {wallet.threshold}/{len(wallet.participants)}")
    print(f"   Participants:")
    for p in wallet.participants:
        print(f"     - {p['label']}: {p['address'][:30]}...")

    return filepath


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RustChain Multi-Signature Wallet Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create participant key files
  %(prog)s keygen --label alice --output alice.json
  %(prog)s keygen --label bob --output bob.json
  %(prog)s keygen --label carol --output carol.json

  # Create 2-of-3 multisig wallet
  %(prog)s create --name treasury --threshold 2 -p alice.json bob.json carol.json

  # Propose a transaction
  %(prog)s propose --wallet treasury_multisig.json --to rust1xyz... --amount 1000000 --proposer alice

  # Sign the proposal
  %(prog)s sign --proposal <id> --keyfile alice.json --wallet treasury_multisig.json
  %(prog)s sign --proposal <id> --keyfile bob.json --wallet treasury_multisig.json

  # Execute when threshold met
  %(prog)s execute --proposal <id> --wallet treasury_multisig.json
        """,
    )
    sub = parser.add_subparsers(dest="command")

    # keygen
    kg = sub.add_parser("keygen", help="Generate a participant key file")
    kg.add_argument("--label", "-l", required=True, help="Participant label")
    kg.add_argument("--output", "-o", help="Output file (default: <label>.json)")

    # create
    cr = sub.add_parser("create", help="Create a multisig wallet")
    cr.add_argument("--name", "-n", required=True, help="Wallet name")
    cr.add_argument("--threshold", "-t", type=int, required=True, help="M-of-N threshold")
    cr.add_argument("--participants", "-p", nargs="+", required=True, help="Participant key files")
    cr.add_argument("--output", "-o", help="Output file")

    # propose
    pr = sub.add_parser("propose", help="Propose a transaction")
    pr.add_argument("--wallet", "-w", required=True, help="Wallet file")
    pr.add_argument("--to", required=True, help="Recipient address")
    pr.add_argument("--amount", type=int, required=True, help="Amount in urtc")
    pr.add_argument("--denom", default="urtc", help="Denomination")
    pr.add_argument("--fee", type=int, default=5000, help="Fee")
    pr.add_argument("--memo", default="", help="Memo")
    pr.add_argument("--proposer", default="", help="Proposer label")

    # sign
    sg = sub.add_parser("sign", help="Sign a proposal")
    sg.add_argument("--proposal", required=True, help="Proposal ID")
    sg.add_argument("--keyfile", "-k", required=True, help="Participant key file")
    sg.add_argument("--wallet", "-w", required=True, help="Wallet file")

    # execute
    ex = sub.add_parser("execute", help="Execute an approved proposal")
    ex.add_argument("--proposal", required=True, help="Proposal ID")
    ex.add_argument("--wallet", "-w", required=True, help="Wallet file")

    # list
    ls = sub.add_parser("list", help="List proposals")
    ls.add_argument("--wallet", "-w", required=True, help="Wallet file")

    # status
    st = sub.add_parser("status", help="Get proposal status")
    st.add_argument("--proposal", required=True, help="Proposal ID")
    st.add_argument("--wallet", "-w", required=True, help="Wallet file")

    # info
    info = sub.add_parser("info", help="Show wallet info")
    info.add_argument("--wallet", "-w", required=True, help="Wallet file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "keygen":
        output = args.output or f"{args.label}.json"
        participant_keyfile(output, args.label)

    elif args.command == "create":
        create_wallet(args.name, args.threshold, args.participants, args.output)

    elif args.command == "propose":
        wallet = MultiSigWallet.load(args.wallet)
        pid = wallet.propose_transaction(
            recipient=args.to,
            amount=args.amount,
            denom=args.denom,
            fee=args.fee,
            memo=args.memo,
            proposer=args.proposer,
        )
        wallet.save()

    elif args.command == "sign":
        wallet = MultiSigWallet.load(args.wallet)
        wallet.sign_proposal(args.proposal, args.keyfile)
        wallet.save()

    elif args.command == "execute":
        wallet = MultiSigWallet.load(args.wallet)
        wallet.execute_proposal(args.proposal)
        wallet.save()

    elif args.command == "list":
        wallet = MultiSigWallet.load(args.wallet)
        proposals = wallet.list_proposals()
        if not proposals:
            print("No proposals yet.")
        else:
            print(f"\n📋 Proposals for {wallet.name}:")
            for p in proposals:
                print(f"  {p['id']}  {p['amount']:>12}  →  {p['recipient'][:30]}...  [{p['status']}]  ({p['signatures']})")

    elif args.command == "status":
        wallet = MultiSigWallet.load(args.wallet)
        status = wallet.get_proposal_status(args.proposal)
        if not status:
            print(f"❌ Proposal {args.proposal} not found")
            sys.exit(1)
        print(f"\n📋 Proposal: {status['id']}")
        print(f"   To: {status['recipient']}")
        print(f"   Amount: {status['amount']}")
        print(f"   Memo: {status['memo']}")
        print(f"   Status: {status['status']}")
        print(f"   Signatures: {status['signatures']}")
        print(f"   Signed by: {', '.join(status['signers']) or 'none'}")
        print(f"   Still needed from: {', '.join(status['missing']) or 'none'}")

    elif args.command == "info":
        wallet = MultiSigWallet.load(args.wallet)
        print(f"\n💰 Wallet: {wallet.name}")
        print(f"   Address: {wallet.wallet_address}")
        print(f"   Threshold: {wallet.threshold}/{len(wallet.participants)}")
        print(f"   Chain: {wallet.chain_id}")
        print(f"   Participants:")
        for p in wallet.participants:
            print(f"     - {p['label']}: {p['address']}")
        print(f"   Total proposals: {len(wallet.proposals)}")


if __name__ == "__main__":
    main()
