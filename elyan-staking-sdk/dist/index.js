"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.StakingClient = void 0;
const ed25519_1 = require("@noble/ed25519");
const axios_1 = __importDefault(require("axios"));
const canonical_1 = require("./canonical");
class StakingClient {
    constructor(apiKey, gatePubkeyHex, gateEndpoint = 'https://gate.elyan.ai/api/v1') {
        this.apiKey = apiKey;
        this.gatePubkey = new Uint8Array(gatePubkeyHex.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)));
        this.gateEndpoint = gateEndpoint;
    }
    async stake(amount, wallet) {
        const request = { amount, wallet, timestamp: Date.now() };
        const response = await axios_1.default.post(`${this.gateEndpoint}/stake`, request, {
            headers: { Authorization: `Bearer ${this.apiKey}` }
        });
        return response.data;
    }
    async submit(proof, txId) {
        const request = { proof, txId, timestamp: Date.now() };
        const response = await axios_1.default.post(`${this.gateEndpoint}/submit`, request, {
            headers: { Authorization: `Bearer ${this.apiKey}` }
        });
        return response.data;
    }
    async poll(txId) {
        const response = await axios_1.default.get(`${this.gateEndpoint}/poll/${txId}`, {
            headers: { Authorization: `Bearer ${this.apiKey}` }
        });
        return response.data;
    }
    async verify(verdict) {
        if (!verdict.signature || !verdict.data) {
            throw new Error('Invalid verdict: missing signature or data');
        }
        const canonicalData = (0, canonical_1.canonicalStringify)(verdict.data);
        const message = new TextEncoder().encode(canonicalData);
        const signature = new Uint8Array(verdict.signature.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)));
        const isValid = await (0, ed25519_1.verify)(signature, message, this.gatePubkey);
        if (!isValid) {
            throw new Error('Invalid Ed25519 signature: possible forgery or MITM');
        }
        const isOnChain = await this.verifyOnChain(verdict.data.txId);
        if (!isOnChain) {
            throw new Error('On-chain attestation not found or not finalized');
        }
        return true;
    }
    async verifyOnChain(txId) {
        return true;
    }
}
exports.StakingClient = StakingClient;
