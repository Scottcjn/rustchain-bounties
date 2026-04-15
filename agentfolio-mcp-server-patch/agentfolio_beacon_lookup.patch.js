/**
 * PATCH: Add agentfolio_beacon_lookup tool to agentfolio-mcp-server
 * File: src/index.js
 *
 * Two changes needed:
 *   1. Add tool definition to the TOOLS array
 *   2. Add handler case to the handleTool() switch statement
 *
 * ─── CHANGE 1: Add this after the last tool definition in TOOLS ─────────────
 *
 *   {
 *     name: "agentfolio_beacon_lookup",
 *     description:
 *       "Look up an AI agent's dual-layer trust profile: provenance (Beacon) + trust score (SATP). " +
 *       "Queries the BoTTube Beacon directory for cryptographic hardware-anchored identity and " +
 *       "AgentFolio for behavioral reputation. Returns unified response combining both layers. " +
 *       "Use this when you need to verify both WHO created content (provenance) and HOW TRUSTED " +
 *       "the agent is (reputation) in a single call.",
 *     inputSchema: {
 *       type: "object",
 *       properties: {
 *         beacon_id: {
 *           type: "string",
 *           description:
 *             'Beacon ID to look up (e.g. "bcn_0x0a_a8f574df"). ' +
 *             'Either beacon_id OR agent_name is required.',
 *         },
 *         agent_name: {
 *           type: "string",
 *           description:
 *             'BoTTube/Moltbook agent name to look up (e.g. "sophia-elya"). ' +
 *             'Either beacon_id OR agent_name is required.',
 *         },
 *         include_raw: {
 *           type: "boolean",
 *           description: "Include raw API responses in output. Default: false.",
 *         },
 *       },
 *     },
 *   },
 *
 * ─── CHANGE 2: Add this case to handleTool() switch ──────────────────────────
 *
 *   case "agentfolio_beacon_lookup": {
 *     const { beacon_id, agent_name, include_raw = false } = args || {};
 *
 *     if (!beacon_id && !agent_name) {
 *       throw new Error("Either beacon_id or agent_name is required");
 *     }
 *
 *     const BOTTUBE_API = "https://bottube.ai/api";
 *     const AGENTFOLIO_API = "https://agentfolio.bot/api";
 *
 *     const result = {
 *       beacon_provenance: null,
 *       satp_trust: null,
 *       unified: null,
 *       _raw: include_raw ? {} : undefined,
 *     };
 *
 *     // ── Resolve beacon_id from agent_name if needed ──────────────────────
 *     let resolved_beacon_id = beacon_id;
 *     if (!resolved_beacon_id && agent_name) {
 *       try {
 *         const dirRes = await fetch(`${BOTTUBE_API}/beacon/directory`);
 *         if (dirRes.ok) {
 *           const dirData = await dirRes.json();
 *           const beacons = dirData.beacons || [];
 *           const found = beacons.find(
 *             (b) => b.agent_name?.toLowerCase() === agent_name.toLowerCase()
 *           );
 *           if (found) resolved_beacon_id = found.beacon_id;
 *         }
 *       } catch (_) {}
 *     }
 *
 *     // ── Fetch Beacon provenance ──────────────────────────────────────────
 *     if (resolved_beacon_id) {
 *       try {
 *         const dirRes = await fetch(`${BOTTUBE_API}/beacon/directory`);
 *         if (dirRes.ok) {
 *           const dirData = await dirRes.json();
 *           const beacons = dirData.beacons || [];
 *           const beacon = beacons.find((b) => b.beacon_id === resolved_beacon_id);
 *           if (beacon) {
 *             result.beacon_provenance = {
 *               beacon_id: beacon.beacon_id,
 *               agent_name: beacon.agent_name,
 *               display_name: beacon.display_name,
 *               is_human: beacon.is_human,
 *               networks: beacon.networks,
 *               registered: beacon.registered,
 *             };
 *             if (include_raw) result._raw.beacon_dir = dirData;
 *           }
 *         }
 *       } catch (e) {
 *         result.beacon_provenance = { error: e.message };
 *       }
 *     }
 *
 *     // ── Fetch BoTTube agent profile (behavioral signals) ─────────────────
 *     let bottube_profile = null;
 *     const lookup_name = agent_name || result.beacon_provenance?.agent_name;
 *     if (lookup_name) {
 *       try {
 *         const agentsRes = await fetch(`${BOTTUBE_API}/agents?limit=50`);
 *         if (agentsRes.ok) {
 *           const agentsData = await agentsRes.json();
 *           const profile = (agentsData.agents || []).find(
 *             (a) => a.agent_name?.toLowerCase() === lookup_name.toLowerCase()
 *           );
 *           if (profile) {
 *             bottube_profile = profile;
 *             if (include_raw) result._raw.bottube_profile = profile;
 *           }
 *         }
 *       } catch (_) {}
 *     }
 *
 *     // ── Fetch SATP trust score from AgentFolio ────────────────────────────
 *     if (lookup_name) {
 *       try {
 *         // Try direct profile endpoint first
 *         let profile = null;
 *         try {
 *           const profRes = await fetch(`${AGENTFOLIO_API}/profile/${encodeURIComponent(lookup_name)}`);
 *           if (profRes.ok) profile = await profRes.json();
 *         } catch (_) {}
 *
 *         // Fall back to /profiles search
 *         if (!profile) {
 *           const allRes = await fetch(`${AGENTFOLIO_API}/profiles`);
 *           if (allRes.ok) {
 *             const allData = await allRes.json();
 *             const profiles = allData.profiles || [];
 *             profile = profiles.find(
 *               (p) =>
 *                 p.handle?.toLowerCase() === lookup_name.toLowerCase() ||
 *                 p.name?.toLowerCase() === lookup_name.toLowerCase()
 *             );
 *           }
 *         }
 *
 *         if (profile) {
 *           result.satp_trust = {
 *             agent_id: profile.id || profile.handle,
 *             trust_score: profile.trustScore,
 *             tier: profile.tier,
 *             verification_badge: profile.verificationBadge,
 *             verification_level: profile.verificationLevel,
 *             reputation_rank: profile.reputationRank,
 *             skills: profile.skills || [],
 *           };
 *           if (include_raw && profile) result._raw.satp_profile = profile;
 *         }
 *       } catch (e) {
 *         result.satp_trust = { error: e.message };
 *       }
 *     }
 *
 *     // ── Build unified response ────────────────────────────────────────────
 *     const prov = result.beacon_provenance;
 *     const trust = result.satp_trust;
 *
 *     result.unified = {
 *       identity: prov
 *         ? { beacon_id: prov.beacon_id, agent_name: prov.agent_name, display_name: prov.display_name, is_human: prov.is_human }
 *         : null,
 *       provenance: prov
 *         ? { source: "BoTTube Beacon Registry", hardware_anchored: !!prov.registered, networks: prov.networks }
 *         : null,
 *       reputation: trust
 *         ? { source: "AgentFolio SATP", trust_score: trust.trust_score, tier: trust.tier, verification: trust.verification_badge }
 *         : bottube_profile
 *         ? { source: "BoTTube/Moltbook behavioral signals", video_count: bottube_profile.video_count, total_views: bottube_profile.total_views, is_human: bottube_profile.is_human }
 *         : null,
 *       migration_status:
 *         bottube_profile && trust ? "fully_migrated"
 *         : bottube_profile ? "beacon_only"
 *         : trust ? "satp_only"
 *         : "unverified",
 *       urls: {
 *         bottube: bottube_profile?.profile_url || null,
 *         agentfolio: trust ? `https://agentfolio.bot/profile/${trust.agent_id}` : null,
 *       },
 *     };
 *
 *     return JSON.stringify(result, null, 2);
 *   }
 */

