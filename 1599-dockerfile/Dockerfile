# RustChain Miner Docker Image
# Multi-stage build for minimal size

# Build stage
FROM rust:1.75 AS builder

WORKDIR /app

# Copy source code
COPY . .

# Build in release mode
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 miner

WORKDIR /app

# Copy binary from builder
COPY --from=builder /app/target/release/rustchain-miner /usr/local/bin/

# Set permissions
RUN chown miner:miner /app

USER miner

# Default command
ENTRYPOINT ["rustchain-miner"]
CMD ["--help"]
