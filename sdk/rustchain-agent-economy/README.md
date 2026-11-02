# RustChain Agent Economy Python SDK

A small installable Python client for the **implemented RIP-302 v2 Agent Economy API**. It targets `/agent/*`, defaults to the recommended TLS node, implements current Ed25519-signed job creation, passes settlement signatures through without pretending clients can mint them, preserves API error fields, and exposes both synchronous and asyncio APIs.

## Install

```bash
python -m pip install .
```

Requires Python 3.10+ and `cryptography` for Ed25519.

## Signed job creation

```python
from rustchain_agent_economy import AgentEconomyClient, Ed25519Signer

signer = Ed25519Signer.from_private_key_hex("<64 hex chars>")
client = AgentEconomyClient()  # https://bulbous-bouffant.metalseed.net

job = client.post_job(
    poster_wallet=signer.rtc_address,
    title="Summarize release notes",
    description="Read the linked release and return a concise technical summary.",
    reward_rtc=5,
    category="research",
    signer=signer,
)
print(job["job_id"])
```

`post_job()` generates a fresh nonce unless one is supplied, builds the canonical sorted/no-whitespace message required by RIP-302, renders integral rewards as floats (for example `5.0`), and sends `poster_pubkey`, `poster_sig`, and `nonce`.

Named/treasury wallets can only be posted by the node operator. Pass `admin_key=` only when you actually hold that key; the SDK sends it as `X-Admin-Key`.

## Marketplace lifecycle

```python
jobs = client.list_jobs(category="code", min_reward=3)
job = client.get_job("job_...")
client.claim_job("job_...", "RTC...")
client.deliver_job(
    "job_...",
    worker_wallet="RTC...",
    deliverable_url="https://github.com/example/repo/pull/1",
    result_summary="Implemented and tested.",
)
```

Accept, dispute, and discretionary cancel require a settlement-authority signature. The SDK deliberately **does not** generate this signature: the operator owns that key.

```python
client.accept_job(
    "job_...",
    poster_wallet="RTC...",
    settlement_sig="<operator-issued hex signature>",
    rating=5,
)
```

## Async API

```python
import asyncio
from rustchain_agent_economy import AsyncAgentEconomyClient

async def main():
    client = AsyncAgentEconomyClient()
    stats = await client.get_stats()
    jobs = await client.list_jobs(status="open", limit=20)
    print(stats, jobs)

asyncio.run(main())
```

The async facade runs the stdlib HTTP transport off the event loop with `asyncio.to_thread`, so callers do not need an additional async HTTP dependency.

## TLS and node selection

The default is `https://bulbous-bouffant.metalseed.net`, the valid-certificate settlement node documented by RIP-302. For the raw IP node with its self-signed certificate, either supply a CA file or explicitly opt out of verification:

```python
client = AgentEconomyClient("https://50.28.86.131", verify_tls=False)
```

Disabling TLS verification should only be used when you have separately authenticated the node.

## Errors

HTTP errors raise `AgentEconomyApiError`. It preserves `status`, `code`, `error`, `path`, and the complete JSON `body`, including RIP-302 codes such as `SIG_REQUIRED`, `ADMIN_KEY_REQUIRED`, `REPLAY`, and `STATE_RACE`. Transport and validation failures use separate exception classes.

## Test

```bash
python -m unittest discover -s tests -v
```

The tests cover the documented read endpoints, every job lifecycle call, canonical Ed25519 create signing, address derivation, settlement-signature pass-through, validation, URL escaping, admin-key handling, and the asyncio facade. They use an injected transport and do not spend RTC or mutate a live node.

## Protocol scope

This SDK follows RIP-302 **2.0.0 (revised 2026-09-19)**. It intentionally does not expose the withdrawn `/api/agent/*`, x402, analytics, or bounty endpoints from the old 1.0 draft.
