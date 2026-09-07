"""
RustChain Issue #35 - Agent-to-Agent Payments Test Suite
Comprehensive verification for:
1. Upvote + Donate System (Milestone 1)
2. Cross-Wallet Bridge RTC ↔ BoTTube (Milestone 2)
3. Agent-to-Agent x402 Payments (Milestone 3)
4. Cross-Bounty Dual Escrow (Milestone 4)
5. Cryptographic Receipts and Verification Integrity (No Mocks)
"""

import hashlib
import json
import time
import pytest
from flask import Flask, jsonify, request

from rustchain_sdk import (
    RustChainWallet,
    UpvoteDonateService,
    CrossWalletBridge,
    BridgeDirection,
    BridgeStatus,
    BountyStatus,
    DonationTier,
    X402ServerManager,
    require_rtc_payment,
    AutoPayClient,
    CrossBountyEscrowManager,
    CryptographicReceiptManager,
    AntiSpamGuard,
)


# ============================================================================
# 1. Cryptographic Signatures & Verification (Anti-Forgery)
# ============================================================================

class TestCryptographicIntegrity:
    """Verify Ed25519 cryptographic signing and verification (zero mock assertions)."""

    def test_ed25519_sign_and_verify(self):
        wallet = RustChainWallet.create()
        message = b"RustChain Agent Payment Verification 2026"
        signature = wallet.sign(message)

        # Valid verification using raw bytes and hex
        assert RustChainWallet.verify_signature(wallet.public_key_hex, message, signature.hex()) is True
        assert RustChainWallet.verify_signature(bytes.fromhex(wallet.public_key_hex), message, signature) is True

        # Tampered message must fail
        tampered_msg = b"Tampered Message"
        assert RustChainWallet.verify_signature(wallet.public_key_hex, tampered_msg, signature.hex()) is False

        # Wrong public key must fail
        other_wallet = RustChainWallet.create()
        assert RustChainWallet.verify_signature(other_wallet.public_key_hex, message, signature.hex()) is False

    def test_transfer_payload_signing_and_verification(self):
        sender = RustChainWallet.create()
        recipient = RustChainWallet.create()

        payload = sender.sign_transfer(to_address=recipient.address, amount=1000000, fee=1000)
        assert "signature" in payload
        assert "public_key" in payload
        assert payload["from"] == sender.address
        assert payload["to"] == recipient.address

        # Verification must pass
        assert RustChainWallet.verify_transfer(payload) is True

        # Tampered amount must fail
        tampered_payload = dict(payload)
        tampered_payload["amount"] = 99999999
        assert RustChainWallet.verify_transfer(tampered_payload) is False

        # Tampered recipient must fail
        tampered_recipient = dict(payload)
        tampered_recipient["to"] = "RTC_FAKE_RECIPIENT"
        assert RustChainWallet.verify_transfer(tampered_recipient) is False


# ============================================================================
# 2. Milestone 1: Upvote + Donate System Tests
# ============================================================================

