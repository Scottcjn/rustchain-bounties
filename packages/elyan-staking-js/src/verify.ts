// SPDX-License-Identifier: MIT
import { createPublicKey, verify as nodeVerify } from "node:crypto";
import { canonicalBytes } from "./canonical.js";

/**
 * Verify an Ed25519 signature over a canonical-JSON message.
 *
 * @param message  The original verdict object (will be canonicalized).
 * @param signature Raw 64-byte Ed25519 signature.
 * @param publicKey Raw 32-byte Ed25519 public key.
 * @returns true iff signature is valid; false otherwise. Never throws on bad input.
 */
export function verifyEd25519(
  message: unknown,
  signature: Uint8Array,
  publicKey: Uint8Array,
): boolean {
  try {
    if (publicKey.length !== 32) return false;
    if (signature.length !== 64) return false;
    // Wrap the raw 32-byte key in a SubjectPublicKeyInfo DER for Node's KeyObject.
    const spki = new Uint8Array([
      0x30, 0x2a, 0x30, 0x05, 0x06, 0x03, 0x2b, 0x65, 0x70, 0x03, 0x21, 0x00,
      ...publicKey,
    ]);
    const key = createPublicKey({
      key: Buffer.from(spki),
      format: "der",
      type: "spki",
    });
    return nodeVerify(null, canonicalBytes(message), key, signature);
  } catch {
    return false;
  }
}

export function hexToBytes(hex: string): Uint8Array {
  const clean = hex.startsWith("0x") ? hex.slice(2) : hex;
  if (clean.length % 2 !== 0) throw new Error("invalid hex length");
  const out = new Uint8Array(clean.length / 2);
  for (let i = 0; i < out.length; i++) {
    out[i] = parseInt(clean.slice(i * 2, i * 2 + 2), 16);
  }
  return out;
}

export function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}
