import nacl from 'tweetnacl';
import { scrypt } from 'scrypt-js';

// BIP39 wordlist (simplified version - in production use full 2048 words)
const BIP39_WORDLIST = [
    'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
    'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
    'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
    'adapt', 'add', 'addict', 'address', 'adjust', 'admit', 'adult', 'advance',
    'advice', 'aerobic', 'affair', 'afford', 'afraid', 'again', 'against', 'age'
    // ... add remaining 2008 words for production
];

class RustChainWallet {
    constructor() {
        this.accounts = new Map();
        this.currentAccount = null;
    }

    /**
     * Generate BIP39 mnemonic phrase
     */
    generateMnemonic(strength = 128) {
        const entropy = new Uint8Array(strength / 8);
        crypto.getRandomValues(entropy);
        
        // Convert entropy to binary string
        let binaryString = '';
        for (let byte of entropy) {
            binaryString += byte.toString(2).padStart(8, '0');
        }
        
        // Add checksum
        const hash = this._sha256(entropy);
        const checksumBits = Math.floor(entropy.length * 8 / 32);
        const checksum = this._bytesToBinary(hash.slice(0, 1)).slice(0, checksumBits);
        binaryString += checksum;
        
        // Split into 11-bit groups and convert to words
        const words = [];
        for (let i = 0; i < binaryString.length; i += 11) {
            const index = parseInt(binaryString.slice(i, i + 11), 2);
            words.push(BIP39_WORDLIST[index % BIP39_WORDLIST.length]);
        }
        
        return words.join(' ');
    }

    /**
     * Derive seed from mnemonic using PBKDF2
     */
    async mnemonicToSeed(mnemonic, passphrase = '') {
        const mnemonicBuffer = new TextEncoder().encode(mnemonic);
        const saltBuffer = new TextEncoder().encode('mnemonic' + passphrase);
        
        const key = await crypto.subtle.importKey(
            'raw',
            mnemonicBuffer,
            { name: 'PBKDF2' },
            false,
            ['deriveBits']
        );
        
        const seed = await crypto.subtle.deriveBits(
            {
                name: 'PBKDF2',
                salt: saltBuffer,
                iterations: 2048,
                hash: 'SHA-512'
            },
            key,
            512
        );
        
        return new Uint8Array(seed);
    }

    /**
     * Generate Ed25519 keypair from seed
     */
    generateKeyPair(seed, index = 0) {
        // Use seed + index to derive private key
        const derivedSeed = this._deriveKey(seed, index);
        const keyPair = nacl.sign.keyPair.fromSeed(derivedSeed.slice(0, 32));
        
        return {
            publicKey: keyPair.publicKey,
            privateKey: keyPair.secretKey
        };
    }

    /**
     * Create new wallet from mnemonic
     */
    async createWallet(mnemonic, password, accountName = 'Account 1') {
        const seed = await this.mnemonicToSeed(mnemonic);
        const keyPair = this.generateKeyPair(seed, 0);
        
        const account = {
            name: accountName,
            publicKey: this._bytesToHex(keyPair.publicKey),
            address: this._publicKeyToAddress(keyPair.publicKey),
            mnemonic: mnemonic,
            seed: seed,
            privateKey: keyPair.privateKey
        };
        
        // Encrypt and store
        const encryptedWallet = await this._encryptWallet(account, password);
        const accountId = this._generateAccountId();
        
        this.accounts.set(accountId, {
            ...account,
            encrypted: encryptedWallet,
            isLocked: false
        });
        
        this.currentAccount = accountId;
        return accountId;
    }

    /**
     * Import wallet from mnemonic
     */
    async importWallet(mnemonic, password, accountName = 'Imported Account') {
        return await this.createWallet(mnemonic, password, accountName);
    }

    /**
     * Sign transaction with Ed25519
     */
    signTransaction(accountId, transactionData) {
        const account = this.accounts.get(accountId);
        if (!account || account.isLocked) {
            throw new Error('Account not found or locked');
        }
        
        const messageBytes = new TextEncoder().encode(JSON.stringify(transactionData));
        const signature = nacl.sign.detached(messageBytes, account.privateKey);
        
        return {
            signature: this._bytesToHex(signature),
            publicKey: account.publicKey,
            transaction: transactionData
        };
    }

    /**
     * Sign arbitrary message
     */
    signMessage(accountId, message) {
        const account = this.accounts.get(accountId);
        if (!account || account.isLocked) {
            throw new Error('Account not found or locked');
        }
        
        const messageBytes = new TextEncoder().encode(message);
        const signature = nacl.sign.detached(messageBytes, account.privateKey);
        
        return {
            signature: this._bytesToHex(signature),
            publicKey: account.publicKey,
            message: message
        };
    }

