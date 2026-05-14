const https = require('https');
const http = require('http');

/**
 * RustChain API client.
 */
class ApiClient {
  /**
   * @param {string} baseUrl
   * @param {string} walletAddress
   */
  constructor(baseUrl, walletAddress) {
    this.baseUrl = (baseUrl || 'https://api.rustchain.xyz').replace(/\/+$/, '');
    this.walletAddress = walletAddress || '';
  }

  /**
   * Generic GET request.
   * @param {string} path
   * @returns {Promise<any>}
   */
  _get(path) {
    return new Promise((resolve, reject) => {
      const url = `${this.baseUrl}${path}`;
      const client = url.startsWith('https') ? https : http;
      client
        .get(url, { headers: { Accept: 'application/json' } }, (res) => {
          let data = '';
          res.on('data', (chunk) => (data += chunk));
          res.on('end', () => {
            try {
              resolve(JSON.parse(data));
            } catch {
              resolve(data);
            }
          });
        })
        .on('error', reject);
    });
  }

  /**
   * Get wallet balance.
   * @returns {Promise<{address: string, amount: string, currency: string}>}
   */
  async getBalance() {
    if (!this.walletAddress) {
      return { address: 'not configured', amount: '0.00', currency: 'RTC' };
    }
    try {
      const res = await this._get(`/wallet/${encodeURIComponent(this.walletAddress)}/balance`);
      return {
        address: this.walletAddress,
        amount: res.balance || res.amount || '0.00',
        currency: 'RTC',
      };
    } catch {
      return { address: this.walletAddress, amount: '—', currency: 'RTC' };
    }
  }

  /**
   * Get miner status for the wallet.
   * @returns {Promise<object>}
   */
  async getMinerStatus() {
    if (!this.walletAddress) {
      return { status: 'not configured', hashrate: '0 H/s', activeWorkers: 0 };
    }
    try {
      const res = await this._get(`/miner/${encodeURIComponent(this.walletAddress)}/status`);
      return res;
    } catch {
      return { status: 'unavailable', hashrate: '—', activeWorkers: 0 };
    }
  }

  /**
   * Get network status.
   * @returns {Promise<{epoch: number, peers: number, blockHeight: number}>}
   */
  async getNetworkStatus() {
    try {
      const res = await this._get('/network/status');
      return {
        epoch: res.epoch || 0,
        peers: res.peers || 0,
        blockHeight: res.blockHeight || res.block_height || 0,
        totalSupply: res.totalSupply || res.total_supply || '—',
      };
    } catch {
      return { epoch: 0, peers: 0, blockHeight: 0, totalSupply: '—' };
    }
  }

  /**
   * Get recent transactions.
   * @returns {Promise<Array>}
   */
  async getRecentTransactions() {
    if (!this.walletAddress) return [];
    try {
      const res = await this._get(`/wallet/${encodeURIComponent(this.walletAddress)}/transactions?limit=10`);
      return res.transactions || res || [];
    } catch {
      return [];
    }
  }
}

module.exports = { ApiClient };
