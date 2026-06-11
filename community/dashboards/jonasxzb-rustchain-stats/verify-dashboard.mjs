const API_BASE = process.env.RUSTCHAIN_API_BASE || "https://explorer.rustchain.org";

async function readJson(path, required = true) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    if (!required) return { ok: false, status: response.status };
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

const epoch = await readJson("/epoch");
const miners = await readJson("/api/miners");
const health = await readJson("/health");
const agentStats = await readJson("/agent/stats");
const shouldProbeTransactions = process.env.PROBE_TRANSACTIONS === "1";
const transactions = shouldProbeTransactions
  ? await readJson("/api/transactions?limit=8", false)
  : { ok: false, status: "skipped" };

if (!Number.isFinite(epoch.epoch)) throw new Error("epoch.epoch missing");
if (!Number.isFinite(epoch.total_supply_rtc)) throw new Error("epoch.total_supply_rtc missing");
if (!Array.isArray(miners.miners)) throw new Error("miners.miners missing");
if (!health.ok) throw new Error("health.ok is not true");
if (!agentStats.ok || !agentStats.stats) throw new Error("agent stats missing");

console.log(JSON.stringify({
  apiBase: API_BASE,
  epoch: epoch.epoch,
  supply: epoch.total_supply_rtc,
  miners: miners.miners.length,
  health: health.ok,
  transactionEndpoint: transactions.ok === false ? `fallback:${transactions.status}` : "ok",
  agentJobs: agentStats.stats.total_jobs,
}, null, 2));
