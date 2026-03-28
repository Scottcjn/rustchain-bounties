/**
 * RustChain Wallet - Background Service Worker
 * Bounty #730 - 40-100 RTC
 */

// Wallet state
let walletState = {
  address: null,
  balance: 0,
  connected: false,
  snapConnected: false
};

// RTC RPC endpoint
const RTC_RPC = 'https://rpc.rustchain.org';

// Initialize wallet
chrome.runtime.onInstalled.addListener(() => {
  console.log('RustChain Wallet installed');
  loadWalletState();
});

// Load wallet state from storage
async function loadWalletState() {
  try {
    const result = await chrome.storage.local.get(['walletState']);
    if (result.walletState) {
      walletState = result.walletState;
      console.log('Wallet state loaded:', walletState);
    }
  } catch (error) {
    console.error('Failed to load wallet state:', error);
  }
}

// Save wallet state to storage
async function saveWalletState() {
  try {
    await chrome.storage.local.set({ walletState });
    console.log('Wallet state saved:', walletState);
  } catch (error) {
    console.error('Failed to save wallet state:', error);
  }
}

// Connect to RTC wallet
async function connectWallet() {
  try {
    // Try to connect via MetaMask Snap first
    const snapResponse = await connectViaSnap();
    if (snapResponse) {
      walletState.address = snapResponse.address;
      walletState.connected = true;
      walletState.snapConnected = true;
      await saveWalletState();
      return snapResponse;
    }

    // Fallback: Generate new wallet
    const newWallet = await generateWallet();
    walletState.address = newWallet.address;
    walletState.connected = true;
    await saveWalletState();
    return newWallet;
  } catch (error) {
    console.error('Failed to connect wallet:', error);
    throw error;
  }
}

// Connect via MetaMask Snap
async function connectViaSnap() {
  try {
    // Invoke MetaMask Snap
    const response = await window.ethereum?.request({
      method: 'wallet_invokeSnap',
      params: {
        snapId: 'npm:rustchain-snap',
        request: {
          method: 'getPublicKey'
        }
      }
    });
    
    if (response) {
      return {
        address: response.address,
        type: 'snap'
      };
    }
    return null;
  } catch (error) {
    console.log('Snap not available, using fallback');
    return null;
  }
}

// Generate new RTC wallet
async function generateWallet() {
  // Simple key generation (in production, use secure RNG)
  const crypto = require('crypto');
  const privateKey = crypto.randomBytes(32).toString('hex');
  
  // Derive address from private key (simplified)
  const address = 'RTC' + crypto.createHash('sha256').update(privateKey).digest('hex').slice(0, 40);
  
  return {
    address,
    privateKey,
    type: 'native'
  };
}

// Get balance from RPC
async function getBalance(address) {
  try {
    const response = await fetch(RTC_RPC, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'getBalance',
        params: [address],
        id: 1
      })
    });
    
    const data = await response.json();
    return data.result || 0;
  } catch (error) {
    console.error('Failed to get balance:', error);
    return 0;
  }
}

// Send RTC transaction
async function sendTransaction(to, amount) {
  try {
    const response = await fetch(RTC_RPC, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'sendTransaction',
        params: [{
          from: walletState.address,
          to,
          amount
        }],
        id: 1
      })
    });
    
    const data = await response.json();
    return data.result;
  } catch (error) {
    console.error('Failed to send transaction:', error);
    throw error;
  }
}

// Message handler for popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.action) {
    case 'connect':
      connectWallet()
        .then(result => sendResponse({ success: true, data: result }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;
    
    case 'getBalance':
      getBalance(walletState.address)
        .then(balance => {
          walletState.balance = balance;
          saveWalletState();
          sendResponse({ success: true, balance });
        });
      return true;
    
    case 'send':
      sendTransaction(request.to, request.amount)
        .then(txHash => sendResponse({ success: true, txHash }))
        .catch(error => sendResponse({ success: false, error: error.message }));
      return true;
    
    case 'getState':
      sendResponse({ success: true, state: walletState });
      return true;
  }
});

// Initialize on startup
connectWallet().catch(console.error);
