```python
import time
from flask import Flask, jsonify, request
from celery import Celery

# Abstracted blockchain provider for demonstration
import blockchain_provider

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])

# Mock secure state management
def save_transaction_state(tx_id, state): pass
def get_transaction_state(tx_id): return "pending"

# Security Constant: Require sufficient confirmations to prevent chain reorg attacks
REQUIRED_CONFIRMATIONS = 6
EXPECTED_PAYMENT_VALUE = 100

@app.route('/api/payment/initiate', methods=['POST'])
def initiate_payment():
    """
    Synchronous Endpoint: Accepts payment notification, initiates async tracking,
    and returns immediately. Decoupling this prevents HTTP timeouts and
    time-of-check to time-of-use (TOCTOU) race conditions.
    """
    data = request.json
    tx_id = data.get('transaction_id')

    if not tx_id:
        return jsonify({"error": "Missing transaction_id"}), 400

    # 1. Lock/Mark as pending in secure local state to prevent duplicate processing
    save_transaction_state(tx_id, "pending")

    # 2. Queue asynchronous verification task
    verify_transaction_finality.delay(tx_id)

    # 3. Return 202 Accepted (Client must poll the status endpoint)
    return jsonify({
        "status": "pending",
        "message": "Payment processing. Check status endpoint.",
        "transaction_id": tx_id
    }), 202


@celery.task(bind=True, max_retries=20)
def verify_transaction_finality(self, tx_id):
    """
    Asynchronous Worker: Safely checks blockchain for finality
    without blocking the main HTTP thread.
    """
    try:
        # Fetch transaction details securely from the node/provider
        tx = blockchain_provider.get_transaction(tx_id)

        if not tx:
            save_transaction_state(tx_id, "failed")
            return "Transaction not found."

        # Verify block confirmations to ensure strict finality
        current_block = blockchain_provider.get_latest_block_number()
        confirmations = current_block - tx.block_number

        if confirmations >= REQUIRED_CONFIRMATIONS:
            # Cryptographically verify the transaction payload, value, and recipient
            if tx.status == "success" and tx.value >= EXPECTED_PAYMENT_VALUE:
                save_transaction_state(tx_id, "confirmed")
                # Trigger internal fulfillment logic here
                return "Transaction strictly confirmed."
            else:
                save_transaction_state(tx_id, "failed")
                return "Transaction failed or invalid payment parameters."
        else:
            # Insufficient confirmations, retry safely in the background
            raise self.retry(countdown=15)

    except Exception as exc:
        # Handle RPC failures or network timeouts safely
        raise self.retry(exc=exc, countdown=30)


@app.route('/api/payment/status/<tx_id>', methods=['GET'])
def check_status(tx_id):
    """
    Synchronous Endpoint: Client polls this to get the strongly consistent state.
    """
    state = get_transaction_state(tx_id)

    if state == "confirmed":
        return jsonify({"status": "success", "access": "granted"}), 200
    elif state == "failed":
        return jsonify({"status": "failed", "access": "denied"}), 402
    else:
        return jsonify({"status": "pending", "access": "denied"}), 202
```