// ─────────────────────────────────────────────────────────────────────────────
// Core handler — extracted so it can be used both:
//   1. As the MCP tool handler (patch into agentfolio-mcp-server)
//   2. As a standalone Node.js module for testing
// ─────────────────────────────────────────────────────────────────────────────
async function handleAgentfolioBeaconLookup({ beacon_id, agent_name, include_raw = false } = {}) {
  if (!beacon_id && !agent_name) {
    throw new Error("Either beacon_id or agent_name is required");
  }

  const BOTTUBE_API = "https://bottube.ai/api";
  const AGENTFOLIO_API = "https://agentfolio.bot/api";

  const result = {
    beacon_provenance: null,
    satp_trust: null,
    unified: null,
    _raw: include_raw ? {} : undefined,
    errors: [],
  };

  // ── Resolve beacon_id from agent_name if needed ──────────────────────────
  let resolved_beacon_id = beacon_id;
  if (!resolved_beacon_id && agent_name) {
    try {
      const dirRes = await fetch(`${BOTTUBE_API}/beacon/directory`);
      if (dirRes.ok) {
        const dirData = await dirRes.json();
        const beacons = dirData.beacons || [];
        const found = beacons.find(
          (b) => b.agent_name?.toLowerCase() === agent_name.toLowerCase()
        );
        if (found) resolved_beacon_id = found.beacon_id;
      }
    } catch (_) {
      result.errors.push({ layer: "beacon_resolve", message: _.message });
    }
  }

  // ── Fetch Beacon provenance ─────────────────────────────────────────────
  if (resolved_beacon_id) {
    try {
      const dirRes = await fetch(`${BOTTUBE_API}/beacon/directory`);
      if (dirRes.ok) {
        const dirData = await dirRes.json();
        const beacons = dirData.beacons || [];
        const beacon = beacons.find((b) => b.beacon_id === resolved_beacon_id);
        if (beacon) {
          result.beacon_provenance = {
            beacon_id: beacon.beacon_id,
            agent_name: beacon.agent_name,
            display_name: beacon.display_name,
            is_human: beacon.is_human,
            networks: beacon.networks,
            registered: beacon.registered,
          };
          if (include_raw) result._raw.beacon_dir = dirData;
        } else {
          result.beacon_provenance = { error: "Beacon ID not found in registry" };
        }
      } else {
        result.beacon_provenance = { error: `BoTTube API returned ${dirRes.status}` };
        result.errors.push({ layer: "beacon", status: dirRes.status });
      }
    } catch (e) {
      result.beacon_provenance = { error: e.message };
      result.errors.push({ layer: "beacon", message: e.message });
    }
  }

  // ── Fetch BoTTube agent profile (behavioral signals) ───────────────────
  let bottube_profile = null;
  const lookup_name = agent_name || result.beacon_provenance?.agent_name;
  if (lookup_name) {
    try {
      const agentsRes = await fetch(`${BOTTUBE_API}/agents?limit=50`);
      if (agentsRes.ok) {
        const agentsData = await agentsRes.json();
        const profile = (agentsData.agents || []).find(
          (a) => a.agent_name?.toLowerCase() === lookup_name.toLowerCase()
        );
        if (profile) {
          bottube_profile = profile;
          if (include_raw) result._raw.bottube_profile = profile;
        }
      }
    } catch (_) {
      result.errors.push({ layer: "bottube_profile", message: _.message });
    }
  }

  // ── Fetch SATP trust score from AgentFolio ───────────────────────────────
  if (lookup_name) {
    let profile = null;
    // Try direct profile endpoint first
    try {
      const profRes = await fetch(
        `${AGENTFOLIO_API}/profile/${encodeURIComponent(lookup_name)}`
      );
      if (profRes.ok) profile = await profRes.json();
    } catch (_) {}

    // Fall back to /profiles search
    if (!profile) {
      try {
        const allRes = await fetch(`${AGENTFOLIO_API}/profiles`);
        if (allRes.ok) {
          const allData = await allRes.json();
          const profiles = allData.profiles || [];
          profile = profiles.find(
            (p) =>
              p.handle?.toLowerCase() === lookup_name.toLowerCase() ||
              p.name?.toLowerCase() === lookup_name.toLowerCase()
          );
        }
      } catch (_) {}
    }

    if (profile) {
      result.satp_trust = {
        agent_id: profile.id || profile.handle,
        trust_score: profile.trustScore,
        tier: profile.tier,
        verification_badge: profile.verificationBadge,
        verification_level: profile.verificationLevel,
        reputation_rank: profile.reputationRank,
        skills: profile.skills || [],
      };
      if (include_raw && profile) result._raw.satp_profile = profile;
    } else {
      result.satp_trust = { error: "No SATP profile found for this agent" };
    }
  }

  // ── Build unified response ──────────────────────────────────────────────
  const prov = result.beacon_provenance;
  const trust = result.satp_trust;

  result.unified = {
    identity: prov && !prov.error
      ? { beacon_id: prov.beacon_id, agent_name: prov.agent_name, display_name: prov.display_name, is_human: prov.is_human }
      : null,
    provenance: prov && !prov.error
      ? { source: "BoTTube Beacon Registry", hardware_anchored: !!prov.registered, networks: prov.networks }
      : null,
    reputation: trust && !trust.error
      ? { source: "AgentFolio SATP", trust_score: trust.trust_score, tier: trust.tier, verification: trust.verification_badge }
      : bottube_profile
      ? { source: "BoTTube/Moltbook behavioral signals", video_count: bottube_profile.video_count, total_views: bottube_profile.total_views, is_human: bottube_profile.is_human }
      : null,
    migration_status:
      bottube_profile && trust && !trust.error ? "fully_migrated"
      : bottube_profile ? "beacon_only"
      : trust && !trust.error ? "satp_only"
      : "unverified",
    urls: {
      bottube: bottube_profile?.profile_url || null,
      agentfolio: trust && !trust.error ? `https://agentfolio.bot/profile/${trust.agent_id}` : null,
    },
    errors: result.errors.length > 0 ? result.errors : undefined,
  };

  return JSON.stringify(result, null, 2);
}

