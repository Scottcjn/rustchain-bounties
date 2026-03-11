// SPDX-License-Identifier: MIT
/**
 * HistoryScreen — transaction / reward history.
 *
 * Features:
 *   - Lists recent transactions (mining rewards, payouts)
 *   - Pull-to-refresh
 *   - Empty-state prompt when no wallet is configured
 *   - Graceful fallback when the node has no history endpoint yet
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
} from 'react-native';

import { useWallet } from '../utils/WalletContext';
import { getHistory } from '../api/rustchain';
import { COLORS, SPACING, FONT } from '../utils/theme';

const TYPE_LABELS = {
  mining_reward: 'Mining Reward',
  bounty_payout: 'Bounty Payout',
  transfer_in: 'Received',
  transfer_out: 'Sent',
};

const TYPE_COLORS = {
  mining_reward: COLORS.accentGreen,
  bounty_payout: COLORS.accentPurple,
  transfer_in: COLORS.accentBlue,
  transfer_out: COLORS.accentRed,
};

function TransactionItem({ item }) {
  const label = TYPE_LABELS[item.type] || item.type || 'Transaction';
  const color = TYPE_COLORS[item.type] || COLORS.textSecondary;

  return (
    <View style={styles.txCard}>
      <View style={styles.txHeader}>
        <View style={[styles.badge, { backgroundColor: color + '33' }]}>
          <Text style={[styles.badgeText, { color }]}>{label}</Text>
        </View>
        {item.epoch != null && (
          <Text style={styles.epoch}>Epoch {item.epoch}</Text>
        )}
      </View>
      <Text style={styles.amount}>
        {item.amount_rtc != null
          ? `${Number(item.amount_rtc).toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 6,
            })} RTC`
          : '—'}
      </Text>
      {item.description ? (
        <Text style={styles.desc}>{item.description}</Text>
      ) : null}
    </View>
  );
}

export default function HistoryScreen() {
  const { walletId } = useWallet();
  const [transactions, setTransactions] = useState([]);
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    if (!walletId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory(walletId);
      setTransactions(data.transactions || []);
      setNote(data.note || null);
    } catch (e) {
      setError(e.message || 'Failed to fetch history');
    } finally {
      setLoading(false);
    }
  }, [walletId]);

  useEffect(() => {
    if (walletId) fetchHistory();
  }, [walletId, fetchHistory]);

  if (!walletId) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.emptyTitle}>No Wallet Connected</Text>
        <Text style={styles.emptyText}>
          Go to the Balance tab and enter your wallet ID to view history.
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity onPress={fetchHistory}>
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {note && (
        <View style={styles.noteBanner}>
          <Text style={styles.noteText}>{note}</Text>
        </View>
      )}

      <FlatList
        data={transactions}
        keyExtractor={(_, idx) => String(idx)}
        renderItem={({ item }) => <TransactionItem item={item} />}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl
            refreshing={loading}
            onRefresh={fetchHistory}
            tintColor={COLORS.accentBlue}
          />
        }
        ListEmptyComponent={
          !loading ? (
            <View style={styles.center}>
              <Text style={styles.emptyText}>No transactions yet.</Text>
            </View>
          ) : null
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bgPrimary },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: SPACING.lg },
  list: { padding: SPACING.md },
  txCard: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 12,
    padding: SPACING.lg,
    marginBottom: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  txHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  badge: { paddingHorizontal: SPACING.sm, paddingVertical: SPACING.xs, borderRadius: 6 },
  badgeText: { fontSize: FONT.sm, fontWeight: '600' },
  epoch: { color: COLORS.textSecondary, fontSize: FONT.sm },
  amount: { color: COLORS.textPrimary, fontSize: FONT.xl, fontWeight: '700' },
  desc: { color: COLORS.textSecondary, fontSize: FONT.md, marginTop: SPACING.xs },
  emptyTitle: { color: COLORS.textPrimary, fontSize: FONT.lg, fontWeight: '600', marginBottom: SPACING.sm },
  emptyText: { color: COLORS.textSecondary, fontSize: FONT.md, textAlign: 'center' },
  errorBanner: {
    backgroundColor: COLORS.accentRed + '22',
    padding: SPACING.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  errorText: { color: COLORS.accentRed, fontSize: FONT.md, flex: 1 },
  retryText: { color: COLORS.accentBlue, fontSize: FONT.md, fontWeight: '600', marginLeft: SPACING.md },
  noteBanner: {
    backgroundColor: COLORS.accentYellow + '22',
    padding: SPACING.md,
  },
  noteText: { color: COLORS.accentYellow, fontSize: FONT.sm },
});
