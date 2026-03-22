# RustChain Mobile Wallet

React Native / Expo mobile wallet for RustChain (RTC) tokens.

## Features

- **Balance check** — View your RTC balance and pending transactions
- **Transaction history** — See your last 20 transactions
- **QR Receive** — Display your wallet address as a QR code
- **Send RTC** — Transfer tokens to other wallets (requires API key)
- **Dark theme** — RustChain orange accent on black

## Screens

| Screen | Description |
|--------|-------------|
| Balance | Shows current RTC balance, pending, and transaction list |
| Receive | QR code + copyable wallet address |
| Send | Transfer form (requires API key) |

## Setup

```bash
cd mobile-wallet
npm install
npm start        # Start Expo dev server
npm run android  # Android
npm run ios       # iOS
```

## Environment Variables

```bash
EXPO_PUBLIC_RUSTCHAIN_API_KEY=your-api-key
EXPO_PUBLIC_RUSTCHAIN_NODE_URL=https://50.28.86.131
```

## Tech Stack

- **React Native** + **Expo** (SDK 52)
- **TypeScript**
- **React Navigation** (bottom tabs)
- **expo-qrcode** (QR generation)
- **expo-clipboard** (copy address)

## License

MIT
