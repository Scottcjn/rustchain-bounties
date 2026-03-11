// SPDX-License-Identifier: MIT
/**
 * React context for wallet state shared across all screens.
 *
 * Stores the wallet ID and provides a setter so the user can enter
 * (or later import) their RustChain wallet address once.
 */

import React, { createContext, useContext, useState, useMemo } from 'react';

const WalletContext = createContext(null);

/**
 * Validate a RustChain wallet ID.
 *
 * Strict format: 38 hex chars + "RTC" suffix (41 total).
 * The upstream API also accepts free-form miner IDs, so we allow
 * alphanumeric + hyphen + underscore as a fallback.
 *
 * @param {string} id – candidate wallet ID
 * @returns {string|null} error message or null if valid
 */
export function validateWalletId(id) {
  if (!id || id.trim().length === 0) {
    return 'Wallet ID is required';
  }
  if (id.length > 64) {
    return 'Wallet ID is too long (max 64 characters)';
  }
  if (!/^[a-zA-Z0-9_-]+$/.test(id)) {
    return 'Wallet ID contains invalid characters';
  }
  return null;
}

export function WalletProvider({ children }) {
  const [walletId, setWalletId] = useState('');

  const value = useMemo(
    () => ({ walletId, setWalletId }),
    [walletId],
  );

  return (
    <WalletContext.Provider value={value}>
      {children}
    </WalletContext.Provider>
  );
}

export function useWallet() {
  const ctx = useContext(WalletContext);
  if (!ctx) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return ctx;
}
