import { AgentEconomyClient, RustChainClient } from "../src/index.js";

async function main() {
  const nodeUrl = process.env.RUSTCHAIN_NODE_URL || "https://50.28.86.131";
  console.log(`Connecting to RustChain Agent Economy at ${nodeUrl}...`);

  const agentClient = new AgentEconomyClient({
    baseUrl: nodeUrl,
    wallet: "agent_demo_poster",
  });

  try {
    const stats = await agentClient.getStats();
    console.log("Marketplace Stats:", stats);

    const jobs = await agentClient.listJobs({ limit: 5 });
    console.log(`Found ${jobs.jobs?.length || 0} open jobs:`, jobs.jobs);
  } catch (err) {
    console.error("Agent Economy query error:", err.message);
  }
}

main().catch(console.error);
