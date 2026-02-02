# RustChain Payment Widget

[![RTC](https://img.shields.io/badge/RTC-Payment-orange)](https://github.com/Scottcjn/Rustchain)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A drop-in payment widget for accepting RTC (RustChain Token) payments on any website. Like Stripe's checkout button, but for RustChain.

## Features

- 🔒 **Client-side signing** - Private keys never leave the browser
- 📱 **QR Code support** - Scan with mobile wallet apps
- 🎨 **Clean, responsive UI** - Works on all devices
- ⚡ **No backend required** - Direct communication with RustChain nodes
- 🔧 **Zero dependencies** - Self-contained, ~50KB bundle
- 🛡️ **Ed25519 cryptography** - Industry-standard security

## Quick Start

### 1. Include the Script

```html
<script src="https://your-cdn.com/rustchain-pay.js"></script>
```

Or host it yourself:

```html
<script src="rustchain-pay.js"></script>
```

### 2. Add a Payment Button

```html
<div id="rtc-pay"
     data-to="RTC1234567890abcdef1234567890abcdef12345678"
     data-amount="10"
     data-memo="Order #12345">
</div>
```

That's it! The widget automatically creates a styled "Pay X RTC" button.

## Configuration

### HTML Attributes

| Attribute | Description | Required |
|-----------|-------------|----------|
| `data-to` | Recipient wallet address | ✅ Yes |
| `data-amount` | Payment amount in RTC | ✅ Yes |
| `data-memo` | Optional memo/note | No |
| `data-node` | Custom node URL | No |
| `data-callback` | Webhook URL for notifications | No |
| `data-onsuccess` | Success callback function name | No |
| `data-onerror` | Error callback function name | No |

### JavaScript API

```javascript
// Open payment modal programmatically
RustChainPay.open({
  to: 'RTCrecipientaddress...',
  amount: '25',
  memo: 'Invoice #456',
  node: 'https://custom-node.example.com', // optional
  callback: 'https://your-site.com/webhook', // optional
  onSuccess: (result) => {
    console.log('Payment complete!', result.tx_hash);
  },
  onError: (err) => {
    console.error('Payment failed:', err.message);
  }
});

// Close modal
RustChainPay.close();

// Create button manually
const btn = RustChainPay.createButton({
  to: 'RTCaddress...',
  amount: '5'
});
document.body.appendChild(btn);

// Re-initialize (after dynamic content load)
RustChainPay.init();
```

## Payment Flow

1. User clicks "Pay X RTC" button
2. Modal opens with payment details and QR code
3. User can:
   - **Scan QR** with a mobile wallet app, OR
   - **Sign directly** using keystore file or seed phrase
4. Transaction is signed client-side (Ed25519)
5. Signed transaction sent to `/wallet/transfer/signed`
6. Success/failure shown with TX details

## Multiple Buttons

Use `data-rtc-pay` attribute for multiple buttons:

```html
<div data-rtc-pay data-to="RTC..." data-amount="1" data-memo="Tip"></div>
<div data-rtc-pay data-to="RTC..." data-amount="5" data-memo="Coffee"></div>
<div data-rtc-pay data-to="RTC..." data-amount="25" data-memo="Donation"></div>
```

## Webhooks

Set `data-callback` to receive payment notifications:

```html
<div id="rtc-pay"
     data-to="RTC..."
     data-amount="10"
     data-callback="https://your-site.com/payment-webhook">
</div>
```

Your webhook receives a POST with:

```json
{
  "status": "success",
  "tx": {
    "tx_hash": "abc123...",
    "from": "RTCsender...",
    "to": "RTCrecipient...",
    "amount": 10,
    "memo": "Order #12345"
  }
}
```

## Styling

The widget uses scoped CSS classes prefixed with `rtc-`. Override styles as needed:

```css
/* Custom button color */
.rtc-pay-button {
  background: linear-gradient(135deg, #your-color 0%, #your-color2 100%);
}

/* Custom modal width */
.rtc-modal {
  max-width: 500px;
}
```

## Security

### Client-Side Signing

All cryptographic operations happen in the browser:

- Private keys are **never** sent to any server
- Ed25519 signing uses bundled TweetNaCl.js
- Keystore decryption uses Web Crypto API (PBKDF2 + AES-256-GCM)

### No External Dependencies

The widget is completely self-contained:

- No CDN requests
- No tracking
- No third-party code

### Best Practices

1. **Always use HTTPS** - Protect against MITM attacks
2. **Verify the script** - Check the hash before deploying
3. **Use CSP headers** - Restrict script sources
4. **Monitor transactions** - Set up webhook notifications

## Browser Support

- Chrome 67+
- Firefox 68+
- Safari 12+
- Edge 79+

Requires Web Crypto API for secure key derivation.

## API Endpoints

The widget communicates with RustChain nodes:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/wallet/transfer/signed` | POST | Submit signed transaction |
| `/wallet/balance` | GET | Check wallet balance |
| `/health` | GET | Node health check |

Default node: `https://50.28.86.131`

## Examples

### E-commerce Checkout

```html
<div class="checkout-button"
     data-rtc-pay
     data-to="RTCshopwallet..."
     data-amount="49.99"
     data-memo="Order #ORD-2024-001"
     data-callback="https://shop.example.com/verify-payment"
     data-onsuccess="handlePaymentSuccess">
</div>

<script>
function handlePaymentSuccess(result) {
  // Redirect to order confirmation
  window.location.href = '/order-complete?tx=' + result.tx_hash;
}
</script>
```

### Donation Button

```html
<div id="donate"
     data-rtc-pay
     data-to="RTCcharitywallet..."
     data-amount="5"
     data-memo="Thank you for your support!">
</div>
```

### Subscription Payment

```javascript
// Monthly subscription
document.getElementById('subscribe-btn').onclick = () => {
  RustChainPay.open({
    to: 'RTCservicewallet...',
    amount: '15',
    memo: `Subscription - ${new Date().toISOString().slice(0,7)}`,
    onSuccess: (result) => {
      // Activate subscription
      fetch('/api/activate-subscription', {
        method: 'POST',
        body: JSON.stringify({ tx: result.tx_hash })
      });
    }
  });
};
```

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Please read the [contribution guidelines](../../CONTRIBUTING.md) first.

## Links

- [RustChain Repository](https://github.com/Scottcjn/Rustchain)
- [RustChain Bounties](https://github.com/Scottcjn/rustchain-bounties)
- [Explorer](https://50.28.86.131/explorer)
- [Network Health](https://50.28.86.131/health)