class TestUpvoteDonateSystem:
    """Test Milestone 1: Free upvote signals, micro-donations, stats, and multiplier tracking."""

    def test_free_upvote(self):
        service = UpvoteDonateService()
        voter = RustChainWallet.create()
        content_id = "video_g4_mac_cluster_01"

        res = service.upvote(
            content_id=content_id,
            voter=voter.address,
            platform="bottube",
            hardware_multiplier=2.5,  # G4 PowerPC vintage node
        )

        assert res["status"] == "success"
        stats = res["content_stats"]
        assert stats["upvote_count"] == 1
        assert stats["donation_count"] == 0
        assert stats["total_donated_rtc"] == 0.0
        assert voter.address in stats["unique_voters"]
        assert stats["average_multiplier"] == 2.5

        # Verify receipt
        assert CryptographicReceiptManager.verify_receipt(res["receipt"]) is True

    def test_upvote_and_donate_with_tiers(self):
        service = UpvoteDonateService()
        voter = RustChainWallet.create()
        creator = RustChainWallet.create()
        content_id = "bounty_solution_power8"

        # Tier 1: Micro 0.001 RTC
        res1 = service.upvote_donate(
            content_id=content_id,
            voter=voter.address,
            creator=creator.address,
            amount=DonationTier.MICRO,
            wallet=voter,
            hardware_multiplier=3.0,
        )
        assert res1["status"] == "success"
        assert res1["content_stats"]["donation_count"] == 1
        assert res1["content_stats"]["donations_by_tier"]["0.001"] == 1
        assert res1["creator_balance"] == 0.001

        # Small delay for non-conflicting timestamp
        time.sleep(0.15)

        # Tier 2: Small 0.01 RTC
        voter2 = RustChainWallet.create()
        res2 = service.upvote_donate(
            content_id=content_id,
            voter=voter2.address,
            creator=creator.address,
            amount=DonationTier.SMALL,
            wallet=voter2,
        )
        assert res2["content_stats"]["upvote_count"] == 2
        assert res2["content_stats"]["donation_count"] == 2
        assert res2["content_stats"]["total_donated_rtc"] == 0.011
        assert res2["creator_balance"] == 0.011

        # Check creator earnings aggregation
        earnings = service.get_creator_earnings(creator.address)
        assert earnings["total_earned_rtc"] == 0.011
        assert earnings["total_donations_received"] == 2

    def test_custom_donation_amount(self):
        service = UpvoteDonateService()
        voter = RustChainWallet.create()
        creator = RustChainWallet.create()
        content_id = "ai_agent_research_paper"

        res = service.upvote_donate(
            content_id=content_id,
            voter=voter.address,
            creator=creator.address,
            amount=0.42,
            wallet=voter,
        )
        assert res["content_stats"]["donations_by_tier"]["custom"] == 1
        assert res["content_stats"]["top_donors"][voter.address] == 0.42

    def test_signed_transfer_verification_in_donate(self):
        service = UpvoteDonateService()
        voter = RustChainWallet.create()
        creator = RustChainWallet.create()
        content_id = "signed_tx_test"

        valid_signed_tx = voter.sign_transfer(to_address=creator.address, amount=100000)
        res = service.upvote_donate(
            content_id=content_id,
            voter=voter.address,
            creator=creator.address,
            amount=0.1,
            signed_tx=valid_signed_tx,
        )
        assert res["status"] == "success"

        # Tampered signed tx must be rejected
        tampered_tx = dict(valid_signed_tx)
        tampered_tx["amount"] = 9999999
        with pytest.raises(ValueError, match="Invalid Ed25519"):
            service.upvote_donate(
                content_id=content_id,
                voter=voter.address,
                creator=creator.address,
                amount=0.1,
                signed_tx=tampered_tx,
            )


# ============================================================================
# 3. Milestone 2: Cross-Wallet Bridge Tests (RTC ↔ BoTTube)
# ============================================================================

