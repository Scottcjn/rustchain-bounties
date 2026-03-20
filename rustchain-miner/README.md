# RustChain Miner

## Overview
The RustChain miner is a tool for participating in the RustChain network by contributing computational resources to validate transactions and secure the network.

## Installation

### Prerequisites
- Rust and Cargo installed
- Git

### Clone and Build
```bash
git clone <repository_url>
cd rustchain-miner
cargo build --release
```

## Usage

### Dry Run Mode
To test the miner without actually participating in the network:

```bash
./target/release/rustchain-miner --dry-run
```

### Configuration
Create a configuration file `config.toml`:
```toml[network]
node_address = "node.rustchain.com:30333"

[miner]
threads = 4
wallet_address = "your_wallet_address_here"
```

## Testing

### Unit Tests
```bash
cargo test
```

### Integration Tests
```bash
cargo test --test integration
```

## Contributing
See the main repository's CONTRIBUTING.md file.

## License
See the main repository's LICENSE file.