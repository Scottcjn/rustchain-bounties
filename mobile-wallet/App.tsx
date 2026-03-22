// SPDX-License-Identifier: MIT
/**
 * RustChain Mobile Wallet
 *
 * Balance check, transaction history, and QR receive.
 * Built with React Native + Expo.
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  RefreshControl,
  ActivityIndicator,
} from "react-native";
import { StatusBar } from "expo-status-bar";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import QRCode from "expo-qrcode";

import { WalletScreen } from "./src/screens/WalletScreen";
import { ReceiveScreen } from "./src/screens/ReceiveScreen";
import { SendScreen } from "./src/screens/SendScreen";

export type RootTabParamList = {
  Wallet: undefined;
  Receive: undefined;
  Send: undefined;
};

const Tab = createBottomTabNavigator<RootTabParamList>();

export const WalletContext = React.createContext<{
  wallet: string;
  setWallet: (w: string) => void;
  apiKey: string;
  setApiKey: (k: string) => void;
}>({
  wallet: "",
  setWallet: () => {},
  apiKey: "",
  setApiKey: () => {},
});

export default function App() {
  const [wallet, setWallet] = useState("");
  const [apiKey, setApiKey] = useState(
    process.env.EXPO_PUBLIC_RUSTCHAIN_API_KEY || ""
  );

  return (
    <WalletContext.Provider value={{ wallet, setWallet, apiKey, setApiKey }}>
      <NavigationContainer>
        <StatusBar style="dark" />
        <Tab.Navigator
          screenOptions={{
            tabBarActiveTintColor: "#FF6B35",
            tabBarInactiveTintColor: "#888",
            tabBarStyle: { paddingBottom: 8, paddingTop: 4, height: 60 },
            headerStyle: { backgroundColor: "#0A0A0A" },
            headerTintColor: "#FF6B35",
            headerTitleStyle: { fontWeight: "700" },
          }}
        >
          <Tab.Screen name="Wallet" component={WalletScreen} options={{ title: "Balance" }} />
          <Tab.Screen name="Receive" component={ReceiveScreen} options={{ title: "Receive" }} />
          <Tab.Screen name="Send" component={SendScreen} options={{ title: "Send" }} />
        </Tab.Navigator>
      </NavigationContainer>
    </WalletContext.Provider>
  );
}
