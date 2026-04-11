// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — Bounty Browser
 *
 * A Webview panel that lets users browse open bounties from the
 * rustchain-bounties GitHub repository, filter by reward tier,
 * and jump directly to the issue on GitHub.
 */

import * as vscode from "vscode";
import * as https from "https";

interface BountyIssue {
    number: number;
    title: string;
    state: string;
    html_url: string;
    labels: { name: string; color: string }[];
    body: string;
}

interface GitHubSearchResponse {
    total_count: number;
    items: BountyIssue[];
}

export class BountyBrowserPanel {
    public static readonly viewType = "rustchain.bountyBrowser";

    private readonly panel: vscode.WebviewPanel;
    private readonly context: vscode.ExtensionContext;
    private bounties: BountyIssue[] = [];
    private currentFilter: string = "all";

    constructor(context: vscode.ExtensionContext) {
        this.context = context;

        this.panel = vscode.window.createWebviewPanel(
            BountyBrowserPanel.viewType,
            "RustChain Bounties",
            { viewColumn: vscode.ViewColumn.One, preserveFocus: true },
            { enableScripts: true, retainContextWhenHidden: true },
        );

        this.panel.webview.onDidReceiveMessage(async (message) => {
            if (message.type === "filter") {
                this.currentFilter = message.value;
                await this.loadBounties();
                this.refreshWebview();
            } else if (message.type === "openUrl") {
                vscode.env.openExternal(vscode.Uri.parse(message.url));
            } else if (message.type === "refresh") {
                await this.loadBounties();
                this.refreshWebview();
            }
        });

        this.panel.onDidDispose(() => {
            // no-op, panel is disposed automatically
        });

        this.loadBounties().then(() => this.refreshWebview());
    }

    private async loadBounties(): Promise<void> {
        try {
            const data = await this.githubSearch();
            this.bounties = data.items;
        } catch {
            this.bounties = [];
        }
    }

    private async githubSearch(): Promise<GitHubSearchResponse> {
        const query = encodeURIComponent("repo:Scottcjn/rustchain-bounties is:issue is:open label:bounty");
        const url = `https://api.github.com/search/issues?q=${query}&per_page=50`;

        return new Promise((resolve, reject) => {
            const req = https.get(url, {
                headers: {
                    "User-Agent": "RustChain-VSCode-Extension/1.0",
                    "Accept": "application/vnd.github+json",
                },
                timeout: 15_000,
            }, (res) => {
                if (res.statusCode === 403) {
                    reject(new Error("GitHub API rate limit exceeded. Try again later."));
                    return;
                }
                if (res.statusCode !== 200) {
                    reject(new Error(`GitHub API error: ${res.statusCode}`));
                    return;
                }
                const chunks: Buffer[] = [];
                res.on("data", (c: Buffer) => chunks.push(c));
                res.on("end", () => {
                    try {
                        resolve(JSON.parse(Buffer.concat(chunks).toString("utf-8")) as GitHubSearchResponse);
                    } catch {
                        reject(new Error("Failed to parse GitHub response"));
                    }
                });
            });
            req.on("error", reject);
            req.on("timeout", () => { req.destroy(); reject(new Error("Request timeout")); });
        });
    }

    private filteredBounties(): BountyIssue[] {
        if (this.currentFilter === "all") { return this.bounties; }
        return this.bounties.filter((b) =>
            b.labels.some((l) => l.name.toLowerCase().includes(this.currentFilter)),
        );
    }

    private bountyTier(label: { name: string }): string {
        const name = label.name.toLowerCase();
        if (name.includes("critical") || name.includes("bounty-s") || name.includes("major")) { return "critical"; }
        if (name.includes("standard") || name.includes("bounty-m")) { return "standard"; }
        if (name.includes("easy") || name.includes("bounty-l")) { return "easy"; }
        return "standard";
    }

    private tierColor(tier: string): string {
        switch (tier) {
            case "critical": return "#B60205";
            case "standard": return "#D4C5F9";
            case "easy": return "#0E8A16";
            default: return "#768390";
        }
    }

    private extractReward(title: string): string {
        const match = title.match(/(\d+)\s*RTC/);
        return match ? `${match[1]} RTC` : "";
    }

