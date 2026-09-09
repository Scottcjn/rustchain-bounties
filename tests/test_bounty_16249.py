import re

def test_fallback_documentation():
    with open("README.md", "r") as f:
        content = f.read()
    
    # Verify single-NUMA documentation exists with code reference
    assert re.search(r"single-NUMA.*node 0.*ggml-coffer-mmap.h:\s*42-45", content, re.DOTALL)
    
    # Verify POWER8-specific components are documented
    power_components = [
        r"mftb.*__powerpc64__",
        r"dcbt.*POWER8.*ggml-neuromorphic-coffers.h:\s*112",
        r"vec_perm.*__POWER8_VECTOR__.*ggml-ram-coffers.h:\s*89"
    ]
    for component in power_components:
        assert re.search(component, content, re.DOTALL)
    
    # Verify build matrix contains all required architectures
    matrix_archs = ["POWER8 \(multi-node\)", "POWER8 \(single\)", "x86_64", "aarch64"]
    for arch in matrix_archs:
        assert re.search(re.escape(arch), content)
