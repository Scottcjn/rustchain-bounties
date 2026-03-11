// SPDX-License-Identifier: MIT
/**
 * BalanceScreen — displays the user's RTC balance.
 *
 * Features:
 *   - Wallet ID input (persisted in context)
 *   - Pull-to-refresh balance query
 *   - Network health indicator
 *   - Epoch / slot sidebar info
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  RefreshControl,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';

import { useWallet, validateWalletId } from '../utils/WalletContext';
import { getBalance, getHealth, getEpoch } from '../api/rustchain';
import { COLORS, SPACING, FONT } from '../utils/theme';

export default function BalanceScreen() {
  const { walletId, setWalletId } = useWallet();

  const [inputValue, setInputValue] = useState(walletId);
  const [balance, setBalance] = useState(null);
  const [health, setHealth] = useState(null);
  const [epoch, setEpoch] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchBalance = useCallback(async () => {
    const err = validateWalletId(inputValue);
    if (err) {
      setError(err);
      return;
    }
    setWalletId(inputValue);
    setLoading(true);
    setError(null);
    try {
      const [balData, healthData, epochData] = await Promise.all([
        getBalance(inputValue),
        getHealth().catch(() => null),
        getEpoch().catch(() => null),
      ]);
      setBalance(balData);
      setHealth(healthData);
      setEpoch(epochData);
    } catch (e) {
      setError(e.message || 'Failed to fetch balance');
    } finally {
      setLoading(false);
    }
  }, [inputValue, setWalletId]);

  // Auto-refresh when screen mounts with a saved wallet
  useEffect(() => {
    if (walletId) {
      setInputValue(walletId);
    }
  }, [walletId]);

  const formatRtc = (amount) => {
    if (amount == null) return '—';
    return `${Number(amount).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    })} RTC`;
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={loading}
          onRefresh={fetchBalance}
          tintColor={COLORS.accentBlue}
        />
      }
    >
      {/* Wallet input */}
      <View style={styles.card}>
        <Text style={styles.label}>Wallet / Miner ID</Text>
        <TextInput
          style={styles.input}
          value={inputValue}
          onChangeText={setInputValue}
          placeholder="e.g. a1b2c3...RTC or miner-name"
          placeholderTextColor={COLORS.textSecondary}
          autoCapitalize="none"
          autoCorrect={false}
        />
        <TouchableOpacity
          style={[styles.button, loading && styles.buttonDisabled]}
          onPress={fetchBalance}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color={COLORS.textPrimary} size="small" />
          ) : (
            <Text style={styles.buttonText}>Check Balance</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Error */}
      {error && (
        <View style={[styles.card, styles.errorCard]}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      {/* Balance display */}
      {balance && (
        <View style={[styles.card, styles.balanceCard]}>
          <Text style={styles.balanceLabel}>Balance</Text>
          <Text style={styles.balanceValue}>{formatRtc(balance.balance_rtc)}</Text>
          <Text style={styles.walletSub}>{balance.wallet_id}</Text>
        </View>
      )}

      {/* Network info */}
      {(health || epoch) && (
        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Network</Text>
          {health && (
            <View style={styles.row}>
              <View style={[styles.dot, health.ok ? styles.dotGreen : styles.dotRed]} />
              <Text style={styles.infoText}>
                Node {health.ok ? 'healthy' : 'down'} — v{health.version || '?'}
              </Text>
            </View>
          )}
          {epoch && (
            <>
              <Text style={styles.infoText}>Epoch {epoch.epoch} · Slot {epoch.slot}</Text>
              <Text style={styles.infoText}>
                {epoch.enrolled_miners} enrolled miners · pot {epoch.epoch_pot} RTC
              </Text>
            </>
          )}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bgPrimary },
  content: { padding: SPACING.md },
  card: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 12,
    padding: SPACING.lg,
    marginBottom: SPACING.md,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  balanceCard: {
    alignItems: 'center',
    borderColor: COLORS.accentBlue,
  },
  errorCard: { borderColor: COLORS.accentRed },
  label: { color: COLORS.textSecondary, fontSize: FONT.md, marginBottom: SPACING.sm },
  input: {
    backgroundColor: COLORS.bgSecondary,
    color: COLORS.textPrimary,
    borderRadius: 8,
    padding: SPACING.md,
    fontSize: FONT.md,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: SPACING.md,
  },
  button: {
    backgroundColor: COLORS.accentBlue,
    borderRadius: 8,
    padding: SPACING.md,
    alignItems: 'center',
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: COLORS.textPrimary, fontSize: FONT.lg, fontWeight: '600' },
  balanceLabel: { color: COLORS.textSecondary, fontSize: FONT.md, marginBottom: SPACING.xs },
  balanceValue: { color: COLORS.accentGreen, fontSize: FONT.xxl, fontWeight: '700' },
  walletSub: { color: COLORS.textSecondary, fontSize: FONT.sm, marginTop: SPACING.sm },
  sectionTitle: { color: COLORS.textPrimary, fontSize: FONT.lg, fontWeight: '600', marginBottom: SPACING.sm },
  row: { flexDirection: 'row', alignItems: 'center', marginBottom: SPACING.xs },
  dot: { width: 8, height: 8, borderRadius: 4, marginRight: SPACING.sm },
  dotGreen: { backgroundColor: COLORS.accentGreen },
  dotRed: { backgroundColor: COLORS.accentRed },
  infoText: { color: COLORS.textSecondary, fontSize: FONT.md, marginBottom: SPACING.xs },
  errorText: { color: COLORS.accentRed, fontSize: FONT.md },
});
