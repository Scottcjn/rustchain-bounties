// SPDX-License-Identifier: MIT
// Canonical JSON serialization: sorted keys, no extra whitespace.
// Mirrors Python's `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`
// so signatures match byte-for-byte across language implementations.

export function canonicalize(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return "[" + value.map(canonicalize).join(",") + "]";
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  const parts = keys.map(
    (k) => JSON.stringify(k) + ":" + canonicalize(obj[k]),
  );
  return "{" + parts.join(",") + "}";
}

export function canonicalBytes(value: unknown): Uint8Array {
  return new TextEncoder().encode(canonicalize(value));
}
