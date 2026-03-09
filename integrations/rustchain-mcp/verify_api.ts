/**
 * verify_api.ts — Quick sanity-check against live RustChain nodes.
 *
 * Usage:  bun run verify_api.ts
 *
 * Checks that every public endpoint used by the MCP server returns an
 * expected HTTP 200 from at least one of the configured nodes.
 */

import axios from "axios";

const NODES = [
    "https://50.28.86.131",
    "https://50.28.86.153",
    "http://76.8.228.245:8099",
];

const client = axios.create({
    timeout: 6000,
    validateStatus: () => true,
    httpsAgent: new (require("https").Agent)({ rejectUnauthorized: false }),
});

type Result = { endpoint: string; node: string; status: number | string };

async function probe(path: string): Promise<Result> {
    for (const node of NODES) {
        try {
            const res = await client.get(`${node}${path}`);
            if (res.status === 200) return { endpoint: path, node, status: 200 };
        } catch {
            /* try next */
        }
    }
    return { endpoint: path, node: "none", status: "UNREACHABLE" };
}

async function probeGitHub(): Promise<Result> {
    try {
        const res = await axios.get(
            "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?labels=bounty&state=open&per_page=1",
            { headers: { Accept: "application/vnd.github+json", "User-Agent": "rustchain-mcp" } }
        );
        return { endpoint: "github /issues (bounty)", node: "github", status: res.status };
    } catch (e: any) {
        return { endpoint: "github /issues (bounty)", node: "github", status: e.message };
    }
}

async function main() {
    console.log("RustChain MCP — API Verification\n");

    const checks = await Promise.all([
        probe("/health"),
        probe("/epoch"),
        probe("/api/miners"),
        probe("/wallet/balance?miner_id=antigravity-gdm"),
        probe("/explorer"),
        probeGitHub(),
    ]);

    let pass = 0;
    let fail = 0;
    for (const r of checks) {
        const ok = r.status === 200;
        console.log(`  ${ok ? "✓" : "✗"} ${r.endpoint.padEnd(45)} ${r.node}  HTTP ${r.status}`);
        ok ? pass++ : fail++;
    }

    console.log(`\n  ${pass} passed, ${fail} failed`);
    if (fail > 0) process.exit(1);
}

main();
