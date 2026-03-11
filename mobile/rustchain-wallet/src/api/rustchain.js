// SPDX-License-Identifier: MIT
/**
 * RustChain API client for the mobile wallet.
 *
 * Talks to the wallet-api-server proxy (scripts/wallet_api_server.py)
 * rather than hitting the node directly, because:
 *   1. The node uses a self-signed cert that mobile rejects.
 *   2. The node lacks CORS headers.
 *
 * All functions return plain objects and throw on network errors.
 */

/** Default base URL — override via setBaseUrl() for dev / staging. */
let BASE_URL = 'http://localhost:8787';

/**
 * Change the API base URL at runtime (useful for config screens).
 * @param {string} url
 */
export function setBaseUrl(url) {
  BASE_URL = url.replace(/\/+$/, '');
}

/** Return the current base URL. */
export function getBaseUrl() {
  return BASE_URL;
}

/**
 * Generic GET helper with timeout and structured error handling.
 * @param {string} path  – e.g. "/api/balance/abc123RTC"
 * @param {number} [timeoutMs=10000]
 * @returns {Promise<object>}
 */
async function apiGet(path, timeoutMs = 10000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const resp = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });

    const body = await resp.json();

    if (!resp.ok) {
      const msg = body.error || `HTTP ${resp.status}`;
      throw new Error(msg);
    }

    return body;
  } finally {
    clearTimeout(timer);
  }
}

// -------------------------------------------------------------------
// Public API
// -------------------------------------------------------------------

/**
 * Fetch the RTC balance for a wallet.
 * @param {string} walletId
 * @returns {Promise<{wallet_id: string, balance_rtc: number, balance_raw: number}>}
 */
export async function getBalance(walletId) {
  return apiGet(`/api/balance/${encodeURIComponent(walletId)}`);
}

/**
 * Fetch transaction / reward history for a wallet.
 * @param {string} walletId
 * @returns {Promise<{wallet_id: string, transactions: Array, note?: string}>}
 */
export async function getHistory(walletId) {
  return apiGet(`/api/history/${encodeURIComponent(walletId)}`);
}

/**
 * Fetch node health status.
 * @returns {Promise<{ok: boolean, version: string, uptime_s: number}>}
 */
export async function getHealth() {
  return apiGet('/api/health');
}

/**
 * Fetch current epoch / slot information.
 * @returns {Promise<{epoch: number, slot: number, enrolled_miners: number}>}
 */
export async function getEpoch() {
  return apiGet('/api/epoch');
}

/**
 * Fetch list of active miners.
 * @returns {Promise<{miners: Array, count: number}>}
 */
export async function getMiners() {
  return apiGet('/api/miners');
}