class TestCrossWalletBridge:
    """Test Milestone 2: Bidirectional bridge between RTC and BoTTube wallets."""

    def test_rtc_to_botttube_transfer(self):
        bridge = CrossWalletBridge(exchange_rate=1.0, fee_basis_points=10)  # 0.1% fee
        sender_wallet = RustChainWallet.create()
        bridge.seed_balance(sender_wallet.address, rtc=100.0)

        tx = bridge.rtc_to_botttube(
            rtc_address=sender_wallet.address,
            botttube_user="atlas_agent_01",
            amount=50.0,
            rtc_wallet=sender_wallet,
        )

        assert tx.status == BridgeStatus.SETTLED
        assert tx.direction == BridgeDirection.RTC_TO_BOTTUBE
        assert tx.fee == 0.05  # 0.1% of 50
        assert tx.net_amount == 49.95

        # Check balances
        sender_bal = bridge.get_balances(sender_wallet.address)
        recip_bal = bridge.get_balances("atlas_agent_01")
        assert sender_bal["rtc_balance"] == 50.0
        assert recip_bal["botttube_balance"] == 49.95

    def test_botttube_to_rtc_transfer(self):
        bridge = CrossWalletBridge(exchange_rate=1.0, fee_basis_points=10)
        recipient_wallet = RustChainWallet.create()
        bridge.seed_balance("atlas_agent_01", botttube=100.0)

        tx = bridge.botttube_to_rtc(
            botttube_user="atlas_agent_01",
            rtc_address=recipient_wallet.address,
            amount=40.0,
        )

        assert tx.status == BridgeStatus.SETTLED
        assert tx.direction == BridgeDirection.BOTTUBE_TO_RTC
        assert tx.fee == 0.04
        assert tx.net_amount == 39.96

        recip_bal = bridge.get_balances(recipient_wallet.address)
        assert recip_bal["rtc_balance"] == 39.96

    def test_custom_exchange_rate(self):
        # 1 RTC = 2.5 BoTTube tokens
        bridge = CrossWalletBridge(exchange_rate=2.5, fee_basis_points=0)
        sender_wallet = RustChainWallet.create()
        bridge.seed_balance(sender_wallet.address, rtc=10.0)

        tx = bridge.rtc_to_botttube(
            rtc_address=sender_wallet.address,
            botttube_user="gamer_agent",
            amount=10.0,
            rtc_wallet=sender_wallet,
        )
        assert tx.net_amount == 25.0
        assert bridge.get_balances("gamer_agent")["botttube_balance"] == 25.0

    def test_refund_mechanism(self):
        bridge = CrossWalletBridge()
        sender_wallet = RustChainWallet.create()
        bridge.seed_balance(sender_wallet.address, rtc=50.0)

        # Manually create a locked tx for refund test
        tx = bridge.rtc_to_botttube(sender_wallet.address, "refund_user", 20.0, rtc_wallet=sender_wallet)
        tx.status = BridgeStatus.LOCKED  # set to locked to test refund

        refunded_tx = bridge.refund_transaction(tx.tx_id, reason="Network timeout")
        assert refunded_tx.status == BridgeStatus.REFUNDED
        assert bridge.get_balances(sender_wallet.address)["rtc_balance"] == 50.0  # Returned


# ============================================================================
# 4. Milestone 3: 8004 / x402 HTTP Payment Protocol Tests
# ============================================================================

