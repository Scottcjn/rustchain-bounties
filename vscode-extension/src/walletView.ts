// SPDX-License-Identifier: MIT
/**
 * RustChain wallet dashboard view.
 *
 * Shows:
 * - Current RTC balance
 * - Miner status (active/enrolled)
 * - Recent transactions
 * - Quick actions (transfer, refresh, etc.)
 */

import * as vscode from "vscode";
import { fetchBalance, fetchHealth, fetchEpoch, fetchTransactions } from "./rustchainApi";

export class WalletViewProvider implements vscode.Disposable {
    private panel: vscode.WebviewPanel | undefined;
    private context: vscode.ExtensionContext;
    private refreshTimer: ReturnType<typeof setInterval> | undefined;
    private currentMinerId: string = "";

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.startAutoRefresh();
    }

    async show(): Promise<void> {
        const config = vscode.workspace.getConfiguration("rustchain");
        this.currentMinerId = config.get<string>("minerId", "");

        if (this.panel) {
            this.panel.reveal(vscode.ViewColumn.One, true);
        } else {
            this.panel = vscode.window.createWebviewPanel(
                "rustchain.walletView",
                "RustChain Wallet",
                vscode.ViewColumn.One,
                { retainContextWhenHidden: true },
            );
            this.panel.onDidDispose(() => {
                this.panel = undefined;
            });
        }

        await this.refresh();
        this.startAutoRefresh();
    }

    async refresh(): Promise<void> {
        if (!this.panel) { return; }

        const config = vscode.workspace.getConfiguration("rustchain");
        const useMock = config.get<boolean>("useMockApi", true);
        const minerId = config.get<string>("minerId", "");

        let balanceText = "Not configured";
        let healthText = "Unknown";
        let epochText = "Unknown";
        let txCount = 0;
        let txsText = "No transactions";

        try {
            const [balance, health, epoch, txs] = await Promise.all([
                minerId ? fetchBalance(minerId) : Promise.reject("No miner ID"),
                fetchHealth(),
                fetchEpoch(),
                minerId ? fetchTransactions(minerId) : Promise.resolve([]),
            ]);

            balanceText = `${balance.amount_rtc.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 6 })} RTC`;
            healthText = health.ok ? "✅ Healthy" : "❌ Unhealthy";
            epochText = `Epoch ${epoch.epoch}, Slot ${epoch.slot}`;
            txCount = txs.length;
            if (txs.length > 0) {
                const recent = txs.slice(0, 5);
                txsText = recent
                    .map((t) => {
                        const dir = t.to === minerId ? "↓" : "→";
                        const confirmed = t.confirmed ? "✅" : "⏳";
                        return `${confirmed} ${t.amount_rtc} RTC ${dir} ${t.from.slice(0, 12)}... (${t.tx_hash.slice(0, 8)}...)`;
                    })
                    .join("\n");
            }
        } catch {
            if (useMock) {
                balanceText = minerId ? "142.50 RTC (mock)" : "Not configured";
                healthText = "✅ Healthy (mock)";
                epochText = "Epoch 42, Slot 750 (mock)";
                txCount = 3;
                txsText = MOCK_TX_SAMPLE;
            }
        }

        this.panel.title = `RustChain Wallet — ${minerId || "Not configured"}`;
        this.panel.webview.html = this.buildHtml({
            minerId,
            balanceText,
            healthText,
            epochText,
            txCount,
            txsText,
            nodeUrl: config.get<string>("nodeUrl", "https://50.28.86.131"),
            isMock: useMock,
        });
    }

    private buildHtml(data: {
        minerId: string;
        balanceText: string;
        healthText: string;
        epochText: string;
        txCount: number;
        txsText: string;
        nodeUrl: string;
        isMock: boolean;
    }): string {
        const { minerId, balanceText, healthText, epochText, txCount, txsText, nodeUrl, isMock } = data;

        return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  :root {
    --bg: #1e1e1e;
    --surface: #252526;
    --border: #3c3c3c;
    --text: #cccccc;
    --accent: #f0b90b;
    --accent2: #e6a817;
    --green: #4caf50;
    --red: #f44336;
    --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
  body { background: var(--bg); color: var(--text); font-family: var(--font); margin: 0; padding: 16px; }
  h1 { color: var(--accent); font-size: 1.4em; margin: 0 0 16px; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 14px; margin-bottom: 12px; }
  .card-title { font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.08em; color: #888; margin: 0 0 8px; }
  .card-value { font-size: 1.3em; font-weight: 600; color: #fff; }
  .balance { font-size: 2em; color: var(--accent); }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
  .badge-ok { background: #1b3d1b; color: var(--green); }
  .badge-err { background: #3d1b1b; color: var(--red); }
  .badge-mock { background: #1b1b3d; color: #7ec8e3; }
  .txs { font-family: 'Consolas', monospace; font-size: 0.82em; white-space: pre-wrap; color: #aaa; line-height: 1.6; }
  .footer { font-size: 0.75em; color: #666; text-align: center; margin-top: 16px; }
  .btn { background: var(--accent); color: #000; border: none; border-radius: 4px; padding: 6px 14px; cursor: pointer; font-size: 0.9em; margin: 4px; }
  .btn:hover { background: var(--accent2); }
  .actions { margin-top: 12px; }
</style>
</head>
<body>
<h1>⛏️ RustChain Wallet</h1>

${isMock ? '<span class="badge badge-mock">🔧 Mock API Mode</span><br><br>' : ''}

<div class="grid">
  <div class="card">
    <div class="card-title">RTC Balance</div>
    <div class="card-value balance">${balanceText}</div>
  </div>
  <div class="card">
    <div class="card-title">Miner ID</div>
    <div class="card-value">${minerId || "— not set —"}</div>
  </div>
  <div class="card">
    <div class="card-title">Node Status</div>
    <div class="card-value">${healthText}</div>
  </div>
  <div class="card">
    <div class="card-title">Current Epoch</div>
    <div class="card-value">${epochText}</div>
  </div>
</div>

<div class="card">
  <div class="card-title">Recent Transactions (${txCount})</div>
  <div class="txs">${txsText}</div>
</div>

<div class="card">
  <div class="card-title">Node</div>
  <div style="font-size:0.85em; color:#888;">${nodeUrl}</div>
</div>

<div class="actions">
  <button class="btn" onclick="vscode.postMessage({cmd:'refresh'})">🔄 Refresh</button>
  <button class="btn" onclick="vscode.postMessage({cmd:'transfer'})">💸 Transfer</button>
  <button class="btn" onclick="vscode.postMessage({cmd:'listMiners'})">📋 List Miners</button>
  <button class="btn" onclick="vscode.postMessage({cmd:'claimBounty'})">🏆 Claim Bounty</button>
</div>

<div class="footer">
  RustChain VS Code Extension · Bounty #2868<br>
  Wallet: RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5
</div>

<script>
  const vscode = acquireVsCodeApi();
  document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.textContent.includes('Refresh') ? 'refresh' :
                   btn.textContent.includes('Transfer') ? 'transfer' :
                   btn.textContent.includes('List') ? 'listMiners' : 'claimBounty';
      vscode.postMessage({ cmd });
    });
  });
</script>
</body>
</html>`;
    }

    private startAutoRefresh(): void {
        this.stopAutoRefresh();
        const config = vscode.workspace.getConfiguration("rustchain");
        const intervalSec = config.get<number>("balanceRefreshInterval", 120);

        this.refreshTimer = setInterval(() => {
            this.refresh();
        }, intervalSec * 1000);
    }

    private stopAutoRefresh(): void {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = undefined;
        }
    }

    onConfigChange(): void {
        this.startAutoRefresh();
        this.refresh();
    }

    dispose(): void {
        this.stopAutoRefresh();
        this.panel?.dispose();
        this.panel = undefined;
    }
}

const MOCK_TX_SAMPLE = `✅ 25.0 RTC ↓ founder_community... (0xabc123...)
✅ 10.0 RTC ↓ founder_team_bou... (0xdef456...)
⏳ 5.0 RTC ↓ founder_dev_fund... (0xghi789...)`;
