// SPDX-License-Identifier: MIT
/**
 * RustChain VS Code Extension — Full Dashboard
 * Features: Wallet Balance | Miner Status | Epoch Timer | Bounty Browser
 * Bounty: #2868
 */

import * as vscode from "vscode";
import * as https from "https";

const CONFIG_KEY = "rustchain";
const NODE_URL = "https://50.28.86.131";
const EPOCH_LENGTH = 2016;
const SLOT_TIME_S = 15;

// ── API ────────────────────────────────────────────────────────────────────
interface NodeHealth { ok: boolean; version: string; uptime_s: number; }
interface WalletBalance { amount_rtc: number; miner_id: string; }
interface Miner { miner: string; is_active: boolean; antiquity_multiplier: number; hardware_type: string; }
interface BountyIssue { number: number; title: string; body: string; labels: { name: string }[]; state: string; }

async function apiGet<T>(path: string): Promise<T | null> {
  return new Promise(resolve => {
    const req = https.get({
      hostname: "50.28.86.131", port: 443, path,
      headers: { "Accept": "application/json" }
    }, res => {
      let d = ""; res.on("data", c => d += c);
      res.on("end", () => { try { resolve(JSON.parse(d)); } catch { resolve(null); } });
    });
    req.on("error", () => resolve(null));
    req.setTimeout(8000, () => { req.destroy(); resolve(null); });
    req.end();
  });
}

async function ghGet<T>(path: string): Promise<T | null> {
  return new Promise(resolve => {
    const req = https.get({
      hostname: "api.github.com", port: 443, path,
      headers: { "User-Agent": "RustChain-VSCode/1.0", "Accept": "application/json" }
    }, res => {
      let d = ""; res.on("data", c => d += c);
      res.on("end", () => { try { resolve(JSON.parse(d)); } catch { resolve(null); } });
    });
    req.on("error", () => resolve(null));
    req.setTimeout(8000, () => { req.destroy(); resolve(null); });
    req.end();
  });
}

// ── Status Bar Items ──────────────────────────────────────────────────────
const balanceItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
const minerItem   = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 99);
const epochItem   = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 98);
balanceItem.text  = "⏳ RTC...";
minerItem.text    = "⚙️ --";
epochItem.text    = "📅 E:--";

