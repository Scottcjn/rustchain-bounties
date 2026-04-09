# OTC Bridge - RustChain Escrow System

A peer-to-peer OTC trading platform for RTC <-> ETH/ERG/USDC with automated escrow.

## Architecture

```
┌─────────────┐    ┌─────────────┐
│   Buyer     │    │   Seller    │
└──────┬──────┘    └──────┬──────┘
       │                  │
       ▼                  ▼
┌─────────────────────────────────────┐
│        Flask OTC Bridge API         │
│  ┌─────────┐  ┌─────────────────┐  │
│  │ Orders  │  │  Escrow Manager  │  │
│  └─────────┘  └─────────────────┘  │
│  ┌─────────┐  ┌─────────────────┐  │
│  │ History │  │ Rate Limiter    │  │
│  └─────────┘  └─────────────────┘  │
└─────────────────────────────────────┘
            │              │
            ▼              ▼
     ┌──────────┐   ┌──────────┐
     │RustChain │   │ ETH/ERG  │
     │Node      │   │ Contract │
     └──────────┘   └──────────┘
```

## API Endpoints

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - List orders
- `GET /api/orders/<id>` - Get order details
- `DELETE /api/orders/<id>` - Cancel order

### Escrow
- `POST /api/escrow/create` - Create escrow
- `POST /api/escrow/deposit` - Deposit to escrow
- `POST /api/escrow/release` - Release funds
- `POST /api/escrow/cancel` - Cancel escrow

### Trading
- `POST /api/trade/execute` - Execute trade
- `GET /api/trade/history` - Trade history

## Running

```bash
pip install flask requests
python app.py
```

## Environment Variables

- `RUSTCHAIN_NODE_URL` - RustChain node URL (default: https://50.28.86.131)
- `ETH_ESCROW_PRIVATE_KEY` - ETH escrow private key
- `ERGO_NODE_URL` - Ergo node URL (default: 50.28.86.131:9053)