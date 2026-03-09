# RustChain API Call Walkthrough

RustChain provides an API for interacting with the blockchain, including functionalities such as querying balances, initiating transfers, and more. This document will walk you through the first API call and show an example of how to sign a transfer request.

## Making Your First API Call

To make an API call to the RustChain API, follow these steps:

1. **Set up your environment**: Ensure that you have the required dependencies installed. You'll need Python and `requests` library to interact with the API.

2. **Get your API Key**: You'll need an API key to authenticate requests. You can obtain this from your RustChain account dashboard.

3. **Making a GET request**: You can start by querying the current blockchain status. The following Python code shows how to make a simple GET request to the RustChain API:

```python
import requests

url = 'https://api.rustchain.com/status'
headers = {'Authorization': 'Bearer YOUR_API_KEY'}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print('Error:', response.status_code)
```

## Signed Transfer Example

Now, let's go through an example of a signed transfer. To send a transaction, you need to create a signed message using your private key.

1. **Prepare your transaction**: Define the transfer details, including the sender, recipient, amount, and any other parameters.

2. **Sign the transaction**: Using your private key, sign the transaction to ensure its authenticity. Here's an example of signing a transfer with Python:

```python
import hashlib
import base64
import json
from ecdsa import SECP256k1, SigningKey

# Transaction details
transaction = {
    'sender': '0xYourSenderAddress',
    'recipient': '0xRecipientAddress',
    'amount': 100,
    'timestamp': 1640995200
}

# Convert the transaction to a JSON string
transaction_json = json.dumps(transaction)
transaction_hash = hashlib.sha256(transaction_json.encode()).hexdigest()

# Sign the hash using your private key
private_key = b'YOUR_PRIVATE_KEY'
sk = SigningKey.from_string(private_key, curve=SECP256k1)
signature = sk.sign(transaction_hash.encode())

# Base64 encode the signature for transmission
signature_b64 = base64.b64encode(signature).decode('utf-8')

print(f'Signed Transaction: {signature_b64}')
```

3. **Send the transaction**: After signing the transaction, you can send it to the RustChain network using a POST request:

```python
url = 'https://api.rustchain.com/transfer'
payload = {
    'transaction': transaction,
    'signature': signature_b64
}
response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print('Transfer Successful:', response.json())
else:
    print('Error:', response.status_code)
```

This will send the signed transfer to the RustChain network and print the result of the transaction.

## Conclusion

This guide provided a simple walkthrough of how to interact with the RustChain API. By following these steps, you can make API calls and sign transactions to perform transfers on the RustChain network.