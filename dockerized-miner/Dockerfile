# RustChain Python Miner Dockerfile
# One-command to start earning RTC
#
# NOTE: Docker miners earn reduced rewards due to anti-VM detection.
# For full rewards, run the miner directly on physical hardware.

FROM python:3.11-slim

LABEL maintainer="RustChain Community"
LABEL description="RustChain Proof-of-Antiquity Miner - One Command Mining"
LABEL version="1.0.0"
LABEL io.rustchain.bounty="dockerized-miner"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    WALLET_NAME="" \
    NODE_URL="https://50.28.86.131"

# Install system dependencies for hardware fingerprinting
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    dmidecode \
    lshw \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 rustchain

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy miner files
COPY miners/ ./miners/

# Copy entrypoint script
COPY docker-miner-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R rustchain:rustchain /app

USER rustchain

# Health check - verify the node is reachable
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD curl -fsk ${NODE_URL}/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "-u", "miners/linux/rustchain_linux_miner.py"]
