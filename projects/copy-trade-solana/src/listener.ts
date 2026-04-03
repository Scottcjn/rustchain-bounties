import {
  Connection,
  PublicKey,
  ConfirmedSignatureInfo,
  ParsedTransactionWithMeta,
} from "@solana/web3.js";
import { EventEmitter } from "events";
import { Trade } from "./types";

/**
 * TradeListener watches a source wallet on Solana and emits parsed Trade
 * objects whenever a confirmed transaction is detected.
 *
 * Usage:
 *   const listener = new TradeListener(connection, sourcePubkey);
 *   listener.on("trade", (trade: Trade) => { ... });
 *   await listener.start();          // begins polling / subscription
 *   listener.stop();                 // teardown
 *
 * Implementation notes:
 *  - Uses onLogs subscription (devnet-compatible) to detect new signatures,
 *    then fetches the parsed transaction to extract transfer details.
 *  - Falls back to polling getSignaturesForAddress when WebSocket is unavailable.
 */
export class TradeListener extends EventEmitter {
  private connection: Connection;
  private source: PublicKey;
  private subscriptionId: number | null = null;
  private polling = false;
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private lastSignature: string | null = null;

  constructor(connection: Connection, sourcePubkey: PublicKey) {
    super();
    this.connection = connection;
    this.source = sourcePubkey;
  }

  /** Start listening via WebSocket log subscription */
  async start(): Promise<void> {
    try {
      this.subscriptionId = this.connection.onLogs(
        this.source,
        async (logInfo) => {
          if (logInfo.err) return;
          const trade = await this.fetchAndParse(logInfo.signature);
          if (trade) this.emit("trade", trade);
        },
        "confirmed"
      );
    } catch {
      // WebSocket unavailable — fall back to polling
      this.startPolling();
    }
  }

  /** Fallback: poll getSignaturesForAddress every 5 s */
  startPolling(intervalMs = 5000): void {
    if (this.polling) return;
    this.polling = true;
    this.pollTimer = setInterval(async () => {
      try {
        const sigs: ConfirmedSignatureInfo[] =
          await this.connection.getSignaturesForAddress(this.source, {
            limit: 10,
            until: this.lastSignature ?? undefined,
          });
        for (const sig of sigs.reverse()) {
          const trade = await this.fetchAndParse(sig.signature);
          if (trade) {
            this.lastSignature = sig.signature;
            this.emit("trade", trade);
          }
        }
      } catch (err) {
        this.emit("error", err);
      }
    }, intervalMs);
  }

  stop(): void {
    if (this.subscriptionId !== null) {
      this.connection.removeOnLogsListener(this.subscriptionId);
      this.subscriptionId = null;
    }
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
    this.polling = false;
  }

  // ---- parsing helpers (also used in tests) ----

  /**
   * Fetch a parsed transaction by signature and extract the first SOL
   * transfer (system program) or SPL token transfer.
   */
  async fetchAndParse(signature: string): Promise<Trade | null> {
    const tx: ParsedTransactionWithMeta | null =
      await this.connection.getParsedTransaction(signature, {
        commitment: "confirmed",
        maxSupportedTransactionVersion: 0,
      });
    if (!tx) return null;
    return TradeListener.parseTrade(signature, tx);
  }

  /**
   * Pure function: extract a Trade from a ParsedTransactionWithMeta.
   * Exported as static so unit tests can call it without an RPC connection.
   */
  static parseTrade(
    signature: string,
    tx: ParsedTransactionWithMeta
  ): Trade | null {
    const instructions = tx.transaction.message.instructions;
    for (const ix of instructions) {
      // Parsed instructions have a `parsed` field
      if (!("parsed" in ix)) continue;
      const parsed = (ix as any).parsed;
      const programId = (ix as any).programId?.toBase58?.() ?? (ix as any).programId;

      // Native SOL transfer (System Program)
      if (
        programId === "11111111111111111111111111111111" &&
        parsed?.type === "transfer"
      ) {
        return {
          signature,
          from: parsed.info.source,
          to: parsed.info.destination,
          amount: parsed.info.lamports,
        };
      }

      // SPL Token transfer
      if (
        programId === "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA" &&
        (parsed?.type === "transfer" || parsed?.type === "transferChecked")
      ) {
        return {
          signature,
          from: parsed.info.source ?? parsed.info.authority,
          to: parsed.info.destination,
          amount: Number(parsed.info.amount ?? parsed.info.tokenAmount?.amount),
          mint: parsed.info.mint,
        };
      }
    }
    return null;
  }
}
