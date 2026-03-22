// SPDX-License-Identifier: MIT
import React, { useState, useContext } from "react";
import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import QRCode from "expo-qrcode";
import * as Clipboard from "expo-clipboard";
import { WalletContext } from "../../App";

export function ReceiveScreen() {
  const { wallet } = useContext(WalletContext);
  const [copied, setCopied] = useState(false);

  if (!wallet) {
    return (
      <View style={styles.centered}>
        <Text style={styles.hint}>Connect your wallet first to get a receive address.</Text>
      </View>
    );
  }

  const receiveURI = `rustchain:${wallet}`;
  const displayAddress = wallet.length > 24
    ? `${wallet.slice(0, 12)}...${wallet.slice(-8)}` : wallet;

  const handleCopy = async () => {
    await Clipboard.setStringAsync(wallet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Receive RTC</Text>
      <Text style={styles.subtitle}>Scan the QR code or copy the address below</Text>
      <View style={styles.qrWrapper}>
        <QRCode value={receiveURI} size={240} backgroundColor="#FFFFFF" color="#0A0A0A" />
      </View>
      <View style={styles.addressBox}>
        <Text style={styles.addressLabel}>Wallet Address</Text>
        <Text style={styles.address} selectable>{displayAddress}</Text>
      </View>
      <TouchableOpacity style={styles.copyBtn} onPress={handleCopy}>
        <Text style={styles.copyBtnText}>{copied ? "✓ Copied!" : "Copy Address"}</Text>
      </TouchableOpacity>
      <Text style={styles.info}>
        Only send RTC to this address. Tokens sent to the wrong network may be unrecoverable.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0A0A0A", padding: 24, alignItems: "center" },
  centered: { flex: 1, backgroundColor: "#0A0A0A", justifyContent: "center", alignItems: "center", padding: 32 },
  hint: { color: "#888", fontSize: 14, textAlign: "center" },
  title: { color: "#FF6B35", fontSize: 24, fontWeight: "800", marginTop: 20, marginBottom: 8 },
  subtitle: { color: "#888", fontSize: 14, marginBottom: 32 },
  qrWrapper: { backgroundColor: "#FFFFFF", padding: 16, borderRadius: 16, marginBottom: 32 },
  addressBox: { backgroundColor: "#1A1A1A", borderRadius: 12, padding: 16, width: "100%", alignItems: "center", borderWidth: 1, borderColor: "#333" },
  addressLabel: { color: "#888", fontSize: 10, textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 },
  address: { color: "#FFF", fontSize: 13, fontFamily: "monospace", textAlign: "center" },
  copyBtn: { backgroundColor: "#FF6B35", paddingVertical: 14, paddingHorizontal: 48, borderRadius: 12, marginTop: 24 },
  copyBtnText: { color: "#FFF", fontSize: 16, fontWeight: "700" },
  info: { color: "#555", fontSize: 12, textAlign: "center", marginTop: 24, lineHeight: 18 },
});
