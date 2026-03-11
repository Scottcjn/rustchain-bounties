// SPDX-License-Identifier: MIT
/**
 * RustChain Mobile Wallet — main entry point.
 *
 * Provides bottom-tab navigation between three core screens:
 *   1. Balance   – live RTC balance display
 *   2. History   – transaction / reward log
 *   3. Receive   – QR code with the user's wallet address
 *
 * Bounty: #1616
 */

import React, { useState, useCallback, useMemo } from 'react';
import { StatusBar } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import BalanceScreen from './src/screens/BalanceScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import ReceiveScreen from './src/screens/ReceiveScreen';
import { WalletProvider } from './src/utils/WalletContext';
import { COLORS } from './src/utils/theme';

const Tab = createBottomTabNavigator();

const TAB_ICONS = {
  Balance: { focused: '💰', default: '💳' },
  History: { focused: '📋', default: '📄' },
  Receive: { focused: '📲', default: '📱' },
};

export default function App() {
  return (
    <WalletProvider>
      <NavigationContainer>
        <StatusBar barStyle="light-content" backgroundColor={COLORS.bgPrimary} />
        <Tab.Navigator
          screenOptions={({ route }) => ({
            headerStyle: { backgroundColor: COLORS.bgSecondary },
            headerTintColor: COLORS.textPrimary,
            tabBarStyle: {
              backgroundColor: COLORS.bgSecondary,
              borderTopColor: COLORS.border,
            },
            tabBarActiveTintColor: COLORS.accentBlue,
            tabBarInactiveTintColor: COLORS.textSecondary,
            tabBarLabel: route.name,
          })}
        >
          <Tab.Screen
            name="Balance"
            component={BalanceScreen}
            options={{ title: 'Balance' }}
          />
          <Tab.Screen
            name="History"
            component={HistoryScreen}
            options={{ title: 'History' }}
          />
          <Tab.Screen
            name="Receive"
            component={ReceiveScreen}
            options={{ title: 'Receive' }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </WalletProvider>
  );
}
