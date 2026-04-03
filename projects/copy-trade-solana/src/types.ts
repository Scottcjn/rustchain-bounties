import { PublicKey } from "@solana/web3.js";

/** Parsed trade event emitted by the listener */
export interface Trade {
  signature: string;
  from: string;
  to: string;
  /** Amount in lamports (SOL) or smallest token unit */
  amount: number;
  /** SPL token mint address — undefined for native SOL transfers */
  mint?: string;
}

/** Minimal config the bot needs at runtime */
export interface BotConfig {
  /** Solana JSON-RPC endpoint (e.g. devnet URL) */
  rpcUrl: string;
  /** Public key of the wallet we are copying */
  sourcePubkey: PublicKey;
  /** Path to the follower keypair JSON file — only needed for live mode */
  keypairPath?: string;
  /** When true, transactions are logged but never sent */
  dryRun: boolean;
}
