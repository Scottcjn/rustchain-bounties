# RustChain Python Miner Dockerfile
# Multi-arch support: amd64 + arm64
# For Raspberry Pi and modern servers
#
# NOTE: Docker miners earn reduced rewards due to anti-VM detection.
# For full rewards, run the miner directly on physical hardware.

# Build from source for multi-arch support
FROM --platform=$BUILDPLATFORM python:3.11-slim AS builder

ARG TARGETOS
ARG TARGETARCH

# Install build dependencies for multi-platform
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    dmidecode \
    lshw \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy miner files
COPY miners/ ./miners/

# Create non-root user
RUN useradd -m -u 1000 rustchain

# Final stage
FROM python:3.11-slim

LABEL maintainer="RustChain Community"
LABEL description="RustChain Proof-of-Antiquity Miner - Multi-arch (amd64 + arm64)"
LABEL version="1.0.0"
LABEL io.rustchain.bounty="dockerized-miner"
LABEL io.rustchain.multiarch="true"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    WALLET_NAME="" \
    NODE_URL="https://50.28.86.131"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    dmidecode \
    lshw \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 rustchain

WORKDIR /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/miners ./miners
COPY --from=builder /etc/passwd /etc/passwd

# Copy entrypoint script
COPY docker-miner-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R rustchain:rustchain /app

USER rustchain

# Health check - verify the node is reachable
HEALTHCHECK --interval=5m --timeout=30s --start-period=1m --retries=3 \
    CMD curl -fsk ${NODE_URL}/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python3", "-u", "miners/linux/rustchain_linux_miner.py"]
