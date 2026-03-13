# Install RustChain Mobile Wallet

**Bounty**: #1616
**Value**: 20 RTC (~$2)

---

## Prerequisites

- Node.js >= 16
- npm or yarn
- React Native CLI
- Android Studio (for Android)
- Xcode (for iOS, macOS only)

---

## Installation Steps

### 1. Install Dependencies

```bash
cd mobile-wallet-app
npm install
```

### 2. Install React Native CLI

```bash
npm install -g react-native-cli
```

### 3. Setup Android (if developing for Android)

1. Install Android Studio
2. Install Android SDK
3. Create emulator or connect device

### 4. Run on Android

```bash
npm run android
```

### 5. Run on iOS (macOS only)

```bash
cd ios
pod install
cd ..
npm run ios
```

---

## Features

### Implemented
- ✅ Wallet creation
- ✅ Balance display
- ✅ Send RTC (UI)
- ✅ Receive RTC (UI)
- ✅ USD conversion

### TODO
- [ ] Actual send functionality
- [ ] Transaction history
- [ ] QR code scanner
- [ ] Secure storage
- [ ] BIP39 wallet generation
- [ ] Ed25519 signing

---

## Screenshots

### Home Screen
- Balance display
- Send/Receive buttons
- Wallet address

### Send Screen
- Address input
- Amount input
- Send button

---

## Configuration

Edit `src/config.js`:

```javascript
export const BASE_URL = 'https://50.28.86.131';
export const DEFAULT_WALLET = '';
```

---

## Testing

```bash
npm test
```

---

## Troubleshooting

### Issue: Metro bundler error

```bash
npx react-native start --reset-cache
```

### Issue: Android build failed

```bash
cd android
./gradlew clean
cd ..
npm run android
```

### Issue: iOS build failed

```bash
cd ios
pod deintegrate
pod install
cd ..
npm run ios
```

---

## Support

- GitHub Issues: https://github.com/Scottcjn/rustchain-bounties/issues
- Documentation: https://github.com/Scottcjn/RustChain

---

**Ready for PR submission!** 🚀
