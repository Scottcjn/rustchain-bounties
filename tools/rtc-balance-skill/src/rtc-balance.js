#!/usr/bin/env node

/**
 * RustChain RTC Balance Checker Skill
 *
 * Usage: /rtc-balance <wallet-address>
 *
 * Fetches and displays the RTC balance for a RustChain wallet address.
 */

const https = require('https');

// RustChain API endpoint
const API_HOST = 'bulbous-bouffant.metalseed.net';
const API_IP = '50.28.86.131';
const API_ENDPOINT = '/wallet/balance';

/**
 * Fetch wallet balance from RustChain API
 * @param {string} address - The wallet address to check
 * @returns {Promise<Object>} Balance data
 */
async function fetchBalance(address) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: API_IP,
      port: 443,
      path: `${API_ENDPOINT}?address=${encodeURIComponent(address)}`,
      method: 'GET',
      rejectUnauthorized: false, // Accept self-signed certificates
      headers: {
        'User-Agent': 'Claude-RTC-Balance-Skill/1.0'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          resolve(parsed);
        } catch (err) {
          reject(new Error(`Failed to parse API response: ${err.message}`));
        }
      });
    });

    req.on('error', (err) => {
      reject(new Error(`API request failed: ${err.message}`));
    });

    req.end();
  });
}

/**
 * Format balance data for display
 * @param {Object} data - Balance data from API
 * @returns {string} Formatted output
 */
function formatBalance(data) {
  if (data.error) {
    return `❌ Error: ${data.error}`;
  }

  const minerId = data.miner_id || 'Unknown';
  const balanceRTC = data.amount_rtc || 0;
  const balanceUSD = (balanceRTC * 0.10).toFixed(2); // Approximate $0.10 per RTC

  return `
💰 **RustChain Wallet Balance**

**Wallet**: ${minerId}
**Balance**: ${balanceRTC} RTC (~$${balanceUSD} USD)
**Raw Amount**: ${data.amount_i64} satoshis

---
*RTC Balance Skill | Powered by RustChain*
  `.trim();
}

/**
 * Main function - called by Claude Code skill system
 * @param {string} args - Command arguments (wallet address)
 * @returns {Promise<string>} Formatted output
 */
async function main(args) {
  // Parse arguments
  const address = args ? args.trim() : null;

  if (!address) {
    return `
❌ **Missing wallet address**

Usage: /rtc-balance <wallet-address>

Example:
  /rtc-balance my-miner-wallet
  /rtc-balance 0x1234...

Replace <wallet-address> with your RustChain wallet address or miner ID.
    `.trim();
  }

  try {
    console.log(`[RTC-Balance] Fetching balance for: ${address}`);
    const data = await fetchBalance(address);
    return formatBalance(data);
  } catch (err) {
    return `❌ **Error fetching balance**: ${err.message}

Please try again or check if the wallet address is correct.`;
  }
}

// Export for use as module or CLI
if (require.main === module) {
  // CLI mode
  const args = process.argv.slice(2).join(' ');
  main(args)
    .then((result) => {
      console.log(result);
      process.exit(0);
    })
    .catch((err) => {
      console.error('Fatal error:', err.message);
      process.exit(1);
    });
} else {
  // Module mode
  module.exports = { main, fetchBalance, formatBalance };
}
