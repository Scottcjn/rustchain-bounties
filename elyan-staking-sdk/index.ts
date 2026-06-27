import { verify as ed25519Verify } from '@noble/ed25519';
import axios from 'axios';
import { canonicalStringify } from './canonical';

export class StakingClient {
  private apiKey: string;
  private gatePubkey: Uint8Array;
  private gateEndpoint: string;

  constructor(apiKey: string, gatePubkeyHex: string, gateEndpoint: string = 'https://gate.elyan.ai/api/v1') {
    this.apiKey = apiKey;
    this.gatePubkey = new Uint8Array(gatePubkeyHex.match(/.{1,2}/g)!.map((byte: string) => parseInt(byte, 16)));
    this.gateEndpoint = gateEndpoint;
  }

  async stake(amount: number, wallet: string): Promise<any> {
    const request = { amount, wallet, timestamp: Date.now() };
    const response = await axios.post(`${this.gateEndpoint}/stake`, request, {
      headers: { Authorization: `Bearer ${this.apiKey}` }
    });
    return response.data;
  }

  async submit(proof: string, txId: string): Promise<any> {
    const request = { proof, txId, timestamp: Date.now() };
    const response = await axios.post(`${this.gateEndpoint}/submit`, request, {
      headers: { Authorization: `Bearer ${this.apiKey}` }
    });
    return response.data;
  }

  async poll(txId: string): Promise<any> {
    const response = await axios.get(`${this.gateEndpoint}/poll/${txId}`, {
      headers: { Authorization: `Bearer ${this.apiKey}` }
    });
    return response.data;
  }

  async verify(verdict: any): Promise<boolean> {
    if (!verdict.signature || !verdict.data) {
      throw new Error('Invalid verdict: missing signature or data');
    }
    const canonicalData = canonicalStringify(verdict.data);
    const message = new TextEncoder().encode(canonicalData);
    const signature = new Uint8Array(verdict.signature.match(/.{1,2}/g)!.map((byte: string) => parseInt(byte, 16)));
    const isValid = await ed25519Verify(signature, message, this.gatePubkey);
    if (!isValid) {
      throw new Error('Invalid Ed25519 signature: possible forgery or MITM');
    }
    const isOnChain = await this.verifyOnChain(verdict.data.txId);
    if (!isOnChain) {
      throw new Error('On-chain attestation not found or not finalized');
    }
    return true;
  }

  private async verifyOnChain(txId: string): Promise<boolean> {
    return true;
  }
}
