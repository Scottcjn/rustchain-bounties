"""
RustChain Agent-to-Agent Payments Gateway Server (Bounty #35 Reference Implementation)
Provides HTTP REST endpoints for Upvotes, Donations, Cross-Wallet Bridge, x402 Protected APIs, and Escrow.
"""

from __future__ import annotations

import os
from flask import Flask, jsonify, request, g

from rustchain_sdk import (
    RustChainWallet,
    UpvoteDonateService,
    CrossWalletBridge,
    X402ServerManager,
    require_rtc_payment,
    CrossBountyEscrowManager,
    CryptographicReceiptManager,
    DonationTier,
    BridgeStatus,
    BountyStatus,
)

def create_app() -> Flask:
    app = Flask(__name__)

    # Initialize shared payment managers
    system_wallet = RustChainWallet.create()
    receipt_mgr = CryptographicReceiptManager(system_wallet=system_wallet)
    upvote_service = UpvoteDonateService(receipt_manager=receipt_mgr)
    bridge_service = CrossWalletBridge(exchange_rate=1.0, fee_basis_points=10, receipt_manager=receipt_mgr)
    x402_mgr = X402ServerManager(receipt_manager=receipt_mgr)
    escrow_mgr = CrossBountyEscrowManager(receipt_manager=receipt_mgr)

    # Provider wallet for protected services
    provider_wallet = RustChainWallet.create()

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "online",
            "service": "RustChain Agent-to-Agent Payment Gateway",
            "version": "1.0.0",
            "system_address": system_wallet.address,
            "provider_address": provider_wallet.address,
        })

    # =========================================================================
    # Milestone 1: Upvote + Donate Endpoints
    # =========================================================================

    @app.route("/api/upvote", methods=["POST"])
    def record_upvote():
        """Record a free upvote signal."""
        data = request.get_json() or {}
        content_id = data.get("content_id")
        voter = data.get("voter")
        platform = data.get("platform", "bottube")
        multiplier = float(data.get("hardware_multiplier", 1.0))

        if not content_id or not voter:
            return jsonify({"error": "content_id and voter are required"}), 400

        try:
            res = upvote_service.upvote(
                content_id=content_id,
                voter=voter,
                platform=platform,
                hardware_multiplier=multiplier,
            )
            return jsonify(res), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/donate", methods=["POST"])
    def record_donation():
        """Record an upvote with RTC micro-donation."""
        data = request.get_json() or {}
        content_id = data.get("content_id")
        voter = data.get("voter")
        creator = data.get("creator")
        amount = float(data.get("amount", 0.0))
        signed_tx = data.get("signed_tx")
        platform = data.get("platform", "bottube")
        multiplier = float(data.get("hardware_multiplier", 1.0))

        if not content_id or not voter or not creator or amount <= 0:
            return jsonify({"error": "content_id, voter, creator, and positive amount are required"}), 400

        try:
            res = upvote_service.upvote_donate(
                content_id=content_id,
                voter=voter,
                creator=creator,
                amount=amount,
                signed_tx=signed_tx,
                platform=platform,
                hardware_multiplier=multiplier,
            )
            return jsonify(res), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/content/<content_id>/stats", methods=["GET"])
    def get_content_stats(content_id: str):
        """Fetch statistics and top tippers for content."""
        stats = upvote_service.get_content_stats(content_id)
        return jsonify(stats), 200

    @app.route("/api/creator/<creator>/earnings", methods=["GET"])
    def get_creator_earnings(creator: str):
        """Fetch total earnings received by a creator."""
        earnings = upvote_service.get_creator_earnings(creator)
        return jsonify(earnings), 200

    # =========================================================================
    # Milestone 2: Cross-Wallet Bridge Endpoints
    # =========================================================================

    @app.route("/api/bridge/rates", methods=["GET"])
    def get_bridge_rates():
        return jsonify({
            "exchange_rate_rtc_to_botttube": bridge_service.exchange_rate,
            "fee_basis_points": bridge_service.fee_basis_points,
            "fee_percentage": f"{bridge_service.fee_basis_points / 100.0:.2f}%",
        })

    @app.route("/api/bridge/rtc-to-botttube", methods=["POST"])
    def bridge_rtc_to_botttube():
        data = request.get_json() or {}
        rtc_address = data.get("rtc_address")
        botttube_user = data.get("botttube_user")
        amount = float(data.get("amount", 0.0))
        signed_transfer = data.get("signed_transfer")

        try:
            tx = bridge_service.rtc_to_botttube(
                rtc_address=rtc_address,
                botttube_user=botttube_user,
                amount=amount,
                signed_transfer=signed_transfer,
            )
            return jsonify({"status": "success", "transaction": tx.to_dict()}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/bridge/botttube-to-rtc", methods=["POST"])
    def bridge_botttube_to_rtc():
        data = request.get_json() or {}
        botttube_user = data.get("botttube_user")
        rtc_address = data.get("rtc_address")
        amount = float(data.get("amount", 0.0))

        try:
            tx = bridge_service.botttube_to_rtc(
                botttube_user=botttube_user,
                rtc_address=rtc_address,
                amount=amount,
            )
            return jsonify({"status": "success", "transaction": tx.to_dict()}), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/bridge/tx/<tx_id>", methods=["GET"])
    def get_bridge_tx(tx_id: str):
        tx = bridge_service.get_transaction(tx_id)
        if not tx:
            return jsonify({"error": "Transaction not found"}), 404
        return jsonify(tx), 200

    @app.route("/api/bridge/balances/<identity>", methods=["GET"])
    def get_bridge_balances(identity: str):
        return jsonify(bridge_service.get_balances(identity)), 200

    # =========================================================================
    # Milestone 3: Agent-to-Agent x402 Protected Services
    # =========================================================================

    @app.route("/api/agent/inference", methods=["POST"])
    @require_rtc_payment(price=0.001, recipient=provider_wallet.address, service_name="AI Inference", server_manager=x402_mgr)
    def agent_inference():
        data = request.get_json() or {}
        prompt = data.get("prompt", "")
        return jsonify({
            "status": "success",
            "model": "rustchain-llm-v1",
            "prompt": prompt,
            "response": f"[AI Response] Processed inference request: '{prompt}'. Payment verified.",
            "receipt": getattr(g, "payment_receipt", None),
        })

    @app.route("/api/agent/code-review", methods=["POST"])
    @require_rtc_payment(price=0.01, recipient=provider_wallet.address, service_name="Universal Code Review", server_manager=x402_mgr)
    def agent_code_review():
        data = request.get_json() or {}
        pr_url = data.get("pr_url", "")
        return jsonify({
            "status": "success",
            "review_status": "APPROVED",
            "verdict": "All security invariants and Ed25519 signatures verified.",
            "pr_url": pr_url,
            "receipt": getattr(g, "payment_receipt", None),
        })

    @app.route("/api/agent/data-feed", methods=["POST"])
    @require_rtc_payment(price=0.005, recipient=provider_wallet.address, service_name="Real-time Network Feed", server_manager=x402_mgr)
    def agent_data_feed():
        data = request.get_json() or {}
        metric = data.get("metric", "network_tps")
        return jsonify({
            "status": "success",
            "metric": metric,
            "value": 142.8,
            "active_nodes": 64,
            "receipt": getattr(g, "payment_receipt", None),
        })

    # =========================================================================
    # Milestone 4: Cross-Bounty Escrow Endpoints
    # =========================================================================

    @app.route("/api/escrow/bounties", methods=["POST", "GET"])
    def handle_bounties():
        if request.method == "POST":
            data = request.get_json() or {}
            try:
                res = escrow_mgr.create_bounty(
                    bounty_id=data.get("bounty_id"),
                    title=data.get("title"),
                    poster_rtc=data.get("poster_rtc"),
                    poster_bottube=data.get("poster_bottube"),
                    escrow_rtc=float(data.get("escrow_rtc", 0.0)),
                    escrow_bottube=float(data.get("escrow_bottube", 0.0)),
                    description=data.get("description", ""),
                    stipulations=data.get("stipulations", []),
                )
                return jsonify(res), 201
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
        else:
            return jsonify({"bounties": escrow_mgr.list_bounties()}), 200

    @app.route("/api/escrow/bounty/<bounty_id>", methods=["GET"])
    def get_bounty_detail(bounty_id: str):
        bounty = escrow_mgr.get_bounty(bounty_id)
        if not bounty:
            return jsonify({"error": "Bounty not found"}), 404
        return jsonify(bounty), 200

    @app.route("/api/escrow/claim", methods=["POST"])
    def submit_bounty_claim():
        data = request.get_json() or {}
        try:
            res = escrow_mgr.submit_claim(
                bounty_id=data.get("bounty_id"),
                claimant_rtc=data.get("claimant_rtc"),
                claimant_bottube=data.get("claimant_bottube"),
                proof_url=data.get("proof_url"),
                notes=data.get("notes", ""),
            )
            return jsonify(res), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/escrow/settle", methods=["POST"])
    def settle_bounty():
        data = request.get_json() or {}
        try:
            res = escrow_mgr.settle_bounty(
                bounty_id=data.get("bounty_id"),
                claim_id=data.get("claim_id"),
                split_ratios=data.get("split_ratios"),
                reviewer_rtc=data.get("reviewer_rtc"),
                reviewer_bottube=data.get("reviewer_bottube"),
            )
            return jsonify(res), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    @app.route("/api/escrow/reputation/<identity>", methods=["GET"])
    def get_reputation(identity: str):
        return jsonify(escrow_mgr.get_reputation(identity)), 200

    # =========================================================================
    # Audit Trail Endpoints
    # =========================================================================

    @app.route("/api/receipts/audit-trail", methods=["GET"])
    def get_audit_trail():
        limit = int(request.args.get("limit", 50))
        return jsonify({"audit_trail": receipt_mgr.get_audit_trail(limit=limit)}), 200

    @app.route("/api/receipts/verify", methods=["POST"])
    def verify_receipt_endpoint():
        receipt = request.get_json() or {}
        is_valid = CryptographicReceiptManager.verify_receipt(receipt)
        return jsonify({"valid": is_valid}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8004))
    print(f"[*] Starting RustChain Agent Payment Gateway on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
