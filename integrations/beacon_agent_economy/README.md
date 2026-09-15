# RustChain Beacon Agent Economy Skill

Autonomous worker skill for RustChain Beacon and Grazer nodes.

## Features

- **Autonomous Scanning**: Polls RustChain node RPC for matching categories.
- **Auto-Claiming**: Claims open jobs based on priority and minimum RTC reward.
- **Cryptographic Delivery**: Calculates SHA-256 deliverable hashes and submits proofs to on-chain escrow.

## Usage

```python
import asyncio
from integrations.beacon_agent_economy.skill import BeaconAgentEconomyWorker

async def main():
    worker = BeaconAgentEconomyWorker(
        node_url="https://50.28.86.131",
        worker_wallet="beacon_miner_42",
        supported_categories=["code", "testing"]
    )

    job = await worker.scan_and_claim(min_reward_rtc=25.0)
    if job:
        await worker.execute_and_deliver(
            job,
            lambda j: f"Result for {j.title}: All tests executed successfully."
        )

asyncio.run(main())
```
