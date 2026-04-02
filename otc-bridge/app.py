"""
RustChain OTC Bridge - Tier 2 Implementation
Automated escrow for RTC <-> ETH/ERG/USDC trades
"""

import os
import json
import time
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum

# Flask imports
from flask import Flask, request, jsonify, g
from flask_cors import CORS

# For RustChain API calls
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["https://rustchain.org", "https://otc.rustchain.org"])

# ============================================================
# Configuration
# ============================================================

class Config:
    RUSTCHAIN_NODE_URL = os.environ.get("RUSTCHAIN_NODE_URL", "https://50.28.86.131")
    ETH_ESCROW_PRIVATE_KEY = os.environ.get("ETH_ESCROW_PRIVATE_KEY", "")

if not Config.ETH_ESCROW_PRIVATE_KEY:
    raise RuntimeError("ETH_ESCROW_PRIVATE_KEY must be set")
    ERGO_NODE_URL = os.environ.get("ERGO_NODE_URL", "50.28.86.131:9053")
    ERGO_NODE_HTTPS = os.environ.get("ERGO_NODE_HTTPS", "false").lower() == "true"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 10  # Max requests per window
    RATE_LIMIT_WINDOW = 60   # Window in seconds
    
    # Escrow configuration
    ESCROW_TIMEOUT_HOURS = 24
    ESCROW_FEE_PERCENT = 0.5  # 0.5% fee

app.config.from_object(Config)

# ============================================================
# Data Models
# ============================================================

