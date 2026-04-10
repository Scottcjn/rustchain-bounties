import * as vscode from 'vscode';
import axios from 'axios';

let statusBarItem: vscode.StatusBarItem;
let refreshTimer: NodeJS.Timer;

const NODE_URL = 'https://50.28.86.131';

export function activate(context: vscode.ExtensionContext) {
    // Create status bar
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    statusBarItem.text = '🔄 Loading...';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Initial load
    updateWalletStatus();
    
    // Auto refresh
    const config = vscode.workspace.getConfiguration('rustchain');
    const interval = config.get('refreshInterval', 60) * 1000;
    refreshTimer = setInterval(updateWalletStatus, interval);
    context.subscriptions.push({ dispose: () => clearInterval(refreshTimer) });

    // Commands
    const refreshCmd = vscode.commands.registerCommand('rustchain.refresh', () => {
        updateWalletStatus();
    });
    context.subscriptions.push(refreshCmd);

    // Create bounty webview
    const bountyProvider = new BountyTreeProvider();
    vscode.window.registerTreeDataProvider('bountyBrowser', bountyProvider);

    // Create miner status webview
    const minerProvider = new MinerTreeProvider();
    vscode.window.registerTreeDataProvider('minerStatus', minerProvider);
}

async function updateWalletStatus() {
    try {
        const config = vscode.workspace.getConfiguration('rustchain');
        const wallet = config.get('wallet', '');
        
        if (!wallet) {
            statusBarItem.text = '⚙️ Set wallet';
            return;
        }

        const response = await axios.get(`${NODE_URL}/wallet/balance?wallet_id=${wallet}`, {
            timeout: 5000
        });
        
        const balance = response.data?.balance || 0;
        statusBarItem.text = `💰 RTC: ${balance.toFixed(2)}`;
        statusBarItem.color = balance > 0 ? '#00ff00' : undefined;
    } catch (error) {
        statusBarItem.text = '❌ Offline';
    }
}

class BountyTreeProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    async getChildren(): Promise<vscode.TreeItem[]> {
        try {
            const response = await axios.get('https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?state=open&per_page=10');
            return response.data.map((issue: any) => {
                const item = new vscode.TreeItem(`#${issue.number}: ${issue.title.slice(0, 40)}`);
                item.command = { command: 'vscode.open', arguments: [issue.html_url], title: 'Open' };
                return item;
            });
        } catch (error) {
            return [new vscode.TreeItem('Error loading bounties')];
        }
    }
    
    getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
        return element;
    }
}

class MinerTreeProvider implements vscode.TreeDataProvider<vscode.TreeItem> {
    async getChildren(): Promise<vscode.TreeItem[]> {
        try {
            const response = await axios.get(`${NODE_URL}/api/miners`, { timeout: 5000 });
            const miners = response.data?.miners || [];
            return miners.map((miner: any) => {
                const status = miner.active ? '🟢 Active' : '🔴 Inactive';
                const item = new vscode.TreeItem(`${miner.name}: ${status}`);
                return item;
            });
        } catch (error) {
            return [new vscode.TreeItem('Node offline')];
        }
    }
    
    getTreeItem(element: vscode.TreeItem): vscode.TreeItem {
        return element;
    }
}

export function deactivate() {}
