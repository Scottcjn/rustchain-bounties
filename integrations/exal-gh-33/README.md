# RustChain Live Balance Verifier

Small T2 integration for bounty #13040. It queries a live RustChain endpoint and
verifies a native RTC wallet balance response.

## Run

```bash
python3 rustchain_balance_verify.py RTCc0ffae7b0e9511b78551f71151f0e1819015a1c0
```

Optional endpoint override:

```bash
python3 rustchain_balance_verify.py RTCc0ffae7b0e9511b78551f71151f0e1819015a1c0 --endpoint https://rustchain.org/wallet/balance
```

## Live Transcript

```text
$ python3 rustchain_balance_verify.py RTCc0ffae7b0e9511b78551f71151f0e1819015a1c0
endpoint: https://rustchain.org/wallet/balance
miner_id: RTCc0ffae7b0e9511b78551f71151f0e1819015a1c0
amount_i64: 0
amount_rtc: 0.0
verification: PASS
```

