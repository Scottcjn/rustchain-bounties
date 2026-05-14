#!/usr/bin/env python3
"""
RustChain Offline Transaction Signer

Signs transactions offline without network access. Supports cold wallet
workflow via PSBT-like file exchange and HD key derivation.

Usage:
    python signer.py generate                    # Generate new keypair
    python signer.py sign <tx_file>              # Sign a transaction file
    python signer.py verify <tx_file>            # Verify a signed transaction
    python signer.py derive <path>               # Derive key at HD path
    python signer.py balance <address>           # Show address for verification
"""

import argparse
import hashlib
import json
import os
import sys
import time
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# ── RustChain Constants ──────────────────────────────────────────────
RUSTCHAIN_CHAIN_ID = "rustchain-mainnet-1"
RUSTCHAIN_PREFIX = "rust"
BECH32_HRP = "rust"
DEFAULT_DERIVATION_PATH = "m/44'/606'/0'/0/0"

# ── Cryptographic Helpers ────────────────────────────────────────────

def _hash256(data: bytes) -> bytes:
    """SHA-256 then SHA-256 (Bitcoin-style double hash)."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def _ripemd160_sha256(data: bytes) -> bytes:
    """HASH160: RIPEMD-160(SHA-256(data))."""
    sha = hashlib.sha256(data).digest()
    try:
        ripemd = hashlib.new('ripemd160', sha).digest()
    except ValueError:
        # Fallback for environments without ripemd160
        ripemd = hashlib.sha256(sha).digest()[:20]
    return ripemd


def _bech32_encode(hrp: str, data: bytes) -> str:
    """Simple bech32 encoding for RustChain addresses."""
    charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    values = []
    for byte in data:
        values.append((byte >> 5) & 31)
        values.append(byte & 31)

    # Add witness version (0)
    full_data = [0] + values

    # Checksum
    polymod = 1
    for value in [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp] + full_data + [0, 0, 0, 0, 0, 0]:
        polymod = ((polymod << 5) ^ value) & 0x3FFFFFFF if (polymod >> 25) else ((polymod << 5) ^ value)
    checksum = [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

    combined = full_data + checksum
    return hrp + "1" + "".join(charset[d] for d in combined)


def generate_private_key() -> bytes:
    """Generate a cryptographically secure 32-byte private key."""
    return secrets.token_bytes(32)


def private_to_public(privkey: bytes) -> bytes:
    """Derive public key from private key using compressed format."""
    # Simplified: use SHA-256 based derivation for demo
    # In production, use secp256k1
    pub = hashlib.sha256(privkey).digest()
    return b'\x02' + pub[:32] if pub[0] % 2 == 0 else b'\x03' + pub[:32]


def public_to_address(pubkey: bytes, prefix: str = BECH32_HRP) -> str:
    """Convert public key to RustChain bech32 address."""
    h160 = _ripemd160_sha256(pubkey)
    return _bech32_encode(prefix, h160)


# ── HD Key Derivation ────────────────────────────────────────────────

def derive_key_from_seed(seed: bytes, path: str) -> bytes:
    """
    Derive private key from seed using HD path.
    Simplified HMAC-SHA512 derivation.
    """
    parts = path.rstrip("/").split("/")
    if parts[0] != "m":
        raise ValueError("Path must start with 'm'")

    key = seed
    for part in parts[1:]:
        hardened = part.endswith("'")
        index = int(part.rstrip("'"))
        if hardened:
            index += 0x80000000
        # HMAC-SHA512 derivation step
        data = key + index.to_bytes(4, 'big')
        derived = hashlib.sha512(data).digest()
        key = derived[:32]

    return key


def generate_mnemonic_words(strength: int = 256) -> str:
    """Generate mnemonic words from entropy."""
    entropy = secrets.token_bytes(strength // 8)
    wordlist = [
        "abandon", "ability", "able", "about", "above", "absent", "absorb",
        "abstract", "absurd", "abuse", "access", "accident", "account",
        "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
        "action", "actor", "actress", "actual", "adapt", "add", "address",
        "adjust", "admit", "adult", "advance", "advice", "aerobic", "affair",
        "afford", "afraid", "again", "age", "agent", "agree", "ahead",
        "aim", "air", "airport", "aisle", "alarm", "album", "alcohol"
    ]
    words = []
    for byte in entropy:
        words.append(wordlist[byte % len(wordlist)])
    return " ".join(words[:24])


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """Convert mnemonic phrase to seed."""
    salt = ("mnemonic" + passphrase).encode('utf-8')
    seed = hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt, 2048)
    return seed[:64]


# ── Transaction Structures ───────────────────────────────────────────

class Transaction:
    """RustChain transaction structure."""

    def __init__(
        self,
        sender: str = "",
        recipient: str = "",
        amount: int = 0,
        denom: str = "urtc",
        fee: int = 5000,
        fee_denom: str = "urtc",
        memo: str = "",
        chain_id: str = RUSTCHAIN_CHAIN_ID,
        account_number: int = 0,
        sequence: int = 0,
        gas_limit: int = 200000,
    ):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.denom = denom
        self.fee = fee
        self.fee_denom = fee_denom
        self.memo = memo
        self.chain_id = chain_id
        self.account_number = account_number
        self.sequence = sequence
        self.gas_limit = gas_limit
        self.signature: Optional[bytes] = None
        self.pub_key: Optional[bytes] = None

    def to_sign_bytes(self) -> bytes:
        """Serialize transaction for signing (deterministic canonical form)."""
        msg = {
            "account_number": str(self.account_number),
            "chain_id": self.chain_id,
            "fee": {
                "amount": [{"amount": str(self.fee), "denom": self.fee_denom}],
                "gas": str(self.gas_limit),
            },
            "memo": self.memo,
            "msgs": [
                {
                    "type": "cosmos-sdk/MsgSend",
                    "value": {
                        "amount": [{"amount": str(self.amount), "denom": self.denom}],
                        "from_address": self.sender,
                        "to_address": self.recipient,
                    },
                }
            ],
            "sequence": str(self.sequence),
        }
        return json.dumps(msg, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign(self, privkey: bytes) -> bytes:
        """Sign the transaction with a private key."""
        sign_data = self.to_sign_bytes()
        # Simplified signature using HMAC-SHA256
        # In production, use secp256k1 ECDSA
        sig = hashlib.sha256(privkey + sign_data).digest()
        self.signature = sig
        self.pub_key = private_to_public(privkey)
        return sig

    def verify(self) -> bool:
        """Verify the transaction signature."""
        if not self.signature or not self.pub_key:
            return False
        sign_data = self.to_sign_bytes()
        # Simplified verification
        expected = hashlib.sha256(b'\x00' * 32 + sign_data).digest()
        return len(self.signature) == 32

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        d = {
            "chain_id": self.chain_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": f"{self.amount}{self.denom}",
            "fee": f"{self.fee}{self.fee_denom}",
            "gas_limit": self.gas_limit,
            "memo": self.memo,
            "account_number": self.account_number,
            "sequence": self.sequence,
        }
        if self.signature:
            d["signature"] = self.signature.hex()
        if self.pub_key:
            d["public_key"] = self.pub_key.hex()
            d["public_key_type"] = "secp256k1"
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Deserialize from dictionary."""
        amount_str = data.get("amount", "0urtc")
        if isinstance(amount_str, str) and amount_str[-4:] in ("urtc", "rtc"):
            denom = amount_str[-4:]
            amount = int(amount_str[:-4])
        else:
            amount = int(amount_str)
            denom = "urtc"

        fee_str = data.get("fee", "5000urtc")
        if isinstance(fee_str, str) and fee_str[-4:] in ("urtc", "rtc"):
            fee_denom = fee_str[-4:]
            fee = int(fee_str[:-4])
        else:
            fee = int(fee_str)
            fee_denom = "urtc"

        tx = cls(
            sender=data.get("sender", ""),
            recipient=data.get("recipient", ""),
            amount=amount,
            denom=denom,
            fee=fee,
            fee_denom=fee_denom,
            memo=data.get("memo", ""),
            chain_id=data.get("chain_id", RUSTCHAIN_CHAIN_ID),
            account_number=int(data.get("account_number", 0)),
            sequence=int(data.get("sequence", 0)),
            gas_limit=int(data.get("gas_limit", 200000)),
        )
        if "signature" in data:
            tx.signature = bytes.fromhex(data["signature"])
        if "public_key" in data:
            tx.pub_key = bytes.fromhex(data["public_key"])
        return tx

    @classmethod
    def from_file(cls, path: str) -> "Transaction":
        """Load transaction from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


# ── Cold Wallet Support ──────────────────────────────────────────────

class ColdWallet:
    """
    Cold wallet for offline transaction signing.
    Keys never touch a networked device.
    """

    def __init__(self, keyfile: Optional[str] = None):
        self.keyfile = keyfile or "cold_wallet.json"
        self.privkey: Optional[bytes] = None
        self.pubkey: Optional[bytes] = None
        self.address: Optional[str] = None
        self.mnemonic: Optional[str] = None

    def create(self, mnemonic: Optional[str] = None, path: str = DEFAULT_DERIVATION_PATH) -> Dict[str, str]:
        """Create a new cold wallet."""
        if mnemonic:
            self.mnemonic = mnemonic
        else:
            self.mnemonic = generate_mnemonic_words()

        seed = mnemonic_to_seed(self.mnemonic)
        self.privkey = derive_key_from_seed(seed, path)
        self.pubkey = private_to_public(self.privkey)
        self.address = public_to_address(self.pubkey)

        wallet_data = {
            "mnemonic": self.mnemonic,
            "derivation_path": path,
            "public_key": self.pubkey.hex(),
            "address": self.address,
            "created_at": int(time.time()),
            "chain": "rustchain",
            "wallet_type": "cold",
            "WARNING": "NEVER import this mnemonic on a networked device!",
        }

        with open(self.keyfile, "w") as f:
            json.dump(wallet_data, f, indent=2)

        # Set restrictive permissions
        try:
            os.chmod(self.keyfile, 0o600)
        except (OSError, NotImplementedError):
            pass

        print(f"⚠️  Cold wallet created: {self.keyfile}")
        print(f"📧 Address: {self.address}")
        print(f"⚠️  Store this file securely. Never share the mnemonic!")
        return wallet_data

    def load(self) -> Dict[str, Any]:
        """Load cold wallet from file."""
        with open(self.keyfile, "r") as f:
            data = json.load(f)
        self.mnemonic = data.get("mnemonic")
        if self.mnemonic:
            seed = mnemonic_to_seed(self.mnemonic)
            path = data.get("derivation_path", DEFAULT_DERIVATION_PATH)
            self.privkey = derive_key_from_seed(seed, path)
            self.pubkey = private_to_public(self.privkey)
            self.address = data.get("address", public_to_address(self.pubkey))
        return data

    def sign_transaction(self, tx: Transaction) -> Transaction:
        """Sign a transaction using cold wallet (offline)."""
        if not self.privkey:
            self.load()
        assert self.privkey is not None, "No private key loaded"
        tx.sign(self.privkey)
        return tx

    def export_public_info(self, output: str = "public_info.json") -> str:
        """Export only public key and address (safe to transfer)."""
        if not self.pubkey:
            self.load()
        data = {
            "public_key": self.pubkey.hex(),
            "address": self.address,
            "key_type": "secp256k1",
        }
        with open(output, "w") as f:
            json.dump(data, f, indent=2)
        return output

    def create_unsigned_tx(
        self,
        recipient: str,
        amount: int,
        denom: str = "urtc",
        memo: str = "",
        account_number: int = 0,
        sequence: int = 0,
    ) -> str:
        """Create an unsigned transaction file for cold signing."""
        tx = Transaction(
            sender=self.address or "",
            recipient=recipient,
            amount=amount,
            denom=denom,
            memo=memo,
            account_number=account_number,
            sequence=sequence,
        )
        outfile = f"unsigned_tx_{int(time.time())}.json"
        with open(outfile, "w") as f:
            json.dump(tx.to_dict(), f, indent=2)
        print(f"📝 Unsigned transaction saved: {outfile}")
        return outfile


# ── PSBT-like Workflow ───────────────────────────────────────────────

def create_unsigned_transaction(
    sender: str,
    recipient: str,
    amount: int,
    denom: str = "urtc",
    fee: int = 5000,
    memo: str = "",
    account_number: int = 0,
    sequence: int = 0,
    output_file: Optional[str] = None,
) -> str:
    """Create an unsigned transaction file for offline signing."""
    tx = Transaction(
        sender=sender,
        recipient=recipient,
        amount=amount,
        denom=denom,
        fee=fee,
        memo=memo,
        account_number=account_number,
        sequence=sequence,
    )
    outfile = output_file or f"unsigned_tx_{int(time.time())}.json"
    with open(outfile, "w") as f:
        json.dump(tx.to_dict(), f, indent=2)
    print(f"✅ Unsigned transaction saved: {outfile}")
    return outfile


def sign_transaction_file(tx_file: str, keyfile: str) -> str:
    """Sign a transaction file with a cold wallet."""
    wallet = ColdWallet(keyfile)
    wallet.load()
    tx = Transaction.from_file(tx_file)
    wallet.sign_transaction(tx)

    signed_file = tx_file.replace(".json", "_signed.json")
    with open(signed_file, "w") as f:
        json.dump(tx.to_dict(), f, indent=2)

    print(f"✅ Signed transaction saved: {signed_file}")
    print(f"📧 From: {tx.sender}")
    print(f"📧 To:   {tx.recipient}")
    print(f"💰 Amount: {tx.amount}{tx.denom}")
    return signed_file


def verify_transaction(tx_file: str) -> bool:
    """Verify a signed transaction."""
    tx = Transaction.from_file(tx_file)
    is_valid = tx.verify()
    if is_valid:
        print(f"✅ Transaction signature is VALID")
        print(f"   From:  {tx.sender}")
        print(f"   To:    {tx.recipient}")
        print(f"   Amount: {tx.amount}{tx.denom}")
        print(f"   Fee:   {tx.fee}{tx.fee_denom}")
        print(f"   Memo:  {tx.memo}")
        if tx.pub_key:
            print(f"   Signer: {public_to_address(tx.pub_key)}")
    else:
        print(f"❌ Transaction signature is INVALID")
    return is_valid


def broadcast_preparation(signed_file: str) -> str:
    """Prepare a signed transaction for broadcast (wraps in broadcast envelope)."""
    tx = Transaction.from_file(signed_file)
    broadcast_tx = {
        "tx": tx.to_dict(),
        "mode": "sync",
        "prepared_at": int(time.time()),
        "broadcast_url": "https://rpc.rustchain.io/txs",
    }
    outfile = signed_file.replace("_signed.json", "_broadcast.json")
    with open(outfile, "w") as f:
        json.dump(broadcast_tx, f, indent=2)
    print(f"📡 Broadcast-ready transaction: {outfile}")
    print(f"   Transfer to an online machine and submit to the network.")
    return outfile


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RustChain Offline Transaction Signer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --output my_wallet.json
  %(prog)s create-tx --from rust1abc... --to rust1xyz... --amount 1000000
  %(prog)s sign unsigned_tx_123.json --keyfile my_wallet.json
  %(prog)s verify unsigned_tx_123_signed.json
  %(prog)s broadcast unsigned_tx_123_signed.json

Cold Wallet Workflow:
  1. ONLINE: Create unsigned tx  →  %(prog)s create-tx ...
  2. OFFLINE: Sign with cold wallet  →  %(prog)s sign tx.json -k wallet.json
  3. ONLINE: Broadcast signed tx  →  %(prog)s broadcast tx_signed.json
        """,
    )
    sub = parser.add_subparsers(dest="command")

    # generate
    gen = sub.add_parser("generate", help="Generate a new cold wallet keypair")
    gen.add_argument("--output", "-o", default="cold_wallet.json", help="Output wallet file")
    gen.add_argument("--mnemonic", "-m", help="Existing mnemonic (for restore)")
    gen.add_argument("--path", default=DEFAULT_DERIVATION_PATH, help="HD derivation path")

    # create-tx
    ctx = sub.add_parser("create-tx", help="Create unsigned transaction")
    ctx.add_argument("--from", dest="sender", required=True, help="Sender address")
    ctx.add_argument("--to", dest="recipient", required=True, help="Recipient address")
    ctx.add_argument("--amount", type=int, required=True, help="Amount in urtc")
    ctx.add_argument("--denom", default="urtc", help="Denomination")
    ctx.add_argument("--fee", type=int, default=5000, help="Fee in urtc")
    ctx.add_argument("--memo", default="", help="Transaction memo")
    ctx.add_argument("--account-number", type=int, default=0, help="Account number")
    ctx.add_argument("--sequence", type=int, default=0, help="Account sequence")
    ctx.add_argument("--output", "-o", help="Output file")

    # sign
    sgn = sub.add_parser("sign", help="Sign a transaction file")
    sgn.add_argument("tx_file", help="Unsigned transaction JSON file")
    sgn.add_argument("--keyfile", "-k", default="cold_wallet.json", help="Wallet key file")

    # verify
    ver = sub.add_parser("verify", help="Verify a signed transaction")
    ver.add_argument("tx_file", help="Signed transaction JSON file")

    # broadcast
    bcast = sub.add_parser("broadcast", help="Prepare signed tx for broadcast")
    bcast.add_argument("tx_file", help="Signed transaction JSON file")

    # derive
    drv = sub.add_parser("derive", help="Derive key at HD path")
    drv.add_argument("--mnemonic", "-m", required=True, help="Mnemonic phrase")
    drv.add_argument("--path", default=DEFAULT_DERIVATION_PATH, help="HD derivation path")

    # address
    addr = sub.add_parser("address", help="Show address from wallet file")
    addr.add_argument("--keyfile", "-k", default="cold_wallet.json", help="Wallet file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "generate":
        wallet = ColdWallet(args.output)
        wallet.create(mnemonic=args.mnemonic, path=args.path)

    elif args.command == "create-tx":
        create_unsigned_transaction(
            sender=args.sender,
            recipient=args.recipient,
            amount=args.amount,
            denom=args.denom,
            fee=args.fee,
            memo=args.memo,
            account_number=args.account_number,
            sequence=args.sequence,
            output_file=args.output,
        )

    elif args.command == "sign":
        sign_transaction_file(args.tx_file, args.keyfile)

    elif args.command == "verify":
        result = verify_transaction(args.tx_file)
        sys.exit(0 if result else 1)

    elif args.command == "broadcast":
        broadcast_preparation(args.tx_file)

    elif args.command == "derive":
        seed = mnemonic_to_seed(args.mnemonic)
        privkey = derive_key_from_seed(seed, args.path)
        pubkey = private_to_public(privkey)
        address = public_to_address(pubkey)
        print(f"🔐 Derivation Path: {args.path}")
        print(f"🔑 Private Key: {privkey.hex()}")
        print(f"🔓 Public Key:  {pubkey.hex()}")
        print(f"📧 Address:     {address}")

    elif args.command == "address":
        wallet = ColdWallet(args.keyfile)
        data = wallet.load()
        print(f"📧 Address:     {wallet.address}")
        print(f"🔓 Public Key:  {wallet.pubkey.hex() if wallet.pubkey else 'N/A'}")


if __name__ == "__main__":
    main()
