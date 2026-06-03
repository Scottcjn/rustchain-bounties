tier: T2
target: rustchain
language: python
endpoints_used: ["/health", "/epoch", "/api/miners", "/wallet/balance?miner_id=<wallet>"]
wallet: RTCc0ffae7b0e9511b78551f71151f0e1819015a1c0
starred: yes

# RustChain Live Balance Verifier

This integration is a small Python script that reads live RustChain node data and verifies a wallet balance response.

It qualifies for T2 because it performs the T1 live reads, then verifies that the wallet balance endpoint returns a matching native RTC wallet, numeric balance fields, and an active-miner cross-check when the wallet is present in the live miner list.

