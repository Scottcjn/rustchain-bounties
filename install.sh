#!/bin/bash

# Exit on error
set -e

# Check for supported platforms
if [[ "$(uname)" == "Darwin" ]]; then
  # macOS (both Intel and Apple Silicon)
  OS="macOS"
  SED_INLINE="-i ''"
  READLINK="greadlink"
  if! command -v greadlink &> /dev/null; then
    echo "Error: greadlink not found. Please install coreutils."
    exit 1
  fi
elif [[ "$(expr substr $(uname -s) 1 5)" == "Linux" ]]; then
  # Linux
  OS="Linux"
  SED_INLINE="-i"
  READLINK="readlink"
else
  echo "Unsupported platform: $(uname)"
  exit 1
fi

# Function to get the absolute path
get_absolute_path() {
  echo "$(cd "$(dirname "$1")"; pwd)/$(basename "$1")"
}

# Set the correct paths
SCRIPT_DIR=$(dirname "$(get_absolute_path "$0")")
RUSTCHAIN_HOME="$HOME/.rustchain"

# Create Rustchain home directory if it doesn't exist
mkdir -p "$RUSTCHAIN_HOME"

# Download and install Rustchain
echo "Downloading Rustchain..."
curl -L https://rustchain.org/releases/latest/rustchain.tar.gz | tar -xz -C "$RUSTCHAIN_HOME"

# Add Rustchain to PATH
echo 'export PATH="$PATH:$HOME/.rustchain/bin"' >> "$HOME/.bashrc"
echo 'export PATH="$PATH:$HOME/.rustchain/bin"' >> "$HOME/.zshrc"

# Source the shell configuration
if [ -f "$HOME/.bashrc" ]; then
  source "$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc"
else
  echo "Failed to source shell configuration. Please add Rustchain to your PATH manually."
  exit 1
fi

# Verify installation
if command -v rustchain &> /dev/null; then
  echo "Rustchain installed successfully!"
else
  echo "Failed to install Rustchain. Please check the installation steps."
  exit 1
fi
