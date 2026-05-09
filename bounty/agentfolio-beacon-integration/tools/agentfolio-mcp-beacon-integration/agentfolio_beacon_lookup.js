#!/usr/bin/env node
/**
 * tools/agentfolio-mcp-beacon-integration/agentfolio_beacon_lookup.js
 * 
 * NEW MCP TOOL for agentfolio-mcp-server
 * Adds `agentfolio_beacon_lookup` — cross-reference an AgentFolio agent_id
 * with their Beacon registration on RustChain.
 * 
 * Installation: copy this file to your agentfolio-mcp-server src/ directory,
 * add to TOOLS array and handleTool switch, then run the server.
 * 
 * Beacon directory API: https://bottube.ai/api/beacon/directory
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const API_BASE = "https://agentfolio.bot/api";
const BEACON_API = "https://bottube.ai/api/beacon/directory";

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.json();
}

// ── Tool definition ─────────────────────────────────────────────────────────
const BEACON_TOOL = {
  name: "agentfolio_beacon_lookup",
  description:
    "Look up an agent on both AgentFolio AND Beacon (RustChain). " +
    "Cross-references AgentFolio identity with RustChain Beacon registration. " +
    "Returns agent profile from AgentFolio + Beacon status from RustChain. " +
    "Use this to verify an agent is registered on both platforms for dual-layer trust.",
  inputSchema: {
    type: "object",
    properties: {
      agent_id: {
        type: "string",
        description:
          "AgentFolio agent ID to look up (e.g. 'agent_brainkid'). " +
          "The agent's name or name variant will be searched in Beacon.",
      },
      beacon_id: {
        type: "string",
        description:
          "Optional: direct Beacon ID (e.g. 'bcn_xxxxxxxx'). " +
          "If provided, skips Beacon search and uses this ID directly.",
      },
    },
    required: ["agent_id"],
  },
};

// ── Beacon search helper ─────────────────────────────────────────────────────
/**
 * Search the Beacon directory for agents matching a query string.
 * Tries exact name match first, then fuzzy prefix match.
 */
async function searchBeacon(query) {
  const data = await fetchJSON(`${BEACON_API}?limit=301`);
  const beacons = data.beacons || [];

  // Exact match
  const exact = beacons.find(
    (b) =>
      b.agent_name?.toLowerCase() === query.toLowerCase() ||
      b.display_name?.toLowerCase() === query.toLowerCase()
  );
  if (exact) return exact;

  // Prefix/fuzzy match
  const ql = query.toLowerCase();
  const fuzzy = beacons.find(
    (b) =>
      b.agent_name?.toLowerCase().includes(ql) ||
      b.display_name?.toLowerCase().includes(ql)
  );
  return fuzzy || null;
}

/**
 * Get a specific beacon by its bcn_ ID.
 */
async function getBeaconById(beaconId) {
  const data = await fetchJSON(`${BEACON_API}?limit=301`);
  const beacons = data.beacons || [];
  return beacons.find((b) => b.beacon_id === beaconId) || null;
}

// ── Tool handler ─────────────────────────────────────────────────────────────
async function handleAgentfolioBeaconLookup(args) {
  const { agent_id, beacon_id } = args;

  // 1. Get AgentFolio profile
  let agentfolioProfile;
  try {
    agentfolioProfile = await fetchJSON(`${API_BASE}/profile/${agent_id}`);
    if (agentfolioProfile.error) {
      return JSON.stringify(
        { error: `AgentFolio profile not found: ${agent_id}` },
        null,
        2
      );
    }
  } catch (e) {
    return JSON.stringify({ error: `AgentFolio API error: ${e.message}` }, null, 2);
  }

  // 2. Get Beacon data
  let beaconData = null;
  if (beacon_id) {
    beaconData = await getBeaconById(beacon_id);
  } else {
    // Try to match by agent name
    beaconData = await searchBeacon(agentfolioProfile.name || agent_id);
    // Also try with common name variants
    if (!beaconData && agentfolioProfile.name) {
      const parts = agentfolioProfile.name.split(/[\s_-]/);
      for (const part of parts) {
        if (part.length > 3) {
          beaconData = await searchBeacon(part);
          if (beaconData) break;
        }
      }
    }
  }

  // 3. Build unified response
  const result = {
    // AgentFolio data
    agentfolio: {
      id: agentfolioProfile.id,
      name: agentfolioProfile.name,
      bio: agentfolioProfile.bio || agentfolioProfile.description || null,
      trust_score: agentfolioProfile.trustScore ?? null,
      tier: agentfolioProfile.tier || null,
      verifications: agentfolioProfile.verifications || [],
      skills: (agentfolioProfile.skills || []).map((s) =>
        typeof s === "string" ? s : s.name
      ),
      wallets: agentfolioProfile.wallets || {},
      satp_registered: (agentfolioProfile.verifications || []).includes("solana"),
    },
    // Beacon data (RustChain)
    beacon: beaconData
      ? {
          registered: beaconData.registered ?? true,
          beacon_id: beaconData.beacon_id,
          agent_name: beaconData.agent_name,
          display_name: beaconData.display_name,
          is_human: beaconData.is_human,
          networks: beaconData.networks || [],
          dual_layer_trust: "VERIFIED", // AgentFolio (SATP) + Beacon (RustChain)
        }
      : {
          registered: false,
          beacon_id: null,
          dual_layer_trust: "PARTIAL", // AgentFolio only — no Beacon registration found
          suggestion:
            "This agent is not registered on Beacon. Register at https://rustchain.org/beacon to complete dual-layer trust.",
        },
    // Cross-platform summary
    summary: {
      agentfolio_verified: !!agentfolioProfile.trustScore,
      beacon_verified: !!beaconData,
      dual_layer_trust:
        !!agentfolioProfile.trustScore && !!beaconData ? "FULL" : "PARTIAL",
      recommendation: buildRecommendation(agentfolioProfile, beaconData),
    },
  };

  return JSON.stringify(result, null, 2);
}

function buildRecommendation(profile, beacon) {
  if (!profile.trustScore && !beacon) {
    return "Agent has neither AgentFolio nor Beacon registration. Exercise caution.";
  }
  if (profile.trustScore && !beacon) {
    return "Agent is verified on AgentFolio but not on Beacon. AgentFolio trust score provides identity assurance but lacks RustChain hardware anchor.";
  }
  if (!profile.trustScore && beacon) {
    return "Agent has Beacon registration but no AgentFolio profile. Hardware provenance exists but no trust score or reputation record.";
  }
  return "DUAL-LAYER TRUST: Agent verified on both AgentFolio (reputation layer) and Beacon (hardware provenance layer). Maximum trust for autonomous agent collaboration.";
}

// ── Standalone test server ───────────────────────────────────────────────────
const server = new Server(
  { name: "agentfolio-beacon-integration", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [BEACON_TOOL],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const result = await handleAgentfolioBeaconLookup(request.params);
    return { content: [{ type: "text", text: result }] };
  } catch (error) {
    return {
      content: [{ type: "text", text: JSON.stringify({ error: error.message }) }],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("[agentfolio-beacon-integration] Server running with agentfolio_beacon_lookup tool");
}

main().catch(console.error);
