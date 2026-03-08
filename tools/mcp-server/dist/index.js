import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";
import { z } from "zod";
import https from "https";
const API_NODES = [
    "https://50.28.86.131",
    // Add other nodes if known
];
const httpsAgent = new https.Agent({
    rejectUnauthorized: false,
});
class RustChainClient {
    async request(path, params = {}) {
        for (const node of API_NODES) {
            try {
                const response = await axios.get(`${node}${path}`, {
                    params,
                    timeout: 5000,
                    validateStatus: () => true,
                    httpsAgent: httpsAgent,
                });
                if (response.status === 200)
                    return response.data;
            }
            catch (error) {
                console.error(`Node ${node} failed:`, error);
            }
        }
        throw new Error("All RustChain nodes failed");
    }
    async getHealth() { return this.request("/health"); }
    async getMiners() { return this.request("/api/miners"); }
    async getEpoch() { return this.request("/epoch"); }
    async getBalance(minerId) {
        return this.request("/wallet/balance", { miner_id: minerId });
    }
}
const client = new RustChainClient();
const server = new Server({ name: "rustchain-mcp", version: "1.0.0" }, { capabilities: { tools: {} } });
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        {
            name: "rustchain_health",
            description: "Check RustChain node health",
            inputSchema: { type: "object", properties: {} },
        },
        {
            name: "rustchain_miners",
            description: "List active RustChain miners",
            inputSchema: { type: "object", properties: {} },
        },
        {
            name: "rustchain_epoch",
            description: "Get current RustChain epoch info",
            inputSchema: { type: "object", properties: {} },
        },
        {
            name: "rustchain_balance",
            description: "Check RTC balance for a wallet",
            inputSchema: {
                type: "object",
                properties: {
                    miner_id: { type: "string", description: "The wallet ID/miner name" },
                },
                required: ["miner_id"],
            },
        },
        {
            name: "rustchain_transfer",
            description: "Send RTC to another wallet (Requires wallet key)",
            inputSchema: {
                type: "object",
                properties: {
                    miner_id: { type: "string", description: "Sender wallet ID" },
                    target_id: { type: "string", description: "Recipient wallet ID" },
                    amount: { type: "number", description: "Amount of RTC to send" },
                    key: { type: "string", description: "Wallet authorization key" },
                },
                required: ["miner_id", "target_id", "amount", "key"],
            },
        },
        {
            name: "rustchain_ledger",
            description: "Query transaction history for a miner",
            inputSchema: {
                type: "object",
                properties: {
                    miner_id: { type: "string", description: "The wallet ID/miner name" },
                },
                required: ["miner_id"],
            },
        },
        {
            name: "rustchain_register_wallet",
            description: "Create a new wallet on RustChain",
            inputSchema: {
                type: "object",
                properties: {
                    miner_id: { type: "string", description: "The desired wallet ID" },
                },
                required: ["miner_id"],
            },
        },
        {
            name: "rustchain_bounties",
            description: "List open RustChain bounties with rewards",
            inputSchema: { type: "object", properties: {} },
        },
    ],
}));
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    try {
        switch (name) {
            case "rustchain_health":
                return { content: [{ type: "text", text: JSON.stringify(await client.getHealth(), null, 2) }] };
            case "rustchain_miners":
                return { content: [{ type: "text", text: JSON.stringify(await client.getMiners(), null, 2) }] };
            case "rustchain_epoch":
                return { content: [{ type: "text", text: JSON.stringify(await client.getEpoch(), null, 2) }] };
            case "rustchain_balance":
                const { miner_id } = z.object({ miner_id: z.string() }).parse(args);
                return { content: [{ type: "text", text: JSON.stringify(await client.getBalance(miner_id), null, 2) }] };
            case "rustchain_transfer":
                const transferArgs = z.object({
                    miner_id: z.string(),
                    target_id: z.string(),
                    amount: z.number(),
                    key: z.string(),
                }).parse(args);
                return { content: [{ type: "text", text: JSON.stringify(await client.request("/wallet/transfer", transferArgs), null, 2) }] };
            case "rustchain_ledger":
                const ledgerArgs = z.object({ miner_id: z.string() }).parse(args);
                return { content: [{ type: "text", text: JSON.stringify(await client.request("/wallet/ledger", ledgerArgs), null, 2) }] };
            case "rustchain_register_wallet":
                const registerArgs = z.object({ miner_id: z.string() }).parse(args);
                return { content: [{ type: "text", text: JSON.stringify(await client.request("/wallet/register", registerArgs), null, 2) }] };
            case "rustchain_bounties":
                return { content: [{ type: "text", text: JSON.stringify(await client.request("/bounties"), null, 2) }] };
            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    }
    catch (error) {
        return {
            isError: true,
            content: [{ type: "text", text: error.message }],
        };
    }
});
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("RustChain MCP Server running on stdio");
}
main().catch((error) => {
    console.error("Server error:", error);
    process.exit(1);
});