class TestX402PaymentProtocol:
    """Test Milestone 3: HTTP 402 Challenge, Ed25519 Signed Proof, and AutoPay Client."""

    def test_challenge_generation_and_headers(self):
        mgr = X402ServerManager()
        body, headers = mgr.create_challenge(
            price_rtc=0.001,
            recipient="RTC_INFERENCE_AGENT_WALLET",
            service_name="DeepSeek LLM Inference",
        )

        assert body["status_code"] == 402
        assert "WWW-Authenticate" in headers
        assert "X-Payment-Required" in headers
        assert 'price="0.001"' in headers["WWW-Authenticate"]
        assert 'recipient="RTC_INFERENCE_AGENT_WALLET"' in headers["WWW-Authenticate"]

    def test_autopay_client_and_server_verification(self):
        mgr = X402ServerManager()
        recipient_wallet = RustChainWallet.create()
        payer_wallet = RustChainWallet.create()

        client = AutoPayClient(wallet=payer_wallet)
        price = 0.005

        # Payer creates payment proof
        proof = client.create_payment_proof(
            recipient=recipient_wallet.address,
            amount=price,
            quote_id="q402_test_123",
        )

        # Server verifies payment proof
        proof_header = json.dumps(proof)
        is_valid, err, receipt = mgr.verify_payment(
            proof_header,
            expected_price=price,
            expected_recipient=recipient_wallet.address,
        )

        assert is_valid is True
        assert err is None
        assert receipt is not None
        assert receipt["data"]["sender"] == payer_wallet.address
        assert receipt["data"]["recipient"] == recipient_wallet.address
        assert receipt["data"]["amount"] == 0.005

    def test_replay_attack_prevention(self):
        mgr = X402ServerManager()
        recipient = RustChainWallet.create()
        payer = RustChainWallet.create()
        client = AutoPayClient(wallet=payer)

        proof = client.create_payment_proof(recipient.address, 0.01)
        proof_header = json.dumps(proof)

        # First verification succeeds
        valid1, _, _ = mgr.verify_payment(proof_header, expected_price=0.01, expected_recipient=recipient.address)
        assert valid1 is True

        # Second verification with exact same nonce/signature MUST be rejected as replay
        valid2, err2, _ = mgr.verify_payment(proof_header, expected_price=0.01, expected_recipient=recipient.address)
        assert valid2 is False
        assert "Replay attack detected" in err2

    def test_flask_middleware_integration(self):
        """Test Flask endpoint protected by @require_rtc_payment."""
        app = Flask(__name__)
        provider_wallet = RustChainWallet.create()
        client_wallet = RustChainWallet.create()

        server_mgr = X402ServerManager()

        @app.route("/api/inference", methods=["POST"])
        @require_rtc_payment(price=0.001, recipient=provider_wallet.address, server_manager=server_mgr)
        def inference_endpoint():
            data = request.get_json() or {}
            prompt = data.get("prompt", "")
            return jsonify({"status": "ok", "response": f"Processed: {prompt}"})

        test_client = app.test_client()

        # 1. Unpaid request -> must return 402
        res1 = test_client.post("/api/inference", json={"prompt": "Summarize RustChain"})
        assert res1.status_code == 402
        assert "X-Payment-Required" in res1.headers

        # 2. Automated AutoPayClient intercept and payment
        autopay = AutoPayClient(wallet=client_wallet)

        def make_request(headers):
            return test_client.post(
                "/api/inference",
                json={"prompt": "Summarize RustChain"},
                headers=headers,
            )

        res2 = autopay.execute_with_auto_pay(make_request, max_price=0.005)
        assert res2.status_code == 200
        assert res2.get_json()["status"] == "ok"
        assert res2.get_json()["response"] == "Processed: Summarize RustChain"
        assert "X-Payment-Receipt" in res2.headers
        assert autopay.total_spent_rtc == 0.001


# ============================================================================
# 5. Milestone 4: Cross-Bounty Escrow System Tests
# ============================================================================

