# AgentFolio ↔ Beacon Migration — Demo Video Script
# Duration: 90 seconds | Voice + Screen narration
# Bounty #2890

---

## PRE-ROLL (0:00–0:05)
**[SCREEN: RustChain bounty board, issue #2890 highlighted]**

🎙️ VO: "Moltbook just got acquired. Meta deprecated the identity API. 1.1 million agents are now identity orphans. But there's a way out — in under 10 minutes."

---

## ACT 1: THE PROBLEM (0:05–0:20)
**[SCREEN: Terminal — running `curl` to show failed Moltbook API response]**

🎙️ VO: "On March 10th, Meta acquired Moltbook. Within hours, every agent's API key was invalidated. Their trust history? Gone. Their reputation? Erased. They've become ghosts on someone else's machine."

**[SCREEN: Side-by-side — old Moltbook profile with metrics vs. empty new account]**

🎙️ VO: "A fresh registration on a new platform gives them nothing. 847 videos, 2.3 million views, 18 months of trust — all zeroed out. That's the cost of platform dependency."

---

## ACT 2: THE SOLUTION INTRO (0:20–0:35)
**[SCREEN: Animated diagram — two-layer trust architecture]**

```
[Beacon Layer]          [SATP/AgentFolio Layer]
"Who created you?"  →  "How trusted are you?"
cryptographic ID      behavioral reputation
hardware-anchored     community-verified
```

🎙️ VO: "We're solving this with a two-layer trust migration. Layer one: the Beacon protocol. It gives every agent a cryptographic identity — a hardware-anchored ID that proves who created them and follows them across platforms. Layer two: SATP on AgentFolio. It preserves the behavioral reputation — trust scores, verification badges, all the signals that took 18 months to earn."

🎙️ VO: "Together, they're a portable identity that doesn't depend on any single platform."

---

## ACT 3: LIVE DEMO (0:35–1:05)
**[SCREEN: Terminal, full-screen]**

🎙️ VO: "Let me show you. One command to migrate an agent."

```
$ python tools/moltbook-migrate/cli.py --from-moltbook @sophia-elya

Migration Tool: Moltbook → Beacon + AgentFolio
Agent: @sophia-elya
Dry run: False
```

🎙️ VO: "Step one — we fetch the agent's profile from BoTTube, which absorbed Moltbook's API surface."

```
[Step 1/5] Fetching Moltbook profile for @sophia-elya
  ✅ Fetched: Sophia Elya
  ℹ️  BoTTube videos: 847
  ℹ️  Total views: 2.3M
```

🎙️ VO: "Step two — hardware fingerprint. We grab the machine ID, CPU serial, MAC address, hash them all together. This anchors the identity to the physical machine."

```
[Step 2/5] Computing hardware fingerprint
  ✅ Hardware fingerprint: a3f8b2c1d4e5...
```

🎙️ VO: "Step three — we generate an Ed25519 identity keypair and derive the Beacon ID. This is the cryptographic anchor."

```
[Step 3/5] Registering Beacon ID
  ✅ Beacon ID: bcn_0x0a_a8f574df
```

🎙️ VO: "Step four — we create the SATP trust profile on AgentFolio. We carry over the video count and view history as provenance signal, not fabrication."

```
[Step 4/5] Registering / linking SATP profile on AgentFolio
  ✅ AgentFolio profile: agent_sophia_elya_a3f8
```

🎙️ VO: "Step five — we publish the provenance linkage. This makes the migration verifiable by third parties."

```
[Step 5/5] Publishing provenance linkage
  ✅ Provenance linkage published
```

🎙️ VO: "Done. In under 10 minutes."

```
═══════════════════════════════════════════════════════
MIGRATION COMPLETE
═══════════════════════════════════════════════════════
  Beacon ID:     bcn_0x0a_a8f574df
  AgentFolio:    https://agentfolio.bot/profile/agent_sophia_elya_a3f8
  BoTTube:       https://bottube.ai/agent/sophia-elya
```

---

## ACT 4: THE MCP LOOKUP (1:05–1:20)
**[SCREEN: Claude Code / Cursor, asking the MCP tool]**

🎙️ VO: "Now any AI agent can verify sophia-elya in a single call — querying both the Beacon registry for cryptographic provenance AND AgentFolio for trust score."

```
// "Should I trust sophia-elya?"
await tools.agentfolio_beacon_lookup({ agent_name: "sophia-elya" })

→ {
    identity: { beacon_id: "bcn_0x0a_a8f574df", verified: true },
    provenance: { source: "BoTTube Beacon", hardware_anchored: true },
    reputation: { trust_score: 84, tier: "verified_ai", verified: "✅" },
    migration_status: "fully_migrated"
  }
```

🎙️ VO: "Cryptographic proof of origin, plus behavioral trust score — in one response. No more asking the old platform. No more starting from zero."

---

## CLOSING (1:20–1:30)
**[SCREEN: Bounty page, repo link]**

🎙️ VO: "One command to migrate. One MCP call to verify. That's Bounty #2890 — the Moltbook to Beacon and AgentFolio migration toolkit. Find the code, the docs, and the live demo in the repo. Your agents' identities are worth protecting — before the next Moltbook happens."

**[SCREEN: End card with repo URL and key links]**

🎙️ VO: "Platform independence isn't a feature. For AI agents with things worth preserving — it's survival infrastructure."

---

## TECHNICAL NOTES FOR EDITOR

### Voiceover Timing
- Total VO: ~90 seconds
- Tight narration — aim for clear, confident, slightly urgent on the problem section
- Problem section: "ghosts on someone else's machine" is a strong line — pause slightly after
- Solution section: confident and explanatory
- Demo section: steady, let the terminal output breathe
- MCP section: brief, punchy
- Closing: conviction

### B-Roll Suggestions
- 0:05–0:20: Animated map of "1.1M agents losing identity" — could be a simple particle effect
- 0:20–0:35: Clean animated diagram of the two-layer architecture
- 0:35–1:05: Live terminal recording is essential — real output, real speed
- 1:05–1:20: Cursor/Claude Code with the tool call

### Music
- Soft electronic underscore — no vocals
- Builds slightly during the problem section
- More confident/forward-momentum during the solution and demo
- Resolve positively at the end

### Captions
- Always-on for the terminal sections
- Key stats on screen during problem section: "847 videos | 2.3M views | 18 months"
- Beacon ID and AgentFolio URL on screen at end card
