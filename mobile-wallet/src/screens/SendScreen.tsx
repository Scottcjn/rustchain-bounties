// SPDX-License-Identifier: MIT
import React, { useState, useContext } from "react";
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert, ScrollView, ActivityIndicator } from "react-native";
import { WalletContext } from "../../App";
import { RustChainService } from "../services/RustChainService";

export function SendScreen() {
  const { wallet, apiKey } = useContext(WalletContext);
  const [toAddress, setToAddress] = useState("");
  const [amount, setAmount] = useState("");
  const [memo, setMemo] = useState("");
  const [sending, setSending] = useState(false);

  const handleSend = async () => {
    if (!wallet) { Alert.alert("Error", "Please connect your wallet first."); return; }
    if (!toAddress.trim()) { Alert.alert("Error", "Please enter a recipient address."); return; }
    if (!amount || isNaN(parseFloat(amount)) || parseFloat(amount) <= 0) { Alert.alert("Error", "Please enter a valid amount."); return; }
    setSending(true);
    try {
      const svc = RustChainService.fromWallet(wallet, apiKey);
      const result = await svc.transfer(toAddress.trim(), parseFloat(amount), memo);
      Alert.alert("Success", `Sent ${amount} RTC to ${toAddress}.\n\nTx ID: ${result.txId}`);
      setToAddress(""); setAmount(""); setMemo("");
    } catch (err: any) {
      Alert.alert("Send Failed", err.message || "An error occurred.");
    } finally {
      setSending(false);
    }
  };

  if (!wallet) {
    return (
      <View style={styles.centered}>
        <Text style={styles.hint}>Connect your wallet first to send RTC.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Send RTC</Text>
      <Text style={styles.label}>Recipient Address</Text>
      <TextInput style={styles.input} placeholder="Wallet name or address" placeholderTextColor="#666"
        value={toAddress} onChangeText={setToAddress} autoCapitalize="none" autoCorrect={false} />
      <Text style={styles.label}>Amount (RTC)</Text>
      <TextInput style={styles.input} placeholder="0.0000" placeholderTextColor="#666"
        value={amount} onChangeText={setAmount} keyboardType="decimal-pad" />
      <Text style={styles.label}>Memo (optional)</Text>
      <TextInput style={[styles.input, { minHeight: 80, textAlignVertical: "top" }]}
        placeholder="Add a note..." placeholderTextColor="#666"
        value={memo} onChangeText={setMemo} multiline />
      <TouchableOpacity style={[styles.sendBtn, sending && { backgroundColor: "#664422" }]} onPress={handleSend} disabled={sending}>
        {sending ? <ActivityIndicator color="#FFF" /> : <Text style={styles.sendBtnText}>Send {amount || "0"} RTC</Text>}
      </TouchableOpacity>
      <Text style={styles.feeNote}>Network fee: negligible (RustChain uses Proof-of-Antiquity)</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0A0A0A", padding: 24 },
  centered: { flex: 1, backgroundColor: "#0A0A0A", justifyContent: "center", alignItems: "center", padding: 32 },
  hint: { color: "#888", fontSize: 14, textAlign: "center" },
  title: { color: "#FF6B35", fontSize: 24, fontWeight: "800", marginBottom: 24, marginTop: 20 },
  label: { color: "#888", fontSize: 12, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8, marginTop: 16 },
  input: { backgroundColor: "#1A1A1A", color: "#FFF", fontSize: 16, padding: 14, borderRadius: 10, borderWidth: 1, borderColor: "#333" },
  sendBtn: { backgroundColor: "#FF6B35", paddingVertical: 16, borderRadius: 12, alignItems: "center", marginTop: 32 },
  sendBtnDisabled: { backgroundColor: "#664422" },
  sendBtnText: { color: "#FFF", fontSize: 16, fontWeight: "700" },
  feeNote: { color: "#555", fontSize: 12, textAlign: "center", marginTop: 16 },
});
