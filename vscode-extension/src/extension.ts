import * as vscode from 'vscode';
import * as https from 'https';

// Type-safe fetch wrapper for VS Code
async function httpGet<T = unknown>(url: string): Promise<{ ok: boolean; data: T | null }> {
    return new Promise((resolve) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk: string) => data += chunk);
            res.on('end', () => {
                try {
                    resolve({
                        ok: res.statusCode === 200,
                        data: JSON.parse(data) as T
                    });
                } catch {
                    resolve({ ok: false, data: null });
                }
            });
        }).on('error', () => {
            resolve({ ok: false, data: null });
        });
    });
}

// Configuration interface
interface RustChainConfig {
    walletName: string;
    nodeUrl: string;
    refreshInterval: number;
}

// API Response types
interface BalanceResponse {
    balance: number;
    balance_nrtc?: number;
}

interface EpochResponse {
    epoch: number;
    slots_in_epoch: number;
    current_slot: number;
}

interface MinersResponse {
    miners?: Array<{
        miner_id: string;
        status: string;
        last_attestation?: string;
    }>;
}

interface Bounty {
    number: number;
    title: string;
    state: string;
    html_url: string;
}

interface BountyIssue {
    number: number;
    title: string;
    state: string;
    html_url: string;
}

interface WebviewMessage {
    command: string;
    url?: string;
}

// Status bar item
let statusBarItem: vscode.StatusBarItem | undefined;
let refreshInterval: ReturnType<typeof setInterval> | undefined;

// Get configuration
function getConfig(): RustChainConfig {
    const config = vscode.workspace.getConfiguration('rustchain');
    return {
        walletName: config.get<string>('walletName', '') || '',
        nodeUrl: config.get<string>('nodeUrl', 'https://50.28.86.131') || 'https://50.28.86.131',
        refreshInterval: config.get<number>('refreshInterval', 60) || 60
    };
}

// API calls
async function fetchBalance(walletName: string, nodeUrl: string): Promise<number | null> {
    try {
        const response = await httpGet<BalanceResponse>(`${nodeUrl}/wallet/balance?wallet_id=${encodeURIComponent(walletName)}`);
        if (!response.ok || !response.data) { return null; }
        return response.data.balance_nrtc ?? response.data.balance ?? 0;
    } catch (error) {
        console.error('Failed to fetch balance:', error);
        return null;
    }
}

async function fetchEpoch(nodeUrl: string): Promise<EpochResponse | null> {
    try {
        const response = await httpGet<EpochResponse>(`${nodeUrl}/epoch`);
        if (!response.ok || !response.data) { return null; }
        return response.data;
    } catch (error) {
        console.error('Failed to fetch epoch:', error);
        return null;
    }
}

async function fetchMinerStatus(walletName: string, nodeUrl: string): Promise<boolean> {
    try {
        const response = await httpGet<MinersResponse>(`${nodeUrl}/api/miners`);
        if (!response.ok || !response.data) { return false; }
        const miners = response.data.miners || [];
        return miners.some(m => m.miner_id === walletName && m.status === 'active');
    } catch (error) {
        console.error('Failed to fetch miner status:', error);
        return false;
    }
}

async function fetchBounties(): Promise<Bounty[]> {
    try {
        const response = await httpGet<BountyIssue[]>('https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?state=open&labels=bounty&per_page=20');
        if (!response.ok || !response.data) { return []; }
        return response.data.map(item => ({
            number: item.number,
            title: item.title,
            state: item.state,
            html_url: item.html_url
        }));
    } catch (error) {
        console.error('Failed to fetch bounties:', error);
        return [];
    }
}

// Update status bar
async function updateStatusBar(): Promise<void> {
    const config = getConfig();
    if (!statusBarItem) {
        statusBarItem = vscode.window.createStatusBarItem('rustchain-balance', vscode.StatusBarAlignment.Left, 100);
    }

    if (!config.walletName) {
        statusBarItem.text = '$(rustchain-icon) ⚠️ No wallet';
        statusBarItem.tooltip = 'Configure rustchain.walletName in settings';
        statusBarItem.show();
        return;
    }

    const balance = await fetchBalance(config.walletName, config.nodeUrl);
    if (balance === null) {
        statusBarItem.text = '$(rustchain-icon) ❌ Offline';
        statusBarItem.tooltip = 'Failed to connect to RustChain node';
    } else {
        const rtc = balance / 100_000_000;
        statusBarItem.text = `$(rustchain-icon) ◎ ${rtc.toFixed(2)} RTC`;
        statusBarItem.tooltip = `Wallet: ${config.walletName}\nBalance: ${rtc.toFixed(8)} RTC`;
    }
    statusBarItem.show();
}

