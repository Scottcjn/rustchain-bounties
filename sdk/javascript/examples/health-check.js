#!/usr/bin/env node
/**
 * examples/health-check.js
 *
 * Pings the real RustChain node and prints health / epoch / miner count.
 * Usage:
 *   node examples/health-check.js
 */

import { RustChainClient, ConnectionError, APIError } from "../src/index.js";

async function main() {
  const client = new RustChainClient();

  try {
    const [health, epoch, miners] = await Promise.all([
      client.health(),
      client.getEpoch(),
      client.getMiners(),
    ]);

    console.log("── RustChain status ──");
    console.log("ok:        ", health.ok);
    console.log("version:   ", health.version);
    console.log("uptime_s:  ", health.uptime_s);
    console.log("epoch:     ", epoch.epoch, "slot", epoch.slot);
    console.log("miners:    ", Array.isArray(miners) ? miners.length : "?");
  } catch (err) {
    if (err instanceof ConnectionError) {
      console.error("Node unreachable. Try again in 30s.");
      process.exit(2);
    }
    if (err instanceof APIError) {
      console.error(`API error ${err.status}: ${err.message}`);
      process.exit(3);
    }
    throw err;
  }
}

main();
