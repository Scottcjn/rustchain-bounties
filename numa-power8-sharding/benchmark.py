"""
NUMA Sharding Benchmark Harness
Compares flat vs NUMA-sharded throughput for pp512 and tg128.
Supports: 7B, 33B GGUF models.
"""
import subprocess, time, json

MODELS = {'7B': 'llama-7b.gguf', '33B': 'llama-33b.gguf'}

def run_benchmark(model_size, mode='flat'):
    """Run llama.cpp inference benchmark."""
    print(f'Running {model_size} {mode} benchmark...')
    # Placeholder: in real run this calls llama-bench or custom harness
    return {'tps': 50.0, 'mode': mode, 'model': model_size}

def compare():
    results = {}
    for size in ['7B', '33B']:
        flat = run_benchmark(size, 'flat')
        numa = run_benchmark(size, 'numa-sharded')
        results[size] = {'flat': flat, 'numa': numa, 'speedup': round(numa['tps']/flat['tps'], 2)}
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    compare()
