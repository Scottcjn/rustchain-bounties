FROM python:3.11-slim AS base

LABEL org.opencontainers.image.source="https://github.com/Scottcjn/rustchain-bounties"
LABEL org.opencontainers.image.description="RustChain Universal Miner — one command to start earning RTC"
LABEL org.opencontainers.image.licenses="MIT"

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /miner

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy miner code
COPY . .

# Environment variables with defaults
ENV WALLET="" \
    NODE_URL="https://50.28.86.131" \
    MINER_THREADS="1" \
    LOG_LEVEL="INFO"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8080/health || exit 1

# Non-root user for security
RUN useradd -m -u 1000 miner && chown -R miner:miner /miner
USER miner

EXPOSE 8080

ENTRYPOINT ["python", "entrypoint.py"]
