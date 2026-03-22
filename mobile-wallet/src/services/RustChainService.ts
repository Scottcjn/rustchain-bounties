// SPDX-License-Identifier: MIT
/**
 * RustChain API Service
 *
 * Client for the RustChain network API.
 * Default node: https://50.28.86.131
 */

export interface BalanceInfo {
  balance: number;
  pending: number;
  lastUpdated: string;
}

export interface TxInfo {
  id: string;
  type: "in" | "out";
  amount: number;
  timestamp: string;
  status: "confirmed" | "pending";
  from: string;
  to: string;
}

export interface TransferResult {
  txId: string;
  status: string;
}

export class RustChainService {
  private readonly baseUrl: string;
  private readonly wallet: string;
  private readonly apiKey: string;

  constructor(wallet: string, apiKey: string = "", nodeUrl: string = "https://50.28.86.131") {
    this.wallet = wallet;
    this.apiKey = apiKey;
    this.baseUrl = nodeUrl;
  }

  static fromWallet(wallet: string, apiKey: string = ""): RustChainService {
    return new RustChainService(wallet, apiKey);
  }

  private async fetch<T>(path: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (this.apiKey) headers["Authorization"] = `Bearer ${this.apiKey}`;
    const response = await fetch(url, { ...options, headers } as RequestInit);
    if (!response.ok) {
      const err = await response.text().catch(() => response.statusText);
      throw new Error(`RustChain API error ${response.status}: ${err}`);
    }
    const text = await response.text();
    if (!text) return {} as T;
    return JSON.parse(text) as T;
  }

  async getBalance(): Promise<BalanceInfo> {
    try {
      const data = await this.fetch<any>(`/wallet/balance?miner_id=${encodeURIComponent(this.wallet)}`);
      return { balance: data.balance ?? data.amount ?? 0, pending: data.pending ?? 0, lastUpdated: new Date().toISOString() };
    } catch {
      return { balance: 0, pending: 0, lastUpdated: new Date().toISOString() };
    }
  }

  async getTransactions(): Promise<TxInfo[]> {
    try {
      const data = await this.fetch<any[]>(`/wallet/transactions?miner_id=${encodeURIComponent(this.wallet)}`);
      return (data || []).map((tx: any) => ({
        id: tx.id || tx.tx_hash || "",
        type: tx.type === "receive" || tx.from !== this.wallet ? "in" : "out",
        amount: parseFloat(tx.amount || tx.value || "0"),
        timestamp: tx.timestamp || tx.time || new Date().toISOString(),
        status: tx.status === "confirmed" ? "confirmed" : "pending",
        from: tx.from || "",
        to: tx.to || "",
      }));
    } catch { return []; }
  }

  async transfer(to: string, amount: number, memo: string = ""): Promise<TransferResult> {
    if (!this.apiKey) throw new Error("Transfer requires EXPO_PUBLIC_RUSTCHAIN_API_KEY.");
    const data = await this.fetch<any>("/wallet/transfer", {
      method: "POST",
      body: JSON.stringify({ from: this.wallet, to, amount, memo }),
    });
    return { txId: data.tx_id || data.hash || data.id || "", status: data.status || "submitted" };
  }
}