// Create webview for bounty browser
function createBountyWebview(bounties: Bounty[]): string {
    const bountyList = bounties.map(b => `
        <div class="bounty-item" onclick="openBounty('${b.html_url}')">
            <div class="bounty-number">#${b.number}</div>
            <div class="bounty-title">${escapeHtml(b.title)}</div>
        </div>
    `).join('');

    return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: var(--vscode-font-family); padding: 10px; margin: 0; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .title { font-size: 16px; font-weight: 600; }
        .refresh-btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none; padding: 5px 12px; cursor: pointer; border-radius: 3px;
        }
        .bounty-item {
            display: flex; padding: 8px; margin: 5px 0;
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-widget-border);
            border-radius: 4px; cursor: pointer;
        }
        .bounty-item:hover { background: var(--vscode-list-hoverBackground); }
        .bounty-number {
            color: var(--vscode-textLink-foreground);
            font-weight: 600; margin-right: 10px; min-width: 50px;
        }
        .bounty-title { font-size: 13px; overflow: hidden; text-overflow: ellipsis; }
        .stats {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
            margin-bottom: 15px;
        }
        .stat-box {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-widget-border);
            padding: 10px; border-radius: 4px; text-align: center;
        }
        .stat-value { font-size: 20px; font-weight: 600; color: var(--vscode-textLink-foreground); }
        .stat-label { font-size: 11px; color: var(--vscode-descriptionForeground); }
    </style>
</head>
<body>
    <div class="header">
        <span class="title">🦀 RustChain Bounties</span>
        <button class="refresh-btn" id="refreshBtn">↻ Refresh</button>
    </div>
    <div class="stats">
        <div class="stat-box">
            <div class="stat-value">${bounties.length}</div>
            <div class="stat-label">Open Bounties</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">30+</div>
            <div class="stat-label">Max RTC per Bounty</div>
        </div>
    </div>
    <div class="bounty-list">
        ${bountyList || '<p>No bounties found</p>'}
    </div>
    <script>
        const vscode = acquireVsCodeApi();
        document.getElementById('refreshBtn').addEventListener('click', () => {
            vscode.postMessage({ command: 'refresh' });
        });
        function openBounty(url) {
            vscode.postMessage({ command: 'openUrl', url });
        }
    </script>
</body>
</html>`;
}

function escapeHtml(text: string): string {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Register commands
function registerCommands(): void {
    vscode.commands.registerCommand('rustchain.refresh', async () => {
        await updateStatusBar();
        vscode.window.showInformationMessage('RustChain dashboard refreshed');
    });

    vscode.commands.registerCommand('rustchain.openBounty', async (bounty?: Bounty) => {
        if (bounty?.html_url) {
            vscode.env.openExternal(vscode.Uri.parse(bounty.html_url));
        }
    });

    vscode.commands.registerCommand('rustchain.claimBounty', async () => {
        const issueNumber = await vscode.window.showInputBox({
            prompt: 'Enter the bounty issue number you want to claim',
            validateInput: (value: string) => {
                const num = parseInt(value, 10);
                return isNaN(num) ? 'Please enter a valid number' : '';
            }
        });
        if (issueNumber) {
            vscode.env.openExternal(
                vscode.Uri.parse(`https://github.com/Scottcjn/rustchain-bounties/issues/${issueNumber}`)
            );
        }
    });
}

// Webview provider
class RustChainBountyProvider implements vscode.WebviewViewProvider {
    constructor(private readonly extensionContext: vscode.ExtensionContext) {}

    resolveWebviewView(webviewView: vscode.WebviewView): void {
        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionContext.extensionUri]
        };

        webviewView.webview.html = createBountyWebview([]);

        webviewView.webview.onDidReceiveMessage((message: WebviewMessage) => {
            switch (message.command) {
                case 'openUrl':
                    if (message.url) {
                        vscode.env.openExternal(vscode.Uri.parse(message.url));
                    }
                    break;
                case 'refresh':
                    this.refreshWebview(webviewView);
                    break;
            }
        });

        this.refreshWebview(webviewView);
    }

    private async refreshWebview(webviewView: vscode.WebviewView): Promise<void> {
        webviewView.webview.html = `<!DOCTYPE html>
<html><body style="font-family: var(--vscode-font-family); padding: 20px; text-align: center;">
    <p>⏳ Loading bounties...</p>
</body></html>`;

        const bounties = await fetchBounties();
        webviewView.webview.html = createBountyWebview(bounties);
    }
}

// Main activation
export async function activate(context: vscode.ExtensionContext): Promise<void> {
    console.log('RustChain Dashboard extension activated');

    registerCommands();

    const provider = new RustChainBountyProvider(context);
    vscode.window.registerWebviewViewProvider('rustchain-bounties', provider);

    await updateStatusBar();

    const config = getConfig();
    refreshInterval = setInterval(() => {
        updateStatusBar();
    }, config.refreshInterval * 1000);

    vscode.workspace.onDidChangeConfiguration((event) => {
        if (event.affectsConfiguration('rustchain')) {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
            const newConfig = getConfig();
            refreshInterval = setInterval(() => {
                updateStatusBar();
            }, newConfig.refreshInterval * 1000);
            updateStatusBar();
        }
    });
}

// Deactivation
export function deactivate(): void {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}
