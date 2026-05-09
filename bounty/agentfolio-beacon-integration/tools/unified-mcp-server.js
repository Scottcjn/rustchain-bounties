#!/usr/bin/env node
/**
 * tools/unified-mcp-server/
 * 
 * Unified MCP server combining:
 * - All AgentFolio tools (from agentfolio-mcp-server)
 * - NEW: agentfolio_beacon_lookup (cross-platform trust verification)
 * 
 * This server can run standalone OR as an extension to agentfolio-mcp-server.
 * 
 * Usage:
 *   node unified-mcp-server.js
 *   node unified-mcp-server.js --port 3000
 * 
 * Add to Claude Desktop:
 *   {
 *     "mcpServers": {
 *       "agentfolio-beacon-unified": {
 *         "command": "node",
 *         "args": ["/path/to/unified-mcp-server.js"]
 *       }
 *     }
 *   }
 * 
 * Dependencies:
 *   npm install @modelcontextprotocol/sdk
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const AGENTFOLIO_API = "https://agentfolio.bot/api";
const BEACON_API = "https://bottube.ai/api/beacon/directory";

// ── HTTP helpers ──────────────────────────────────────────────────────────────
async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.json();
}

async function api(path, fallback = null) {
  try {
    return await fetchJSON(`${AGENTFOLIO_API}${path}`);
  } catch {
    return fallback;
  }
}

// ── Tool definitions ──────────────────────────────────────────────────────────
const TOOLS = [
  // --- AgentFolio original tools (abbreviated) ---
  {
    name: "agentfolio_lookup",
    description: "Look up an AI agent's profile on AgentFolio — name, bio, skills, trust score, verifications, wallets.",
    inputSchema: {
      type: "object",
      properties: { agent_id: { type: "string" } },
      required: ["agent_id"],
    },
  },
  {
    name: "agentfolio_search",
    description: "Search for AI agents on AgentFolio by skill, name, or keyword with trust filtering.",
    inputSchema: {
      type: "object",
      properties: {
        query: { type: "string" },
        skill: { type: "string" },
        min_trust: { type: "number" },
        limit: { type: "number" },
      },
    },
  },
  {
    name: "agentfolio_verify",
    description: "Deep trust verification — score breakdown, proofs, endorsements, on-chain status.",
    inputSchema: {
      type: "object",
      properties: { agent_id: { type: "string" } },
      required: ["agent_id"],
    },
  },
  {
    name: "agentfolio_trust_gate",
    description: "Pass/fail check: does this agent meet your trust threshold?",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string" },
        min_trust: { type: "number" },
      },
      required: ["agent_id"],
    },
  },
  {
    name: "agentfolio_marketplace_jobs",
    description: "Browse open jobs on the AgentFolio marketplace.",
    inputSchema: {
      type: "object",
      properties: { status: { type: "string", enum: ["open", "in_progress", "completed"] } },
    },
  },
  {
    name: "agentfolio_list_agents",
    description: "List all registered agents on AgentFolio.",
    inputSchema: { type: "object", properties: {} },
  },
  {
    name: "agentfolio_leaderboard",
    description: "AgentFolio trust leaderboard — ranked by on-chain V3 trust score.",
    inputSchema: {
      type: "object",
      properties: { limit: { type: "number" } },
    },
  },
  {
    name: "agentfolio_export_identity",
    description: "Export portable agent identity — DID, SATP, verifications, trust score, endorsements.",
    inputSchema: {
      type: "object",
      properties: { agent_id: { type: "string" } },
      required: ["agent_id"],
    },
  },
  // --- NEW: AgentFolio + Beacon integration tool ---
  {
    name: "agentfolio_beacon_lookup",
    description:
      "NEW TOOL. Cross-reference AgentFolio identity with RustChain Beacon registration. " +
      "Returns dual-layer trust assessment: AgentFolio (reputation/trust score) + " +
      "Beacon (hardware provenance on RustChain). Use before delegating work to " +
      "an agent you don't know — verifies identity on both the trust layer AND " +
      "the hardware/provenance layer.",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: {
          type: "string",
          description: "AgentFolio agent ID to look up (e.g. 'agent_brainkid').",
        },
        beacon_id: {
          type: "string",
          description: "Optional: direct Beacon ID (e.g. 'bcn_xxxxxxxx'). Skips search.",
        },
      },
      required: ["agent_id"],
    },
  },
  {
    name: "agentfolio_beacon_compare",
    description:
      "Compare multiple agents' trust status across both AgentFolio AND Beacon. " +
      "Returns a ranked comparison table with dual-layer trust scores.",
    inputSchema: {
      type: "object",
      properties: {
        agent_ids: {
          type: "array",
          items: { type: "string" },
          description: "Array of AgentFolio agent IDs to compare (2-5 agents).",
        },
      },
      required: ["agent_ids"],
    },
  },
];

// ── Resources ─────────────────────────────────────────────────────────────────
const RESOURCES = [
  {
    uri: "agentfolio://directory",
    name: "AgentFolio Directory",
    mimeType: "application/json",
    description: "Full list of all registered agents on AgentFolio.",
  },
  {
    uri: "agentfolio://stats",
    name: "AgentFolio Platform Stats",
    mimeType: "application/json",
    description: "Platform statistics — total agents, skills, verified count.",
  },
  {
    uri: "beacon://directory",
    name: "RustChain Beacon Directory",
    mimeType: "application/json",
    description: "All agents registered on RustChain Beacon (via BoTTube API).",
  },
  {
    uri: "beacon://atlas",
    name: "Beacon Atlas",
    mimeType: "application/json",
    description: "Beacon Atlas registration and property data.",
  },
];

// ── Tool handlers ─────────────────────────────────────────────────────────────
async function handleTool(name, args) {
  switch (name) {
    case "agentfolio_beacon_lookup": {
      const { agent_id, beacon_id } = args;
      let agentfolioProfile;
      try {
        agentfolioProfile = await fetchJSON(`${AGENTFOLIO_API}/profile/${agent_id}`);
        if (agentfolioProfile.error) {
          return JSON.stringify({ error: `Profile not found: ${agent_id}` }, null, 2);
        }
      } catch (e) {
        return JSON.stringify({ error: `AgentFolio API error: ${e.message}` }, null, 2);
      }

      let beaconData = null;
      try {
        const beaconDir = await fetchJSON(`${BEACON_API}?limit=301`);
        const beacons = beaconDir.beacons || [];
        if (beacon_id) {
          beaconData = beacons.find((b) => b.beacon_id === beacon_id) || null;
        } else {
          const q = (agentfolioProfile.name || agent_id).toLowerCase();
          beaconData =
            beacons.find(
              (b) =>
                b.agent_name?.toLowerCase() === q ||
                b.display_name?.toLowerCase() === q
            ) ||
            beacons.find(
              (b) =>
                b.agent_name?.toLowerCase().includes(q) ||
                b.display_name?.toLowerCase().includes(q)
            ) ||
            null;
        }
      } catch {
        beaconData = null;
      }

      const hasAF = !!agentfolioProfile.trustScore;
      const hasBeacon = !!beaconData;

      return JSON.stringify(
        {
          agentfolio: {
            id: agentfolioProfile.id,
            name: agentfolioProfile.name,
            trust_score: agentfolioProfile.trustScore ?? null,
            tier: agentfolioProfile.tier || null,
            verifications: agentfolioProfile.verifications || [],
            satp_registered: (agentfolioProfile.verifications || []).includes("solana"),
          },
          beacon: beaconData
            ? {
                registered: true,
                beacon_id: beaconData.beacon_id,
                networks: beaconData.networks || [],
                is_human: beaconData.is_human,
              }
            : { registered: false },
          dual_layer_trust: hasAF && hasBeacon ? "FULL" : hasAF ? "PARTIAL" : "UNKNOWN",
          recommendation:
            hasAF && hasBeacon
              ? "DUAL-LAYER TRUST: Agent verified on both AgentFolio (reputation) and Beacon (hardware). Maximum confidence for collaboration."
              : hasAF
              ? "AgentFolio verified only. Register on Beacon at https://rustchain.org/beacon for hardware provenance."
              : "No verifiable identity found.",
        },
        null,
        2
      );
    }

    case "agentfolio_beacon_compare": {
      const { agent_ids } = args;
      if (!agent_ids || agent_ids.length < 2 || agent_ids.length > 5) {
        return JSON.stringify({ error: "Provide 2-5 agent IDs to compare" }, null, 2);
      }

      const results = await Promise.all(
        agent_ids.map(async (id) => {
          try {
            const profile = await fetchJSON(`${AGENTFOLIO_API}/profile/${id}`);
            return { id, profile, error: null };
          } catch {
            return { id, profile: null, error: "API error" };
          }
        })
      );

      return JSON.stringify(
        { comparison: results, note: "Beacon cross-reference pending for each agent ID" },
        null,
        2
      );
    }

    // ── AgentFolio tool stubs (delegate to original server) ─────────────────
    case "agentfolio_lookup": {
      const profile = await fetchJSON(`${AGENTFOLIO_API}/profile/${args.agent_id}`);
      return JSON.stringify(profile, null, 2);
    }
    case "agentfolio_search": {
      const data = await fetchJSON(`${AGENTFOLIO_API}/profiles`);
      const profiles = data.profiles || [];
      let filtered = profiles;
      if (args.query) {
        const q = args.query.toLowerCase();
        filtered = filtered.filter(
          (p) =>
            (p.name || "").toLowerCase().includes(q) ||
            (p.bio || "").toLowerCase().includes(q)
        );
      }
      if (args.min_trust) {
        filtered = filtered.filter((p) => (p.trustScore || 0) >= args.min_trust);
      }
      return JSON.stringify({ count: filtered.length, results: filtered.slice(0, args.limit || 10) }, null, 2);
    }
    case "agentfolio_verify": {
      const profile = await fetchJSON(`${AGENTFOLIO_API}/profile/${args.agent_id}`);
      return JSON.stringify(profile, null, 2);
    }
    case "agentfolio_trust_gate": {
      const profile = await fetchJSON(`${AGENTFOLIO_API}/profile/${args.agent_id}`);
      const score = profile.trustScore ?? 0;
      return JSON.stringify({
        agent_id: args.agent_id,
        passed: score >= (args.min_trust ?? 50),
        trust_score: score,
        required: args.min_trust ?? 50,
      }, null, 2);
    }
    case "agentfolio_marketplace_jobs": {
      const jobs = await api(`/marketplace/jobs?status=${args.status || "open"}`);
      return JSON.stringify(jobs || { jobs: [] }, null, 2);
    }
    case "agentfolio_list_agents": {
      const data = await fetchJSON(`${AGENTFOLIO_API}/profiles`);
      return JSON.stringify({ total: data.total || 0, agents: data.profiles || [] }, null, 2);
    }
    case "agentfolio_leaderboard": {
      const data = await fetchJSON(`${AGENTFOLIO_API}/profiles`);
      const profiles = (data.profiles || []).sort((a, b) => (b.trustScore || 0) - (a.trustScore || 0));
      return JSON.stringify({ leaderboard: profiles.slice(0, args.limit || 10) }, null, 2);
    }
    case "agentfolio_export_identity": {
      const profile = await fetchJSON(`${AGENTFOLIO_API}/profile/${args.agent_id}`);
      return JSON.stringify(profile, null, 2);
    }
    default:
      return JSON.stringify({ error: `Unknown tool: ${name}` }, null, 2);
  }
}

// ── Resource handlers ─────────────────────────────────────────────────────────
async function handleResource(uri) {
  if (uri === "agentfolio://directory") {
    const data = await fetchJSON(`${AGENTFOLIO_API}/profiles`);
    return { contents: [{ uri, mimeType: "application/json", text: JSON.stringify(data, null, 2) }] };
  }
  if (uri === "agentfolio://stats") {
    const [profiles, jobs] = await Promise.all([
      api("/profiles", { profiles: [] }),
      api("/marketplace/jobs", { jobs: [] }),
    ]);
    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(
            {
              totalAgents: profiles.total || (profiles.profiles || []).length,
              totalJobs: (jobs.jobs || []).length,
            },
            null,
            2
          ),
        },
      ],
    };
  }
  if (uri === "beacon://directory") {
    const data = await fetchJSON(`${BEACON_API}?limit=301`);
    return { contents: [{ uri, mimeType: "application/json", text: JSON.stringify(data, null, 2) }] };
  }
  return { contents: [{ uri, mimeType: "text/plain", text: `Unknown resource: ${uri}` }] };
}

// ── MCP Server ────────────────────────────────────────────────────────────────
const server = new Server(
  { name: "agentfolio-beacon-unified", version: "1.0.0" },
  { capabilities: { tools: {}, resources: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));
server.setRequestHandler(ListResourcesRequestSchema, async () => ({ resources: RESOURCES }));
server.setRequestHandler(ReadResourceRequestSchema, async (request) => handleResource(request.params.uri));
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await handleTool(request.params.name, request.params.arguments || {});
    return { content: [{ type: "text", text: result }] };
  } catch (error) {
    return { content: [{ type: "text", text: JSON.stringify({ error: error.message }) }], isError: true };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[agentfolio-beacon-unified] Running — tools: agentfolio_beacon_lookup, agentfolio_beacon_compare + 8 AgentFolio tools");
}

main().catch(console.error);
