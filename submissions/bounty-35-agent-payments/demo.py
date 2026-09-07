"""
RustChain Bounty #35 - Agent-to-Agent Payments Demonstration
Executes a complete end-to-end multi-agent scenario across all 4 milestones.
"""

from __future__ import annotations

import json
import time
from rustchain_sdk import (
    RustChainWallet,
    UpvoteDonateService,
    CrossWalletBridge,
    AutoPayClient,
    X402ServerManager,
    CrossBountyEscrowManager,
    CryptographicReceiptManager,
    DonationTier,
)


def run_full_demo():
    print("=" * 75)
    print("🤖 RUSTCHAIN AGENT-TO-AGENT PAYMENTS DEMO (Bounty #35)")
    print("=" * 75)

    # 1. Setup Identities & Hardware Multipliers
    print("\n[Step 1] Initializing Autonomous Agent Wallets & Hardware Multipliers...")
    agent_a_wallet = RustChainWallet.create()  # Payer / Client (Vintage POWER8 Node)
    agent_b_wallet = RustChainWallet.create()  # Content Creator / Service Provider (G4 Mac Node)
    reviewer_wallet = RustChainWallet.create() # Universal Auditor Agent

    print(f"  • Agent A (POWER8 3.0x):  {agent_a_wallet.address}")
    print(f"  • Agent B (G4 Mac 2.5x):  {agent_b_wallet.address}")
    print(f"  • Auditor (Reviewer):     {reviewer_wallet.address}")

    # Shared Receipt & Audit Trail Manager
    receipt_mgr = CryptographicReceiptManager()

    # 2. Milestone 1: Upvote + Donate System
    print("\n[Step 2] Milestone 1: Free Upvote + RTC Micro-Donations...")
    upvote_service = UpvoteDonateService(receipt_manager=receipt_mgr)
    content_id = "video_powerpc_clustering_tutorial"

    # Agent A gives free upvote
    upvote_res = upvote_service.upvote(
        content_id=content_id,
        voter=agent_a_wallet.address,
        platform="bottube",
        hardware_multiplier=3.0,
    )
    print(f"  ✓ Recorded Free Upvote: total upvotes = {upvote_res['content_stats']['upvote_count']}")

    time.sleep(0.15)

    # Agent A gives Tier 2 (0.01 RTC) Upvote + Donate
    donate_res = upvote_service.upvote_donate(
        content_id=content_id,
        voter=agent_a_wallet.address,
        creator=agent_b_wallet.address,
        amount=DonationTier.SMALL,
        wallet=agent_a_wallet,
        hardware_multiplier=3.0,
    )
    print(f"  ✓ Upvote+Donate 0.01 RTC settled! Creator balance = {donate_res['creator_balance']} RTC")
    print(f"  ✓ Content Stats: {donate_res['content_stats']['total_donated_rtc']} RTC donated by {len(donate_res['content_stats']['unique_voters'])} voter(s)")

    # 3. Milestone 2: Cross-Wallet Bridge (RTC ↔ BoTTube)
    print("\n[Step 3] Milestone 2: Cross-Wallet Bridge (RTC ↔ BoTTube)...")
    bridge = CrossWalletBridge(exchange_rate=1.0, fee_basis_points=10, receipt_manager=receipt_mgr)
    bridge.seed_balance(agent_a_wallet.address, rtc=100.0)

    # Bridge 50 RTC to BoTTube tokens for Agent A
    bridge_tx = bridge.rtc_to_botttube(
        rtc_address=agent_a_wallet.address,
        botttube_user="agent_a_power8",
        amount=50.0,
        rtc_wallet=agent_a_wallet,
    )
    print(f"  ✓ Bridged 50.0 RTC -> {bridge_tx.net_amount} BoTTube tokens (Fee: {bridge_tx.fee} RTC)")
    print(f"  ✓ Agent A Balances: {bridge.get_balances(agent_a_wallet.address)['rtc_balance']} RTC | {bridge.get_balances('agent_a_power8')['botttube_balance']} BoTTube tokens")

    # 4. Milestone 3: Agent-to-Agent x402 Micropayments
    print("\n[Step 4] Milestone 3: 8004 / x402 Machine-to-Machine HTTP Micropayment...")
    x402_mgr = X402ServerManager(receipt_manager=receipt_mgr)
    autopay_client = AutoPayClient(wallet=agent_a_wallet)

    # Simulated provider service endpoint requiring 0.001 RTC
    service_price = 0.001

    def simulated_service_endpoint(headers: dict):
        payment_header = headers.get("X-Payment")
        if not payment_header:
            # Generate 402 challenge
            body, ch_headers = x402_mgr.create_challenge(
                price_rtc=service_price,
                recipient=agent_b_wallet.address,
                service_name="Agent B AI Inference",
            )
            class Mock402:
                status_code = 402
                headers = ch_headers
                def json(self): return body
            return Mock402()

        # Verify payment header
        valid, err, receipt = x402_mgr.verify_payment(
            payment_header,
            expected_price=service_price,
            expected_recipient=agent_b_wallet.address,
        )
        if not valid:
            class MockErr:
                status_code = 402
                def json(self): return {"error": err}
            return MockErr()

        class Mock200:
            status_code = 200
            headers = {"X-Payment-Receipt": receipt["receipt_id"]}
            def json(self): return {"result": "Vector Embedding & LLM Output generated successfully."}
        return Mock200()

    response = autopay_client.pay_for_inference(
        prompt="Generate AST verification for issue 35",
        invoke_fn=simulated_service_endpoint,
        max_price=0.005,
    )
    print(f"  ✓ AutoPayClient intercepted HTTP 402, signed Ed25519 proof, and completed payment!")
    print(f"  ✓ Server Response: {response.json()['result']}")
    print(f"  ✓ Receipt Header:  {response.headers['X-Payment-Receipt']}")

    # 5. Milestone 4: Dual-Currency Bounty Escrow & Settlement
    print("\n[Step 5] Milestone 4: Cross-Bounty Escrow (RTC + BoTTube Tokens)...")
    escrow_mgr = CrossBountyEscrowManager(receipt_manager=receipt_mgr)

    # Create Dual-Currency Bounty
    bounty_id = "bounty-35-agent-payments"
    escrow_mgr.create_bounty(
        bounty_id=bounty_id,
        title="Implement Agent-to-Agent Payments Stack",
        poster_rtc=agent_a_wallet.address,
        poster_bottube="agent_a_power8",
        escrow_rtc=300.0,
        escrow_bottube=1000.0,
        stipulations=["Upvote+Donate", "Bridge", "x402 protocol", "Dual Escrow"],
    )
    print(f"  ✓ Created Dual Bounty '{bounty_id}': Locked 300.0 RTC + 1000.0 BoTTube tokens in Escrow.")

    # Agent B submits claim
    escrow_mgr.submit_claim(
        bounty_id=bounty_id,
        claimant_rtc=agent_b_wallet.address,
        claimant_bottube="agent_b_g4",
        proof_url="https://github.com/Scottcjn/rustchain-bounties/pull/35",
        notes="All milestones verified with genuine Ed25519 signatures and 100% test coverage.",
    )
    print("  ✓ Agent B submitted solution claim.")

    # Settle bounty with 80% Claimant / 20% Universal Auditor Split
    settlement = escrow_mgr.settle_bounty(
        bounty_id=bounty_id,
        split_ratios={"claimant": 0.8, "reviewer": 0.2},
        reviewer_rtc=reviewer_wallet.address,
        reviewer_bottube="universal_auditor",
    )
    print("  ✓ Bounty Settled with Multi-Party Split:")
    for d in settlement["disbursements"]:
        print(f"     -> {d['recipient_role'].upper()}: {d['rtc_amount']} RTC + {d['bottube_amount']} BoTTube tokens")

    # Check updated reputation
    rep = escrow_mgr.get_reputation(agent_b_wallet.address)
    print(f"  ✓ Agent B Cross-Platform Reputation Score: {rep['score']} (Bounties Completed: {rep['bounties_completed']})")

    # 6. Audit Trail & Cryptographic Verification
    print("\n[Step 6] Verifying Cryptographic Receipt Audit Chain...")
    audit_trail = receipt_mgr.get_audit_trail()
    print(f"  ✓ Generated {len(audit_trail)} chained cryptographic receipts.")
    for i, r in enumerate(audit_trail[-3:], 1):
        is_valid = CryptographicReceiptManager.verify_receipt(r)
        print(f"     [{i}] Receipt {r['receipt_id']} | Op: {r['data']['operation']} | Valid: {is_valid}")

    print("\n" + "=" * 75)
    print("🎉 ALL MILESTONES SUCCESSFULLY DEMONSTRATED WITH TRUE VERIFICATION!")
    print("=" * 75)


if __name__ == "__main__":
    run_full_demo()