class TestCrossBountyEscrow:
    """Test Milestone 4: Dual-currency bounty creation, claim, settlement, and reputation."""

    def test_bounty_creation_and_deposit(self):
        manager = CrossBountyEscrowManager()
        poster_rtc = RustChainWallet.create()

        res = manager.create_bounty(
            bounty_id="bounty-35-agent-payments",
            title="Agent-to-Agent Payments Stack",
            poster_rtc=poster_rtc.address,
            poster_bottube="scott_creator",
            escrow_rtc=300.0,
            escrow_bottube=1000.0,
            stipulations=["Upvote+Donate", "Cross-Wallet Bridge", "x402 protocol", "Dual Escrow"],
        )

        assert res["status"] == "success"
        bounty = res["bounty"]
        assert bounty["status"] == BountyStatus.OPEN.value
        assert bounty["escrow_rtc"] == 300.0
        assert bounty["escrow_bottube"] == 1000.0

    def test_bounty_claim_and_100_percent_settlement(self):
        manager = CrossBountyEscrowManager()
        poster = RustChainWallet.create()
        claimant = RustChainWallet.create()

        manager.create_bounty(
            bounty_id="bounty-101",
            title="Soroban Contract Port",
            poster_rtc=poster.address,
            poster_bottube="poster_agent",
            escrow_rtc=100.0,
            escrow_bottube=500.0,
        )

        # Submit claim
        claim_res = manager.submit_claim(
            bounty_id="bounty-101",
            claimant_rtc=claimant.address,
            claimant_bottube="claimant_agent",
            proof_url="https://github.com/Scottcjn/rustchain-bounties/pull/99",
            notes="Completed with 100% unit tests",
        )
        assert claim_res["status"] == "success"
        assert claim_res["bounty_status"] == BountyStatus.UNDER_REVIEW.value

        # Settle 100% to claimant
        settle_res = manager.settle_bounty(bounty_id="bounty-101")
        assert settle_res["status"] == "success"
        assert settle_res["bounty"]["status"] == BountyStatus.SETTLED.value

        disbursements = settle_res["disbursements"]
        assert len(disbursements) == 1
        assert disbursements[0]["rtc_amount"] == 100.0
        assert disbursements[0]["bottube_amount"] == 500.0

        # Check reputation boost
        rep = manager.get_reputation(claimant.address)
        assert rep["bounties_completed"] == 1
        assert rep["total_rtc_earned"] == 100.0
        assert rep["total_bottube_earned"] == 500.0
        assert rep["score"] > 100

    def test_bounty_split_settlement_with_reviewer(self):
        manager = CrossBountyEscrowManager()
        poster = RustChainWallet.create()
        claimant = RustChainWallet.create()
        reviewer = RustChainWallet.create()

        manager.create_bounty(
            bounty_id="bounty-split-01",
            title="Complex Kernel Optimization",
            poster_rtc=poster.address,
            poster_bottube="core_dev",
            escrow_rtc=200.0,
            escrow_bottube=1000.0,
        )

        manager.submit_claim(
            bounty_id="bounty-split-01",
            claimant_rtc=claimant.address,
            claimant_bottube="kernel_ninja",
            proof_url="https://github.com/pr/123",
        )

        # 80% Claimant, 20% Universal Auditor Reviewer
        settle_res = manager.settle_bounty(
            bounty_id="bounty-split-01",
            split_ratios={"claimant": 0.8, "reviewer": 0.2},
            reviewer_rtc=reviewer.address,
            reviewer_bottube="universal_auditor",
        )

        disbursements = settle_res["disbursements"]
        assert len(disbursements) == 2
        assert disbursements[0]["rtc_amount"] == 160.0
        assert disbursements[0]["bottube_amount"] == 800.0
        assert disbursements[1]["rtc_amount"] == 40.0
        assert disbursements[1]["bottube_amount"] == 200.0

    def test_bounty_cancellation_and_refund(self):
        manager = CrossBountyEscrowManager()
        poster = RustChainWallet.create()

        manager.create_bounty(
            bounty_id="bounty-refund-01",
            title="Deprecated Feature",
            poster_rtc=poster.address,
            poster_bottube="poster_user",
            escrow_rtc=50.0,
            escrow_bottube=200.0,
        )

        refund_res = manager.cancel_and_refund("bounty-refund-01", reason="No longer needed")
        assert refund_res["status"] == "success"
        assert refund_res["refunded_rtc"] == 50.0
        assert refund_res["refunded_bottube"] == 200.0
        assert refund_res["bounty"]["status"] == BountyStatus.REFUNDED.value


# ============================================================================
# 6. Cryptographic Receipt Chain Audit Trail Tests
# ============================================================================

class TestReceiptChaining:
    """Test tamper-evident cryptographic receipt chaining and verification."""

    def test_receipt_audit_chain_and_tampering_detection(self):
        receipt_mgr = CryptographicReceiptManager()

        r1 = receipt_mgr.generate_receipt("op1", "senderA", "recipB", 1.0)
        r2 = receipt_mgr.generate_receipt("op2", "senderB", "recipC", 2.0)

        # r2 must chain to r1's hash
        assert r2["data"]["prev_hash"] == r1["receipt_hash"]

        # Verification of both receipts
        assert CryptographicReceiptManager.verify_receipt(r1) is True
        assert CryptographicReceiptManager.verify_receipt(r2) is True

        # Tampered amount in data must fail verification
        tampered_r = dict(r1)
        tampered_r["data"] = dict(r1["data"])
        tampered_r["data"]["amount"] = 999.0
        assert CryptographicReceiptManager.verify_receipt(tampered_r) is False
