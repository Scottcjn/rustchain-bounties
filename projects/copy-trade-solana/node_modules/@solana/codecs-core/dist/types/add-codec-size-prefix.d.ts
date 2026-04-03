import { Codec, Decoder, Encoder, FixedSizeCodec, FixedSizeDecoder, FixedSizeEncoder, VariableSizeCodec, VariableSizeDecoder, VariableSizeEncoder } from './codec';
type NumberEncoder = Encoder<bigint | number> | Encoder<number>;
type FixedSizeNumberEncoder<TSize extends number = number> = FixedSizeEncoder<bigint | number, TSize> | FixedSizeEncoder<number, TSize>;
type NumberDecoder = Decoder<bigint> | Decoder<number>;
type FixedSizeNumberDecoder<TSize extends number = number> = FixedSizeDecoder<bigint, TSize> | FixedSizeDecoder<number, TSize>;
type NumberCodec = Codec<bigint | number, bigint> | Codec<number>;
type FixedSizeNumberCodec<TSize extends number = number> = FixedSizeCodec<bigint | number, bigint, TSize> | FixedSizeCodec<number, number, TSize>;
/**
 * Stores the size of the `encoder` in bytes as a prefix using the `prefix` encoder.
 *
 * See {@link addCodecSizePrefix} for more information.
 *
 * @typeParam TFrom - The type of the value to encode.
 *
 * @see {@link addCodecSizePrefix}
 */
export declare function addEncoderSizePrefix<TFrom>(encoder: FixedSizeEncoder<TFrom>, prefix: FixedSizeNumberEncoder): FixedSizeEncoder<TFrom>;
export declare function addEncoderSizePrefix<TFrom>(encoder: Encoder<TFrom>, prefix: NumberEncoder): VariableSizeEncoder<TFrom>;
/**
 * Bounds the size of the nested `decoder` by reading its encoded `prefix`.
 *
 * See {@link addCodecSizePrefix} for more information.
 *
 * @typeParam TTo - The type of the decoded value.
 *
 * @see {@link addCodecSizePrefix}
 */
export declare function addDecoderSizePrefix<TTo>(decoder: FixedSizeDecoder<TTo>, prefix: FixedSizeNumberDecoder): FixedSizeDecoder<TTo>;
export declare function addDecoderSizePrefix<TTo>(decoder: Decoder<TTo>, prefix: NumberDecoder): VariableSizeDecoder<TTo>;
/**
 * Stores the byte size of any given codec as an encoded number prefix.
 *
 * This sets a limit on variable-size codecs and tells us when to stop decoding.
 * When encoding, the size of the encoded data is stored before the encoded data itself.
 * When decoding, the size is read first to know how many bytes to read next.
 *
 * @typeParam TFrom - The type of the value to encode.
 * @typeParam TTo - The type of the decoded value.
 *
 * @example
 * For example, say we want to bound a variable-size base-58 string using a `u32` size prefix.
 * Here’s how you can use the `addCodecSizePrefix` function to achieve that.
 *
 * ```ts
 * const getU32Base58Codec = () => addCodecSizePrefix(getBase58Codec(), getU32Codec());
 *
 * getU32Base58Codec().encode('hello world');
 * // 0x0b00000068656c6c6f20776f726c64
 * //   |       └-- Our encoded base-58 string.
 * //   └-- Our encoded u32 size prefix.
 * ```
 *
 * @remarks
 * Separate {@link addEncoderSizePrefix} and {@link addDecoderSizePrefix} functions are also available.
 *
 * ```ts
 * const bytes = addEncoderSizePrefix(getBase58Encoder(), getU32Encoder()).encode('hello');
 * const value = addDecoderSizePrefix(getBase58Decoder(), getU32Decoder()).decode(bytes);
 * ```
 *
 * @see {@link addEncoderSizePrefix}
 * @see {@link addDecoderSizePrefix}
 */
export declare function addCodecSizePrefix<TFrom, TTo extends TFrom>(codec: FixedSizeCodec<TFrom, TTo>, prefix: FixedSizeNumberCodec): FixedSizeCodec<TFrom, TTo>;
export declare function addCodecSizePrefix<TFrom, TTo extends TFrom>(codec: Codec<TFrom, TTo>, prefix: NumberCodec): VariableSizeCodec<TFrom, TTo>;
export {};
//# sourceMappingURL=add-codec-size-prefix.d.ts.map