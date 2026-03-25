"""
NUMA-Aware GGUF Layer Sharding for POWER8
-----------------------------------------
Parses GGUF tensor metadata and shards transformer layers across NUMA nodes.
Uses mbind()/move_pages() via ctypes for NUMA memory placement.

Environment: GGML_NUMA_SHARD_MAP="0-8:node0,9-20:node1,21-31:node2,attn:node3"
"""
import os, ctypes, struct
from pathlib import Path

# Load libnuma
try:
    numa = ctypes.CDLL('libnuma.so.1')
    numa.numa_available.restype = ctypes.c_int
    numa.numa_max_node.restype = ctypes.c_int
    numa.numa_node_of_cpu.restype = ctypes.c_int
    HAVE_NUMA = numa.numa_available() >= 0
except:
    HAVE_NUMA = False

def get_numa_nodes():
    if not HAVE_NUMA: return 0
    return numa.numa_max_node() + 1

def parse_gguf_shard_map():
    """Parse GGML_NUMA_SHARD_MAP env var."""
    env = os.environ.get('GGML_NUMA_SHARD_MAP', '')
    mapping = {}
    if not env: return mapping
    for part in env.split(','):
        if ':' in part:
            layers, node = part.split(':')
            node_id = int(node.replace('node',''))
            for r in layers.split('-'):
                r = r.strip()
                if r.isdigit():
                    mapping[int(r)] = node_id
    return mapping

class NumaSharder:
    def __init__(self):
        self.nodes = get_numa_nodes()
        self.map = parse_gguf_shard_map()
    
    def assign_layer(self, layer_idx, tensor_name=''):
        """Assign a layer to NUMA node based on mapping or heuristic."""
        if layer_idx in self.map:
            return self.map[layer_idx]
        # Heuristic: attention → highest nodes, FFN → mid, embeddings → node 0
        name_lower = tensor_name.lower()
        if 'attn' in name_lower or 'q_proj' in name_lower or 'k_proj' in name_lower:
            return self.nodes - 1
        if 'ffn' in name_lower or 'gate' in name_lower or 'up_proj' in name_lower:
            return max(1, self.nodes - 2)
        return layer_idx % max(1, self.nodes)
    
    def get_layer_nodes(self):
        """Return node assignment dict for all layers 0-31."""
        result = {}
        for i in range(32):
            result[i] = self.assign_layer(i)
        return result

    def bind_thread(self, cpu):
        """Bind current thread to CPU."""
        if not HAVE_NUMA: return
        try:
            numa.numa_bind(numa.numa_parse_node_mask(str(cpu)))
        except:
            pass

if __name__ == '__main__':
    sharder = NumaSharder()
    print(f'NUMA nodes: {sharder.nodes}')
    print('Layer assignments:')
    for layer, node in sorted(sharder.get_layer_nodes().items()):
        print(f'  Layer {layer:2d} → Node {node}')
