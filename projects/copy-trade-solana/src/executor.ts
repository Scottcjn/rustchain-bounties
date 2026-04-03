import {
  Connection,
  Keypair,
  Transaction,
  TransactionInstruction,
  sendAndConfirmTransaction,
  SystemProgram,
  PublicKey,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import { Trade } from "./types";

export interface ExecuteResult {
  success: boolean;
  signature?: string;
  error?: string;
  dryRun: boolean;
}

/**
 * Executor signs and submits copy-trade transactions.
 *
 * In dry-run mode it logs what *would* be sent but never touches the network.
 * In live mode it builds and sends a matching transaction from the follower
 * wallet.
 *
 * TODO (sprint-2):
 *  - Apply risk-limit checks (max per-trade, daily cap)
 *  - Support SPL token transfers (requires associated-token-account lookup)
 *  - Slippage / priority-fee configuration
 */
export class Executor {
  private connection: Connection;
  private keypair: Keypair;
  private dryRun: boolean;

  constructor(connection: Connection, keypair: Keypair, dryRun = true) {
    this.connection = connection;
    this.keypair = keypair;
    this.dryRun = dryRun;
  }

  /** Build and (optionally) send a transaction that mirrors the given trade */
  async executeTrade(trade: Trade): Promise<ExecuteResult> {
    // For now we only handle native SOL transfers.
    // SPL token mirroring will be added in sprint-2.
    if (trade.mint) {
      return {
        success: false,
        error: "SPL token copy-trade not yet implemented",
        dryRun: this.dryRun,
      };
    }

    const instruction = SystemProgram.transfer({
      fromPubkey: this.keypair.publicKey,
      toPubkey: new PublicKey(trade.to),
      lamports: trade.amount,
    });

    if (this.dryRun) {
      console.log(
        `[DRY-RUN] Would send ${trade.amount / LAMPORTS_PER_SOL} SOL → ${trade.to}`
      );
      return { success: true, dryRun: true };
    }

    // --- Live execution ---
    try {
      const tx = new Transaction().add(instruction);
      const sig = await sendAndConfirmTransaction(this.connection, tx, [
        this.keypair,
      ]);
      console.log(`[LIVE] Sent ${trade.amount / LAMPORTS_PER_SOL} SOL → ${trade.to} | sig: ${sig}`);
      return { success: true, signature: sig, dryRun: false };
    } catch (err: any) {
      console.error("[LIVE] Transaction failed:", err.message);
      return { success: false, error: err.message, dryRun: false };
    }
  }

  /** Build an instruction from a trade — useful for testing without sending */
  static buildInstruction(
    fromPubkey: PublicKey,
    trade: Trade
  ): TransactionInstruction {
    return SystemProgram.transfer({
      fromPubkey,
      toPubkey: new PublicKey(trade.to),
      lamports: trade.amount,
    });
  }
}
