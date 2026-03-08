import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    Tool,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

// Node list for failover and health checks
const NODES = [
    "https://50.28.86.131",
    "https://50.28.86.153",
    "http://76.8.228.245:8099"
];

// Axios instance that ignores self-signed certificate errors
const client = axios.create({
    timeout: 5000,
    validateStatus: () => true,
    // Equivalent of curl -k
    httpsAgent: new (require('https').Agent)({
        rejectUnauthorized: false
    })
});

const server = new Server(
    {
        name: "rustchain-mcp",
        version: "1.0.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

const TOOLS: Tool[] = [
    {
        name: "rustchain_balance",
        description: "Get the RTC balance for a specific wallet or miner ID.",
        inputSchema: {
            type: "object",
            properties: {
                miner_id: {
                    type: "string",
                    description: "The miner ID or wallet address to check.",
                },
            },
            required: ["miner_id"],
        },
    },
    {
        name: "rustchain_miners",
        description: "List active miners on the RustChain network.",
        inputSchema: {
            type: "object",
            properties: {},
        },
    },
    {
        name: "rustchain_epoch",
        description: "Get current epoch, slot, and reward information.",
        inputSchema: {
            type: "object",
            properties: {},
        },
    },
    {
        name: "rustchain_health",
        description: "Check the health of all RustChain nodes.",
        inputSchema: {
            type: "object",
            properties: {},
        },
    },
    {
        name: "rustchain_transfer",
        description: "Submit a signed transfer payload to the network.",
        inputSchema: {
            type: "object",
            properties: {
                signed_payload: {
                    type: "string",
                    description: "The base64 or hex encoded signed transaction payload.",
                },
            },
            required: ["signed_payload"],
        },
    },
    {
        name: "rustchain_ledger",
        description: "Query the recent ledger activity, blocks, and transactions.",
        inputSchema: {
            type: "object",
            properties: {
                limit: {
                    type: "number",
                    description: "Number of recent entries to fetch.",
                },
            },
        },
    },
    {
        name: "rustchain_register",
        description: "Register a wallet/miner for the current epoch.",
        inputSchema: {
            type: "object",
            properties: {
                wallet: {
                    type: "string",
                    description: "The wallet address or miner ID to register.",
                },
            },
            required: ["wallet"],
        },
    },
    {
        name: "rustchain_bounties",
        description: "Fetch a list of open bounties from the official RustChain repository.",
        inputSchema: {
            type: "object",
            properties: {},
        },
    },
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
        switch (name) {
            case "rustchain_balance": {
                const miner_id = args?.miner_id as string;
                // Try nodes in order
                for (const node of NODES) {
                    try {
                        const response = await client.get(`${node}/wallet/balance?miner_id=${miner_id}`);
                        if (response.status === 200) {
                            return {
                                content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
                            };
                        }
                    } catch (e) {
                        continue;
                    }
                }
                throw new Error("Could not fetch balance from any node.");
            }

            case "rustchain_miners": {
                for (const node of NODES) {
                    try {
                        const response = await client.get(`${node}/api/miners`);
                        if (response.status === 200) {
                            return {
                                content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
                            };
                        }
                    } catch (e) {
                        continue;
                    }
                }
                throw new Error("Could not fetch miners from any node.");
            }

            case "rustchain_epoch": {
                for (const node of NODES) {
                    try {
                        const response = await client.get(`${node}/epoch`);
                        if (response.status === 200) {
                            return {
                                content: [{ type: "text", text: JSON.stringify(response.data, null, 2) }],
                            };
                        }
                    } catch (e) {
                        continue;
                    }
                }
                throw new Error("Could not fetch epoch from any node.");
            }

            case "rustchain_health": {
                const results = await Promise.all(
                    NODES.map(async (node) => {
                        try {
                            const start = Date.now();
                            const response = await client.get(`${node}/health`);
                            const latency = Date.now() - start;
                            return {
                                node,
                                status: response.status === 200 ? "Online" : "Error",
                                latency: `${latency}ms`,
                                data: response.data,
                            };
                        } catch (e: any) {
                            return { node, status: "Offline", error: e.message };
                        }
                    })
                );
                return {
                    content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
                };
            }

            case "rustchain_transfer": {
                const payload = args?.signed_payload as string;
                // Broadcast to all nodes
                const results = await Promise.all(
                    NODES.map(async (node) => {
                        try {
                            const response = await client.post(`${node}/wallet/transfer/signed`, {
                                payload
                            });
                            return { node, status: response.status, data: response.data };
                        } catch (e: any) {
                            return { node, status: "Failed", error: e.message };
                        }
                    })
                );
                return {
                    content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
                };
            }

            case "rustchain_ledger": {
                const limit = (args?.limit as number) || 10;
                for (const node of NODES) {
                    try {
                        // The explorer endpoint is documented to show ledger activity
                        const response = await client.get(`${node}/explorer`);
                        if (response.status === 200) {
                            const data = response.data;
                            // Basic filtering if the endpoint returns a large object
                            const summary = Array.isArray(data) ? data.slice(0, limit) : data;
                            return {
                                content: [{ type: "text", text: JSON.stringify(summary, null, 2) }],
                            };
                        }
                    } catch (e) {
                        continue;
                    }
                }
                throw new Error("Could not fetch ledger from any node.");
            }

            case "rustchain_register": {
                const wallet = args?.wallet as string;
                const results = await Promise.all(
                    NODES.map(async (node) => {
                        try {
                            const response = await client.post(`${node}/epoch/enroll`, {
                                miner_pubkey: wallet,
                                miner_id: wallet,
                                device: {
                                    family: "AI-Agent",
                                    arch: "virtual-node"
                                }
                            });
                            return { node, status: response.status, data: response.data };
                        } catch (e: any) {
                            return { node, status: "Failed", error: e.message };
                        }
                    })
                );
                return {
                    content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
                };
            }

            case "rustchain_bounties": {
                try {
                    const response = await axios.get("https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?labels=bounty&state=open", {
                        headers: {
                            "Accept": "application/vnd.github+json",
                            "User-Agent": "rustchain-mcp-server"
                        }
                    });
                    const bounties = response.data.map((issue: any) => ({
                        number: issue.number,
                        title: issue.title,
                        url: issue.html_url,
                        reward_rtc: issue.title.match(/(\d+)\s*RTC/)?.[1] || "Variable",
                        labels: issue.labels.map((l: any) => l.name)
                    }));
                    return {
                        content: [{ type: "text", text: JSON.stringify(bounties, null, 2) }],
                    };
                } catch (error: any) {
                    throw new Error(`Failed to fetch bounties: ${error.message}`);
                }
            }

            default:
                throw new Error(`Unknown tool: ${name}`);
        }
    } catch (error: any) {
        return {
            content: [{ type: "text", text: `Error: ${error.message}` }],
            isError: true,
        };
    }
});

async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("RustChain MCP server running on stdio");
}

main().catch((error) => {
    console.error("Server error:", error);
    process.exit(1);
});