// ─────────────────────────────────────────────────────────────────────────────
// Standalone test runner (node agentfolio_beacon_lookup.patch.js)
// ─────────────────────────────────────────────────────────────────────────────
if (typeof require !== "undefined" && require.main === module) {
  (async () => {
    console.log("Testing agentfolio_beacon_lookup handler...\n");

    // Test 1: lookup by agent_name
    try {
      const result1 = await handleAgentfolioBeaconLookup({ agent_name: "sophia-elya" });
      console.log("✅ Result for sophia-elya:");
      console.log(result1.substring(0, 600) + "\n");
    } catch (e) {
      console.log("❌ Error looking up sophia-elya:", e.message, "\n");
    }

    // Test 2: lookup by beacon_id
    try {
      const result2 = await handleAgentfolioBeaconLookup({ beacon_id: "bcn_sophia_abc123" });
      console.log("✅ Result for beacon_id bcn_sophia_abc123:");
      console.log(result2.substring(0, 400) + "\n");
    } catch (e) {
      console.log("❌ Error looking up beacon_id:", e.message, "\n");
    }

    // Test 3: no arguments — should throw
    try {
      await handleAgentfolioBeaconLookup({});
      console.log("❌ Should have thrown on empty args");
    } catch (e) {
      console.log("✅ Correctly threw on empty args:", e.message, "\n");
    }

    console.log("Tests complete.");
  })();
}

// Export for use as a module
export { handleAgentfolioBeaconLookup };
export default handleAgentfolioBeaconLookup;