    private renderCard(bounty: BountyIssue): string {
        const reward = this.extractReward(bounty.title);
        const tierLabel = bounty.labels.find((l) =>
            ["critical", "standard", "easy"].some((t) => l.name.toLowerCase().includes(t)),
        );
        const tier = this.tierTier(tierLabel);
        const tierColor = this.tierColor(tier);
        const tierName = tier.charAt(0).toUpperCase() + tier.slice(1);

        const labelBadges = bounty.labels
            .filter((l) => !["bounty", "help wanted", "good first issue"].includes(l.name.toLowerCase()))
            .slice(0, 4)
            .map((l) => `<span class="badge" style="background:#${l.color}20;color:#${l.color};border:1px solid #${l.color}50">${l.name}</span>`)
            .join("");

        return `
        <div class="bounty-card" onclick="openUrl('${bounty.html_url}')">
            <div class="card-header">
                <span class="bounty-number">#${bounty.number}</span>
                <span class="tier-badge" style="background:${tierColor}20;color:${tierColor};border:1px solid ${tierColor}50">
                    ${tierName}
                </span>
                ${reward ? `<span class="reward-badge">💰 ${reward}</span>` : ""}
            </div>
            <div class="card-title">${this.escapeHtml(bounty.title.replace(/^\[BOUNTY[^\]]*\]\s*/, ""))}</div>
            <div class="card-labels">${labelBadges}</div>
        </div>`;
    }

    private tierTier(label?: { name: string }): string {
        if (!label) { return "standard"; }
        const name = label.name.toLowerCase();
        if (name.includes("critical") || name.includes("major")) { return "critical"; }
        if (name.includes("easy") || name.includes("bounty-l")) { return "easy"; }
        return "standard";
    }

    private escapeHtml(text: string): string {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    private refreshWebview(): void {
        const filtered = this.filteredBounties();
        const cards = filtered.map((b) => this.renderCard(b)).join("");

        this.panel.webview.html = this.getHtml(cards);
    }

    private getHtml(cards: string): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RustChain Bounties</title>
<style>
  body { font-family: var(--vscode-font-family); background: var(--vscode-editor-background); color: var(--vscode-editor-foreground); margin: 0; padding: 16px; }
  .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
  h1 { font-size: 16px; margin: 0; }
  .refresh-btn { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; }
  .refresh-btn:hover { background: var(--vscode-button-hoverBackground); }
  .filters { display: flex; gap: 6px; margin-bottom: 16px; flex-wrap: wrap; }
  .filter-btn { background: var(--vscode-badge-background); color: var(--vscode-badge-foreground); border: none; padding: 4px 10px; border-radius: 12px; cursor: pointer; font-size: 11px; }
  .filter-btn.active { background: #0E8A16; color: white; }
  .bounty-card { background: var(--vscode-editorWidget-background); border: 1px solid var(--vscode-widget-border, #454545); border-radius: 6px; padding: 12px; margin-bottom: 10px; cursor: pointer; transition: border-color 0.15s; }
  .bounty-card:hover { border-color: var(--vscode-focusBorder, #0E8A16); }
  .card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
  .bounty-number { font-size: 11px; color: var(--vscode-descriptionForeground); }
  .tier-badge { font-size: 10px; padding: 2px 6px; border-radius: 8px; font-weight: 600; }
  .reward-badge { font-size: 11px; margin-left: auto; }
  .card-title { font-size: 13px; font-weight: 500; margin-bottom: 6px; line-height: 1.4; }
  .card-labels { display: flex; gap: 4px; flex-wrap: wrap; }
  .badge { font-size: 10px; padding: 2px 6px; border-radius: 8px; }
  .empty { text-align: center; color: var(--vscode-descriptionForeground); padding: 40px; font-size: 13px; }
</style>
</head>
<body>
  <div class="header">
    <h1>💰 RustChain Bounties</h1>
    <button class="refresh-btn" onclick="sendMsg({type:'refresh'})">🔄 Refresh</button>
  </div>
  <div class="filters">
    <button class="filter-btn ${this.currentFilter === "all" ? "active" : ""}" onclick="sendMsg({type:'filter',value:'all'})">All</button>
    <button class="filter-btn ${this.currentFilter === "critical" ? "active" : ""}" onclick="sendMsg({type:'filter',value:'critical'})">🔥 Critical</button>
    <button class="filter-btn ${this.currentFilter === "standard" ? "active" : ""}" onclick="sendMsg({type:'filter',value:'standard'})">📋 Standard</button>
    <button class="filter-btn ${this.currentFilter === "easy" ? "active" : ""}" onclick="sendMsg({type:'filter',value:'easy'})">✅ Easy</button>
    <button class="filter-btn ${this.currentFilter === "good first issue" ? "active" : ""}" onclick="sendMsg({type:'filter',value:'good first issue'})">🌱 Good First Issue</button>
    <button class="filter-btn ${this.currentFilter === "integration" ? "active" : ""}" onclick="sendMsg({type:'filter',value:'integration'})">🔌 Integration</button>
  </div>
  ${cards || '<div class="empty">No bounties found. Click Refresh to try again.</div>'}
  <script>
    const vscode = acquireVsCodeApi();
    function sendMsg(msg) { vscode.postMessage(msg); }
    function openUrl(url) { sendMsg({type:'openUrl',url}); }
  </script>
</body>
</html>`;
    }
}
