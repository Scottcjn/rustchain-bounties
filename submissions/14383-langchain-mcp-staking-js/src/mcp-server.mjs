#!/usr/bin/env node
import { createInterface } from "node:readline";
import { stdin as input, stdout as output } from "node:process";
import { fileURLToPath } from "node:url";

import { StakeAndAcquireClient } from "./core.js";
import { stakeAndAcquireSchema } from "./langchain-tool.js";

export const toolDefinition = {
  name: "stake_and_acquire",
  description: "Stake RTC to acquire a self-improvement skill and return a verified attestation or refunded fail-safe result.",
  inputSchema: stakeAndAcquireSchema,
};

function rpcResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}

function rpcError(id, code, message, data = undefined) {
  return { jsonrpc: "2.0", id, error: { code, message, ...(data ? { data } : {}) } };
}

export async function handleMcpMessage(message, { client = new StakeAndAcquireClient() } = {}) {
  if (message.method === "initialize") {
    return rpcResult(message.id, {
      protocolVersion: "2025-11-25",
      serverInfo: {
        name: "elyan-staking-agent-tools",
        version: "0.1.0",
      },
      capabilities: {
        tools: {},
      },
    });
  }

  if (message.method === "tools/list") {
    return rpcResult(message.id, { tools: [toolDefinition] });
  }

  if (message.method === "tools/call") {
    if (message.params?.name !== "stake_and_acquire") {
      return rpcError(message.id, -32602, "unknown tool", { name: message.params?.name });
    }
    const result = await client.stakeAndAcquire(message.params?.arguments || {});
    return rpcResult(message.id, {
      content: [
        {
          type: "text",
          text: JSON.stringify(result, null, 2),
        },
      ],
      isError: result.ok === false,
    });
  }

  if (message.method === "notifications/initialized") {
    return undefined;
  }

  return rpcError(message.id, -32601, "method not found", { method: message.method });
}

export async function runStdioServer({ client = new StakeAndAcquireClient() } = {}) {
  const rl = createInterface({ input, crlfDelay: Infinity });
  for await (const line of rl) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    let response;
    try {
      response = await handleMcpMessage(JSON.parse(trimmed), { client });
    } catch (error) {
      response = rpcError(null, -32603, "internal error", { error: error.message });
    }

    if (response) output.write(`${JSON.stringify(response)}\n`);
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  runStdioServer();
}
