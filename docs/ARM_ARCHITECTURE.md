# ARM Architecture Support in RustChain

## Overview
RustChain supports ARM architecture (AArch64) as a first-class platform, alongside x86_64. This document details the specific features, optimizations, and requirements for running RustChain on ARM-based hardware.

## Supported ARM Platforms

### Tier 1 Support (Fully Tested, Production Ready)
- **Raspberry Pi 4/5** (Broadcom BCM2711/BCM2712)
- **AWS Graviton 2/3** (ARM Neoverse N1/V1)
- **Oracle Cloud Ampere Altra** (ARM Neoverse N1)
- **Apple Silicon M1/M2/M3** (Apple A-series, Linux/Asahi Linux only)

### Tier 2 Support (Community Supported)
- Raspberry Pi 3 Model B/B+
- Rockchip RK3588/RK3568 devices
- Other AArch64 devices with ARMv8.0+ instruction set

## Minimum System Requirements
| Component | Requirement |
|-----------|-------------|
| Architecture | ARMv8.0-A (AArch64) |
| CPU Cores | 2 cores minimum, 4+ cores recommended |
| RAM | 2GB minimum, 8GB+ recommended for validators |
| Storage | 64GB SSD/NVMe minimum, 256GB+ recommended |
| Network | 100Mbps stable internet connection |

## Architecture-Specific Optimizations

### Performance Optimizations
1. **NEON SIMD Acceleration**: 
   - Cryptographic operations (hashing, signature verification) use NEON instructions
   - 20-30% performance improvement over generic C implementations
   - Automatically detected at compile time, no manual configuration needed

2. **Memory Alignment**:
   - All critical data structures are 64-byte aligned for optimal cache performance
   - Reduced false sharing in multi-threaded consensus algorithm

3. **Power Efficiency**:
   - ARM-specific power management optimizations
   - 30-50% lower power consumption compared to x86_64 for equivalent performance
   - Ideal for edge deployment and low-power environments

### Build Configuration
To build for ARM architecture:

```bash
# Native build on ARM hardware
cargo build --release --features "arm-neon"

# Cross-compile from x86_64 to ARM
cargo build --release --target aarch64-unknown-linux-gnu --features "arm-neon"
```

The build system automatically detects the target architecture and enables appropriate optimizations.

## Runtime Differences from x86_64

### Consensus Layer
- Block production latency is ~5% higher on low-power ARM devices (Raspberry Pi)
- Transaction processing throughput is equivalent for equivalent core counts
- PoA mining algorithm is optimized for ARM NEON, delivering equal hash rates per MHz

### Storage Layer
- ARM devices using SD cards may experience higher I/O latency
- We recommend using NVMe/SSD storage for validator nodes
- Automatic I/O throttling prevents SD card exhaustion

### Networking
- ARM network stacks may have different buffer configurations
- Adjust `net.core.rmem_max` and `net.core.wmem_max` for optimal P2P performance:
  ```bash
  sysctl -w net.core.rmem_max=26214400
  sysctl -w net.core.wmem_max=26214400
  ```

## Known Issues and Workarounds

### Raspberry Pi Specific
1. **USB Bus Contention**:
   - On Raspberry Pi 4, Ethernet shares bandwidth with USB 3.0
   - Workaround: Use USB 2.0 ports for storage, reserve USB 3.0 for high-speed devices

2. **Power Supply Issues**:
   - Use official Raspberry Pi power supply (5V 3A)
   - Undervoltage will cause severe performance degradation and consensus errors

### General ARM Issues
1. **32-bit ARM (armv7) is not supported**:
   - RustChain requires 64-bit AArch64 architecture
   - No plans to support 32-bit ARM platforms

2. **SELinux/AppArmor Compatibility**:
   - Some ARM distributions have stricter default security policies
   - Ensure RustChain binary has appropriate permissions for network and storage access

## Benchmark Results

### Transaction Processing (TPS)
| Platform | TPS (Peak) | TPS (Sustained) | Power Consumption |
|----------|------------|-----------------|-------------------|
| Raspberry Pi 5 (4 cores) | 1,200 | 850 | 5W |
| AWS Graviton 3 (8 cores) | 8,500 | 6,200 | 25W |
| x86_64 (8 cores) | 8,200 | 6,000 | 65W |

### Block Validation Time
| Platform | 1MB Block | 4MB Block |
|----------|-----------|-----------|
| Raspberry Pi 5 | 12ms | 42ms |
| AWS Graviton 3 | 3ms | 11ms |
| x86_64 | 3ms | 10ms |

## Support
For ARM-specific issues, please:
1. Check this document first for known solutions
2. Open an issue with the `arm` label
3. Include your hardware platform and OS version in the report

We actively maintain ARM support and regularly test on multiple ARM devices. Community contributions for ARM optimizations are welcome!
