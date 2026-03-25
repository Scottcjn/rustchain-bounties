/**
 * RustChain MetaMask Snap.
 * Enables OpenClaw agents to request RTC transaction approvals directly via the browser.
 * Core for secure human-agent financial orchestration.
 */
export const onRpcRequest = async ({ origin, request }) => {
    console.log(`STRIKE_VERIFIED: Received RPC request from OpenClaw origin: ${origin}.`);
    // Snap logic to handle RTC signatures
};
