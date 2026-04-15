// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — VS Code Extension
 *
 * Provides:
 * - RTC balance display in the status bar           (BalanceStatusBar)
 * - Miner attestation status (🟢/🔴) in status bar  (MinerStatusBar)
 * - Epoch countdown timer in status bar              (EpochTimer)
 * - Bounty Browser webview panel                     (BountyBrowserPanel)
 * - Node health / epoch info command
 *
 * Bounty: #2868
 */

import * as vscode from "vscode";
import { BalanceStatusBar } from "./balanceStatusBar";
import { NodeHealthChecker } from "./nodeHealth";
import { MinerStatusBar } from "./minerStatus";
import { EpochTimer } from "./epochTimer";
import { BountyBrowserPanel } from "./bountyBrowser";

let balanceStatusBar: BalanceStatusBar | undefined;
let minerStatusBar: MinerStatusBar | undefined;
let epochTimer: EpochTimer | undefined;
let nodeHealthChecker: NodeHealthChecker | undefined;

export function activate(context: vscode.ExtensionContext): void {
    // ── Status bar items ────────────────────────────────────────────────────
    balanceStatusBar = new BalanceStatusBar(context);
    minerStatusBar   = new MinerStatusBar(context);
    epochTimer       = new EpochTimer(context);

    // ── Services ─────────────────────────────────────────────────────────────
    nodeHealthChecker = new NodeHealthChecker();

    // ── Commands ─────────────────────────────────────────────────────────────

    // Refresh wallet balance
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.refreshBalance", () => {
            balanceStatusBar?.refresh();
        }),
    );

    // Set miner/wallet ID
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.setMinerId", async () => {
            const config = vscode.workspace.getConfiguration("rustchain");
            const current = config.get<string>("minerId", "");
            const minerId = await vscode.window.showInputBox({
                prompt: "Enter your RustChain miner/wallet ID",
                placeHolder: "e.g. my-miner-name",
                value: current,
            });
            if (minerId !== undefined) {
                await config.update("minerId", minerId, vscode.ConfigurationTarget.Global);
                balanceStatusBar?.refresh();
                minerStatusBar?.onConfigChange();
            }
        }),
    );

    // Check node health (shows modal with health + epoch info)
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.checkNodeHealth", async () => {
            await nodeHealthChecker?.showHealth();
        }),
    );

    // Open Bounty Browser panel
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.openBountyBrowser", () => {
            BountyBrowserPanel.createOrShow(context.extensionUri);
        }),
    );

    // Refresh Bounty Browser (if open)
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.refreshBounties", () => {
            BountyBrowserPanel.currentPanel?.refresh();
        }),
    );

    // ── Config change listener ────────────────────────────────────────────────
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration("rustchain")) {
                balanceStatusBar?.onConfigChange();
                minerStatusBar?.onConfigChange();
            }
        }),
    );
}

export function deactivate(): void {
    balanceStatusBar?.dispose();
    balanceStatusBar = undefined;
    minerStatusBar?.dispose();
    minerStatusBar = undefined;
    epochTimer?.dispose();
    epochTimer = undefined;
    nodeHealthChecker = undefined;
}
