import * as vscode from 'vscode';
import axios from 'axios';

const NODE_URL = 'https://50.28.86.131';

interface WalletInfo {
    wallet: string;
    balance: number;
    lastClaim?: string;
}

interface EpochInfo {
    epoch: number;
    startTime: string;
    endTime: string;
    blocksRemaining: number;
}

interface MinerStatus {
    wallet: string;
    status: 'active' | 'inactive';
    lastAttestation?: string;
}

export function activate(context: vscode.ExtensionContext) {
    // Register the dashboard view
    const provider = new RustChainDashboardProvider();
    
    vscode.window.registerWebviewViewProvider(
        'rustchain.dashboard',
        provider
    );

    // Refresh command
    const refreshCommand = vscode.commands.registerCommand(
        'rustchain.refresh',
        () => provider.refresh()
    );

    context.subscriptions.push(refreshCommand);
    
    // Status bar item
    const statusItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        100
    );
    statusItem.text = "$(pulse) RustChain";
    statusItem.command = 'rustchain.refresh';
    statusItem.show();
    context.subscriptions.push(statusItem);

    // Initial fetch
    provider.refresh();
}

class RustChainDashboardProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;

    resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;
        webviewView.webview.html = this.getHtml();
        this.refresh();
    }

    async refresh() {
        if (!this._view) return;

        const config = vscode.workspace.getConfiguration('rustchain');
        const walletName = config.get<string>('walletName') || 'Not configured';
        const nodeUrl = config.get<string>('nodeUrl') || NODE_URL;

        let walletInfo: WalletInfo = { wallet: walletName, balance: 0 };
        let epochInfo: EpochInfo | null = null;
        let minerStatus: MinerStatus | null = null;
        let error = '';

        try {
            // Fetch wallet balance
            const balanceRes = await axios.get(`${nodeUrl}/wallet/balance`, {
                params: { wallet_id: walletName },
                timeout: 5000
            });
            walletInfo = { wallet: walletName, ...balanceRes.data };
        } catch (e: any) {
            error += `Wallet: ${e.message}\n`;
        }

        try {
            // Fetch epoch info
            const epochRes = await axios.get(`${nodeUrl}/epoch`, { timeout: 5000 });
            epochInfo = epochRes.data;
        } catch (e: any) {
            error += `Epoch: ${e.message}\n`;
        }

        try {
            // Check miner status
            const minersRes = await axios.get(`${nodeUrl}/api/miners`, { timeout: 5000 });
            const miners: MinerStatus[] = minersRes.data.miners || [];
            minerStatus = miners.find(m => m.wallet === walletName) || null;
        } catch (e: any) {
            error += `Miners: ${e.message}`;
        }

        this._view.webview.html = this.getHtml(walletInfo, epochInfo, minerStatus, error);
    }

    private getHtml(
        wallet?: WalletInfo,
        epoch?: EpochInfo | null,
        miner?: MinerStatus | null,
        error?: string
    ): string {
        const balance = wallet?.balance ?? '?';
        const status = miner?.status === 'active' ? '🟢 Active' : '🔴 Inactive';
        
        return `
<!DOCTYPE html>
<html>
<head>
    <style>
        body { padding: 10px; font-family: var(--vscode-font-family); }
        .card { background: var(--vscode-editor-background); border: 1px solid var(--vscode-widget-border); border-radius: 4px; padding: 10px; margin-bottom: 10px; }
        .title { font-weight: bold; margin-bottom: 5px; }
        .value { font-size: 1.2em; color: var(--vscode-textLink-foreground); }
        .status-active { color: #4caf50; }
        .status-inactive { color: #f44336; }
        .error { color: #ff9800; font-size: 0.9em; }
        .refresh-btn { background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; padding: 5px 10px; cursor: pointer; }
    </style>
</head>
<body>
    <button class="refresh-btn" onclick="vscode.postMessage({command: 'refresh'})">🔄 Refresh</button>
    
    <div class="card">
        <div class="title">💰 Wallet Balance</div>
        <div class="value">${balance} RTC</div>
        <div>${wallet?.wallet || 'Not configured'}</div>
    </div>

    <div class="card">
        <div class="title">⛏️ Miner Status</div>
        <div class="${miner?.status === 'active' ? 'status-active' : 'status-inactive'}">${status}</div>
        ${miner?.lastAttestation ? `<div>Last: ${miner.lastAttestation}</div>` : ''}
    </div>

    <div class="card">
        <div class="title">📅 Epoch</div>
        ${epoch ? `
            <div>Epoch #${epoch.epoch}</div>
            <div>Blocks remaining: ${epoch.blocksRemaining}</div>
        ` : '<div>Loading...</div>'}
    </div>

    ${error ? `<div class="error">⚠️ ${error}</div>` : ''}
    
    <script>
        const vscode = acquireVsCodeApi();
        window.addEventListener('message', e => {
            if (e.data.command === 'refresh') location.reload();
        });
    </script>
</body>
</html>`;
    }
}
