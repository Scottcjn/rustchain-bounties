#!/usr/bin/env node
/**
 * examples/balance.js
 *
 * Looks up a RustChain wallet balance by name or address.
 * Usage:
 *   node examples/balance.js <wallet-name-or-address>
 *
 * Example:
 *   node examples/balance.js zxy0314-work
 */

import { RustChainClient, APIError, ConnectionError } from "../src/index.js";

const RTC_USD = 0.10;

async function main() {
  const wallet = process.argv[2];
  if (!wallet) {
    console.error("usage: node examples/balance.js <wallet-name-or-address>");
    process.exit(64);
  }

  const client = new RustChainClient();

  try {
    const result = await client.getBalance(wallet);
    const rtc = Number(result.balance ?? 0);
    const usd = (rtc * RTC_USD).toFixed(2);

    console.log(`Wallet:   ${wallet}`);
    console.log(`Balance:  ${rtc.toFixed(2)} RTC ($${usd} USD)`);
  } catch (err) {
    if (err instanceof APIError && err.status === 404) {
      console.error(`Wallet not found: ${wallet}`);
      process.exit(1);
    }
    if (err instanceof ConnectionError) {
      console.error("Error: Node unreachable — retry in 30s");
      process.exit(2);
    }
    console.error(`Error: ${err.message}`);
    process.exit(3);
  }
}

main();
