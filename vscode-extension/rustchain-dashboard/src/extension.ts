import * as vscode from "vscode";

function getConfig(key, def) {
    return vscode.workspace.getConfiguration("rustchain").get(key, def);
}

async function fetchAPI(path) {
    try {
        const url = getConfig("nodeUrl", "https://50.28.86.131") + path;
        const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
        return await res.json();
    } catch { return null; }
}

class WalletProvider {
    constructor() { this._onDidChange = new vscode.EventEmitter(); }
    get onDidChangeTreeData() { return this._onDidChange.event; }
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e) { return e; }
    async getChildren() {
        const addr = getConfig("walletAddress", "");
        if (!addr) {
            const item = new vscode.TreeItem("Set rustchain.walletAddress in settings");
            item.command = { command: "workbench.action.openSettings", title: "Settings", arguments: ["rustchain.walletAddress"] };
            return [item];
        }
        const data = await fetchAPI("/api/balance/" + addr);
        const balance = (data && data.balance) ? data.balance : "???";
        const item = new vscode.TreeItem("Balance: " + balance + " RTC", vscode.TreeItemCollapsibleState.None);
        item.iconPath = new vscode.ThemeIcon("wallet");
        item.tooltip = "Address: " + addr;
        return [item];
    }
}

class MinerProvider {
    constructor() { this._onDidChange = new vscode.EventEmitter(); }
    get onDidChangeTreeData() { return this._onDidChange.event; }
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e) { return e; }
    async getChildren() {
        const data = await fetchAPI("/api/miners");
        if (!data || !Array.isArray(data)) { return [new vscode.TreeItem("Unable to fetch miners")]; }
        return data.slice(0, 10).map(function(m) {
            const addr = String(m.address || "???").slice(0, 8);
            const status = m.active ? "Attesting" : "Offline";
            const item = new vscode.TreeItem(addr + "... - " + status);
            item.tooltip = JSON.stringify(m, null, 2);
            return item;
        });
    }
}

class BountyProvider {
    constructor() { this._onDidChange = new vscode.EventEmitter(); }
    get onDidChangeTreeData() { return this._onDidChange.event; }
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e) { return e; }
    async getChildren() {
        try {
            const res = await fetch("https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?labels=bounty&state=open&per_page=10", { signal: AbortSignal.timeout(8000) });
            const issues = await res.json();
            return issues.filter(function(i) { return !i.pull_request && !i.assignee; }).map(function(issue) {
                const title = issue.title.replace(/\[.*?\]\s*/, "").slice(0, 50);
                const item = new vscode.TreeItem(title);
                item.tooltip = issue.body ? issue.body.slice(0, 200) : "";
                item.command = { command: "vscode.open", title: "Open", arguments: [vscode.Uri.parse(issue.html_url)] };
                item.iconPath = new vscode.ThemeIcon("gift");
                return item;
            });
        } catch { return [new vscode.TreeItem("GitHub API unavailable")]; }
    }
}

class EpochProvider {
    constructor() { this._onDidChange = new vscode.EventEmitter(); }
    get onDidChangeTreeData() { return this._onDidChange.event; }
    refresh() { this._onDidChange.fire(); }
    getTreeItem(e) { return e; }
    async getChildren() {
        const data = await fetchAPI("/api/epoch");
        const nextEpoch = (data && data.next_epoch) ? data.next_epoch : "Unknown";
        const item = new vscode.TreeItem("Next epoch: " + nextEpoch);
        item.iconPath = new vscode.ThemeIcon("clock");
        return [item];
    }
}

function activate(ctx) {
    const wallet = new WalletProvider();
    const miners = new MinerProvider();
    const bounties = new BountyProvider();
    const epoch = new EpochProvider();

    ctx.subscriptions.push(
        vscode.window.registerTreeDataProvider("rustchain.wallet", wallet),
        vscode.window.registerTreeDataProvider("rustchain.miners", miners),
        vscode.window.registerTreeDataProvider("rustchain.bounties", bounties),
        vscode.window.registerTreeDataProvider("rustchain.epoch", epoch),
        vscode.commands.registerCommand("rustchain.refresh", function() { wallet.refresh(); miners.refresh(); bounties.refresh(); epoch.refresh(); }),
        vscode.commands.registerCommand("rustchain.claimBounty", function() { vscode.env.openExternal(vscode.Uri.parse("https://github.com/Scottcjn/rustchain-bounties")); }),
        vscode.commands.registerCommand("rustchain.openNode", function() { vscode.env.openExternal(vscode.Uri.parse(getConfig("nodeUrl", "https://50.28.86.131"))); }),
        vscode.commands.registerCommand("rustchain.copyAddress", function() { vscode.env.clipboard.writeText(getConfig("walletAddress", "")); vscode.window.showInformationMessage("Wallet address copied"); })
    );

    const statusItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    statusItem.command = "rustchain.refresh";
    async function updateStatus() {
        const addr = getConfig("walletAddress", "");
        if (addr) {
            const data = await fetchAPI("/api/balance/" + addr);
            statusItem.text = "RTC: " + ((data && data.balance) ? data.balance : "??");
        } else {
            statusItem.text = "RTC: --";
        }
        statusItem.tooltip = "Click to refresh RustChain";
        statusItem.show();
    }
    updateStatus();
    setInterval(updateStatus, getConfig("refreshInterval", 30) * 1000);
}

function deactivate() {}

module.exports = { activate, deactivate };
