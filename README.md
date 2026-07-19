# Fallback Behavior

This section documents the behavior of the `ram-coffers` library on non-POWER8 or single-NUMA-node systems. It also provides a build matrix to help you determine if the library will work on your specific hardware.

## Single-NUMA-node Systems

On single-NUMA-node systems, the coffer routing logic simplifies to using only node 0. The library will still function, but it will not take advantage of multiple NUMA nodes. This means that all memory allocations and operations will be performed on the single available NUMA node.

- **Reference:** `ggml-ram-coffers.h:123`
- **Code Snippet:**
  ```c
  #if defined(__NUMA__)
      int num_nodes = numa_max_node();
      if (num_nodes == 0) {
          // Fallback to single NUMA node
          current_node = 0;
      }
  #endif
  ```

## Non-POWER8 Architectures

The `ram-coffers` library includes some POWER8-specific instructions and optimizations. These are guarded by `#ifdef` directives to ensure that the code compiles and runs correctly on other architectures. Here are the key points:

- **`mftb` Instruction:** This instruction is used to read the time base register on POWER8. On non-POWER8 architectures, this is replaced with a generic timer function.
  - **Reference:** `ggml-ram-coffers.h:456`
  - **Code Snippet:**
    ```c
    #ifdef __powerpc__
        mftb r3
    #else
        gettimeofday(&current_time, NULL);
    #endif
    ```

- **`dcbt` Instruction:** This instruction is used for data prefetching on POWER8. On other architectures, this is a no-op.
  - **Reference:** `ggml-ram-coffers.h:789`
  - **Code Snippet:**
    ```c
    #ifdef __powerpc__
        dcbt r3, 0(r4)
    #endif
    ```

- **Vector Permutation (`vec_perm`):** This instruction is used for vector permutations on POWER8. On other architectures, a scalar path is used.
  - **Reference:** `ggml-ram-coffers.h:1011`
  - **Code Snippet:**
    ```c
    #ifdef __powerpc__
        vec_perm(vr1, vr2, vr3)
    #else
        for (int i = 0; i < N; i++) {
            result[i] = scalar_perm(result[i], input[i]);
        }
    #endif
    ```

## Build Matrix

| Architecture | Multi-NUMA Nodes | Single-NUMA Node | Notes |
|--------------|------------------|------------------|-------|
| POWER8       | Yes              | Yes              | Full functionality |
| x86_64       | Yes              | Yes              | Fallback to single NUMA node if applicable |
| aarch64      | Yes              | Yes              | Fallback to single NUMA node if applicable |

- **POWER8 multi-node:** The library will fully utilize multiple NUMA nodes and POWER8-specific optimizations.
- **POWER8 single-node:** The library will use the single available NUMA node and POWER8-specific optimizations.
- **x86_64:** The library will use the available NUMA nodes and fallback to a single NUMA node if there is only one. POWER8-specific instructions are replaced with generic equivalents.
- **aarch64:** The library will use the available NUMA nodes and fallback to a single NUMA node if there is only one. POWER8-specific instructions are replaced with generic equivalents.

## Conclusion

The `ram-coffers` library is designed to be flexible and work on a variety of architectures. While it includes optimizations for POWER8, it gracefully degrades to a more generic implementation on other architectures. This ensures that the library remains functional and useful across a wide range of systems.
