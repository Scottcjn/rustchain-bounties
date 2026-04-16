import * as vscode from "vscode";

const NODE_URL = () => vscode.workspace.getConfiguration("rustchain").get<string>("nodeUrl", "https://50.28.86.131");
const WALLET = () => vscode.workspace.getConfiguration("rustchain").get<string>("walletAddress", "");
const INTERVAL = () => vscode.workspace.getConfiguration("rustchain").get<number>("refreshInterval", 30);

async function fetchAPI(path: string): Promise<any> {
    try {
        const url = ;
        const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
        return await res.json();
    } catch { return null; }
}

class WalletProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChange = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChange.event;
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e: vscode.TreeItem) { return e; }
    async getChildren(): Promise<vscode.TreeItem[]> {
        const addr = WALLET();
        if (!addr) {
            const item = new vscode.TreeItem("Set walletAddress in settings");
            item.command = { command: "workbench.action.openSettings", title: "Settings", arguments: ["rustchain.walletAddress"] };
            return [item];
        }
        const data = await fetchAPI(`/api/balance/${addr}`);
        const balance = data?.balance ?? "???";
        const item = new vscode.TreeItem(`Balance: ${balance} RTC`, vscode.TreeItemCollapsibleState.None);
        item.iconPath = new vscode.ThemeIcon("wallet");
        item.tooltip = `Address: ${addr}`;
        return [item];
    }
}

class MinerProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChange = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChange.event;
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e: vscode.TreeItem) { return e; }
    async getChildren(): Promise<vscode.TreeItem[]> {
        const data = await fetchAPI("/api/miners");
        if (!data || !Array.isArray(data)) { return [new vscode.TreeItem("Unable to fetch miners")]; }
        return data.slice(0, 10).map((m: any) => {
            const status = m.active ? "🟢 Attesting" : "🔴 Offline";
            const item = new vscode.TreeItem(`${m.address?.slice(0,8)}... - ${status}`);
            item.tooltip = JSON.stringify(m, null, 2);
            return item;
        });
    }
}

class BountyProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChange = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChange.event;
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e: vscode.TreeItem) { return e; }
    async getChildren(): Promise<vscode.TreeItem[]> {
        try {
            const res = await fetch("https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?labels=bounty&state=open&per_page=10", { signal: AbortSignal.timeout(8000) });
            const issues = await res.json();
            return issues.filter((i: any) => !i.pull_request && !i.assignee).map((issue: any) => {
                const title = issue.title.replace(/\[.*?\]\s*/, "").slice(0, 50);
                const item = new vscode.TreeItem(title);
                item.tooltip = issue.body?.slice(0, 200);
                item.command = { command: "vscode.open", title: "Open", arguments: [vscode.Uri.parse(issue.html_url)] };
                item.iconPath = new vscode.ThemeIcon("gift");
                return item;
            });
        } catch { return [new vscode.TreeItem("GitHub API unavailable")]; }
    }
}

class EpochProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    private _onDidChange = new vscode.EventEmitter<void>();
    readonly onDidChangeTreeData = this._onDidChange.event;
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e: vscode.TreeItem) { return e; }
    async getChildren(): Promise<vscode.TreeItem[]> {
        const data = await fetchAPI("/api/epoch");
        const nextEpoch = data?.next_epoch ?? "Unknown";
        const item = new vscode.TreeItem(`Next epoch: ${nextEpoch}`);
        item.iconPath = new vscode.ThemeIcon("clock");
        return [item];
    }
}

export function activate(ctx: vscode.ExtensionContext) {
    const wallet = new WalletProvider();
    const miners = new MinerProvider();
    const bounties = new BountyProvider();
    const epoch = new EpochProvider();

    ctx.subscriptions.push(
        vscode.window.registerTreeDataProvider("rustchain.wallet", wallet),
        vscode.window.registerTreeDataProvider("rustchain.miners", miners),
        vscode.window.registerTreeDataProvider("rustchain.bounties", bounties),
        vscode.window.registerTreeDataProvider("rustchain.epoch", epoch),
        vscode.commands.registerCommand("rustchain.refresh", () => { wallet.refresh(); miners.refresh(); bounties.refresh(); epoch.refresh(); }),
        vscode.commands.registerCommand("rustchain.claimBounty", () => vscode.env.openExternal(vscode.Uri.parse("https://github.com/Scottcjn/rustchain-bounties"))),
        vscode.commands.registerCommand("rustchain.openNode", () => vscode.env.openExternal(vscode.Uri.parse(NODE_URL()))),
        vscode.commands.registerCommand("rustchain.copyAddress", () => { vscode.env.clipboard.writeText(WALLET()); vscode.window.showInformationMessage("Wallet address copied"); })
    );

    // Status bar
    const statusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusItem.command = "rustchain.refresh";
    async function updateStatus() {
        const addr = WALLET();
        if (addr) {
            const data = await fetchAPI(`/api/balance/${addr}`);
            statusItem.text = `RTC: ${data?.balance ?? "??"}`;
        } else {
            statusItem.text = "RTC: --";
        }
        statusItem.tooltip = "Click to refresh RustChain";
        statusItem.show();
    }
    updateStatus();
    setInterval(updateStatus, INTERVAL() * 1000);
}

export function deactivate() {}
