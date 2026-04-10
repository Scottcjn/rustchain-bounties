/**
 * RustChain MCP Server
 *
 * Exposes RustChain network tools via the Model Context Protocol so any
 * MCP-compatible IDE (Claude Code, Cursor, Windsurf, VS Code Copilot …)
 * can query the chain directly from the terminal.
 *
 * Tools
 * -----
 * rustchain_health            — node health with automatic failover
 * rustchain_balance            — RTC balance for a wallet / miner_id
 * rustchain_miners             — list active miners and architectures
 * rustchain_epoch              — current epoch info (slot, height, rewards)
 * rustchain_create_wallet      — register a new agent wallet on the network
 * rustchain_submit_attestation — submit a hardware fingerprint for a miner
 * rustchain_bounties           — list open RustChain bounties from this repo
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import { RustChainClient } from "./client.js";
// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function pretty(data) {
    return JSON.stringify(data, null, 2);
}
function toolResult(content) {
    return { content: [{ type: "text", text: content }] };
}
function errorResult(message) {
    return { content: [{ type: "text", text: `Error: ${message}` }] };
}
// ---------------------------------------------------------------------------
// Server
// ---------------------------------------------------------------------------
const RUSTCHAIN_BOUNTIES_URL = "https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/BOUNTY_LEDGER.md";
async function fetchBounties() {
    try {
        const res = await fetch(RUSTCHAIN_BOUNTIES_URL, { signal: AbortSignal.timeout(10_000) });
        if (!res.ok)
            return `Could not fetch bounty ledger (HTTP ${res.status})`;
        const text = await res.text();
        // Parse markdown table: | # | Title | Reward | Status |
        const lines = text.split("\n");
        const rows = ["## Open RustChain Bounties", ""];
        rows.push("| # | Title | Reward | Labels |");
        rows.push("|---|-------|--------|--------|");
        for (const line of lines) {
            if (!line.startsWith("|") || line.startsWith("|--"))
                continue;
            const cols = line.split("|").map((c) => c.trim()).filter(Boolean);
            if (cols.length < 3)
                continue;
            // Simple heuristic: open bounties have "open" in the line
            if (line.toLowerCase().includes("**open**") || line.toLowerCase().includes("open")) {
                const num = cols[0]?.replace("#", "").trim();
                const title = cols[1]?.replace(/\*\*/g, "").trim();
                const reward = cols[2]?.replace(/\*\*/g, "").trim();
                const labels = cols.slice(3).join(", ").replace(/\*\*/g, "");
                rows.push(`| ${num} | ${title} | ${reward} | ${labels} |`);
            }
        }
        return rows.join("\n");
    }
    catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return `Failed to fetch bounties: ${msg}`;
    }
}
// ---------------------------------------------------------------------------
// Tool handler
// ---------------------------------------------------------------------------
async function handleToolCall(name, args) {
    const client = RustChainClient.fromEnv();
    try {
        switch (name) {
            case "rustchain_health": {
                const data = await client.health();
                return toolResult(pretty(data));
            }
            case "rustchain_balance": {
                const walletId = String(args.wallet_id ?? args.miner_id ?? "");
                if (!walletId) {
                    return errorResult("wallet_id (or miner_id) is required");
                }
                const data = await client.balance(walletId);
                return toolResult(pretty(data));
            }
            case "rustchain_miners": {
                const data = await client.miners();
                return toolResult(pretty(data));
            }
            case "rustchain_epoch": {
                const data = await client.epoch();
                return toolResult(pretty(data));
            }
            case "rustchain_create_wallet": {
                const walletName = String(args.wallet_name ?? "");
                if (!walletName) {
                    return errorResult("wallet_name is required");
                }
                const data = await client.createWallet(walletName);
                return toolResult(pretty(data));
            }
            case "rustchain_submit_attestation": {
                const walletId = String(args.wallet_id ?? "");
                const hardwareFingerprint = String(args.hardware_fingerprint ?? "");
                if (!walletId || !hardwareFingerprint) {
                    return errorResult("wallet_id and hardware_fingerprint are required");
                }
                const data = await client.submitAttestation(walletId, hardwareFingerprint);
                return toolResult(pretty(data));
            }
            case "rustchain_bounties": {
                const data = await fetchBounties();
                return toolResult(data);
            }
            default:
                return errorResult(`Unknown tool: ${name}`);
        }
    }
    catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        return errorResult(msg);
    }
}
// ---------------------------------------------------------------------------
// Bootstrap
// ---------------------------------------------------------------------------
const server = new Server({
    name: "rustchain-mcp",
    version: "1.0.0",
}, {
    capabilities: {
        tools: {},
    },
});
// Register tool-list handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "rustchain_health",
                description: "Check RustChain node health across all known nodes with automatic failover. " +
                    "Returns status, peer count, block height, and timestamp.",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
            {
                name: "rustchain_balance",
                description: "Query the RTC balance for a wallet or miner ID on the RustChain network. " +
                    "Requires a wallet_id (or miner_id) string argument.",
                inputSchema: {
                    type: "object",
                    properties: {
                        wallet_id: {
                            type: "string",
                            description: "Wallet name or miner ID to query",
                        },
                    },
                    required: ["wallet_id"],
                },
            },
            {
                name: "rustchain_miners",
                description: "List all active miners currently participating in the RustChain network, " +
                    "including their addresses, architectures, and status.",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
            {
                name: "rustchain_epoch",
                description: "Get the current epoch information including epoch number, slot, block height, " +
                    "accumulated rewards, and number of miners online.",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
            {
                name: "rustchain_create_wallet",
                description: "Register a new wallet on the RustChain network. " +
                    "Returns the assigned wallet_id and address. " +
                    "Requires a wallet_name string argument.",
                inputSchema: {
                    type: "object",
                    properties: {
                        wallet_name: {
                            type: "string",
                            description: "Desired name for the new wallet",
                        },
                    },
                    required: ["wallet_name"],
                },
            },
            {
                name: "rustchain_submit_attestation",
                description: "Submit a hardware fingerprint attestation for a miner to join the RustChain network. " +
                    "Requires wallet_id and hardware_fingerprint string arguments.",
                inputSchema: {
                    type: "object",
                    properties: {
                        wallet_id: {
                            type: "string",
                            description: "Wallet ID of the miner",
                        },
                        hardware_fingerprint: {
                            type: "string",
                            description: "Hardware fingerprint / measurement string",
                        },
                    },
                    required: ["wallet_id", "hardware_fingerprint"],
                },
            },
            {
                name: "rustchain_bounties",
                description: "List all open RustChain bounties from the official bounty ledger, " +
                    "including issue numbers, titles, rewards, and labels.",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
        ],
    };
});
// Register tool-call handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args = {} } = request.params;
    return await handleToolCall(name, args);
});
export { server };
//# sourceMappingURL=server.js.map