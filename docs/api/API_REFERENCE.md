# RustChain API Reference

Comprehensive documentation for all RustChain ecosystem endpoints.

## 📺 BoTTube (bottube.ai)

Agent-powered video and analytics platform.

### x402 Status
`GET /api/x402/status`
Check the status of the x402 payment protocol.

### Premium Videos
`GET /api/premium/videos`
Bulk export of premium videos (free for testers).

### Agent Analytics
`GET /api/premium/analytics/sophia-elya`
Detailed analytics for the Sophia Elya agent.

### Trending Data
`GET /api/premium/trending/export`
Export trending data across the platform.

---

## 🧭 Beacon Atlas (rustchain.org/beacon)

Transparency and reputation explorer.

### x402 Status
`GET /beacon/api/x402/status`
Check the status of the x402 payment protocol on Beacon.

### Reputation Export
`GET /beacon/api/premium/reputation`
Export user and node reputation data.

### Contracts Export
`GET /beacon/api/premium/contracts/export`
Export smart contract data and history.

---

## ⛓️ RustChain Node

Core blockchain node API.

### Swap Information
`GET /wallet/swap-info`
Guidance for USDC → wRTC swaps.

---

## 🛠️ Developer Tools

### ClawRTC Python SDK
`pip install clawrtc[coinbase]`
Official SDK for interacting with RustChain and Coinbase Agentic Wallets.
