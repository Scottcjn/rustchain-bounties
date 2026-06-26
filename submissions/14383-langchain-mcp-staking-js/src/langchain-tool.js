import { StakeAndAcquireClient } from "./core.js";

export const stakeAndAcquireSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    skill: {
      type: "string",
      description: "Skill or capability to acquire, for example self-improve:lint.",
    },
    bond_rtc: {
      type: "number",
      description: "RTC bond to stake for the acquisition attempt.",
      exclusiveMinimum: 0,
    },
    agent: {
      type: "string",
      description: "Public agent identifier to bind into the canonical request.",
    },
    metadata: {
      type: "object",
      description: "Optional public metadata such as repo, run id, or policy tag.",
    },
  },
  required: ["skill", "bond_rtc"],
};

export class ElyanStakeAndAcquireTool {
  constructor(options = {}) {
    this.name = options.name || "stake_and_acquire";
    this.description = options.description || [
      "Stake RTC to acquire a self-improvement skill through the open Elyan gate.",
      "Returns a verified signed attestation on success.",
      "If the gate is unavailable or denies the request, returns refunded=true with the reason.",
    ].join(" ");
    this.schema = stakeAndAcquireSchema;
    this.client = options.client || new StakeAndAcquireClient(options);
  }

  async call(input) {
    return JSON.stringify(await this.invoke(input));
  }

  async _call(input) {
    return this.call(input);
  }

  async invoke(input) {
    return this.client.stakeAndAcquire(input);
  }
}

export async function createLangChainTool(options = {}) {
  let DynamicStructuredTool;
  let z;

  try {
    ({ DynamicStructuredTool } = await import("@langchain/core/tools"));
    ({ z } = await import("zod"));
  } catch {
    return new ElyanStakeAndAcquireTool(options);
  }

  const client = options.client || new StakeAndAcquireClient(options);
  return new DynamicStructuredTool({
    name: options.name || "stake_and_acquire",
    description: options.description || "Stake RTC for self-improvement and return verified attestation or refunded fail-safe result.",
    schema: z.object({
      skill: z.string().min(1),
      bond_rtc: z.number().positive(),
      agent: z.string().optional(),
      metadata: z.record(z.unknown()).optional(),
    }),
    func: async (input) => JSON.stringify(await client.stakeAndAcquire(input)),
  });
}
