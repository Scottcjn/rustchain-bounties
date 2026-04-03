import { ReadonlyUint8Array } from './readonly-uint8array';
/**
 * Concatenates an array of `Uint8Array`s into a single `Uint8Array`.
 * Reuses the original byte array when applicable.
 *
 * @param byteArrays - The array of byte arrays to concatenate.
 *
 * @example
 * ```ts
 * const bytes1 = new Uint8Array([0x01, 0x02]);
 * const bytes2 = new Uint8Array([]);
 * const bytes3 = new Uint8Array([0x03, 0x04]);
 * const bytes = mergeBytes([bytes1, bytes2, bytes3]);
 * //    ^ [0x01, 0x02, 0x03, 0x04]
 * ```
 */
export declare const mergeBytes: (byteArrays: Uint8Array[]) => Uint8Array;
/**
 * Pads a `Uint8Array` with zeroes to the specified length.
 * If the array is longer than the specified length, it is returned as-is.
 *
 * @param bytes - The byte array to pad.
 * @param length - The desired length of the byte array.
 *
 * @example
 * Adds zeroes to the end of the byte array to reach the desired length.
 * ```ts
 * const bytes = new Uint8Array([0x01, 0x02]);
 * const paddedBytes = padBytes(bytes, 4);
 * //    ^ [0x01, 0x02, 0x00, 0x00]
 * ```
 *
 * @example
 * Returns the original byte array if it is already at the desired length.
 * ```ts
 * const bytes = new Uint8Array([0x01, 0x02]);
 * const paddedBytes = padBytes(bytes, 2);
 * // bytes === paddedBytes
 * ```
 */
export declare const padBytes: (bytes: ReadonlyUint8Array | Uint8Array, length: number) => ReadonlyUint8Array | Uint8Array;
/**
 * Fixes a `Uint8Array` to the specified length.
 * If the array is longer than the specified length, it is truncated.
 * If the array is shorter than the specified length, it is padded with zeroes.
 *
 * @param bytes - The byte array to truncate or pad.
 * @param length - The desired length of the byte array.
 *
 * @example
 * Truncates the byte array to the desired length.
 * ```ts
 * const bytes = new Uint8Array([0x01, 0x02, 0x03, 0x04]);
 * const fixedBytes = fixBytes(bytes, 2);
 * //    ^ [0x01, 0x02]
 * ```
 *
 * @example
 * Adds zeroes to the end of the byte array to reach the desired length.
 * ```ts
 * const bytes = new Uint8Array([0x01, 0x02]);
 * const fixedBytes = fixBytes(bytes, 4);
 * //    ^ [0x01, 0x02, 0x00, 0x00]
 * ```
 *
 * @example
 * Returns the original byte array if it is already at the desired length.
 * ```ts
 * const bytes = new Uint8Array([0x01, 0x02]);
 * const fixedBytes = fixBytes(bytes, 2);
 * // bytes === fixedBytes
 * ```
 */
export declare const fixBytes: (bytes: ReadonlyUint8Array | Uint8Array, length: number) => ReadonlyUint8Array | Uint8Array;
/**
 * Returns true if and only if the provided `data` byte array contains
 * the provided `bytes` byte array at the specified `offset`.
 *
 * @param data - The byte sequence to search for.
 * @param bytes - The byte array in which to search for `data`.
 * @param offset - The position in `bytes` where the search begins.
 *
 * @example
 * ```ts
 * const bytes = new Uint8Array([0x01, 0x02, 0x03, 0x04]);
 * const data = new Uint8Array([0x02, 0x03]);
 * containsBytes(bytes, data, 1); // true
 * containsBytes(bytes, data, 2); // false
 * ```
 */
export declare function containsBytes(data: ReadonlyUint8Array | Uint8Array, bytes: ReadonlyUint8Array | Uint8Array, offset: number): boolean;
//# sourceMappingURL=bytes.d.ts.map