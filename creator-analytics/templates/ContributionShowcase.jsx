import React from 'react';

function ContributionShowcase() {
    return (
        <div>
            <header>
                <h1>Upstream Contributions Showcase</h1>
                <p>A showcase of our 44+ merged upstream contributions to major open-source projects.</p>
            </header>
            <main>
                <section className="merged-contributions">
                    <h2>Merged Contributions</h2>
                    <ul>
                        <li><a href="https://github.com/openssl/openssl/pull/30437">OpenSSL</a>: PowerPC AES-GCM security fixes (26K stars)</li>
                        <li><a href="https://github.com/libdragon/libdragon/pull/849">libdragon</a>: N64 homebrew SDK macOS build fix</li>
                        <li><a href="https://github.com/capstone-engine/capstone/pull/2889">capstone</a>: Multi-arch disassembly portability fix (8K stars)</li>
                        <li><a href="https://github.com/Blosc/c-blosc2/pull/723">c-blosc2</a>: PowerPC VSX fixes</li>
                        <li><a href="https://github.com/Hazix/hacl-star/pull/1068">hacl-star</a>: AltiVec fix for formal-verified crypto</li>
                        <li><a href="https://github.com/wolfSSL/wolfssl/pull/9932">wolfSSL</a>: POWER8 hardware AES (2K stars)</li>
                        <li><a href="https://github.com/NationalSecurityAgency/ghidra/pull/9036">NSA Ghidra</a>: PowerPC reverse engineering support (53K stars)</li>
                        <li><a href="https://github.com/LLNL/vllm/pull/37586">vLLM</a>: IBM POWER8 CPU backend (30K stars)</li>
                        <li><a href="https://github.com/python/cpython/pull/146118">CPython</a>: BLAKE2 SIMD128 on POWER8 (65K stars)</li>
                        <li><a href="https://github.com/pytorch/pytorch/pull/179619">PyTorch</a>: POWER8 Kineto guard (85K stars)</li>
                        <li><a href="https://github.com/llvm/llvm-project/pull/188558">LLVM</a>: PowerPC fixes (100K+ stars)</li>
                    </ul>
                </section>
                <section className="in-review">
                    <h2>In Review Contributions</h2>
                    <ul>
                        <li>Various contributions under review included above.</li>
                    </ul>
                </section>
            </main>
        </div>
    );
}

export default ContributionShowcase;