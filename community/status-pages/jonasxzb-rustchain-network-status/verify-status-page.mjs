import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pagePath = path.join(__dirname, "index.html");

const nodes = [
  "https://rustchain.org",
  "https://explorer.rustchain.org",
  "https://50.28.86.131",
];

async function fetchJson(url) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${url} returned HTTP ${response.status}`);
  }
  return response.json();
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const html = await fs.readFile(pagePath, "utf8");

for (const expected of [
  "RustChain Network Status",
  "Attestation Nodes",
  "Architecture Breakdown",
  "Epoch Progress",
  "Recent Miner Attestations",
  "setInterval(refresh, REFRESH_MS)",
  "https://rustchain.org",
  "https://explorer.rustchain.org",
  "https://50.28.86.131",
]) {
  assert(html.includes(expected), `Missing expected page content: ${expected}`);
}

const healthResults = await Promise.all(
  nodes.map(async (baseUrl) => {
    const health = await fetchJson(`${baseUrl}/health`);
    assert(health.ok === true, `${baseUrl}/health did not report ok: true`);
    return { baseUrl, version: health.version, uptime_s: health.uptime_s };
  }),
);

const minersPayload = await fetchJson("https://rustchain.org/api/miners");
const miners = Array.isArray(minersPayload) ? minersPayload : minersPayload.miners;
assert(Array.isArray(miners), "/api/miners did not return a miners array");
assert(miners.length > 0, "/api/miners returned no miners");

const families = new Set(
  miners.map((miner) => miner.device_family || miner.hardware_type || miner.device_arch || "Unknown"),
);

const epoch = await fetchJson("https://rustchain.org/epoch");
assert(Number.isFinite(Number(epoch.epoch)), "/epoch missing numeric epoch");
assert(Number.isFinite(Number(epoch.slot)), "/epoch missing numeric slot");
assert(Number.isFinite(Number(epoch.blocks_per_epoch)), "/epoch missing numeric blocks_per_epoch");

console.log(
  JSON.stringify(
    {
      ok: true,
      checked_nodes: healthResults,
      miner_count: miners.length,
      architecture_groups: [...families].sort(),
      epoch: epoch.epoch,
      slot: epoch.slot,
      blocks_per_epoch: epoch.blocks_per_epoch,
    },
    null,
    2,
  ),
);