    /**
     * Encrypt wallet with AES-256-GCM
     */
    async _encryptWallet(account, password) {
        const salt = crypto.getRandomValues(new Uint8Array(16));
        const iv = crypto.getRandomValues(new Uint8Array(12));
        
        // Derive key using scrypt
        const key = await scrypt(
            new TextEncoder().encode(password),
            salt,
            16384, // N
            8,     // r
            1,     // p
            32     // dkLen
        );
        
        const cryptoKey = await crypto.subtle.importKey(
            'raw',
            key,
            { name: 'AES-GCM' },
            false,
            ['encrypt']
        );
        
        const plaintext = JSON.stringify({
            mnemonic: account.mnemonic,
            privateKey: this._bytesToHex(account.privateKey),
            seed: this._bytesToHex(account.seed)
        });
        
        const ciphertext = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv: iv },
            cryptoKey,
            new TextEncoder().encode(plaintext)
        );
        
        return {
            salt: this._bytesToHex(salt),
            iv: this._bytesToHex(iv),
            ciphertext: this._bytesToHex(new Uint8Array(ciphertext))
        };
    }

    /**
     * Decrypt wallet
     */
    async _decryptWallet(encryptedData, password) {
        const salt = this._hexToBytes(encryptedData.salt);
        const iv = this._hexToBytes(encryptedData.iv);
        const ciphertext = this._hexToBytes(encryptedData.ciphertext);
        
        // Derive key using scrypt
        const key = await scrypt(
            new TextEncoder().encode(password),
            salt,
            16384, // N
            8,     // r
            1,     // p
            32     // dkLen
        );
        
        const cryptoKey = await crypto.subtle.importKey(
            'raw',
            key,
            { name: 'AES-GCM' },
            false,
            ['decrypt']
        );
        
        const plaintext = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv: iv },
            cryptoKey,
            ciphertext
        );
        
        return JSON.parse(new TextDecoder().decode(plaintext));
    }

    /**
     * Lock wallet
     */
    lockWallet(accountId) {
        const account = this.accounts.get(accountId);
        if (account) {
            account.isLocked = true;
            // Clear sensitive data from memory
            delete account.privateKey;
            delete account.seed;
            delete account.mnemonic;
        }
    }

    /**
     * Unlock wallet
     */
    async unlockWallet(accountId, password) {
        const account = this.accounts.get(accountId);
        if (!account) {
            throw new Error('Account not found');
        }
        
        const decryptedData = await this._decryptWallet(account.encrypted, password);
        
        account.privateKey = this._hexToBytes(decryptedData.privateKey);
        account.seed = this._hexToBytes(decryptedData.seed);
        account.mnemonic = decryptedData.mnemonic;
        account.isLocked = false;
        
        return true;
    }

    /**
     * Get account info
     */
    getAccount(accountId) {
        const account = this.accounts.get(accountId);
        if (!account) return null;
        
        return {
            id: accountId,
            name: account.name,
            address: account.address,
            publicKey: account.publicKey,
            isLocked: account.isLocked
        };
    }

    /**
     * List all accounts
     */
    getAccounts() {
        return Array.from(this.accounts.entries()).map(([id, account]) => ({
            id,
            name: account.name,
            address: account.address,
            publicKey: account.publicKey,
            isLocked: account.isLocked
        }));
    }

    // Utility methods
    _sha256(data) {
        // Simple SHA-256 implementation or use crypto.subtle.digest
        return crypto.subtle.digest('SHA-256', data);
    }

    _deriveKey(seed, index) {
        // Simple key derivation - use HMAC-SHA512 in production
        const combined = new Uint8Array(seed.length + 4);
        combined.set(seed);
        combined.set(new Uint8Array(new Uint32Array([index]).buffer), seed.length);
        return combined;
    }

    _publicKeyToAddress(publicKey) {
        // Simple address derivation - implement proper RustChain address format
        const hash = this._sha256(publicKey);
        return 'RC' + this._bytesToHex(hash.slice(0, 20));
    }

    _bytesToHex(bytes) {
        return Array.from(bytes)
            .map(byte => byte.toString(16).padStart(2, '0'))
            .join('');
    }

    _hexToBytes(hex) {
        const result = new Uint8Array(hex.length / 2);
        for (let i = 0; i < hex.length; i += 2) {
            result[i / 2] = parseInt(hex.substr(i, 2), 16);
        }
        return result;
    }

    _bytesToBinary(bytes) {
        return Array.from(bytes)
            .map(byte => byte.toString(2).padStart(8, '0'))
            .join('');
    }

    _generateAccountId() {
        return 'account_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
}

export default RustChainWallet;