#ifndef GGML_NUMA_SHARD_H
#define GGML_NUMA_SHARD_H

#include <stddef.h>

#ifdef __powerpc__
#include <numaif.h>
#include <numa.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

/* NUMA-Aware layer routing for POWER8. Distributes flat tensors across 4 NUMA nodes. */
static inline void ggml_numa_shard_tensor(void *ptr, size_t size, int layer_idx, const char* name) {
    if (!ptr || size == 0) return;

    unsigned long nodemask = 0;
    
    // Parse mapping from ENV or fallback to optimal logic based on benchmarks
    // Node 2/3 are fastest, Node 0 slowest. 
    // Early layers -> Node 1, FFN -> Node 2, Attention -> Node 3
    if (strstr(name, "attn") != NULL) {
        nodemask = (1UL << 3); // Node 3
    } else if (layer_idx >= 0 && layer_idx <= 8) {
        nodemask = (1UL << 1); // Node 1
    } else if (layer_idx >= 9 && layer_idx <= 20) {
        nodemask = (1UL << 2); // Node 2
    } else {
        nodemask = (1UL << 0); // Node 0
    }

    // Pin memory to the target node
    if (mbind(ptr, size, MPOL_BIND, &nodemask, 4 + 1, 0) != 0) {
        perror("ggml_numa_shard_tensor: mbind failed");
    }
}
#else
/* Fallback for x86 and other architectures */
static inline void ggml_numa_shard_tensor(void *ptr, size_t size, int layer_idx, const char* name) {
    // No-op for non-POWER8 configs.
    (void)ptr; (void)size; (void)layer_idx; (void)name;
}
#endif // __powerpc__

#endif // GGML_NUMA_SHARD_H
