// SPDX-License-Identifier: MIT
/**
 * Bounty Browser — a VS Code WebviewPanel that lists open RustChain bounties
 * fetched from the GitHub Issues API.
 *
 * Opening: via the "RustChain: Browse Bounties" command.
 * Clicking a bounty opens the GitHub issue in the default browser.
 * "Claim Bounty" button opens the PR template for the selected issue.
 */

import * as vscode from "vscode";
import { fetchBounties, GitHubIssue } from "./rustchainApi";

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

export function escapeHtml(s: string): string {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

export class BountyBrowserPanel {
    public static currentPanel: BountyBrowserPanel | undefined;
    private static readonly viewType = "rustchainBounties";

    private readonly panel: vscode.WebviewPanel;
    private readonly disposables: vscode.Disposable[] = [];

    // -------------------------------------------------------------------------
    // Public factory
    // -------------------------------------------------------------------------

    public static createOrShow(extensionUri: vscode.Uri): void {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (BountyBrowserPanel.currentPanel) {
            BountyBrowserPanel.currentPanel.panel.reveal(column);
            BountyBrowserPanel.currentPanel.refresh();
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            BountyBrowserPanel.viewType,
            "RustChain Bounties",
            column ?? vscode.ViewColumn.One,
            { enableScripts: true },
        );

        BountyBrowserPanel.currentPanel = new BountyBrowserPanel(panel);
    }

    // -------------------------------------------------------------------------
    // Constructor
    // -------------------------------------------------------------------------

    private constructor(panel: vscode.WebviewPanel) {
        this.panel = panel;
        this.panel.webview.html = this.loadingHtml();

        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);

        this.panel.webview.onDidReceiveMessage(
            (message: { command: string; issueNumber?: number; issueUrl?: string }) => {
                if (message.command === "openIssue" && message.issueUrl) {
                    void vscode.env.openExternal(vscode.Uri.parse(message.issueUrl));
                } else if (message.command === "claimBounty" && message.issueNumber) {
                    const prUrl = `https://github.com/Scottcjn/rustchain-bounties/compare/main...main?` +
                        `quick_pull=1&template=PULL_REQUEST_TEMPLATE.md&title=` +
                        encodeURIComponent(`[BOUNTY #${message.issueNumber}] Your solution title`) +
                        `&body=` +
                        encodeURIComponent(`## Bounty Claim\n- Issue number: #${message.issueNumber}\n- Wallet ID: \n\n## Description\n`);
                    void vscode.env.openExternal(vscode.Uri.parse(prUrl));
                } else if (message.command === "refresh") {
                    this.refresh();
                }
            },
            null,
            this.disposables,
        );

        this.refresh();
    }

    // -------------------------------------------------------------------------
    // Refresh
    // -------------------------------------------------------------------------

    public async refresh(): Promise<void> {
        this.panel.webview.html = this.loadingHtml();
        try {
            const bounties = await fetchBounties();
            this.panel.webview.html = this.buildHtml(bounties);
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err);
            this.panel.webview.html = this.errorHtml(msg);
        }
    }

    public dispose(): void {
        BountyBrowserPanel.currentPanel = undefined;
        this.panel.dispose();
        for (const d of this.disposables) { d.dispose(); }
    }

    // -------------------------------------------------------------------------
    // HTML builders
    // -------------------------------------------------------------------------

    private loadingHtml(): string {
        return `<!DOCTYPE html><html><body style="font-family:sans-serif;padding:24px">
            <h2>🔍 Loading RustChain Bounties…</h2>
        </body></html>`;
    }

    private errorHtml(message: string): string {
        return `<!DOCTYPE html><html><body style="font-family:sans-serif;padding:24px">
            <h2>⚠️ Could not load bounties</h2>
            <p>${escapeHtml(message)}</p>
            <button onclick="acquireVsCodeApi().postMessage({command:'refresh'})">Retry</button>
        </body></html>`;
    }

    private buildHtml(bounties: GitHubIssue[]): string {
        const rows = bounties.map((issue) => {
            const reward = issue.reward ? `<span class="reward">${escapeHtml(issue.reward)}</span>` : "";
            const title = escapeHtml(issue.title.replace(/\[BOUNTY:[^\]]*\]\s*/i, ""));
            return `
            <div class="bounty-card">
                <div class="bounty-header">
                    <span class="issue-num">#${issue.number}</span>
                    ${reward}
                </div>
                <div class="bounty-title">${title}</div>
                <div class="bounty-actions">
                    <button class="btn-view" onclick="openIssue(${issue.number}, '${escapeHtml(issue.html_url)}')">
                        View Issue
                    </button>
                    <button class="btn-claim" onclick="claimBounty(${issue.number})">
                        ⚡ Claim Bounty
                    </button>
                </div>
            </div>`;
        }).join("\n");

        return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RustChain Bounties</title>
<style>
  body { font-family: var(--vscode-font-family, sans-serif); padding: 16px; color: var(--vscode-foreground); background: var(--vscode-editor-background); }
  h1 { font-size: 1.3em; margin-bottom: 4px; }
  .subtitle { color: var(--vscode-descriptionForeground); margin-bottom: 16px; font-size: 0.9em; }
  .bounty-card { border: 1px solid var(--vscode-panel-border, #444); border-radius: 6px; padding: 12px 16px; margin-bottom: 10px; }
  .bounty-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
  .issue-num { color: var(--vscode-descriptionForeground); font-size: 0.85em; }
  .reward { background: var(--vscode-badge-background, #0078d4); color: var(--vscode-badge-foreground, #fff); border-radius: 12px; padding: 2px 10px; font-size: 0.85em; font-weight: 600; }
  .bounty-title { font-weight: 500; margin-bottom: 10px; }
  .bounty-actions { display: flex; gap: 8px; }
  button { cursor: pointer; padding: 4px 12px; border-radius: 4px; border: none; font-size: 0.9em; }
  .btn-view { background: var(--vscode-button-secondaryBackground, #3a3d41); color: var(--vscode-button-secondaryForeground, #ccc); }
  .btn-claim { background: var(--vscode-button-background, #0078d4); color: var(--vscode-button-foreground, #fff); font-weight: 600; }
  .refresh-row { margin-bottom: 14px; }
  .btn-refresh { background: transparent; border: 1px solid var(--vscode-panel-border, #555); color: var(--vscode-foreground); }
</style>
</head>
<body>
<h1>🏆 RustChain Bounties</h1>
<p class="subtitle">${bounties.length} open bounties — click "Claim Bounty" to open a PR template</p>
<div class="refresh-row">
  <button class="btn-refresh" onclick="refresh()">🔄 Refresh</button>
</div>
${rows || "<p>No open bounties found.</p>"}
<script>
const vscode = acquireVsCodeApi();
function openIssue(num, url) { vscode.postMessage({ command: 'openIssue', issueNumber: num, issueUrl: url }); }
function claimBounty(num) { vscode.postMessage({ command: 'claimBounty', issueNumber: num }); }
function refresh() { vscode.postMessage({ command: 'refresh' }); }
</script>
</body>
</html>`;
    }
}
