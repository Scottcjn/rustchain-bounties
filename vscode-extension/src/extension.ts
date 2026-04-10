// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — VS Code Extension
 *
 * Provides:
 * - RTC balance display in the status bar
 * - Epoch countdown timer in the status bar
 * - Miner/wallet active status indicator
 * - Bounty browser sidebar panel
 * - RustChain config file syntax highlighting
 * - Code snippets for RustChain development
 *
 * Bounty: #2868
 */

import * as vscode from "vscode";
import { BalanceStatusBar } from "./balanceStatusBar";
import { NodeHealthChecker } from "./nodeHealth";
import { EpochTimer } from "./epochTimer";
import { MinerStatus } from "./minerStatus";
import { BountyBrowserProvider } from "./bountyBrowser";

let balanceStatusBar: BalanceStatusBar | undefined;
let nodeHealthChecker: NodeHealthChecker | undefined;
let epochTimer: EpochTimer | undefined;
let minerStatus: MinerStatus | undefined;

export function activate(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration("rustchain");

    // --- Status bar: RTC balance ---
    balanceStatusBar = new BalanceStatusBar(context);

    // --- Status bar: Epoch countdown ---
    epochTimer = new EpochTimer(context);

    // --- Status bar: Miner active/idle indicator ---
    minerStatus = new MinerStatus(context);

    // --- Sidebar: Bounty browser ---
    const bountyBrowser = new BountyBrowserProvider(context);
    vscode.window.registerTreeDataProvider("rustchainBounties", bountyBrowser);

    // --- Node health checker ---
    nodeHealthChecker = new NodeHealthChecker();

    // --- Commands ---
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.refreshBalance", () => {
            balanceStatusBar?.refresh();
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
                minerStatus?.onConfigChange();
            }
        }),
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.checkNodeHealth", async () => {
            await nodeHealthChecker?.showHealth();
        }),
    );

    // React to configuration changes.
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration("rustchain")) {
                balanceStatusBar?.onConfigChange();
                minerStatus?.onConfigChange();
            }
        }),
    );
}

export function deactivate(): void {
    balanceStatusBar?.dispose();
    balanceStatusBar = undefined;
    epochTimer?.dispose();
    epochTimer = undefined;
    minerStatus?.dispose();
    minerStatus = undefined;
    nodeHealthChecker = undefined;
}