function formatCountdown(slots: number): string {
  const secs = slots * SLOT_TIME_S;
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  const s = secs % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

async function refreshBalance() {
  const wallet = vscode.workspace.getConfiguration(CONFIG_KEY).get<string>("minerId", "");
  if (!wallet) { balanceItem.text = "⚠️ Set wallet"; return; }
  const data = await apiGet<WalletBalance>(`/wallet/balance?wallet_id=${encodeURIComponent(wallet)}`);
  balanceItem.text = data ? `💰 ${data.amount_rtc.toFixed(4)} RTC` : "❌ Balance error";
}

async function refreshMiner() {
  const wallet = vscode.workspace.getConfiguration(CONFIG_KEY).get<string>("minerId", "");
  if (!wallet) { minerItem.text = "⚙️ --"; return; }
  const data = await apiGet<{ miners: Miner[] }>("/api/miners");
  const miner = data?.miners.find(m => m.miner === wallet);
  if (data && miner) {
    minerItem.text = miner.is_active ? "🟢 Miner active" : "🔴 Miner offline";
    minerItem.tooltip = `${wallet}\n${miner.is_active ? "Attesting correctly" : "Not attesting!"}\nAntiquity: ×${miner.antiquity_multiplier.toFixed(3)}`;
  } else {
    minerItem.text = "🔴 Miner offline";
  }
}

async function refreshEpoch() {
  const health = await apiGet<NodeHealth>("/health");
  if (health) {
    const slotsElapsed = Math.floor(health.uptime_s / SLOT_TIME_S);
    const epoch = Math.floor(slotsElapsed / EPOCH_LENGTH);
    const slotInEpoch = slotsElapsed % EPOCH_LENGTH;
    const remaining = EPOCH_LENGTH - slotInEpoch;
    epochItem.text = `📅 E${epoch} ${formatCountdown(remaining)}`;
  }
}

// ── Bounty Sidebar Webview ────────────────────────────────────────────────
export class BountySidebarProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = "rustchain.bountySidebar";
  private view?: vscode.WebviewView;

  resolveWebviewView(view: vscode.WebviewView) {
    this.view = view;
    view.webview.options = { enableScripts: true };
    this.load();
    view.webview.onDidReceiveMessage(msg => {
      if (msg.type === "refresh") this.load();
      if (msg.type === "open") vscode.commands.executeCommand("vscode.open", vscode.Uri.parse(`https://github.com/Scottcjn/rustchain-bounties/issues/${msg.number}`));
      if (msg.type === "createPR") vscode.commands.executeCommand("vscode.open", vscode.Uri.parse(`https://github.com/Scottcjn/rustchain-bounties/pull/new/main`));
    });
  }

  async load() {
    if (!this.view) return;
    const bounties = await ghGet<BountyIssue[]>(`/repos/Scottcjn/rustchain-bounties/issues?state=open&labels=bounty&per_page=20`);
    this.view.webview.html = this.html(bounties || []);
  }

  html(bounties: BountyIssue[]): string {
    const items = bounties.map(b => {
      const reward = b.title.match(/(\d+)\s*RTC/i);
      const rewardText = reward ? `${reward[1]} RTC` : "Bounty";
      const desc = (b.body || "").slice(0, 120).replace(/[#*`\n]/g, " ").trim();
      return `<div class="b">
        <div class="t">#${b.number} ${b.title.replace(/\[BOUNTY.*?\]/i, "").trim()}</div>
        <div class="r">💰 ${rewardText}</div>
        <div class="d">${desc}...</div>
        <button onclick="open(${b.number})">Open Issue</button>
        <button onclick="pr(${b.number})">Create PR</button>
      </div>`;
    }).join("") || "<p style='color:#888;text-align:center;padding:20px'>No open bounties</p>";

    return `<!DOCTYPE html><html><head>
    <meta charset="utf-8"><style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;padding:8px;background:transparent;color:#ccc}
    h2{font-size:14px;color:#e0e0e0;margin-bottom:8px;padding:4px 0}
    .b{background:#1e1e1e;border-radius:6px;padding:10px;margin-bottom:8px;border:1px solid #333}
    .t{font-weight:600;color:#4fc3f7;font-size:12px;margin-bottom:4px;word-break:break-word}
    .r{display:inline-block;background:#1b5e20;color:#a5d6a7;padding:1px 6px;border-radius:3px;font-size:11px;font-weight:700;margin-bottom:6px}
    .d{color:#9e9e9e;font-size:11px;line-height:1.4;margin-bottom:8px}
    button{background:#0d47a1;color:white;padding:3px 8px;border-radius:4px;border:none;font-size:11px;cursor:pointer;margin-right:4px}
    button:hover{background:#1565c0}
    .refresh{background:#1e1e1e;border:1px solid #444;color:#aaa;padding:5px 10px;border-radius:4px;font-size:11px;cursor:pointer;width:100%;margin-bottom:8px}
    .refresh:hover{background:#2a2a2a}
    </style></head><body>
    <button class="refresh" onclick="refresh()">🔄 Refresh Bounties</button>
    <h2>💰 Open Bounties (${bounties.length})</h2>
    ${items}
    <script>
    const vscode=acquireVsCodeApi();
    function refresh(){vscode.postMessage({type:'refresh'})}
    function open(n){vscode.postMessage({type:'open',number:n})}
    function pr(n){vscode.postMessage({type:'createPR',number:n})}
    </script>
    </body></html>`;
  }
}

// ── Activate ──────────────────────────────────────────────────────────────
let bountyProvider: BountySidebarProvider;
let refreshIntervals: NodeJS.Timeout[] = [];

export function activate(ctx: vscode.ExtensionContext) {
  // Register sidebar
  bountyProvider = new BountySidebarProvider(ctx);
  ctx.subscriptions.push(
    vscode.window.registerWebviewViewProvider(BountySidebarProvider.viewType, bountyProvider)
  );

  // Show status bars
  balanceItem.show(); minerItem.show(); epochItem.show();

  // Commands
  vscode.commands.registerCommand("rustchain.setWallet", async () => {
    const w = await vscode.window.showInputBox({ prompt: "Wallet/miner ID:", placeHolder: "e.g. my-miner" });
    if (w !== undefined) {
      await vscode.workspace.getConfiguration(CONFIG_KEY).update("minerId", w, true);
      refreshAll();
    }
  });
  vscode.commands.registerCommand("rustchain.refreshAll", refreshAll);
  vscode.commands.registerCommand("rustchain.checkBalance", async () => {
    await refreshBalance();
    const wallet = vscode.workspace.getConfiguration(CONFIG_KEY).get<string>("minerId","");
    const data = await apiGet<WalletBalance>(`/wallet/balance?wallet_id=${encodeURIComponent(wallet)}`);
    if (data) vscode.window.showInformationMessage(`💰 ${data.amount_rtc.toFixed(4)} RTC`);
  });
  vscode.commands.registerCommand("rustchain.openBounty", async (n?: number) => {
    if (!n) { const s = await vscode.window.showInputBox({prompt:"Issue number:"}); if (s) n=parseInt(s); }
    if (n) vscode.commands.executeCommand("vscode.open", vscode.Uri.parse(`https://github.com/Scottcjn/rustchain-bounties/issues/${n}`));
  });
  vscode.commands.registerCommand("rustchain.createBountyPR", () => {
    vscode.commands.executeCommand("vscode.open", vscode.Uri.parse("https://github.com/Scottcjn/rustchain-bounties/pull/new/main"));
  });

  // Config change handler
  ctx.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
    if (e.affectsConfiguration(CONFIG_KEY)) { stopRefresh(); startRefresh(); refreshAll(); }
  }));

  startRefresh();
  refreshAll();
}

function startRefresh() {
  const ival = (vscode.workspace.getConfiguration(CONFIG_KEY).get<number>("balanceRefreshInterval", 120) || 120) * 1000;
  refreshIntervals.push(setInterval(refreshBalance, ival));
  refreshIntervals.push(setInterval(refreshMiner, 30000));
  refreshIntervals.push(setInterval(refreshEpoch, 15000));
}

function stopRefresh() { refreshIntervals.forEach(i => clearInterval(i)); refreshIntervals = []; }

async function refreshAll() {
  await Promise.all([refreshBalance(), refreshMiner(), refreshEpoch()]);
}

export function deactivate() { stopRefresh(); }
