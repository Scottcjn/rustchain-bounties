import React from 'react';

const ContributionPage = () => {
    return (
        <>
            <header>
                <h1>Upstream Contributions Showcase</h1>
                <p>A showcase of our 44+ merged upstream contributions to major open-source projects.</p>
            </header>
            <main>
                <section className="contributions">
                    <h2>Merged Contributions</h2>
                    <div className="contribution-card">
                        <h3>OpenSSL</h3>
                        <p>Stars: 26K</p>
                        <p>PRs: <a href="https://github.com/openssl/openssl/pull/30437">#30437</a>, <a href="https://github.com/openssl/openssl/pull/30452">#30452</a></p>
                        <p>Impact: PowerPC AES-GCM security fixes, merged to master + 5 release branches</p>
                    </div>
                    <div className="contribution-card">
                        <h3>libdragon</h3>
                        <p>Stars: —</p>
                        <p>PR: <a href="https://github.com/libdragon/libdragon/pull/849">#849</a></p>
                        <p>Impact: N64 homebrew SDK macOS build fix</p>
                    </div>
                    <div className="contribution-card">
                        <h3>capstone</h3>
                        <p>Stars: 8K</p>
                        <p>PR: <a href="https://github.com/capstone-engine/capstone/pull/2889">#2889</a></p>
                        <p>Impact: Multi-arch disassembly portability fix</p>
                    </div>
                    {/* Additional contributions can follow the same structure */}
                </section>
                <section className="in-review">
                    <h2>In Review Contributions</h2>
                    <div className="in-review-card">
                        <h3>wolfSSL</h3>
                        <p>Stars: 2K</p>
                        <p>PR: <a href="https://github.com/wolfSSL/wolfssl/pull/9932">#9932</a></p>
                        <p>Impact: POWER8 hardware AES (in review)</p>
                    </div>
                    <div className="in-review-card">
                        <h3>NSA Ghidra</h3>
                        <p>Stars: 53K</p>
                        <p>PR: <a href="https://github.com/NationalSecurityAgency/ghidra/pull/9036">#9036</a></p>
                        <p>Impact: PowerPC reverse engineering support (in review)</p>
                    </div>
                    {/* Additional in-review contributions can follow the same structure */}
                </section>
            </main>
            <footer>
                <p>For contributions, see our <a href="/CONTRIBUTING.md">Contributing Guidelines</a></p>
            </footer>
        </>
    );
};

export default ContributionPage;