import { SolanaErrorCode } from './codes';
export declare function getHumanReadableErrorMessage<TErrorCode extends SolanaErrorCode>(code: TErrorCode, context?: object): string;
export declare function getErrorMessage<TErrorCode extends SolanaErrorCode>(code: TErrorCode, context?: Record<string, unknown>): string;
//# sourceMappingURL=message-formatter.d.ts.map