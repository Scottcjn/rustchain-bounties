import { SolanaError } from './error';
type TransactionError = string | {
    [key: string]: unknown;
};
/**
 * Keep in sync with https://github.com/anza-xyz/agave/blob/master/rpc-client-types/src/response.rs
 * @hidden
 */
export interface RpcSimulateTransactionResult {
    accounts: ({
        data: string | {
            parsed: unknown;
            program: string;
            space: number;
        } | [encodedBytes: string, encoding: 'base58' | 'base64' | 'base64+zstd' | 'binary' | 'jsonParsed'];
        executable: boolean;
        lamports: number;
        owner: string;
        rentEpoch: number;
        space?: number;
    } | null)[] | null;
    err: TransactionError | null;
    innerInstructions?: {
        index: number;
        instructions: ({
            accounts: number[];
            data: string;
            programIdIndex: number;
            stackHeight?: number;
        } | {
            parsed: unknown;
            program: string;
            programId: string;
            stackHeight?: number;
        } | {
            accounts: string[];
            data: string;
            programId: string;
            stackHeight?: number;
        })[];
    }[] | null;
    logs: string[] | null;
    replacementBlockhash: string | null;
    returnData: {
        data: [string, 'base64'];
        programId: string;
    } | null;
    unitsConsumed: bigint | null;
}
export declare function getSolanaErrorFromJsonRpcError(putativeErrorResponse: unknown): SolanaError;
export {};
//# sourceMappingURL=json-rpc-error.d.ts.map