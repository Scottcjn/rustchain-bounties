import { Codec, Decoder, Encoder, FixedSizeCodec, FixedSizeDecoder, FixedSizeEncoder, VariableSizeCodec, VariableSizeDecoder, VariableSizeEncoder } from './codec';
import { ReadonlyUint8Array } from './readonly-uint8array';
/**
 * Creates an encoder that writes a `Uint8Array` sentinel after the encoded value.
 * This is useful to delimit the encoded value when being read by a decoder.
 *
 * See {@link addCodecSentinel} for more information.
 *
 * @typeParam TFrom - The type of the value to encode.
 *
 * @see {@link addCodecSentinel}
 */
export declare function addEncoderSentinel<TFrom>(encoder: FixedSizeEncoder<TFrom>, sentinel: ReadonlyUint8Array): FixedSizeEncoder<TFrom>;
export declare function addEncoderSentinel<TFrom>(encoder: Encoder<TFrom>, sentinel: ReadonlyUint8Array): VariableSizeEncoder<TFrom>;
/**
 * Creates a decoder that continues reading until
 * a given `Uint8Array` sentinel is found.
 *
 * See {@link addCodecSentinel} for more information.
 *
 * @typeParam TTo - The type of the decoded value.
 *
 * @see {@link addCodecSentinel}
 */
export declare function addDecoderSentinel<TTo>(decoder: FixedSizeDecoder<TTo>, sentinel: ReadonlyUint8Array): FixedSizeDecoder<TTo>;
export declare function addDecoderSentinel<TTo>(decoder: Decoder<TTo>, sentinel: ReadonlyUint8Array): VariableSizeDecoder<TTo>;
/**
 * Creates a Codec that writes a given `Uint8Array` sentinel after the encoded
 * value and, when decoding, continues reading until the sentinel is found.
 *
 * This sets a limit on variable-size codecs and tells us when to stop decoding.
 *
 * @typeParam TFrom - The type of the value to encode.
 * @typeParam TTo - The type of the decoded value.
 *
 * @example
 * ```ts
 * const codec = addCodecSentinel(getUtf8Codec(), new Uint8Array([255, 255]));
 * codec.encode('hello');
 * // 0x68656c6c6fffff
 * //   |        └-- Our sentinel.
 * //   └-- Our encoded string.
 * ```
 *
 * @remarks
 * Note that the sentinel _must not_ be present in the encoded data and
 * _must_ be present in the decoded data for this to work.
 * If this is not the case, dedicated errors will be thrown.
 *
 * ```ts
 * const sentinel = new Uint8Array([108, 108]); // 'll'
 * const codec = addCodecSentinel(getUtf8Codec(), sentinel);
 *
 * codec.encode('hello'); // Throws: sentinel is in encoded data.
 * codec.decode(new Uint8Array([1, 2, 3])); // Throws: sentinel missing in decoded data.
 * ```
 *
 * Separate {@link addEncoderSentinel} and {@link addDecoderSentinel} functions are also available.
 *
 * ```ts
 * const bytes = addEncoderSentinel(getUtf8Encoder(), sentinel).encode('hello');
 * const value = addDecoderSentinel(getUtf8Decoder(), sentinel).decode(bytes);
 * ```
 *
 * @see {@link addEncoderSentinel}
 * @see {@link addDecoderSentinel}
 */
export declare function addCodecSentinel<TFrom, TTo extends TFrom>(codec: FixedSizeCodec<TFrom, TTo>, sentinel: ReadonlyUint8Array): FixedSizeCodec<TFrom, TTo>;
export declare function addCodecSentinel<TFrom, TTo extends TFrom>(codec: Codec<TFrom, TTo>, sentinel: ReadonlyUint8Array): VariableSizeCodec<TFrom, TTo>;
//# sourceMappingURL=add-codec-sentinel.d.ts.map