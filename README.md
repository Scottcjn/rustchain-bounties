# RustChain Miner

## Quick Start

To get started mining RTC, ensure you have Docker and Docker Compose installed. Follow the steps below to set up the miner.

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-repo-url/rustchain-bounties.git
cd rustchain-bounties
```

### Step 2: Build the Docker Image

```bash
docker-compose build
```

### Step 3: Run the Miner

You can start the mining with the following command:

```bash
docker-compose up
```

### Step 4: Health Check

The miner has a health check endpoint exposed which is accessible through:

```bash
http://localhost:8080/
```

## Configuration

Here are the environment variables needed to run the RustChain Miner:

- **WALLET**: Your RTC wallet address (e.g., `your-wallet-address`). This is where your earnings will be sent.
- **NODE_URL**: The RustChain node URL (e.g., `http://localhost:3030`) you would like to connect to.

## Features
- Easy setup using Docker and Docker Compose to run the miner.
- **WALLET**: Your RTC wallet address.
- **NODE_URL**: The RustChain node URL you would like to connect to.

## Stopping the Miner
To stop the miner, run:

```bash
docker-compose down
```