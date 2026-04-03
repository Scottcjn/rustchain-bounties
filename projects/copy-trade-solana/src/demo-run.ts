#!/usr/bin/env ts-node
/**
 * Sprint-2 end-to-end devnet demo.
 *
 * Creates 3 ephemeral follower keypairs, airdrops SOL, simulates 3 source
 * trades, mirrors them via the Executor (obeying policy), waits for
 * confirmations, and appends explorer URLs to PROOFS.md.
 *
 * Falls back to dry-run if airdrop / network calls fail.
 */
import {
  Connection,
  Keypair,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import * as fs from "fs";
import * as path from "path";
import { config as loadEnv } from "dotenv";
import { Executor } from "./executor";
import { Trade } from "./types";
import { DEFAULT_POLICY } from "./policy";

loadEnv();

const RPC_URL = process.env.RPC_URL || "https://api.devnet.solana.com";
const NUM_FOLLOWERS = 3;
const AIRDROP_LAMPORTS = LAMPORTS_PER_SOL; // 1 SOL each
const TRADE_AMOUNT_LAMPORTS = 10_000_000; // 0.01 SOL per trade
const PROOFS_PATH = path.resolve(__dirname, "..", "PROOFS.md");

interface DemoResult {
  follower: string;
  tradeIndex: number;
  signature?: string;
  explorerUrl?: string;
  dryRun: boolean;
  error?: string;
}

async function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function run() {
  console.log("=== Copy-Trade Sprint-2 — Devnet Demo ===\n");
  console.log(`RPC: ${RPC_URL}`);
  console.log(`Policy: minTrade=${DEFAULT_POLICY.minTradeLamports} maxPerWallet=${DEFAULT_POLICY.maxPerWalletLamports} slippage=${DEFAULT_POLICY.slippagePct}%\n`);

  const connection = new Connection(RPC_URL, "confirmed");
  let liveMode = true;

  // --- Create 3 ephemeral follower keypairs ---
  const followers: Keypair[] = [];
  for (let i = 0; i < NUM_FOLLOWERS; i++) {
    const kp = process.env[`KEYPAIR_PATH_${i + 1}`]
      ? Executor.loadOrGenerateKeypair(process.env[`KEYPAIR_PATH_${i + 1}`])
      : Keypair.generate();
    followers.push(kp);
    console.log(`Follower ${i + 1}: ${kp.publicKey.toBase58()}`);
  }

  // --- Airdrop SOL to each follower ---
  console.log("\n--- Airdrop phase ---");
  for (const kp of followers) {
    const exec = new Executor(connection, kp, false);
    const ok = await exec.fundFromAirdrop(AIRDROP_LAMPORTS);
    if (!ok) {
      console.warn("Airdrop failed — falling back to dry-run mode for all trades.");
      liveMode = false;
      break;
    }
    // Small delay between airdrops to avoid rate limiting
    await sleep(1500);
  }

  // --- Simulate 3 source trades ---
  const sourcePubkey = Keypair.generate().publicKey.toBase58();
  const trades: Trade[] = [];
  for (let i = 0; i < NUM_FOLLOWERS; i++) {
    trades.push({
      signature: `SRC_TRADE_${i + 1}_${Date.now()}`,
      from: sourcePubkey,
      to: Keypair.generate().publicKey.toBase58(), // random destination
      amount: TRADE_AMOUNT_LAMPORTS,
    });
  }

  console.log("\n--- Execution phase ---");
  const results: DemoResult[] = [];

  for (let i = 0; i < NUM_FOLLOWERS; i++) {
    const trade = trades[i];
    const follower = followers[i];
    const executor = new Executor(connection, follower, !liveMode, DEFAULT_POLICY);

    console.log(`\nTrade ${i + 1}: ${trade.amount / LAMPORTS_PER_SOL} SOL → ${trade.to.slice(0, 8)}…`);
    const res = await executor.executeTrade(trade);

    const demoResult: DemoResult = {
      follower: follower.publicKey.toBase58(),
      tradeIndex: i + 1,
      dryRun: res.dryRun,
    };

    if (res.success && res.signature) {
      demoResult.signature = res.signature;
      demoResult.explorerUrl = `https://explorer.solana.com/tx/${res.signature}?cluster=devnet`;
      console.log(`  ✓ ${demoResult.explorerUrl}`);
    } else if (res.success && res.dryRun) {
      console.log(`  ✓ [dry-run] would have sent`);
    } else {
      demoResult.error = res.error;
      console.log(`  ✗ Error: ${res.error}`);
    }

    results.push(demoResult);
  }

  // --- Write results to PROOFS.md ---
  console.log("\n--- Writing to PROOFS.md ---");
  const timestamp = new Date().toISOString();
  let proofLines = `\n## Sprint-2 Demo — ${timestamp}\n\n`;
  proofLines += `Mode: ${liveMode ? "LIVE (devnet)" : "DRY-RUN (network unavailable)"}\n`;
  proofLines += `RPC: ${RPC_URL}\n\n`;

  for (const r of results) {
    if (r.explorerUrl) {
      proofLines += `- **Trade ${r.tradeIndex}** (follower \`${r.follower.slice(0, 8)}…\`): [${r.signature!.slice(0, 16)}…](${r.explorerUrl})\n`;
    } else if (r.dryRun) {
      proofLines += `- **Trade ${r.tradeIndex}** (follower \`${r.follower.slice(0, 8)}…\`): DRY-RUN — policy passed, tx simulated\n`;
    } else {
      proofLines += `- **Trade ${r.tradeIndex}** (follower \`${r.follower.slice(0, 8)}…\`): FAILED — ${r.error}\n`;
    }
  }

  if (!liveMode) {
    proofLines += `\n> Note: Airdrop/network calls failed; results are dry-run simulations.\n`;
  }

  const existing = fs.readFileSync(PROOFS_PATH, "utf-8");
  fs.writeFileSync(PROOFS_PATH, existing + proofLines);
  console.log("PROOFS.md updated.");

  console.log("\n=== Demo complete ===");
}

run().catch((err) => {
  console.error("Demo failed:", err);
  process.exit(1);
});
