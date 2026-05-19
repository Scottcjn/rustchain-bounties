const vscode = require('vscode');

/**
 * WebView panel for the RustChain Wallet & Miner Dashboard.
 */
class WalletPanel {
  /**
   * @param {vscode.ExtensionContext} context
   * @param {vscode.Uri} extensionUri
   * @param {import('./apiClient').ApiClient} apiClient
   */
  constructor(panel, extensionUri, apiClient) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this.apiClient = apiClient;
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    this._panel.webview.html = this._getHtml();
    this.refresh();
  }

  static currentPanel = undefined;
  static viewType = 'rustchainDashboard';

  static createOrShow(extensionUri, apiClient) {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    if (WalletPanel.currentPanel) {
      WalletPanel.currentPanel._panel.reveal(column);
      WalletPanel.currentPanel.refresh();
      return;
    }

    const panel = vscode.window.createWebviewPanel(
      WalletPanel.viewType,
      'RustChain Dashboard',
      column || vscode.ViewColumn.One,
      { enableScripts: true }
    );

    WalletPanel.currentPanel = new WalletPanel(panel, extensionUri, apiClient);
  }

  async refresh() {
    try {
      const [balance, miner, network, txs] = await Promise.all([
        this.apiClient.getBalance(),
        this.apiClient.getMinerStatus(),
        this.apiClient.getNetworkStatus(),
        this.apiClient.getRecentTransactions(),
      ]);
      const data = { balance, miner, network, transactions: txs, updatedAt: new Date().toISOString() };
      this._panel.webview.postMessage({ type: 'update', data });
    } catch (err) {
      // Silently fail — panel will show loading state
    }
  }

  dispose() {
    WalletPanel.currentPanel = undefined;
    this._panel.dispose();
    this._disposables.forEach((d) => d.dispose());
  }

  _getHtml() {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RustChain Dashboard</title>
  <style>
    :root {
      --bg: #1e1e2e;
      --card-bg: #2a2a3d;
      --accent: #f97316;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --success: #22c55e;
      --border: #3a3a5c;
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--bg);
      color: var(--text);
      padding: 20px;
    }
    h1 { font-size: 24px; margin-bottom: 4px; color: var(--accent); }
    .subtitle { color: var(--muted); margin-bottom: 24px; font-size: 14px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
    }
    .card h2 { font-size: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }
    .card .value { font-size: 32px; font-weight: 700; color: var(--accent); }
    .card .sub { font-size: 13px; color: var(--muted); margin-top: 6px; }
    .stat-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); }
    .stat-row:last-child { border-bottom: none; }
    .stat-label { color: var(--muted); }
    .stat-value { font-weight: 600; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
    .badge-active { background: #16a34a33; color: var(--success); }
    .badge-offline { background: #dc262633; color: #ef4444; }
    table { width: 100%; border-collapse: collapse; margin-top: 8px; }
    th, td { text-align: left; padding: 8px; border-bottom: 1px solid var(--border); font-size: 13px; }
    th { color: var(--muted); text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
    .updated { text-align: right; color: var(--muted); font-size: 12px; margin-top: 16px; }
  </style>
</head>
<body>
  <h1>⛏️ RustChain Dashboard</h1>
  <p class="subtitle">Wallet & Miner Monitor</p>

  <div class="grid">
    <div class="card">
      <h2>💰 Wallet Balance</h2>
      <div class="value" id="balance">—</div>
      <div class="sub" id="address">Loading...</div>
    </div>
    <div class="card">
      <h2>⛏️ Miner Status</h2>
      <div id="miner-status"><span class="badge badge-offline">Loading</span></div>
      <div class="sub" id="miner-hashrate"></div>
    </div>
    <div class="card">
      <h2>🌐 Network</h2>
      <div class="stat-row"><span class="stat-label">Epoch</span><span class="stat-value" id="epoch">—</span></div>
      <div class="stat-row"><span class="stat-label">Block Height</span><span class="stat-value" id="blockHeight">—</span></div>
      <div class="stat-row"><span class="stat-label">Peers</span><span class="stat-value" id="peers">—</span></div>
      <div class="stat-row"><span class="stat-label">Total Supply</span><span class="stat-value" id="totalSupply">—</span></div>
    </div>
  </div>

  <div class="card">
    <h2>📋 Recent Transactions</h2>
    <table>
      <thead><tr><th>Hash</th><th>Amount</th><th>Type</th><th>Time</th></tr></thead>
      <tbody id="tx-body"><tr><td colspan="4" style="text-align:center;color:var(--muted)">Loading...</td></tr></tbody>
    </table>
  </div>

  <div class="updated" id="updated">—</div>

  <script>
    const vscode = acquireVsCodeApi();
    window.addEventListener('message', (event) => {
      const msg = event.data;
      if (msg.type === 'update') {
        const d = msg.data;
        document.getElementById('balance').textContent = d.balance.amount + ' RTC';
        document.getElementById('address').textContent = d.balance.address;

        const minerEl = document.getElementById('miner-status');
        const active = d.miner.status === 'active' || d.miner.status === 'mining';
        minerEl.innerHTML = '<span class="badge ' + (active ? 'badge-active' : 'badge-offline') + '">' + d.miner.status + '</span>';
        document.getElementById('miner-hashrate').textContent = 'Hashrate: ' + (d.miner.hashrate || '—') + ' | Workers: ' + (d.miner.activeWorkers || 0);

        document.getElementById('epoch').textContent = d.network.epoch;
        document.getElementById('blockHeight').textContent = d.network.blockHeight;
        document.getElementById('peers').textContent = d.network.peers;
        document.getElementById('totalSupply').textContent = d.network.totalSupply;

        const tbody = document.getElementById('tx-body');
        if (d.transactions && d.transactions.length > 0) {
          tbody.innerHTML = d.transactions.map(tx =>
            '<tr><td>' + (tx.hash || '—').substring(0, 16) + '...</td><td>' + (tx.amount || '—') + '</td><td>' + (tx.type || '—') + '</td><td>' + (tx.timestamp || '—') + '</td></tr>'
          ).join('');
        } else {
          tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--muted)">No recent transactions</td></tr>';
        }

        document.getElementById('updated').textContent = 'Updated: ' + new Date(d.updatedAt).toLocaleTimeString();
      }
    });
  </script>
</body>
</html>`;
  }
}

module.exports = { WalletPanel };
