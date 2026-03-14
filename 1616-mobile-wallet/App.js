import React, { useState } from 'react';
import { StyleSheet, Text, View, TextInput, Button, FlatList, SafeAreaView } from 'react-native';

export default function App() {
  const [address, setAddress] = useState('');
  const [balance, setBalance] = useState(null);
  const [transactions, setTransactions] = useState([]);

  const checkBalance = async () => {
    try {
      const response = await fetch('https://rpc.rustchain.com', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'eth_getBalance',
          params: [address, 'latest'],
          id: 1
        })
      });
      const data = await response.json();
      if (data.result) {
        const balance = parseInt(data.result, 16) / 1e18;
        setBalance(balance.toFixed(4));
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const renderTransaction = ({ item }) => (
    <View style={styles.txItem}>
      <Text style={styles.txHash}>{item.hash.substring(0, 10)}...</Text>
      <Text style={styles.txValue}>{item.value} RTC</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>🔗 RustChain Wallet</Text>
      
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Enter RTC address"
          placeholderTextColor="#888"
          value={address}
          onChangeText={setAddress}
        />
        <Button title="Check Balance" onPress={checkBalance} color="#00d9ff" />
      </View>

      {balance && (
        <View style={styles.balanceContainer}>
          <Text style={styles.balanceLabel}>Balance</Text>
          <Text style={styles.balanceValue}>{balance} RTC</Text>
        </View>
      )}

      <View style={styles.txContainer}>
        <Text style={styles.txTitle}>Recent Transactions</Text>
        <FlatList
          data={transactions}
          renderItem={renderTransaction}
          keyExtractor={(item, index) => index.toString()}
        />
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#1a1a2e', padding: 20 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#00d9ff', textAlign: 'center', marginBottom: 30 },
  inputContainer: { marginBottom: 20 },
  input: { backgroundColor: '#16213e', color: '#fff', padding: 15, borderRadius: 10, marginBottom: 10, borderWidth: 1, borderColor: '#00d9ff' },
  balanceContainer: { alignItems: 'center', marginBottom: 30 },
  balanceLabel: { color: '#888', fontSize: 16 },
  balanceValue: { color: '#00d9ff', fontSize: 48, fontWeight: 'bold' },
  txContainer: { flex: 1 },
  txTitle: { color: '#fff', fontSize: 18, marginBottom: 10 },
  txItem: { flexDirection: 'row', justifyContent: 'space-between', padding: 15, backgroundColor: '#16213e', borderRadius: 10, marginBottom: 10 },
  txHash: { color: '#fff', fontFamily: 'monospace' },
  txValue: { color: '#00d9ff', fontWeight: 'bold' }
});
