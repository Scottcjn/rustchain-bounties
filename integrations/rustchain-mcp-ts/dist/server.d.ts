/**
 * RustChain MCP Server
 *
 * Exposes RustChain network tools via the Model Context Protocol so any
 * MCP-compatible IDE (Claude Code, Cursor, Windsurf, VS Code Copilot …)
 * can query the chain directly from the terminal.
 *
 * Tools
 * -----
 * rustchain_health            — node health with automatic failover
 * rustchain_balance            — RTC balance for a wallet / miner_id
 * rustchain_miners             — list active miners and architectures
 * rustchain_epoch              — current epoch info (slot, height, rewards)
 * rustchain_create_wallet      — register a new agent wallet on the network
 * rustchain_submit_attestation — submit a hardware fingerprint for a miner
 * rustchain_bounties           — list open RustChain bounties from this repo
 */
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
declare const server: Server<{
    method: string;
    params?: {
        [x: string]: unknown;
        _meta?: {
            [x: string]: unknown;
            progressToken?: string | number | undefined;
            "io.modelcontextprotocol/related-task"?: {
                taskId: string;
            } | undefined;
        } | undefined;
    } | undefined;
}, {
    method: string;
    params?: {
        [x: string]: unknown;
        _meta?: {
            [x: string]: unknown;
            progressToken?: string | number | undefined;
            "io.modelcontextprotocol/related-task"?: {
                taskId: string;
            } | undefined;
        } | undefined;
    } | undefined;
}, {
    [x: string]: unknown;
    _meta?: {
        [x: string]: unknown;
        progressToken?: string | number | undefined;
        "io.modelcontextprotocol/related-task"?: {
            taskId: string;
        } | undefined;
    } | undefined;
}>;
export { server };
//# sourceMappingURL=server.d.ts.map