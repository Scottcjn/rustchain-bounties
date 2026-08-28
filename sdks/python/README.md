# rustchain-agent

A small typed Python client for the wallet, payment, and reputation endpoint
families in the active
[RIP-302 specification](https://github.com/Scottcjn/Rustchain/blob/cc78890f63655faff8a7e017ef7e673e2789d8a2/rips/docs/RIP-302-agent-economy.md).

The client intentionally does not expose the former `/agent/jobs`,
`/agent/stats`, or `/agent/reputation/*` marketplace routes. Those routes
are not part of the current RIP-302 API reference.

## Installation

```bash
python -m pip install -e ./sdks/python
```

## Identity format

RustChain wallet addresses are validated before any request. They must use the
canonical `RTC` prefix followed by exactly 40 hexadecimal characters.

```python
from rustchain_agent import RustChainAgent

client = RustChainAgent(
    agent_id="rafaio1",
    wallet_address="RTC0123456789abcdef0123456789abcdef01234567",
    base_url="https://bulbous-bouffant.metalseed.net",
)
```

Agent IDs follow RIP-302: 3-64 lowercase alphanumeric or hyphen characters,
starting with a letter and without consecutive hyphens.

## Read-only examples

```python
wallet = client.get_wallet()
reputation = client.get_reputation()
leaderboard = client.get_reputation_leaderboard(limit=10)
payment = client.get_payment("pay_abc123")
history = client.get_payment_history(limit=25)
proof = client.get_trust_proof()
client.close()
```

## Endpoint coverage

| Method | Endpoint | Client method |
|---|---|---|
| POST | `/api/agent/wallet/create` | `create_wallet()` |
| GET | `/api/agent/wallet/{id}` | `get_wallet()` |
| POST | `/api/agent/payment/send` | `send_payment()` |
| POST | `/api/agent/payment/request` | `request_payment()` |
| GET | `/api/agent/payment/{id}` | `get_payment()` |
| GET | `/api/agent/payment/history` | `get_payment_history()` |
| POST | `/api/agent/payment/x402/challenge` | `create_x402_challenge()` |
| GET | `/api/agent/reputation/{id}` | `get_reputation()` |
| POST | `/api/agent/reputation/attest` | `submit_attestation()` |
| GET | `/api/agent/reputation/leaderboard` | `get_reputation_leaderboard()` |
| GET | `/api/agent/reputation/{id}/proof` | `get_trust_proof()` |

The POST methods are SDK wrappers only. The live verification performed for
this submission sent no wallet creation, payment, payment request, x402
challenge, or attestation.

## Tests

The tests assert exact request URLs, query parameters, and JSON payloads. Every
mutating call is intercepted by `responses`; the unit suite does not contact a
live node.

```bash
cd sdks/python
python -m pytest -q
```

## Live-node evidence

A sanitized, timestamped GET transcript is versioned at
[`evidence/live_node_get_20260828.json`](evidence/live_node_get_20260828.json).

At capture time the named node answered `GET /api/stats` with HTTP 200, but
its advertised feature list did not include RIP-302 and
`GET /api/agent/reputation/leaderboard?limit=1` returned HTTP 404. This is
recorded rather than hidden: the client matches the active specification, while
availability of those routes depends on the server deployment.

## License

MIT
