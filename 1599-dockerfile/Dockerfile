# RustChain Miner Docker Image
# Multi-stage build for minimal size

FROM rust:1.75 AS builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 miner
WORKDIR /app
COPY --from=builder /app/target/release/rustchain-miner /usr/local/bin/
RUN chown miner:miner /app
USER miner
ENTRYPOINT ["rustchain-miner"]
CMD ["--help"]
