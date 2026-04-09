// SPDX-License-Identifier: MIT
import * as vscode from "vscode";
import { BalanceStatusBar } from "./balanceStatusBar";
import { NodeHealthChecker } from "./nodeHealth";
import { MinerStatusProvider } from "./minerProvider";
import { BountyProvider } from "./bountyProvider";

let balanceStatusBar: BalanceStatusBar | undefined;

export function activate(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration("rustchain");

    // Status bar: RTC balance
    balanceStatusBar = new BalanceStatusBar(context);

    // Sidebar: Miner status
    const minerProvider = new MinerStatusProvider(context);
    vscode.window.registerTreeDataProvider("rustchain-miner", minerProvider);

    // Sidebar: Bounty browser
    const bountyProvider = new BountyProvider();
    vscode.window.registerTreeDataProvider("rustchain-bounties", bountyProvider);

    // Commands
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.refreshMiner", () => minerProvider.refresh()),
        vscode.commands.registerCommand("rustchain.refreshBounties", () => bountyProvider.refresh()),
        vscode.commands.registerCommand("rustchain.checkHealth", async () => {
            const checker = new NodeHealthChecker();
            await checker.check();
        })
    );
}

export function deactivate(): void {
    balanceStatusBar?.dispose();
}
