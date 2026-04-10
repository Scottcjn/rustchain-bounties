# SPDX-License-Identifier: MIT
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir requests

# Download the RustChain universal miner from the main repository
RUN mkdir -p /app/miners && \
    curl -s -o /app/miners/rustchain_universal_miner.py \
    "https://raw.githubusercontent.com/Scottcjn/Rustchain/main/deprecated/old_miners/rustchain_universal_miner.py" && \
    chmod +x /app/miners/rustchain_universal_miner.py

# Set environment variables
ENV RUSTCHAIN_NODE=${NODE_URL:-https://50.28.86.131}
ENV WALLET=${WALLET:-}

# Health check - simple curl to verify connectivity
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -s -k "${RUSTCHAIN_NODE}/health" > /dev/null || exit 1

# Run the miner
CMD ["python", "/app/miners/rustchain_universal_miner.py"]
