# Dockerized RustChain Miner
> Last updated: 2026-04-09
## Overview
The Dockerized RustChain Miner allows users to easily set up and run the miner using Docker and Docker Compose. This feature simplifies the process of earning RTC by providing a one-command solution for starting the mining process.
## How It Works
The implementation includes a `Dockerfile` located at `reproducible/Dockerfile`, which sets up a Python environment and runs the `rustchain_universal_miner.py` script. The `docker-compose.yml` file defines the miner service, allowing users to configure environment variables such as WALLET and NODE_URL. A health check is also included to monitor the miner's status.
## Configuration
- **WALLET**: Your RTC wallet address (e.g., `your-wallet-address`).
- **NODE_URL**: The RustChain node URL (e.g., `http://localhost:3030`).
## Usage
To start mining RTC, run the following command:
```bash
docker-compose up
```
## References
- Closes issue #2865