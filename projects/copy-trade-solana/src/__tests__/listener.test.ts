/**
 * Unit tests for TradeListener.parseTrade — uses mock RPC data so no
 * network connection is needed.
 */
import { PublicKey } from "@solana/web3.js";
import { TradeListener } from "../listener";
import { Trade } from "../types";

// ---- helpers to build mock parsed transactions ----

function mockParsedTx(instructions: any[]): any {
  return {
    transaction: {
      message: {
        instructions,
      },
    },
    meta: {},
  };
}

function solTransferIx(from: string, to: string, lamports: number) {
  return {
    programId: new PublicKey("11111111111111111111111111111111"),
    parsed: {
      type: "transfer",
      info: { source: from, destination: to, lamports },
    },
  };
}

function splTransferIx(authority: string, dest: string, amount: string, mint: string) {
  return {
    programId: new PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
    parsed: {
      type: "transfer",
      info: { authority, source: authority, destination: dest, amount, mint },
    },
  };
}

// ---- tests ----

describe("TradeListener.parseTrade", () => {
  const sig = "TestSig123";

  it("parses a native SOL transfer", () => {
    const from = "SourcePubkey111111111111111111111111111111111";
    const to = "DestPubkey1111111111111111111111111111111111";
    const lamports = 50_000_000; // 0.05 SOL

    const tx = mockParsedTx([solTransferIx(from, to, lamports)]);
    const trade = TradeListener.parseTrade(sig, tx);

    expect(trade).not.toBeNull();
    expect(trade!.signature).toBe(sig);
    expect(trade!.from).toBe(from);
    expect(trade!.to).toBe(to);
    expect(trade!.amount).toBe(lamports);
    expect(trade!.mint).toBeUndefined();
  });

  it("parses an SPL token transfer", () => {
    const authority = "Authority11111111111111111111111111111111111";
    const dest = "Dest111111111111111111111111111111111111111111";
    const amount = "1000000";
    const mint = "MintAddr1111111111111111111111111111111111111";

    const tx = mockParsedTx([splTransferIx(authority, dest, amount, mint)]);
    const trade = TradeListener.parseTrade(sig, tx);

    expect(trade).not.toBeNull();
    expect(trade!.amount).toBe(1_000_000);
    expect(trade!.mint).toBe(mint);
  });

  it("returns null when no transfer instruction is present", () => {
    const tx = mockParsedTx([
      { programId: new PublicKey("11111111111111111111111111111111"), parsed: { type: "createAccount", info: {} } },
    ]);
    expect(TradeListener.parseTrade(sig, tx)).toBeNull();
  });

  it("returns null for empty instructions", () => {
    const tx = mockParsedTx([]);
    expect(TradeListener.parseTrade(sig, tx)).toBeNull();
  });

  it("skips unparsed (compiled) instructions gracefully", () => {
    const tx = mockParsedTx([
      { programId: new PublicKey("11111111111111111111111111111111"), data: "base64stuff", accounts: [] },
    ]);
    expect(TradeListener.parseTrade(sig, tx)).toBeNull();
  });
});
