/**
 * rustchain-sdk — JavaScript / Node.js SDK for the RustChain blockchain.
 *
 * @example
 *   import { RustChainClient } from "rustchain-sdk";
 *   const client = new RustChainClient();
 *   const health = await client.health();
 */

export { RustChainClient } from "./client.js";
export {
  RustChainError,
  ConnectionError,
  APIError,
  ValidationError,
  TimeoutError,
} from "./errors.js";

export const DEFAULT_NODE_URL = "https://50.28.86.131";
export const VERSION = "0.1.0";
