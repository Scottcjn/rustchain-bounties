# ============================================================
# RustChain Miner Docker Image
# Based on python:3.11-slim — multi-arch (amd64 + arm64)
# ============================================================

FROM python:3.11-slim AS base

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Clone the RustChain repo
RUN git clone --depth=1 https://github.com/Scottcjn/Rustchain.git /tmp/rustchain

# ---- Build stage: find the right miner script ----
FROM base AS builder

COPY --from=base /tmp/rustchain /tmp/rustchain

# Detect platform and copy the appropriate miner
RUN case "$(uname -m)" in \
        x86_64)   MINER_DIR="/tmp/rustchain/miners/linux" ;; \
        aarch64|arm64) MINER_DIR="/tmp/rustchain/miners/linux" ;; \
        armv7l)   MINER_DIR="/tmp/rustchain/miners/linux" ;; \
        ppc64le|ppc64) MINER_DIR="/tmp/rustchain/miners/ppc" ;; \
        *)        MINER_DIR="/tmp/rustchain/miners/linux" ;; \
    esac && \
    echo "Miner directory: $MINER_DIR" && \
    ls "$MINER_DIR"/

# ---- Production stage ----
FROM base AS production

# Copy miner scripts from builder
COPY --from=builder /tmp/rustchain/miners/linux/ /app/miners/
COPY --from=builder /tmp/rustchain/miners/ /app/miners/

# Copy shared Python modules
COPY --from=builder /tmp/rustchain/vintage_miner/ /app/vintage_miner/
COPY --from=builder /tmp/rustchain/miners/color_logs.py /app/miners/

# Copy entrypoint script
COPY docker-miner-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-miner-entrypoint.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash miner && \
    chown -R miner:miner /app
USER miner

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-miner-entrypoint.sh"]
