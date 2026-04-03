/**
 * To add a new error, follow the instructions at
 * https://github.com/anza-xyz/kit/tree/main/packages/errors#adding-a-new-error
 *
 * WARNING:
 *   - Don't change the meaning of an error message.
 */
import { SolanaErrorCode } from './codes';
/**
 * A map of every {@link SolanaError} code to the error message shown to developers in development
 * mode.
 */
export declare const SolanaErrorMessages: Readonly<{
    [P in SolanaErrorCode]: string;
}>;
//# sourceMappingURL=messages.d.ts.map