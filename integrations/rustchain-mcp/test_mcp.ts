/**
 * test_mcp.ts — Smoke-tests the MCP server's tool dispatch.
 *
 * Usage:  bun run test_mcp.ts
 *
 * Spawns the MCP server as a subprocess, sends a JSON-RPC
 * initialize + tools/call sequence over stdin/stdout, and
 * asserts that each tool returns a non-error content block.
 */

import { spawn } from "child_process";
import * as path from "path";

const SERVER = path.join(import.meta.dir, "index.ts");
const TIMEOUT_MS = 15_000;

// ---------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------

function send(proc: ReturnType<typeof spawn>, msg: object) {
    const body = JSON.stringify(msg);
    proc.stdin!.write(`Content-Length: ${Buffer.byteLength(body)}\r\n\r\n${body}`);
}

function assertOk(label: string, result: any) {
    if (result?.isError) throw new Error(`${label} returned isError`);
    const text: string = result?.content?.[0]?.text ?? "";
    if (text.startsWith("Error:")) throw new Error(`${label} => ${text}`);
    console.log(`  ✓ ${label}`);
}

// ---------------------------------------------------------------------------
// main
// ---------------------------------------------------------------------------

async function main() {
    console.log("RustChain MCP — Tool Smoke Tests\n");

    const proc = spawn("bun", ["run", SERVER], {
        stdio: ["pipe", "pipe", "inherit"],
    });

    let buffer = "";
    const results: Record<number, any> = {};
    const pending: Record<number, (v: any) => void> = {};

    proc.stdout!.on("data", (chunk: Buffer) => {
        buffer += chunk.toString();
        while (true) {
            const sep = buffer.indexOf("\r\n\r\n");
            if (sep === -1) break;
            const header = buffer.slice(0, sep);
            const lenMatch = header.match(/Content-Length:\s*(\d+)/i);
            if (!lenMatch) { buffer = buffer.slice(sep + 4); continue; }
            const len = parseInt(lenMatch[1], 10);
            const bodyStart = sep + 4;
            if (buffer.length < bodyStart + len) break;
            const body = buffer.slice(bodyStart, bodyStart + len);
            buffer = buffer.slice(bodyStart + len);
            try {
                const msg = JSON.parse(body);
                if (msg.id !== undefined && pending[msg.id]) {
                    pending[msg.id](msg.result ?? msg.error);
                    delete pending[msg.id];
                }
            } catch { /* ignore parse errors */ }
        }
    });

    function rpc(id: number, method: string, params: object): Promise<any> {
        return new Promise((resolve, reject) => {
            pending[id] = resolve;
            send(proc, { jsonrpc: "2.0", id, method, params });
            setTimeout(() => {
                if (pending[id]) { delete pending[id]; reject(new Error(`timeout id=${id}`)); }
            }, TIMEOUT_MS);
        });
    }

    try {
        // 1. Initialize
        await rpc(1, "initialize", {
            protocolVersion: "2024-11-05",
            capabilities: {},
            clientInfo: { name: "test", version: "0.0.1" },
        });

        // 2. Test each tool
        const tests: Array<[number, string, object]> = [
            [2, "rustchain_health", {}],
            [3, "rustchain_epoch", {}],
            [4, "rustchain_miners", {}],
            [5, "rustchain_balance", { miner_id: "antigravity-gdm" }],
            [6, "rustchain_ledger", { limit: 5 }],
            [7, "rustchain_bounties", {}],
        ];

        for (const [id, tool, args] of tests) {
            const result = await rpc(id, "tools/call", { name: tool, arguments: args });
            assertOk(tool, result);
        }

        console.log("\n  All tools passed.");
    } catch (err: any) {
        console.error("\n  FAIL:", err.message);
        process.exitCode = 1;
    } finally {
        proc.stdin!.end();
        proc.kill();
    }
}

main();