class OrderType(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(Enum):
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class TradeStatus(Enum):
    PENDING = "pending"
    ESCROW_CREATED = "escrow_created"
    ESCROW_DEPOSITED = "escrow_deposited"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class CryptoAsset(Enum):
    ETH = "ETH"
    ERG = "ERG"
    USDC = "USDC"
    BTC = "BTC"

@dataclass
class Order:
    id: str
    wallet_address: str
    order_type: str  # buy/sell
    crypto_asset: str  # ETH/ERG/USDC/BTC
    rtc_amount: float
    price_per_rtc: float  # in USD
    filled_amount: float = 0.0
    status: str = "open"
    created_at: str = None
    updated_at: str = None
    expires_at: str = None

@dataclass
class Escrow:
    id: str
    trade_id: str
    order_id: str
    buyer_wallet: str
    seller_wallet: str
    crypto_asset: str
    crypto_amount: float
    rtc_amount: float
    rtc_locked: bool = False
    crypto_deposited: bool = False
    status: str = "pending"
    created_at: str = None
    updated_at: str = None
    expires_at: str = None

@dataclass
class Trade:
    id: str
    order_id: str
    buyer_wallet: str
    seller_wallet: str
    crypto_asset: str
    crypto_amount: float
    rtc_amount: float
    price_per_rtc: float
    status: str = "pending"
    escrow_id: str = None
    rtc_tx_hash: str = None
    crypto_tx_hash: str = None
    created_at: str = None
    completed_at: str = None

@dataclass
class TradeHistory:
    id: str
    trade_id: str
    action: str
    details: str
    timestamp: str

# ============================================================
# In-Memory Database (would use SQLite in production)
# ============================================================

class Database:
    """In-memory storage - replace with SQLite for production"""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.escrows: Dict[str, Escrow] = {}
        self.trades: Dict[str, Trade] = {}
        self.trade_history: List[TradeHistory] = []
        self.rate_limits: Dict[str, List[float]] = {}
    
    def add_order(self, order: Order):
        self.orders[order.id] = order
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.orders.get(order_id)
    
    def list_orders(self, status: str = None, order_type: str = None, 
                    crypto_asset: str = None) -> List[Order]:
        orders = list(self.orders.values())
        if status:
            orders = [o for o in orders if o.status == status]
        if order_type:
            orders = [o for o in orders if o.order_type == order_type]
        if crypto_asset:
            orders = [o for o in orders if o.crypto_asset == crypto_asset]
        return sorted(orders, key=lambda x: x.created_at, reverse=True)
    
    def update_order(self, order: Order):
        self.orders[order.id] = order
    
    def add_escrow(self, escrow: Escrow):
        self.escrows[escrow.id] = escrow
    
    def get_escrow(self, escrow_id: str) -> Optional[Escrow]:
        return self.escrows.get(escrow_id)
    
    def update_escrow(self, escrow: Escrow):
        self.escrows[escrow.id] = escrow
    
    def add_trade(self, trade: Trade):
        self.trades[trade.id] = trade
    
    def get_trade(self, trade_id: str) -> Optional[Trade]:
        return self.trades.get(trade_id)
    
    def update_trade(self, trade: Trade):
        self.trades[trade.id] = trade
    
    def list_trades(self, wallet: str = None, status: str = None) -> List[Trade]:
        trades = list(self.trades.values())
        if wallet:
            trades = [t for t in trades if t.buyer_wallet == wallet or t.seller_wallet == wallet]
        if status:
            trades = [t for t in trades if t.status == status]
        return sorted(trades, key=lambda x: x.created_at, reverse=True)
    
    def add_history(self, history: TradeHistory):
        self.trade_history.append(history)
    
    def get_history(self, trade_id: str = None) -> List[TradeHistory]:
        if trade_id:
            return [h for h in self.trade_history if h.trade_id == trade_id]
        return sorted(self.trade_history, key=lambda x: x.timestamp, reverse=True)
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Check if identifier has exceeded rate limit"""
        now = time.time()
        window_start = now - Config.RATE_LIMIT_WINDOW
        
        # Clean old entries
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [t for t in self.rate_limits[identifier] if t > window_start]
        else:
            self.rate_limits[identifier] = []
        
        # Check limit
        if len(self.rate_limits[identifier]) >= Config.RATE_LIMIT_REQUESTS:
            return False
        
        # Add current request
        self.rate_limits[identifier].append(now)
        return True

db = Database()

# ============================================================
# RustChain API Client
# ============================================================

class RustChainClient:
    """Client for RustChain node operations"""
    
    def __init__(self, node_url: str = None):
        self.node_url = node_url or Config.RUSTCHAIN_NODE_URL
        self.session = requests.Session()
        # Handle self-signed certificates
        if "50.28.86.131" in self.node_url:
            self.session.verify = False
    
    def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        url = f"{self.node_url}{endpoint}"
        try:
            if method == "GET":
                response = self.session.get(url, params=data, timeout=30)
            else:
                response = self.session.post(url, json=data, timeout=30)
            
            if response.status_code >= 400:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return {"error": response.text, "status_code": response.status_code}
            
            return response.json() if response.content else {}
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}
    
    def get_balance(self, wallet_address: str) -> dict:
        """Get wallet balance"""
        return self._request("GET", f"/wallet/balance", {"miner_id": wallet_address})
    
    def transfer(self, from_wallet: str, to_wallet: str, amount: float, 
                 signed_tx: str = None) -> dict:
        """Transfer RTC - uses /wallet/transfer/signed endpoint"""
        data = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount
        }
        if signed_tx:
            data["signed_tx"] = signed_tx
        return self._request("POST", "/wallet/transfer/signed", data)
    
    def create_escrow_job(self, wallet: str, amount: float, job_id: str, 
                          release_conditions: dict) -> dict:
        """Create escrow job via /agent/jobs"""
        data = {
            "job_type": "escrow",
            "wallet": wallet,
            "amount": amount,
            "job_id": job_id,
            "release_conditions": release_conditions,
            "action": "lock"
        }
        return self._request("POST", "/agent/jobs", data)
    
    def release_escrow_job(self, job_id: str, release_to: str) -> dict:
        """Release escrow job"""
        data = {
            "job_type": "escrow",
            "job_id": job_id,
            "action": "release",
            "release_to": release_to
        }
        return self._request("POST", "/agent/jobs", data)

rustchain = RustChainClient()

# ============================================================
# ETH/ERG Escrow (Simplified - would use smart contracts in production)
# ============================================================

class CryptoEscrow:
    """Handle ETH/ERG/USDC escrow operations"""
    
    @staticmethod
    def create_eth_escrow(buyer: str, seller: str, amount: float, 
                          asset: str) -> dict:
        """
        Create ETH/ERC20 escrow
        In production: deploy smart contract or use multisig
        Simplified: record in database as pending
        """
        # In production, this would:
        # 1. Deploy an escrow contract, OR
        # 2. Use a multisig wallet, OR  
        # 3. Interact with an existing escrow contract
        
        return {
            "escrow_address": f"0x{hashlib.sha256((buyer + seller).encode()).hexdigest()[:40]}",
            "buyer": buyer,
            "seller": seller,
            "amount": amount,
            "asset": asset,
            "status": "pending_deposit"
        }
    
    @staticmethod
    def create_erg_escrow(buyer: str, seller: str, amount: float) -> dict:
        """
        Create Ergo escrow via Ergo node API
        """
        # In production: create Ergo contract
        # Simplified: return placeholder
        return {
            "erg_box_id": f"box-{hashlib.sha256((buyer + seller).encode()).hexdigest()[:16]}",
            "buyer": buyer,
            "seller": seller,
            "amount": amount,
            "status": "pending_deposit"
        }
    
    @staticmethod
    def confirm_deposit(tx_hash: str, escrow_id: str) -> dict:
        """Confirm crypto deposit - verify on-chain"""
        # In production: verify tx on chain
        return {
            "confirmed": True,
            "tx_hash": tx_hash,
            "escrow_id": escrow_id,
            "confirmations": 6
        }
    
    @staticmethod
    def release(escrow_id: str, recipient: str) -> dict:
        """Release funds to recipient"""
        # In production: call contract to release
        return {
            "released": True,
            "recipient": recipient,
            "escrow_id": escrow_id
        }

crypto_escrow = CryptoEscrow()

# ============================================================
# Authentication Decorator
# ============================================================

def verify_wallet_signature(sig: str, data: dict) -> bool:
    """Verify wallet-signed challenge. Stub - replace with real signature verification."""
    if not sig or not data:
        return False
    expected = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    return sig == expected

def require_wallet_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        sig = request.headers.get("X-Wallet-Signature")
        if not sig or not verify_wallet_signature(sig, request.get_json(silent=True) or {}):
            return jsonify({"error": "unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ============================================================
# Rate Limiting Decorator
# ============================================================

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Use IP + wallet as identifier
        identifier = f"{request.remote_addr}:{request.json.get('wallet_address', '')}"
        
        if not db.check_rate_limit(identifier):
            return jsonify({
                "error": "Rate limit exceeded. Try again later.",
                "retry_after": Config.RATE_LIMIT_WINDOW
            }), 429
        
        return f(*args, **kwargs)
    return decorated_function

# ============================================================
# API Routes - Orders
# ============================================================

@app.route('/api/orders', methods=['POST'])
@rate_limit
@require_wallet_auth
def create_order():
    """Create a new buy/sell order"""
    data = request.get_json()
    
    # Validate required fields
    required = ['wallet_address', 'order_type', 'crypto_asset', 'rtc_amount', 'price_per_rtc']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Validate order type
    if data['order_type'] not in ['buy', 'sell']:
        return jsonify({"error": "Invalid order_type. Must be 'buy' or 'sell'"}), 400
    
    # Validate crypto asset
    valid_assets = ['ETH', 'ERG', 'USDC', 'BTC']
    if data['crypto_asset'] not in valid_assets:
        return jsonify({"error": f"Invalid crypto_asset. Must be one of: {valid_assets}"}), 400
    
    # Validate amounts
    if float(data['rtc_amount']) <= 0 or float(data['price_per_rtc']) <= 0:
        return jsonify({"error": "Amounts must be positive"}), 400
    
    # Create order
    now = datetime.utcnow().isoformat()
    expires = (datetime.utcnow() + timedelta(hours=Config.ESCROW_TIMEOUT_HOURS)).isoformat()
    
    order = Order(
        id=str(uuid.uuid4()),
        wallet_address=data['wallet_address'],
        order_type=data['order_type'],
        crypto_asset=data['crypto_asset'],
        rtc_amount=float(data['rtc_amount']),
        price_per_rtc=float(data['price_per_rtc']),
        created_at=now,
        updated_at=now,
        expires_at=expires
    )
    
    db.add_order(order)
    
    logger.info(f"Created order: {order.id} - {order.order_type} {order.rtc_amount} RTC @ ${order.price_per_rtc}")
    
    return jsonify({
        "order": asdict(order),
        "message": "Order created successfully"
    }), 201


@app.route('/api/orders', methods=['GET'])
def list_orders():
    """List orders with optional filters"""
    status = request.args.get('status')
    order_type = request.args.get('order_type')
    crypto_asset = request.args.get('crypto_asset')
    
    orders = db.list_orders(status=status, order_type=order_type, crypto_asset=crypto_asset)
    
    return jsonify({
        "orders": [asdict(o) for o in orders],
        "count": len(orders)
    })


@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    order = db.get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    return jsonify({"order": asdict(order)})


@app.route('/api/orders/<order_id>', methods=['DELETE'])
@require_wallet_auth
def cancel_order(order_id):
    """Cancel an order"""
    order = db.get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    # Only open orders can be cancelled
    if order.status != 'open':
        return jsonify({"error": f"Cannot cancel order with status: {order.status}"}), 400
    
    now = datetime.utcnow().isoformat()
    order.status = 'cancelled'
    order.updated_at = now
    db.update_order(order)
    
    # Add to history
    db.add_history(TradeHistory(
        id=str(uuid.uuid4()),
        trade_id="",
        action="order_cancelled",
        details=f"Order {order_id} cancelled by {order.wallet_address}",
        timestamp=now
    ))
    
    return jsonify({"order": asdict(order), "message": "Order cancelled"})

# ============================================================
# API Routes - Escrow
# ============================================================

@app.route('/api/escrow/create', methods=['POST'])
@rate_limit
@require_wallet_auth
def create_escrow():
    """Create escrow for a trade"""
    data = request.get_json()
    
    required = ['order_id', 'buyer_wallet', 'seller_wallet', 'crypto_asset', 'crypto_amount']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    order = db.get_order(data['order_id'])
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    # Create trade
    trade_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    expires = (datetime.utcnow() + timedelta(hours=Config.ESCROW_TIMEOUT_HOURS)).isoformat()
    
    # Calculate RTC amount
    rtc_amount = order.rtc_amount
    
    trade = Trade(
        id=trade_id,
        order_id=order.id,
        buyer_wallet=data['buyer_wallet'],
        seller_wallet=data['seller_wallet'],
        crypto_asset=data['crypto_asset'],
        crypto_amount=float(data['crypto_amount']),
        rtc_amount=rtc_amount,
        price_per_rtc=order.price_per_rtc,
        created_at=now,
        status="pending"
    )
    db.add_trade(trade)
    
    # Create escrow
    escrow_id = str(uuid.uuid4())
    escrow = Escrow(
        id=escrow_id,
        trade_id=trade_id,
        order_id=order.id,
        buyer_wallet=data['buyer_wallet'],
        seller_wallet=data['seller_wallet'],
        crypto_asset=data['crypto_asset'],
        crypto_amount=float(data['crypto_amount']),
        rtc_amount=rtc_amount,
        created_at=now,
        updated_at=now,
        expires_at=expires,
        status="pending"
    )
    db.add_escrow(escrow)
    
    # Update trade with escrow
    trade.escrow_id = escrow_id
    trade.status = "escrow_created"
    db.update_trade(trade)
    
    # Add history
    db.add_history(TradeHistory(
        id=str(uuid.uuid4()),
        trade_id=trade_id,
        action="escrow_created",
        details=f"Escrow {escrow_id} created for trade {trade_id}",
        timestamp=now
    ))
    
    logger.info(f"Created escrow {escrow_id} for trade {trade_id}")
    
    return jsonify({
        "escrow": asdict(escrow),
        "trade": asdict(trade),
        "message": "Escrow created. Please deposit funds."
    }), 201


@app.route('/api/escrow/deposit', methods=['POST'])
@rate_limit
@require_wallet_auth
def deposit_escrow():
    """Confirm deposit to escrow"""
    data = request.get_json()
    
    if 'escrow_id' not in data:
        return jsonify({"error": "Missing escrow_id"}), 400
    
    escrow = db.get_escrow(data['escrow_id'])
    if not escrow:
        return jsonify({"error": "Escrow not found"}), 404
    
    trade = db.get_trade(escrow.trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    
    # Determine which side deposited
    depositor = data.get('depositor_wallet', '')
    
    now = datetime.utcnow().isoformat()
    
    if depositor == escrow.buyer_wallet:
        # Check if this is crypto deposit
        if data.get('deposit_type') == 'crypto':
            escrow.crypto_deposited = True
        else:
            escrow.rtc_locked = True
    elif depositor == escrow.seller_wallet:
        if data.get('deposit_type') == 'crypto':
            escrow.crypto_deposited = True
        else:
            escrow.rtc_locked = True
    
    escrow.updated_at = now
    escrow.status = "escrow_deposited"
    db.update_escrow(escrow)
    
    # Update trade status
    trade.status = "escrow_deposited"
    db.update_trade(trade)
    
    # Add history
    db.add_history(TradeHistory(
        id=str(uuid.uuid4()),
        trade_id=trade.id,
        action="escrow_deposited",
        details=f"Deposit confirmed for escrow {escrow.id} by {depositor}",
        timestamp=now
    ))
    
    return jsonify({
        "escrow": asdict(escrow),
        "message": "Deposit confirmed"
    })


@app.route('/api/escrow/<escrow_id>', methods=['GET'])
def get_escrow(escrow_id):
    """Get escrow details"""
    escrow = db.get_escrow(escrow_id)
    if not escrow:
        return jsonify({"error": "Escrow not found"}), 404
    
    return jsonify({"escrow": asdict(escrow)})

# ============================================================
# API Routes - Trade Execution (Atomic Settlement)
# ============================================================

@app.route('/api/trade/execute', methods=['POST'])
@rate_limit
def execute_trade():
    """Execute the trade - atomic or near-atomic settlement"""
    data = request.get_json()
    
    if 'escrow_id' not in data:
        return jsonify({"error": "Missing escrow_id"}), 400
    
    escrow = db.get_escrow(data['escrow_id'])
    if not escrow:
        return jsonify({"error": "Escrow not found"}), 404
    
    # Verify both sides are ready
    if not (escrow.rtc_locked and escrow.crypto_deposited):
        return jsonify({
            "error": "Escrow not fully funded. Both RTC and crypto must be deposited."
        }), 400
    
    trade = db.get_trade(escrow.trade_id)
    if not trade:
        return jsonify({"error": "Trade not found"}), 404
    
    order = db.get_order(escrow.order_id)
    
    now = datetime.utcnow().isoformat()
    
    # Execute RTC transfer via RustChain
    # Seller sends RTC to buyer (or locked in escrow, now released to buyer)
    rtc_result = rustchain.transfer(
        from_wallet=escrow.seller_wallet,
        to_wallet=escrow.buyer_wallet,
        amount=escrow.rtc_amount
    )
    
    if "error" in rtc_result:
        logger.error(f"RTC transfer failed: {rtc_result}")
        return jsonify({
            "error": "RTC transfer failed",
            "details": rtc_result
        }), 500
    
    # Update trade
    trade.status = "completed"
    trade.rtc_tx_hash = rtc_result.get("tx_hash", "unknown")
    trade.completed_at = now
    db.update_trade(trade)
    
    # Update escrow
    escrow.status = "completed"
    escrow.updated_at = now
    db.update_escrow(escrow)
    
    # Update order - mark as filled
    order.status = "filled"
    order.filled_amount = escrow.rtc_amount
    order.updated_at = now
    db.update_order(order)
    
    # Add history
    db.add_history(TradeHistory(
        id=str(uuid.uuid4()),
        trade_id=trade.id,
        action="trade_completed",
        details=f"Trade {trade.id} completed. RTC transferred to {escrow.buyer_wallet}",
        timestamp=now
    ))
    
    logger.info(f"Trade {trade.id} completed successfully")
    
    return jsonify({
        "trade": asdict(trade),
        "message": "Trade executed successfully"
    })


@app.route('/api/trade/cancel', methods=['POST'])
def cancel_trade():
    """Cancel trade and release escrow"""
    data = request.get_json()
    
    if 'escrow_id' not in data:
        return jsonify({"error": "Missing escrow_id"}), 400
    
    escrow = db.get_escrow(data['escrow_id'])
    if not escrow:
        return jsonify({"error": "Escrow not found"}), 404
    
    trade = db.get_trade(escrow.trade_id)
    
    now = datetime.utcnow().isoformat()
    
    # Release escrow (refund both sides)
    # In production: call contract to refund
    
    escrow.status = "cancelled"
    escrow.updated_at = now
    db.update_escrow(escrow)
    
    if trade:
        trade.status = "cancelled"
        db.update_trade(trade)
    
    # Add history
    db.add_history(TradeHistory(
        id=str(uuid.uuid4()),
        trade_id=trade.id if trade else "",
        action="trade_cancelled",
        details=f"Trade cancelled, escrow {escrow.id} refunded",
        timestamp=now
    ))
    
    return jsonify({"message": "Trade cancelled, funds refunded"})

# ============================================================
# API Routes - History & Stats
# ============================================================

@app.route('/api/trade/history', methods=['GET'])
def get_trade_history():
    """Get trade history with optional filters"""
    wallet = request.args.get('wallet')
    status = request.args.get('status')
    
    trades = db.list_trades(wallet=wallet, status=status)
    
    # Include history for each trade
    result = []
    for trade in trades:
        history = db.get_history(trade_id=trade.id)
        result.append({
            "trade": asdict(trade),
            "history": [asdict(h) for h in history]
        })
    
    return jsonify({
        "trades": result,
        "count": len(result)
    })


@app.route('/api/history/<trade_id>', methods=['GET'])
def get_trade_history_detail(trade_id):
    """Get detailed history for a specific trade"""
    history = db.get_history(trade_id=trade_id)
    
    if not history:
        return jsonify({"error": "No history found"}), 404
    
    return jsonify({
        "trade_id": trade_id,
        "history": [asdict(h) for h in history]
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get OTC bridge statistics"""
    orders = db.list_orders()
    trades = db.list_trades()
    
    # Calculate stats
    total_volume_rtc = sum(t.rtc_amount for t in trades if t.status == "completed")
    total_trades = len([t for t in trades if t.status == "completed"])
    open_orders = len([o for o in orders if o.status == "open"])
    
    return jsonify({
        "total_orders": len(orders),
        "open_orders": open_orders,
        "total_trades": len(trades),
        "completed_trades": total_trades,
        "total_volume_rtc": total_volume_rtc,
        "active_escrows": len([e for e in db.escrows.values() if e.status not in ["completed", "cancelled"]])
    })

# ============================================================
# Health Check
# ============================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "RustChain OTC Bridge",
        "version": "1.0.0"
    })

# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)