...

### Fallback Behavior

#### 1. Single-NUMA-Node Systems
On systems with only a single NUMA node (node 0), ram-coffers automatically routes all memory operations to the default node. The NUMA-aware allocation falls back to standard `malloc` behavior when no additional nodes are detected (see `ggml-coffer-mmap.h:42-45`). Memory operations use scalar paths instead of vectorized instructions.

#### 2. Non-POWER8 Architectures
The following POWER8-specific components are conditionally compiled:
- `mftb` timebase instructions (disabled via `#ifndef __powerpc64__` at `ggml-ram-coffers.h:27`)
- `dcbt` cache prefetching (guarded by `#ifdef POWER8` at `ggml-neuromorphic-coffers.h:112`)
- `vec_perm` vector permutations (replaced with scalar loops when `__POWER8_VECTOR__` is undefined - see `ggml-ram-coffers.h:89`)

On x86_64/aarch64, these fall back to:
- Standard C timers (`clock_gettime`)
- Software-based cache management
- Scalar memory operations

#### 3. Build Compatibility Matrix
| Architecture       | NUMA Nodes | Supported | Fallback Behavior               |
|--------------------|------------|-----------|---------------------------------|
| POWER8 (multi-node)| 2+         | ✅ Full   | Native vector instructions      |
| POWER8 (single)    | 1          | ✅ Full   | Scalar paths + node 0 routing   |
| x86_64             | Any        | ✅ Partial| Timer/cache fallbacks + scalar  |
| aarch64            | Any        | ✅ Partial| Same as x86_64                  |

...
