# RustChain Bounty Client - Reproducible Container
#
# This Dockerfile ensures reproducible builds for bounty tooling.
# All versions are pinned to prevent supply-chain attacks.

FROM python:3.11-slim-bookworm@sha256:6d1e8b2c9d1f8e5e2f4c3b8a9d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_INPUT=1

# Pin all Python dependencies to specific versions
# These pins ensure deterministic builds
RUN pip install --no-cache-dir \
    pytest==8.0.0 \
    pyyaml==6.0.1 \
    requests==2.31.0 \
    gh==2.39.0 \
   GitPython==3.1.42 \
    cryptography==42.0.5

# Pin git version
RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.43.0-1+deb12u1 \
    curl=7.88.1-10+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only dependency files first for better caching
COPY requirements.txt ./

# Copy source code
COPY . .

# Create non-root user for security
RUN useradd -m -s /bin/bash bountyuser && \
    chown -R bountyuser:bountyuser /app
USER bountyuser

# Default command runs tests
CMD ["pytest", "-v"]
