tier: T2
target: rustchain
language: python
endpoints_used: [https://rustchain.org/wallet/balance]
wallet: RTCc0ffae7b0e9511b78551f71151f0e1819015a1c0
starred: yes

# RustChain Live Balance Verifier

This integration queries RustChain's live wallet balance endpoint and verifies
that the response is internally consistent for a native RTC wallet/miner ID.

It performs three checks:

- the endpoint returns the same `miner_id` that was requested
- `amount_i64` and `amount_rtc` are numeric
- `amount_rtc` matches `amount_i64 / 100000000`

