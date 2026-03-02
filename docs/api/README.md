# RustChain Node API Documentation

This directory contains the OpenAPI 3.0 specification and Swagger UI for the RustChain Node API.

## Files

- `openapi.yaml` - OpenAPI 3.0 specification file
- `swagger.html` - Self-contained Swagger UI page
- `README.md` - This file

## Quick Start

### View the Documentation

1. Start a local web server in this directory:
   ```bash
   python3 -m http.server 8000
   ```

2. Open in your browser:
   ```
   http://localhost:8000/swagger.html
   ```

### Validate the Spec

Install swagger-cli:
```bash
npm install -g @redocly/cli
```

Validate:
```bash
redocly lint openapi.yaml
```

Or using swagger-cli:
```bash
npm install -g swagger-cli
swagger-cli validate openapi.yaml
```

## API Base URLs

- Production: `https://rustchain.org`
- Alternative: `https://50.28.86.131`

## Testing Endpoints

### Health Check
```bash
curl -sk https://rustchain.org/health
```

### Epoch Information
```bash
curl -sk https://rustchain.org/epoch
```

### Active Miners
```bash
curl -sk https://rustchain.org/api/miners
```

### Miner Balance
```bash
curl -sk "https://rustchain.org/wallet/balance?miner_id=YOUR_MINER_ID"
```

## Authentication

Some endpoints require an `X-Admin-Key` header:

```bash
curl -sk https://rustchain.org/attest/challenge \
  -H "X-Admin-Key: YOUR_ADMIN_KEY" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Endpoints Overview

### Public Endpoints (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Node health check |
| GET | `/ready` | Readiness probe |
| GET | `/epoch` | Current epoch, slot, enrolled miners |
| GET | `/api/miners` | Active miners with attestation data |
| GET | `/api/stats` | Network statistics |
| GET | `/api/hall_of_fame` | Hall of Fame leaderboard (5 categories) |
| GET | `/api/fee_pool` | RIP-301 fee pool statistics |
| GET | `/balance?miner_id=X` | Miner balance lookup |
| GET | `/wallet/balance?miner_id=X` | Alternative balance endpoint |
| GET | `/lottery/eligibility?miner_id=X` | Epoch eligibility check |
| GET | `/explorer` | Block explorer page (redirect) |

### Authenticated Endpoints (X-Admin-Key)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/attest/challenge` | Get attestation challenge |
| POST | `/attest/submit` | Submit hardware attestation |
| POST | `/epoch/enroll` | Enroll for epoch |
| POST | `/wallet/transfer/signed` | Ed25519 signed transfer |
| POST | `/wallet/transfer` | Admin transfer |
| POST | `/withdraw/request` | Withdrawal request |

## Rate Limiting

If you receive HTTP 429 (Too Many Requests), implement exponential backoff before retrying.

## TLS Note

The node currently uses a self-signed certificate. For testing with curl:

```bash
curl -sk https://rustchain.org/health
```

## Version

API Version: 2.2.1-rip200

## License

MIT
