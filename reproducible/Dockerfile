# RustChain Bounty Tools - Reproducible Container
# This Dockerfile pins all dependencies for deterministic builds

FROM python:3.11-slim-bookworm@sha256:04cd27899595a99dfe77709d96f08876bf2ee99139ee2f0fe9ac948005034e5b

LABEL maintainer="RustChain Community"
LABEL description="Reproducible environment for RustChain bounty tooling"

# Pin all environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install pinned dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Pin apt packages
    curl=7.88.1-10+deb12u14 \
    git=1:2.39.5-0+deb12u3 \
    sqlite3=3.40.1-2+deb12u2 \
    && rm -rf /var/lib/apt/lists/*

# Install pinned Python packages
RUN pip install --no-cache-dir \
    pytest==8.0.0 \
    pyyaml==6.0.1 \
    requests==2.31.0 \
    httpx==0.26.0

# Create working directory
WORKDIR /app

# Copy only necessary files for testing
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Default command runs tests
CMD ["pytest", "tests/", "-v", "--tb=short"]
