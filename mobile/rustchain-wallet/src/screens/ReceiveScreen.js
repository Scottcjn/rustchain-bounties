// SPDX-License-Identifier: MIT
/**
 * ReceiveScreen — QR code display for receiving RTC.
 *
 * Features:
 *   - Renders a QR code encoding the wallet ID
 *   - Tap-to-copy wallet address
 *   - Share button for quick sharing
 *   - Prompts the user to set a wallet on the Balance tab first
 */

import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Share,
  Platform,
} from 'react-native';

import { useWallet } from '../utils/WalletContext';
import { COLORS, SPACING, FONT } from '../utils/theme';

// QR code rendering — the library is optional so the screen degrades
// gracefully in environments where native SVG is unavailable (e.g. web).
let QRCode = null;
try {
  QRCode = require('react-native-qrcode-svg').default;
} catch {
  // Will fall back to text-only display below.
}

export default function ReceiveScreen() {
  const { walletId } = useWallet();
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      // Clipboard API differs across RN versions; try the modern API first.
      const Clipboard =
        require('@react-native-clipboard/clipboard')?.default ??
        require('react-native').Clipboard;
      Clipboard.setString(walletId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      Alert.alert('Wallet ID', walletId);
    }
  }, [walletId]);

  const handleShare = useCallback(async () => {
    try {
      await Share.share({
        message: `My RustChain wallet address:\n${walletId}`,
        title: 'RustChain Wallet Address',
      });
    } catch {
      // User cancelled — no-op.
    }
  }, [walletId]);

  if (!walletId) {
    return (
      <View style={[styles.container, styles.center]}>
        <Text style={styles.emptyTitle}>No Wallet Set</Text>
        <Text style={styles.emptyText}>
          Enter your wallet ID on the Balance tab to generate a receive QR code.
        </Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, styles.center]}>
      <Text style={styles.heading}>Receive RTC</Text>
      <Text style={styles.subheading}>
        Show this QR code to the sender, or share your address.
      </Text>

      {/* QR Code */}
      <View style={styles.qrContainer}>
        {QRCode ? (
          <QRCode
            value={walletId}
            size={220}
            backgroundColor={COLORS.textPrimary}
            color={COLORS.bgPrimary}
          />
        ) : (
          <View style={styles.qrFallback}>
            <Text style={styles.qrFallbackText}>
              QR preview unavailable.{'\n'}Install react-native-qrcode-svg.
            </Text>
          </View>
        )}
      </View>

      {/* Wallet address */}
      <TouchableOpacity style={styles.addressBox} onPress={handleCopy}>
        <Text style={styles.address} numberOfLines={1} ellipsizeMode="middle">
          {walletId}
        </Text>
        <Text style={styles.copyHint}>
          {copied ? 'Copied!' : 'Tap to copy'}
        </Text>
      </TouchableOpacity>

      {/* Share button */}
      <TouchableOpacity style={styles.shareButton} onPress={handleShare}>
        <Text style={styles.shareText}>Share Address</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bgPrimary },
  center: { justifyContent: 'center', alignItems: 'center', padding: SPACING.lg },
  heading: { color: COLORS.textPrimary, fontSize: FONT.xl, fontWeight: '700', marginBottom: SPACING.xs },
  subheading: { color: COLORS.textSecondary, fontSize: FONT.md, textAlign: 'center', marginBottom: SPACING.lg },
  qrContainer: {
    backgroundColor: COLORS.textPrimary,
    borderRadius: 16,
    padding: SPACING.lg,
    marginBottom: SPACING.lg,
  },
  qrFallback: {
    width: 220,
    height: 220,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.bgCard,
    borderRadius: 8,
  },
  qrFallbackText: { color: COLORS.textSecondary, fontSize: FONT.sm, textAlign: 'center' },
  addressBox: {
    backgroundColor: COLORS.bgCard,
    borderRadius: 8,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.lg,
    borderWidth: 1,
    borderColor: COLORS.border,
    alignItems: 'center',
    maxWidth: '90%',
    marginBottom: SPACING.md,
  },
  address: { color: COLORS.accentBlue, fontSize: FONT.md, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
  copyHint: { color: COLORS.textSecondary, fontSize: FONT.sm, marginTop: SPACING.xs },
  shareButton: {
    backgroundColor: COLORS.accentPurple,
    borderRadius: 8,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.xl,
  },
  shareText: { color: COLORS.textPrimary, fontSize: FONT.lg, fontWeight: '600' },
  emptyTitle: { color: COLORS.textPrimary, fontSize: FONT.lg, fontWeight: '600', marginBottom: SPACING.sm },
  emptyText: { color: COLORS.textSecondary, fontSize: FONT.md, textAlign: 'center' },
});
