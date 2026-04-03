#!/usr/bin/env ts-node
import { Connection, Keypair, PublicKey, LAMPORTS_PER_SOL } from "@solana/web3.js";
import * as fs from "fs";
import * as path from "path";
import { config as loadEnv } from "dotenv";
import { TradeListener } from "./listener";
import { Executor } from "./executor";
import { Trade } from "./types";

loadEnv(); // reads .env from project root

// ---- helpers ----

function env(key: string, fallback?: string): string {
  const v = process.env[key] ?? fallback;
  if (!v) {
    console.error(`Missing env var: ${key}`);
    process.exit(1);
  }
  return v;
}

function loadKeypair(p: string): Keypair {
  const raw = JSON.parse(fs.readFileSync(path.resolve(p), "utf-8"));
  return Keypair.fromSecretKey(Uint8Array.from(raw));
}

// ---- CLI ----

const [, , command] = process.argv;

async function demo() {
  console.log("=== Copy-Trade Bot — DEMO (dry-run) ===\n");

  const rpcUrl = env("RPC_URL", "https://api.devnet.solana.com");
  // Use a well-known devnet address as a demonstration source
  const sourcePubkey = new PublicKey(
    env("SOURCE_PUBKEY", "11111111111111111111111111111111")
  );

  const connection = new Connection(rpcUrl, "confirmed");
  const dummyKeypair = Keypair.generate(); // throwaway for demo

  const listener = new TradeListener(connection, sourcePubkey);
  const executor = new Executor(connection, dummyKeypair, /* dryRun */ true);

  // Simulate a trade event to prove the pipeline works end-to-end
  const fakeTrade: Trade = {
    signature: "DEMO_SIG_" + Date.now(),
    from: sourcePubkey.toBase58(),
    to: Keypair.generate().publicKey.toBase58(),
    amount: 0.05 * LAMPORTS_PER_SOL,
  };

  console.log("Simulated trade detected:");
  console.log(JSON.stringify(fakeTrade, null, 2));
  console.log();

  const result = await executor.executeTrade(fakeTrade);
  console.log("Executor result:", result);
  console.log("\nDemo complete. Use 'start' command with real keys for live mode.");
}

async function start() {
  console.log("=== Copy-Trade Bot — LIVE ===\n");

  const rpcUrl = env("RPC_URL");
  const sourcePubkey = new PublicKey(env("SOURCE_PUBKEY"));
  const keypairPath = env("KEYPAIR_PATH"); // path to follower wallet JSON

  const connection = new Connection(rpcUrl, "confirmed");
  const keypair = loadKeypair(keypairPath);

  console.log(`RPC:    ${rpcUrl}`);
  console.log(`Source: ${sourcePubkey.toBase58()}`);
  console.log(`Wallet: ${keypair.publicKey.toBase58()}\n`);

  const listener = new TradeListener(connection, sourcePubkey);
  const executor = new Executor(connection, keypair, /* dryRun */ false);

  listener.on("trade", async (trade: Trade) => {
    console.log(`\n[TRADE] ${trade.signature}`);
    console.log(`  ${trade.from} → ${trade.to}  amount=${trade.amount}${trade.mint ? `  mint=${trade.mint}` : ""}`);
    const result = await executor.executeTrade(trade);
    console.log(`  result: ${JSON.stringify(result)}`);
  });

  listener.on("error", (err: Error) => {
    console.error("[LISTENER ERROR]", err.message);
  });

  await listener.start();
  console.log("Listening for trades… (Ctrl-C to stop)");

  // Graceful shutdown
  process.on("SIGINT", () => {
    console.log("\nStopping…");
    listener.stop();
    process.exit(0);
  });
}

// ---- dispatch ----

(async () => {
  switch (command) {
    case "demo":
      await demo();
      break;
    case "start":
      await start();
      break;
    default:
      console.log("Usage: ts-node src/index.ts <demo|start>");
      console.log("  demo        — dry-run with simulated trade (no keys needed)");
      console.log("  start       — live mode (requires .env with RPC_URL, SOURCE_PUBKEY, KEYPAIR_PATH)");
      console.log("\nSee also: npm run demo:devnet — sprint-2 end-to-end devnet demo");
      process.exit(1);
  }
})();
