#!/bin/bash
# RustChain Miner Build Script
# Builds for all supported platforms including cross-compilation targets

set -e

echo "🦀 RustChain Miner Build Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Rust is installed
if ! command -v cargo &> /dev/null; then
    echo -e "${RED}Error: Rust/Cargo not found${NC}"
    echo "Please install Rust from https://rustup.rs"
    exit 1
fi

echo -e "${GREEN}✓${NC} Rust installed: $(rustc --version)"

# Clean previous builds
echo -e "\n${YELLOW}Cleaning previous builds...${NC}"
cargo clean

# Build for native platform
echo -e "\n${YELLOW}Building for native platform...${NC}"
cargo build --release
echo -e "${GREEN}✓${NC} Native build complete: target/release/rustchain-miner"

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
cargo test --release
echo -e "${GREEN}✓${NC} Tests passed"

# Run Clippy
echo -e "\n${YELLOW}Running Clippy...${NC}"
cargo clippy -- -D warnings
echo -e "${GREEN}✓${NC} Clippy checks passed"

# Cross-compilation targets (optional)
if [[ "$1" == "--cross" ]]; then
    echo -e "\n${YELLOW}Building cross-compilation targets...${NC}"
    
    # ARM64 Linux
    echo -e "\n  Building for aarch64-unknown-linux-gnu..."
    rustup target add aarch64-unknown-linux-gnu 2>/dev/null || true
    cargo build --release --target aarch64-unknown-linux-gnu && \
        echo -e "  ${GREEN}✓${NC} ARM64 Linux build complete" || \
        echo -e "  ${RED}✗${NC} ARM64 Linux build failed (missing toolchain)"
    
    # PowerPC64 Linux (bonus target for +10 RTC)
    echo -e "\n  Building for powerpc64-unknown-linux-gnu..."
    rustup target add powerpc64-unknown-linux-gnu 2>/dev/null || true
    cargo build --release --target powerpc64-unknown-linux-gnu && \
        echo -e "  ${GREEN}✓${NC} PowerPC64 build complete (+10 RTC bonus!)" || \
        echo -e "  ${RED}✗${NC} PowerPC64 build failed (missing toolchain)"
    
    # macOS ARM64
    echo -e "\n  Building for aarch64-apple-darwin..."
    rustup target add aarch64-apple-darwin 2>/dev/null || true
    cargo build --release --target aarch64-apple-darwin && \
        echo -e "  ${GREEN}✓${NC} macOS ARM64 build complete" || \
        echo -e "  ${RED}✗${NC} macOS ARM64 build failed (missing toolchain)"
fi

echo -e "\n${GREEN}================================${NC}"
echo -e "${GREEN}Build complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "Binaries:"
echo "  - target/release/rustchain-miner (native)"
if [[ "$1" == "--cross" ]]; then
    echo "  - target/aarch64-unknown-linux-gnu/release/rustchain-miner (ARM64 Linux)"
    echo "  - target/powerpc64-unknown-linux-gnu/release/rustchain-miner (PowerPC64)"
    echo "  - target/aarch64-apple-darwin/release/rustchain-miner (macOS ARM64)"
fi
echo ""
echo "Run with:"
echo "  ./target/release/rustchain-miner"
echo ""
