#!/bin/bash
#
# RustChain Miner for Cray-1
# Build Script
#
# This script builds the RustChain miner for Cray-1 supercomputer
# using the Cray Fortran Translator (CFT) and Cray Assembly (CAL).
#
# Usage: ./build.sh
#
# Prerequisites:
#   - Cray Fortran Translator (CFT)
#   - Cray Assembly Language (CAL) assembler
#   - COS (Cray Operating System) or compatible environment
#

set -e

echo "========================================"
echo "RustChain Miner for Cray-1"
echo "Build Script v0.1.0"
echo "========================================"
echo

# Configuration
CFT_OPTS="-C -O"
CAL_OPTS="-O"
LD_OPTS="-lcos -lmath"

SRC_DIR="src"
OBJ_DIR="obj"
BIN_DIR="bin"

# Create output directories
mkdir -p "$OBJ_DIR"
mkdir -p "$BIN_DIR"

echo "[BUILD] Cleaning previous build..."
rm -f "$OBJ_DIR"/*.o "$BIN_DIR"/*

echo
echo "[BUILD] Compiling Fortran sources..."

# Compile Fortran sources
echo "  - miner_main.f"
cft $CFT_OPTS -o "$OBJ_DIR/miner_main.o" "$SRC_DIR/miner_main.f"

echo "  - mining.f"
cft $CFT_OPTS -o "$OBJ_DIR/mining.o" "$SRC_DIR/mining.f"

echo "  - network.f"
cft $CFT_OPTS -o "$OBJ_DIR/network.o" "$SRC_DIR/network.f"

echo "  - utils.f"
cft $CFT_OPTS -o "$OBJ_DIR/utils.o" "$SRC_DIR/utils.f"

echo
echo "[BUILD] Assembling Cray sources..."

# Assemble Cray assembly sources
echo "  - hw_cray.s"
cal $CAL_OPTS -o "$OBJ_DIR/hw_cray.o" "$SRC_DIR/hw_cray.s"

echo "  - attest.s"
cal $CAL_OPTS -o "$OBJ_DIR/attest.o" "$SRC_DIR/attest.s"

echo "  - vector_ops.s"
cal $CAL_OPTS -o "$OBJ_DIR/vector_ops.o" "$SRC_DIR/vector_ops.s"

echo "  - pit_cray.s"
cal $CAL_OPTS -o "$OBJ_DIR/pit_cray.o" "$SRC_DIR/pit_cray.s"

echo
echo "[BUILD] Linking..."

# Link all object files
ld $LD_OPTS -o "$BIN_DIR/miner.com" \
    "$OBJ_DIR/miner_main.o" \
    "$OBJ_DIR/mining.o" \
    "$OBJ_DIR/network.o" \
    "$OBJ_DIR/utils.o" \
    "$OBJ_DIR/hw_cray.o" \
    "$OBJ_DIR/attest.o" \
    "$OBJ_DIR/vector_ops.o" \
    "$OBJ_DIR/pit_cray.o"

echo
echo "[BUILD] Creating load module..."

# Create loadable module
mkload -n RUSTCHAIN_MINER "$BIN_DIR/miner.com"

echo
echo "========================================"
echo "Build complete!"
echo "========================================"
echo
echo "Output: $BIN_DIR/miner.com"
echo "Load module: $BIN_DIR/RUSTCHAIN_MINER"
echo
echo "To run:"
echo "  LOAD RUSTCHAIN_MINER"
echo "  RUSTCHAIN_MINER -w RTC4325af95d26d59c3ef025963656d22af638bb96b"
echo
