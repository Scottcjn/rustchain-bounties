// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — VS Code Extension
 *
 * Provides:
 * - RTC balance display in the status bar
 * - Miner status indicator (green/red)
 * - Epoch countdown timer
 * - Bounty browser panel
 * - RustChain config file syntax highlighting
 * - Code snippets for RustChain development
 *
 * Bounty: #2868
 */

import * as vscode from "vscode";
import { BalanceStatusBar } from "./balanceStatusBar";
import { NodeHealthChecker } from "./nodeHealth";
import { MinerStatus } from "./minerStatus";
import { EpochTimer } from "./epochTimer";
import { QuickActionsProvider } from "./quickActions";

let balanceStatusBar: BalanceStatusBar | undefined;
let nodeHealthChecker: NodeHealthChecker | undefined;
let minerStatus: MinerStatus | undefined;
let epochTimer: EpochTimer | undefined;
let quickActions: QuickActionsProvider | undefined;

export function activate(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration("rustchain");

    // --- Quick Actions (register all commands first) ---
    quickActions = new QuickActionsProvider(context);

    // --- Status bar: RTC balance ---
    balanceStatusBar = new BalanceStatusBar(context);

    // --- Status bar: Miner status (green/red) ---
    minerStatus = new MinerStatus(context);

    // --- Status bar: Epoch countdown ---
    epochTimer = new EpochTimer(context);

    // --- Node health checker ---
    nodeHealthChecker = new NodeHealthChecker();

    // --- Commands ---
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.refreshBalance", () => {
            balanceStatusBar?.refresh();
            minerStatus?.refresh();
            epochTimer?.refresh();
        }),
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.setMinerId", async () => {
            const current = config.get<string>("minerId", "");
            const minerId = await vscode.window.showInputBox({
                prompt: "Enter your RustChain miner/wallet ID",
                placeHolder: "e.g. my-miner-name",
                value: current,
            });
            if (minerId !== undefined) {
                await vscode.workspace
                    .getConfiguration("rustchain")
                    .update("minerId", minerId, vscode.ConfigurationTarget.Global);
                balanceStatusBar?.refresh();
                minerStatus?.refresh();
            }
        }),
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.checkNodeHealth", async () => {
            await nodeHealthChecker?.showHealth();
        }),
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.openBountyBrowser", async () => {
            const { BountyBrowserPanel } = await import("./bountyBrowser");
            new BountyBrowserPanel(context);
        }),
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.claimBounty", async () => {
            await vscode.commands.executeCommand("rustchain.openBountyBrowser");
        }),
    );

    // React to configuration changes.
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration("rustchain")) {
                balanceStatusBar?.onConfigChange();
                minerStatus?.onConfigChange();
                epochTimer?.onConfigChange();
            }
        }),
    );
}

export function deactivate(): void {
    balanceStatusBar?.dispose();
    nodeHealthChecker = undefined;
    minerStatus?.dispose();
    epochTimer?.dispose();
    balanceStatusBar = undefined;
    minerStatus = undefined;
    epochTimer = undefined;
    quickActions = undefined;
}
