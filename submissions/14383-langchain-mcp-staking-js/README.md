# LangChain + MCP Staking Tool

JavaScript/TypeScript-friendly delivery for bounty #14383. It wraps the open Elyan staking gate as:

- a LangChain-compatible `stake_and_acquire` tool
- a dependency-free MCP stdio server exposing the same tool
- a shared verifier that returns a signed verdict plus on-chain attestation on success

The package is dependency-free for tests and runtime smoke checks. If `@langchain/core` and `zod` are installed, `createLangChainTool()` returns a real `DynamicStructuredTool`; otherwise it returns a compatible fallback object with `name`, `description`, `schema`, `call()`, `_call()`, and `invoke()`.

## Quickstart: LangChain JS

```js
import { createLangChainTool } from "./src/index.js";

const tool = await createLangChainTool({
  gateUrl: process.env.ELYAN_GATE_URL,
  apiKey: process.env.ELYAN_GATE_API_KEY,
  gatePublicKeyPem: process.env.ELYAN_GATE_PUBLIC_KEY_PEM,
});

const resultJson = await tool.call({
  skill: "self-improve:tests",
  bond_rtc: 2,
  agent: "my-agent",
  metadata: { repo: "owner/repo", run: "ci-123" },
});

console.log(JSON.parse(resultJson));
```

## Quickstart: MCP

```bash
cd submissions/14383-langchain-mcp-staking-js
ELYAN_GATE_URL=https://gate.example.com \
ELYAN_GATE_API_KEY=... \
ELYAN_GATE_PUBLIC_KEY_PEM="$(cat gate.pub.pem)" \
node src/mcp-server.mjs
```

MCP tool:

```json
{
  "name": "stake_and_acquire",
  "arguments": {
    "skill": "self-improve:lint",
    "bond_rtc": 1,
    "agent": "my-agent"
  }
}
```

## Fail-Safe Semantics

The tool never hides stake safety from the caller:

- gate available + verdict passes + signature/attestation verify: `ok: true`, `refunded: false`
- gate returns 4xx/5xx or network failure: `ok: false`, `refunded: true`, `refund_reason: "gate_unavailable"`
- gate denies the skill: `ok: false`, `refunded: true`, `refund_reason: "gate_denied"`
- signature or attestation verification fails: `ok: false`, `refunded: true`, `refund_reason: "verification_failed"`

Successful results verify:

- Ed25519 signature over canonical JSON
- configured gate public key match
- attestation status
- request hash
- verdict hash

## Environment

```text
ELYAN_GATE_URL=https://gate.example.com
ELYAN_GATE_PATH=/stake
ELYAN_GATE_API_KEY=optional-bearer-token
ELYAN_GATE_PUBLIC_KEY_PEM=-----BEGIN PUBLIC KEY-----...
ELYAN_AGENT_ID=lxx197818
```

## Tests

```bash
node --test test/stake-and-acquire.test.mjs
```

Covered cases:

- successful LangChain/MCP staking call
- signed Ed25519 verdict verification
- confirmed attestation hash verification
- gate unavailable refund path
- gate denial refund path
- invalid signature fail-closed path
- MCP `tools/list` and `tools/call`

Wallet ID for claim: `lxx197818`
