import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  TextInput,
  Alert,
} from 'react-native';

const App = () => {
  const [balance, setBalance] = useState(0);
  const [walletAddress, setWalletAddress] = useState('');
  const [sendAddress, setSendAddress] = useState('');
  const [sendAmount, setSendAmount] = useState('');

  const BASE_URL = 'https://50.28.86.131';

  // Load wallet on startup
  useEffect(() => {
    loadWallet();
  }, []);

  const loadWallet = async () => {
    // TODO: Load wallet from secure storage
    // For now, use placeholder
    setWalletAddress('RTC' + Math.random().toString(36).substring(2, 42));
    fetchBalance();
  };

  const fetchBalance = async () => {
    try {
      const response = await fetch(
        `${BASE_URL}/wallet/balance?miner_id=${walletAddress}`
      );
      const data = await response.json();
      setBalance(data.amount_rtc || 0);
    } catch (error) {
      console.error('Failed to fetch balance:', error);
      Alert.alert('Error', 'Failed to fetch balance');
    }
  };

  const createWallet = () => {
    // TODO: Implement proper wallet creation with BIP39
    const newAddress = 'RTC' + Math.random().toString(36).substring(2, 42);
    setWalletAddress(newAddress);
    Alert.alert('Success', 'Wallet created: ' + newAddress);
    fetchBalance();
  };

  const sendRTC = async () => {
    if (!sendAddress || !sendAmount) {
      Alert.alert('Error', 'Please enter address and amount');
      return;
    }

    // TODO: Implement proper send functionality
    Alert.alert('Success', `Sent ${sendAmount} RTC to ${sendAddress}`);
    setSendAddress('');
    setSendAmount('');
    fetchBalance();
  };

  const receiveRTC = () => {
    Alert.alert(
      'Receive RTC',
      `Your wallet address:\n${walletAddress}\n\nShare this address to receive RTC.`
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>RustChain Wallet</Text>
      </View>

      <View style={styles.balanceCard}>
        <Text style={styles.balanceLabel}>Balance</Text>
        <Text style={styles.balanceAmount}>{balance.toFixed(2)} RTC</Text>
        <Text style={styles.balanceUSD}>≈ ${(balance * 0.1).toFixed(2)} USD</Text>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionButton} onPress={sendRTC}>
          <Text style={styles.actionButtonText}>Send</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton} onPress={receiveRTC}>
          <Text style={styles.actionButtonText}>Receive</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.sendCard}>
        <Text style={styles.cardTitle}>Send RTC</Text>
        <TextInput
          style={styles.input}
          placeholder="Wallet Address"
          value={sendAddress}
          onChangeText={setSendAddress}
        />
        <TextInput
          style={styles.input}
          placeholder="Amount (RTC)"
          value={sendAmount}
          onChangeText={setSendAmount}
          keyboardType="numeric"
        />
        <TouchableOpacity style={styles.sendButton} onPress={sendRTC}>
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.walletCard}>
        <Text style={styles.cardTitle}>Your Wallet</Text>
        <Text style={styles.walletAddress}>
          {walletAddress || 'No wallet created'}
        </Text>
        {!walletAddress && (
          <TouchableOpacity style={styles.createButton} onPress={createWallet}>
            <Text style={styles.createButtonText}>Create Wallet</Text>
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#3498db',
    alignItems: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: 'white',
  },
  balanceCard: {
    margin: 20,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  balanceLabel: {
    fontSize: 16,
    color: '#666',
  },
  balanceAmount: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#333',
    marginVertical: 10,
  },
  balanceUSD: {
    fontSize: 18,
    color: '#999',
  },
  actions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 20,
  },
  actionButton: {
    backgroundColor: '#3498db',
    paddingHorizontal: 40,
    paddingVertical: 15,
    borderRadius: 10,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  sendCard: {
    margin: 20,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 12,
    marginBottom: 15,
    fontSize: 16,
  },
  sendButton: {
    backgroundColor: '#2ecc71',
    paddingVertical: 15,
    borderRadius: 5,
    alignItems: 'center',
  },
  sendButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  walletCard: {
    margin: 20,
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  walletAddress: {
    fontSize: 14,
    color: '#666',
    fontFamily: 'monospace',
    marginBottom: 15,
  },
  createButton: {
    backgroundColor: '#9b59b6',
    paddingVertical: 15,
    borderRadius: 5,
    alignItems: 'center',
  },
  createButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default App;
