// SPDX-License-Identifier: MIT
import React, { useState, useEffect, useContext, useCallback } from "react";
import {
  View, Text, StyleSheet, ScrollView, TextInput,
  TouchableOpacity, RefreshControl, ActivityIndicator, Alert,
} from "react-native";
import { WalletContext } from "../../App";
import { RustChainService } from "../services/RustChainService";

export function WalletScreen() {
  const { wallet, setWallet } = useContext(WalletContext);
  const [balance, setBalance] = useState<{balance: number; pending: number; lastUpdated: string} | null>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [walletInput, setWalletInput] = useState(wallet);

  const fetchBalance = useCallback(async () => {
    if (!wallet) return;
    setLoading(true);
    try {
      const svc = RustChainService.fromWallet(wallet);
      const bal = await svc.getBalance();
      setBalance(bal);
      const txs = await svc.getTransactions();
      setTransactions(txs.slice(0, 20));
    } catch (err: any) {
      Alert.alert("Error", err.message || "Failed to fetch balance");
    } finally {
      setLoading(false);
    }
  }, [wallet]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await fetchBalance();
    setRefreshing(false);
  }, [fetchBalance]);

  useEffect(() => { if (wallet) fetchBalance(); }, [wallet, fetchBalance]);

  const handleSetWallet = () => {
    if (!walletInput.trim()) { Alert.alert("Error", "Please enter a wallet name."); return; }
    setWallet(walletInput);
  };

  if (!wallet) {
    return (
      <View style={styles.centered}>
        <Text style={styles.title}>RustChain Wallet</Text>
        <Text style={styles.subtitle}>Enter your wallet name to get started</Text>
        <TextInput style={styles.input} placeholder="Wallet name or address"
          placeholderTextColor="#666" value={walletInput} onChangeText={setWalletInput}
          autoCapitalize="none" autoCorrect={false} />
        <TouchableOpacity style={styles.button} onPress={handleSetWallet}>
          <Text style={styles.buttonText}>Connect Wallet</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#FF6B35" />}
    >
      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>Balance</Text>
        {loading && !balance ? <ActivityIndicator color="#FF6B35" size="large" /> : (
          <>
            <Text style={styles.balanceAmount}>{balance ? `${balance.balance.toFixed(4)} RTC` : "—"}</Text>
            {balance && balance.pending > 0 && <Text style={styles.pendingText}>+{balance.pending.toFixed(4)} pending</Text>}
            <Text style={styles.lastUpdated}>Updated: {balance?.lastUpdated || "—"}</Text>
          </>
        )}
      </View>
      <View style={styles.walletInfo}>
        <Text style={styles.walletLabel}>Wallet</Text>
        <Text style={styles.walletAddress} numberOfLines={1}>{wallet}</Text>
      </View>
      <Text style={styles.sectionTitle}>Transaction History</Text>
      {transactions.length === 0 && !loading && <Text style={styles.emptyText}>No transactions yet.</Text>}
      {transactions.map((tx) => (
        <View key={tx.id} style={styles.txRow}>
          <View style={styles.txLeft}>
            <Text style={[styles.txType, tx.type === "in" ? styles.txIn : styles.txOut]}>
              {tx.type === "in" ? "↓ Received" : "↑ Sent"}
            </Text>
            <Text style={styles.txDate}>{tx.timestamp}</Text>
          </View>
          <View style={styles.txRight}>
            <Text style={[styles.txAmount, tx.type === "in" ? styles.txIn : styles.txOut]}>
              {tx.type === "in" ? "+" : "-"}{tx.amount.toFixed(4)} RTC
            </Text>
            <Text style={styles.txStatus}>{tx.status}</Text>
          </View>
        </View>
      ))}
      <TouchableOpacity style={styles.disconnectBtn} onPress={() => { setWallet(""); setWalletInput(""); }}>
        <Text style={styles.disconnectText}>Disconnect Wallet</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0A0A0A", padding: 16 },
  centered: { flex: 1, backgroundColor: "#0A0A0A", justifyContent: "center", alignItems: "center", padding: 32 },
  title: { color: "#FF6B35", fontSize: 28, fontWeight: "800", marginBottom: 8 },
  subtitle: { color: "#888", fontSize: 14, marginBottom: 32, textAlign: "center" },
  input: { backgroundColor: "#1A1A1A", color: "#FFF", fontSize: 16, padding: 16, borderRadius: 12, width: "100%", marginBottom: 16, borderWidth: 1, borderColor: "#333" },
  button: { backgroundColor: "#FF6B35", paddingVertical: 14, paddingHorizontal: 40, borderRadius: 12, width: "100%", alignItems: "center" },
  buttonText: { color: "#FFF", fontSize: 16, fontWeight: "700" },
  balanceCard: { backgroundColor: "#1A1A1A", borderRadius: 16, padding: 24, alignItems: "center", marginBottom: 16, borderWidth: 1, borderColor: "#333" },
  balanceLabel: { color: "#888", fontSize: 12, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 },
  balanceAmount: { color: "#FF6B35", fontSize: 40, fontWeight: "800" },
  pendingText: { color: "#FFB800", fontSize: 14, marginTop: 4 },
  lastUpdated: { color: "#555", fontSize: 11, marginTop: 12 },
  walletInfo: { backgroundColor: "#1A1A1A", borderRadius: 12, padding: 16, marginBottom: 20, borderWidth: 1, borderColor: "#333" },
  walletLabel: { color: "#888", fontSize: 10, textTransform: "uppercase", letterSpacing: 1, marginBottom: 4 },
  walletAddress: { color: "#FFF", fontSize: 14, fontFamily: "monospace" },
  sectionTitle: { color: "#FFF", fontSize: 18, fontWeight: "700", marginBottom: 12 },
  emptyText: { color: "#555", fontSize: 14, textAlign: "center", marginVertical: 32 },
  txRow: { backgroundColor: "#1A1A1A", borderRadius: 10, padding: 14, marginBottom: 8, flexDirection: "row", justifyContent: "space-between", borderWidth: 1, borderColor: "#222" },
  txLeft: { flex: 1 },
  txRight: { alignItems: "flex-end" },
  txType: { fontSize: 14, fontWeight: "600", marginBottom: 2 },
  txIn: { color: "#4ADE80" },
  txOut: { color: "#FF6B35" },
  txDate: { color: "#555", fontSize: 11 },
  txAmount: { fontSize: 14, fontWeight: "700", marginBottom: 2 },
  txStatus: { fontSize: 10, textTransform: "uppercase" },
  disconnectBtn: { marginTop: 24, marginBottom: 40, alignItems: "center" },
  disconnectText: { color: "#FF4444", fontSize: 14 },
});
