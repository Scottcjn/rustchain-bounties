import { SolanaError } from './error';
export declare function getSolanaErrorFromInstructionError(
/**
 * The index of the instruction inside the transaction.
 */
index: bigint | number, instructionError: string | {
    [key: string]: unknown;
}): SolanaError;
//# sourceMappingURL=instruction-error.d.ts.map